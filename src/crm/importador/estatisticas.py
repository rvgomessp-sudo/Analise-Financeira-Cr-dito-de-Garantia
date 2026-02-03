"""
Estatísticas de Importação

Acumula métricas durante o processo de importação das bases PGFN,
gerando resumo executivo e distribuições por temperatura, porte,
UF e situação especial (RJ/Falência).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


def _fmt_brl(v: float) -> str:
    """Formata valor em BRL resumido"""
    if v >= 1e12:
        return f"R$ {v/1e12:,.2f} tri"
    if v >= 1e9:
        return f"R$ {v/1e9:,.2f} bi"
    if v >= 1e6:
        return f"R$ {v/1e6:,.2f} mi"
    if v >= 1e3:
        return f"R$ {v/1e3:,.2f} mil"
    return f"R$ {v:,.2f}"


@dataclass
class EstatisticasImportacao:
    """Acumula estatísticas durante a importação das bases PGFN."""

    # Contadores gerais
    total_linhas: int = 0
    total_contas: int = 0
    duplicados: int = 0
    oportunidades_geradas: int = 0

    # Por temperatura
    por_temperatura: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Por porte estimado
    por_porte: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Por UF
    por_uf: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Situações especiais
    recuperacao_judicial: int = 0
    falencia: int = 0

    # Valores agregados
    soma_divida_total: float = 0.0
    soma_potencial_sg: float = 0.0
    soma_valor_descoberto: float = 0.0
    soma_valor_garantia_ineficiente: float = 0.0

    # Maior conta (por potencial SG)
    maior_potencial_cnpj: str = ""
    maior_potencial_nome: str = ""
    maior_potencial_valor: float = 0.0

    # Erros
    erros: List[str] = field(default_factory=list)

    # Arquivos processados
    arquivos: List[Dict] = field(default_factory=list)

    # Timestamps
    inicio: datetime = field(default_factory=datetime.now)
    fim: Optional[datetime] = None

    def registrar_conta(self, conta) -> None:
        """Registra métricas de uma conta importada."""
        self.total_contas += 1

        # Temperatura
        if conta.temperatura:
            self.por_temperatura[conta.temperatura.name] += 1

        # Porte
        if conta.porte:
            self.por_porte[conta.porte.name] += 1

        # UF
        if conta.endereco_fiscal and conta.endereco_fiscal.uf:
            self.por_uf[conta.endereco_fiscal.uf] += 1

        # Situação especial
        if 'recuperacao_judicial' in conta.tags:
            self.recuperacao_judicial += 1
        if 'falencia' in conta.tags:
            self.falencia += 1

        # Valores
        if conta.dados_pgfn:
            pgfn = conta.dados_pgfn
            self.soma_divida_total += pgfn.divida_total
            self.soma_potencial_sg += pgfn.potencial_sg
            self.soma_valor_descoberto += pgfn.valor_descoberto
            self.soma_valor_garantia_ineficiente += pgfn.valor_garantia_ineficiente

            # Rastrear maior potencial
            if pgfn.potencial_sg > self.maior_potencial_valor:
                self.maior_potencial_valor = pgfn.potencial_sg
                self.maior_potencial_cnpj = conta.cnpj
                self.maior_potencial_nome = conta.razao_social

    def registrar_arquivo(self, nome: str, temperatura: str, qtd: int) -> None:
        """Registra arquivo processado."""
        self.arquivos.append({
            'arquivo': nome,
            'temperatura': temperatura,
            'contas': qtd,
        })

    def registrar_erro(self, mensagem: str) -> None:
        """Registra erro durante importação."""
        self.erros.append(mensagem)

    def finalizar(self) -> None:
        """Marca fim da importação."""
        self.fim = datetime.now()

    @property
    def duracao_segundos(self) -> float:
        if self.fim:
            return (self.fim - self.inicio).total_seconds()
        return (datetime.now() - self.inicio).total_seconds()

    @property
    def top_ufs(self) -> List[tuple]:
        """Top 10 UFs por quantidade de contas"""
        return sorted(
            self.por_uf.items(), key=lambda x: x[1], reverse=True
        )[:10]

    def gerar_resumo(self) -> str:
        """Gera resumo textual completo da importação."""
        linhas = []
        linhas.append("=" * 80)
        linhas.append("  RESUMO DA IMPORTAÇÃO — BASES PGFN MARCO ZERO")
        linhas.append("=" * 80)

        # Geral
        linhas.append(f"\n  Arquivos processados: {len(self.arquivos)}")
        for arq in self.arquivos:
            linhas.append(
                f"    {arq['temperatura']:>5}: {arq['arquivo']} "
                f"({arq['contas']:,} contas)"
            )

        linhas.append(f"\n  Total de linhas lidas:        {self.total_linhas:>10,}")
        linhas.append(f"  Total de contas criadas:      {self.total_contas:>10,}")
        linhas.append(f"  Duplicados removidos:         {self.duplicados:>10,}")
        linhas.append(f"  Oportunidades geradas:        {self.oportunidades_geradas:>10,}")

        # Temperatura
        linhas.append(f"\n  Por Temperatura:")
        for temp in ['HOT', 'WARM', 'COLD']:
            qtd = self.por_temperatura.get(temp, 0)
            pct = qtd / self.total_contas * 100 if self.total_contas else 0
            linhas.append(f"    {temp:>5}: {qtd:>10,}  ({pct:>5.1f}%)")

        # Porte
        linhas.append(f"\n  Por Porte Estimado:")
        for porte in ['GRANDE', 'MEDIO', 'PEQUENO', 'MICRO', 'MEI']:
            qtd = self.por_porte.get(porte, 0)
            pct = qtd / self.total_contas * 100 if self.total_contas else 0
            linhas.append(f"    {porte:>8}: {qtd:>10,}  ({pct:>5.1f}%)")

        # Situações especiais
        linhas.append(f"\n  Situações Especiais:")
        linhas.append(f"    Recuperação Judicial:  {self.recuperacao_judicial:>10,}")
        linhas.append(f"    Falência:              {self.falencia:>10,}")

        # Valores
        linhas.append(f"\n  Valores Agregados:")
        linhas.append(f"    Dívida Total:                 {_fmt_brl(self.soma_divida_total):>20}")
        linhas.append(f"    Potencial SG:                 {_fmt_brl(self.soma_potencial_sg):>20}")
        linhas.append(f"    Valor Descoberto:             {_fmt_brl(self.soma_valor_descoberto):>20}")
        linhas.append(f"    Garantia Ineficiente:         {_fmt_brl(self.soma_valor_garantia_ineficiente):>20}")

        # Maior potencial
        if self.maior_potencial_valor > 0:
            linhas.append(f"\n  Maior Potencial SG:")
            linhas.append(f"    {self.maior_potencial_nome[:60]}")
            linhas.append(f"    CNPJ: {self.maior_potencial_cnpj}")
            linhas.append(f"    Potencial: {_fmt_brl(self.maior_potencial_valor)}")

        # Top UFs
        if self.top_ufs:
            linhas.append(f"\n  Top 10 UFs:")
            for uf, qtd in self.top_ufs:
                pct = qtd / self.total_contas * 100 if self.total_contas else 0
                barra = '#' * int(pct / 2)
                linhas.append(f"    {uf:>2}: {qtd:>10,}  ({pct:>5.1f}%)  {barra}")

        # Erros
        if self.erros:
            linhas.append(f"\n  Erros ({len(self.erros)}):")
            for erro in self.erros[:10]:
                linhas.append(f"    - {erro}")
            if len(self.erros) > 10:
                linhas.append(f"    ... e mais {len(self.erros) - 10} erros")

        # Tempo
        linhas.append(f"\n  Tempo de processamento: {self.duracao_segundos:.1f}s")
        linhas.append("=" * 80)

        return "\n".join(linhas)

    def to_dict(self) -> Dict:
        return {
            'total_linhas': self.total_linhas,
            'total_contas': self.total_contas,
            'duplicados': self.duplicados,
            'oportunidades_geradas': self.oportunidades_geradas,
            'por_temperatura': dict(self.por_temperatura),
            'por_porte': dict(self.por_porte),
            'por_uf': dict(self.por_uf),
            'recuperacao_judicial': self.recuperacao_judicial,
            'falencia': self.falencia,
            'soma_divida_total': self.soma_divida_total,
            'soma_potencial_sg': self.soma_potencial_sg,
            'soma_valor_descoberto': self.soma_valor_descoberto,
            'soma_valor_garantia_ineficiente': self.soma_valor_garantia_ineficiente,
            'maior_potencial': {
                'cnpj': self.maior_potencial_cnpj,
                'nome': self.maior_potencial_nome,
                'valor': self.maior_potencial_valor,
            },
            'top_ufs': self.top_ufs,
            'erros': len(self.erros),
            'duracao_segundos': round(self.duracao_segundos, 1),
        }
