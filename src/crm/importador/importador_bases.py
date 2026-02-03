"""
Importador de Bases PGFN Marco Zero

Lê os 3 CSVs segmentados (hot/warm/cold) e converte para objetos CRM:
    - Cria Conta com DadosPGFN para cada CNPJ
    - Gera Oportunidades automáticas por tipo de conversão
    - Classifica porte estimado a partir da dívida/ticket
    - Detecta empresas em Recuperação Judicial / Falência no nome

Formato CSV esperado (separador ;):
    CPF_CNPJ;NOME;UF;REGIAO;TEMPERATURA;QTD_INSCRICOES;DIVIDA_TOTAL;
    TICKET_MEDIO;ANO_MIN;ANO_MAX;QTD_SEGURO_GARANTIA;QTD_CARTA_FIANCA;
    QTD_DEPOSITO;QTD_PENHORA;QTD_SEM_GARANTIA;VALOR_DESCOBERTO;
    VALOR_GARANTIA_INEFICIENTE;POTENCIAL_SG
"""

import csv
import re
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from src.crm.models.conta import (
    Conta, PorteEmpresa, SituacaoCadastral, DadosPGFN, TemperaturaLead,
)
from src.crm.models.oportunidade import (
    Oportunidade, TipoGarantiaOportunidade, EtapaOportunidade,
)
from src.crm.importador.estatisticas import EstatisticasImportacao


# Termos para detecção de RJ/Falência (mesma lógica do validacao_base_grande.py)
TERMOS_RJ = [
    'RECUPERACAO JUDICIAL', 'RECUPERAÇÃO JUDICIAL',
    'EM RECUPERACAO', 'EM RECUPERAÇÃO',
    'RECUPERACAO JUD', 'RECUPERAÇÃO JUD',
]
TERMOS_FALENCIA = [
    'FALENCIA', 'FALÊNCIA', 'MASSA FALIDA',
    'EM FALENCIA', 'EM FALÊNCIA',
]


def _safe_float(val: str) -> float:
    """Converte string para float, retorna 0.0 se inválido"""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _safe_int(val: str) -> int:
    """Converte string para int, retorna 0 se inválido"""
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _safe_int_or_none(val: str) -> Optional[int]:
    """Converte string para int, retorna None se inválido"""
    try:
        v = int(float(val))
        return v if v > 0 else None
    except (ValueError, TypeError):
        return None


def detectar_situacao_nome(nome: str) -> Optional[str]:
    """
    Detecta Recuperação Judicial ou Falência pelo nome da empresa.
    Retorna 'RECUPERACAO_JUDICIAL', 'FALENCIA' ou None.
    """
    if not nome:
        return None
    nome_upper = nome.upper()
    for termo in TERMOS_FALENCIA:
        if termo in nome_upper:
            return 'FALENCIA'
    for termo in TERMOS_RJ:
        if termo in nome_upper:
            return 'RECUPERACAO_JUDICIAL'
    return None


def estimar_porte_por_divida(divida_total: float, ticket_medio: float) -> PorteEmpresa:
    """
    Estima porte da empresa com base no volume de dívida e ticket médio.

    Heurística (na ausência de faturamento real):
        - Dívida > R$ 100M  ou ticket > R$ 10M  → GRANDE
        - Dívida > R$  10M  ou ticket > R$  1M  → MEDIO
        - Dívida > R$   1M  ou ticket > R$ 100k → PEQUENO
        - Dívida > R$ 100k                      → MICRO
        - Demais                                 → MEI
    """
    if divida_total > 100_000_000 or ticket_medio > 10_000_000:
        return PorteEmpresa.GRANDE
    if divida_total > 10_000_000 or ticket_medio > 1_000_000:
        return PorteEmpresa.MEDIO
    if divida_total > 1_000_000 or ticket_medio > 100_000:
        return PorteEmpresa.PEQUENO
    if divida_total > 100_000:
        return PorteEmpresa.MICRO
    return PorteEmpresa.MEI


class ImportadorBasesPGFN:
    """
    Importador das bases PGFN Marco Zero para o CRM.

    Lê os 3 CSVs (hot, warm, cold) e converte cada linha em:
        - 1 Conta com DadosPGFN preenchido
        - 0 ou mais Oportunidades (conforme potencial e tipo de conversão)

    Uso:
        importador = ImportadorBasesPGFN(diretorio=".")
        contas, oportunidades, stats = importador.importar_todas()
    """

    MAPA_TEMPERATURA = {
        'HOT': TemperaturaLead.HOT,
        'WARM': TemperaturaLead.WARM,
        'COLD': TemperaturaLead.COLD,
    }

    def __init__(self, diretorio: str = "."):
        self.diretorio = Path(diretorio)
        self._contador_contas = 0
        self._contador_oportunidades = 0

    # ================================================================
    # PÚBLICO
    # ================================================================

    def importar_todas(
        self,
        arquivo_hot: str = "base_brasil_marco_zero_hot_LIMPA.csv",
        arquivo_warm: str = "base_brasil_marco_zero_warm_LIMPA.csv",
        arquivo_cold: str = "base_brasil_marco_zero_cold_LIMPA.csv",
        limite_cold: Optional[int] = None,
    ) -> Tuple[List[Conta], List[Oportunidade], EstatisticasImportacao]:
        """
        Importa todas as bases.

        Args:
            arquivo_hot:  Nome do CSV HOT
            arquivo_warm: Nome do CSV WARM
            arquivo_cold: Nome do CSV COLD
            limite_cold:  Limitar nº de registros COLD (útil para testes).
                          None = carregar todos.

        Returns:
            (contas, oportunidades, estatísticas)
        """
        stats = EstatisticasImportacao()
        contas: List[Conta] = []
        oportunidades: List[Oportunidade] = []

        for nome_arquivo, temp_esperada in [
            (arquivo_hot, 'HOT'),
            (arquivo_warm, 'WARM'),
            (arquivo_cold, 'COLD'),
        ]:
            limite = limite_cold if temp_esperada == 'COLD' and limite_cold else None
            caminho = self.diretorio / nome_arquivo
            if not caminho.exists():
                stats.registrar_erro(f"Arquivo não encontrado: {caminho}")
                continue

            c, o = self._importar_arquivo(caminho, temp_esperada, stats, limite)
            contas.extend(c)
            oportunidades.extend(o)

        stats.finalizar()
        return contas, oportunidades, stats

    def importar_arquivo_unico(
        self,
        caminho: str,
        temperatura_padrao: str = "COLD",
        limite: Optional[int] = None,
    ) -> Tuple[List[Conta], List[Oportunidade], EstatisticasImportacao]:
        """Importa um único arquivo CSV."""
        stats = EstatisticasImportacao()
        path = Path(caminho)
        if not path.exists():
            stats.registrar_erro(f"Arquivo não encontrado: {path}")
            stats.finalizar()
            return [], [], stats

        contas, oportunidades = self._importar_arquivo(
            path, temperatura_padrao, stats, limite,
        )
        stats.finalizar()
        return contas, oportunidades, stats

    # ================================================================
    # INTERNO
    # ================================================================

    def _importar_arquivo(
        self,
        caminho: Path,
        temp_esperada: str,
        stats: EstatisticasImportacao,
        limite: Optional[int] = None,
    ) -> Tuple[List[Conta], List[Oportunidade]]:
        """Lê um CSV e retorna listas de Conta e Oportunidade."""
        contas: List[Conta] = []
        oportunidades: List[Oportunidade] = []
        cnpjs_vistos: set = set()

        with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for i, row in enumerate(reader):
                if limite and i >= limite:
                    break

                stats.total_linhas += 1
                cnpj_raw = row.get('CPF_CNPJ', '').strip()

                # Pular se CNPJ vazio
                if not cnpj_raw:
                    stats.registrar_erro("Linha sem CPF_CNPJ")
                    continue

                # Deduplicar dentro do mesmo arquivo
                cnpj_normalizado = re.sub(r'[^0-9]', '', cnpj_raw)
                if cnpj_normalizado in cnpjs_vistos:
                    stats.duplicados += 1
                    continue
                cnpjs_vistos.add(cnpj_normalizado)

                # Converter linha → Conta
                try:
                    conta = self._linha_para_conta(row, temp_esperada)
                    contas.append(conta)
                    stats.registrar_conta(conta)
                except Exception as e:
                    stats.registrar_erro(
                        f"Erro ao converter CNPJ {cnpj_raw}: {e}"
                    )
                    continue

                # Gerar Oportunidades automáticas
                ops = self._gerar_oportunidades(conta)
                oportunidades.extend(ops)
                stats.oportunidades_geradas += len(ops)

        stats.registrar_arquivo(caminho.name, temp_esperada, len(contas))
        return contas, oportunidades

    def _linha_para_conta(self, row: Dict[str, str], temp_esperada: str) -> Conta:
        """Converte uma linha CSV em uma Conta com DadosPGFN."""
        self._contador_contas += 1

        cnpj_raw = row.get('CPF_CNPJ', '').strip()
        nome = row.get('NOME', '').strip()
        uf = row.get('UF', '').strip()
        regiao = row.get('REGIAO', '').strip()
        temperatura_csv = row.get('TEMPERATURA', temp_esperada).strip().upper()

        divida_total = _safe_float(row.get('DIVIDA_TOTAL', '0'))
        ticket_medio = _safe_float(row.get('TICKET_MEDIO', '0'))

        # Dados PGFN
        dados_pgfn = DadosPGFN(
            uf=uf,
            regiao=regiao,
            qtd_inscricoes=_safe_int(row.get('QTD_INSCRICOES', '0')),
            divida_total=divida_total,
            ticket_medio=ticket_medio,
            ano_min=_safe_int_or_none(row.get('ANO_MIN', '')),
            ano_max=_safe_int_or_none(row.get('ANO_MAX', '')),
            qtd_seguro_garantia=_safe_int(row.get('QTD_SEGURO_GARANTIA', '0')),
            qtd_carta_fianca=_safe_int(row.get('QTD_CARTA_FIANCA', '0')),
            qtd_deposito=_safe_int(row.get('QTD_DEPOSITO', '0')),
            qtd_penhora=_safe_int(row.get('QTD_PENHORA', '0')),
            qtd_sem_garantia=_safe_int(row.get('QTD_SEM_GARANTIA', '0')),
            valor_descoberto=_safe_float(row.get('VALOR_DESCOBERTO', '0')),
            valor_garantia_ineficiente=_safe_float(
                row.get('VALOR_GARANTIA_INEFICIENTE', '0')
            ),
            potencial_sg=_safe_float(row.get('POTENCIAL_SG', '0')),
        )

        # Detectar RJ/Falência
        situacao_nome = detectar_situacao_nome(nome)
        situacao_cadastral = SituacaoCadastral.NAO_VERIFICADA
        tags = []
        if situacao_nome == 'RECUPERACAO_JUDICIAL':
            tags.append('recuperacao_judicial')
        elif situacao_nome == 'FALENCIA':
            tags.append('falencia')

        # Temperatura
        temperatura = self.MAPA_TEMPERATURA.get(
            temperatura_csv, TemperaturaLead.COLD
        )
        tags.append(f'pgfn_{temperatura.name.lower()}')
        tags.append('marco_zero')

        # Porte estimado
        porte = estimar_porte_por_divida(divida_total, ticket_medio)

        conta = Conta(
            id=f"PGFN-{self._contador_contas:06d}",
            cnpj=cnpj_raw,
            razao_social=nome,
            situacao_cadastral=situacao_cadastral,
            porte=porte,
            temperatura=temperatura,
            regiao=regiao,
            dados_pgfn=dados_pgfn,
            tags=tags,
            segmento="Seguro Garantia Judicial",
            fonte_enriquecimento="PGFN Marco Zero",
        )

        # Preencher UF no endereço fiscal (somente UF disponível)
        if uf:
            from src.crm.models.conta import Endereco
            conta.endereco_fiscal = Endereco(
                tipo="Fiscal", logradouro="", numero="", uf=uf,
            )

        return conta

    def _gerar_oportunidades(self, conta: Conta) -> List[Oportunidade]:
        """
        Gera oportunidades automáticas conforme perfil da conta.

        Regras:
            HOT  → Oportunidade de cross-sell (ampliar SG p/ inscrições descobertas)
            WARM → Oportunidade de conversão (substituir carta fiança/depósito por SG)
            COLD → Oportunidade de new business (se potencial > R$ 1M)
        """
        oportunidades: List[Oportunidade] = []
        if not conta.dados_pgfn:
            return oportunidades

        pgfn = conta.dados_pgfn

        if conta.temperatura == TemperaturaLead.HOT:
            # Cross-sell: já usa SG, tem valor descoberto
            if pgfn.valor_descoberto > 0:
                self._contador_oportunidades += 1
                op = Oportunidade(
                    id=f"OP-PGFN-{self._contador_oportunidades:06d}",
                    conta_id=conta.id,
                    nome=f"Cross-sell SG Judicial — {conta.razao_social[:50]}",
                    tipo_garantia=TipoGarantiaOportunidade.JUDICIAL,
                    etapa=EtapaOportunidade.QUALIFICACAO_PJ,
                    valor_garantia=Decimal(str(pgfn.valor_descoberto)),
                    observacoes=(
                        f"Conta HOT: já possui {pgfn.qtd_seguro_garantia} SG. "
                        f"Valor descoberto: R$ {pgfn.valor_descoberto:,.2f}. "
                        f"Total inscrições: {pgfn.qtd_inscricoes}."
                    ),
                )
                oportunidades.append(op)

        elif conta.temperatura == TemperaturaLead.WARM:
            # Conversão: substituir garantias ineficientes por SG
            if pgfn.valor_garantia_ineficiente > 0:
                self._contador_oportunidades += 1
                op = Oportunidade(
                    id=f"OP-PGFN-{self._contador_oportunidades:06d}",
                    conta_id=conta.id,
                    nome=f"Conversão p/ SG — {conta.razao_social[:50]}",
                    tipo_garantia=TipoGarantiaOportunidade.JUDICIAL,
                    etapa=EtapaOportunidade.PESQUISA_SINAIS,
                    valor_garantia=Decimal(str(pgfn.valor_garantia_ineficiente)),
                    observacoes=(
                        f"Conta WARM: {pgfn.qtd_carta_fianca} carta(s) fiança, "
                        f"{pgfn.qtd_deposito} depósito(s). "
                        f"Valor garantia ineficiente: R$ {pgfn.valor_garantia_ineficiente:,.2f}. "
                        f"Potencial SG: R$ {pgfn.potencial_sg:,.2f}."
                    ),
                )
                oportunidades.append(op)

            # Se também tem valor descoberto, gerar segunda oportunidade
            if pgfn.valor_descoberto > 0:
                self._contador_oportunidades += 1
                op2 = Oportunidade(
                    id=f"OP-PGFN-{self._contador_oportunidades:06d}",
                    conta_id=conta.id,
                    nome=f"Nova SG (descoberto) — {conta.razao_social[:50]}",
                    tipo_garantia=TipoGarantiaOportunidade.JUDICIAL,
                    etapa=EtapaOportunidade.PESQUISA_SINAIS,
                    valor_garantia=Decimal(str(pgfn.valor_descoberto)),
                    observacoes=(
                        f"Conta WARM: valor sem nenhuma garantia: "
                        f"R$ {pgfn.valor_descoberto:,.2f}."
                    ),
                )
                oportunidades.append(op2)

        elif conta.temperatura == TemperaturaLead.COLD:
            # New business: só se potencial relevante (> R$ 1M)
            if pgfn.potencial_sg > 1_000_000:
                self._contador_oportunidades += 1
                op = Oportunidade(
                    id=f"OP-PGFN-{self._contador_oportunidades:06d}",
                    conta_id=conta.id,
                    nome=f"Prospecção SG Judicial — {conta.razao_social[:50]}",
                    tipo_garantia=TipoGarantiaOportunidade.JUDICIAL,
                    etapa=EtapaOportunidade.PESQUISA_SINAIS,
                    valor_garantia=Decimal(str(pgfn.potencial_sg)),
                    observacoes=(
                        f"Conta COLD: {pgfn.qtd_inscricoes} inscrições, "
                        f"nenhuma garantia. "
                        f"Potencial SG: R$ {pgfn.potencial_sg:,.2f}."
                    ),
                )
                oportunidades.append(op)

        return oportunidades
