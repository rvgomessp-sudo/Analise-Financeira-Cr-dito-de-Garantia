"""
Enriquecedor de Dados

Motor de enriquecimento de contas PJ.
Em produção, integra com APIs externas (Receita Federal, PNCP, etc.).
Aqui implementa a lógica de orquestração e regras de qualidade.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Callable

from src.crm.models.conta import (
    Conta, PorteEmpresa, SituacaoCadastral,
    TipoEstabelecimento, Endereco, StatusDados,
)
from src.crm.enriquecimento.validador_cnpj import ValidadorCNPJ


@dataclass
class ResultadoEnriquecimento:
    """Resultado do processo de enriquecimento"""
    conta_id: str
    cnpj: str
    sucesso: bool
    campos_atualizados: List[str] = field(default_factory=list)
    campos_faltantes: List[str] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    fonte: str = ""
    data_enriquecimento: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'conta_id': self.conta_id,
            'cnpj': self.cnpj,
            'sucesso': self.sucesso,
            'campos_atualizados': self.campos_atualizados,
            'campos_faltantes': self.campos_faltantes,
            'erros': self.erros,
            'fonte': self.fonte,
        }


class Enriquecedor:
    """
    Motor de enriquecimento de dados PJ.

    Modos de operação:
        - Tempo real: ao criar/editar conta
        - Batch: jobs diários/semanais

    Fontes (plugáveis via callbacks):
        - Receita Federal (CNPJ, situação, CNAE, porte)
        - PNCP (editais, contratos públicos)
        - Notícias (mudanças societárias, mercado)
        - Dados financeiros (balanços públicos)
    """

    def __init__(self):
        self.validador_cnpj = ValidadorCNPJ()
        self._fontes: Dict[str, Callable] = {}
        self._regras_qualidade: List[Callable] = []

    def registrar_fonte(self, nome: str, callback: Callable) -> None:
        """
        Registra uma fonte de enriquecimento.

        O callback recebe o CNPJ e retorna Dict com dados ou None.
        Ex: {'razao_social': '...', 'cnae_principal': '...', ...}
        """
        self._fontes[nome] = callback

    def registrar_regra_qualidade(self, callback: Callable) -> None:
        """
        Registra regra de qualidade pós-enriquecimento.

        O callback recebe a Conta e retorna List[str] de problemas.
        """
        self._regras_qualidade.append(callback)

    def enriquecer_conta(self, conta: Conta,
                         fontes: List[str] = None) -> ResultadoEnriquecimento:
        """
        Enriquece uma conta com dados de fontes externas.

        Fluxo:
            1. Valida CNPJ
            2. Consulta fontes registradas
            3. Aplica dados ao objeto Conta
            4. Executa regras de qualidade
            5. Marca conta como verificada ou com erro
        """
        resultado = ResultadoEnriquecimento(
            conta_id=conta.id,
            cnpj=conta.cnpj,
            sucesso=False,
        )

        # 1. Validar CNPJ
        validacao = self.validador_cnpj.validar(conta.cnpj)
        if not validacao.valido:
            resultado.erros.append(f"CNPJ inválido: {validacao.erro}")
            conta.status_dados = StatusDados.ERRO_VALIDACAO
            return resultado

        # 2. Consultar fontes
        fontes_usar = fontes or list(self._fontes.keys())
        dados_consolidados = {}

        for nome_fonte in fontes_usar:
            if nome_fonte not in self._fontes:
                resultado.erros.append(f"Fonte '{nome_fonte}' não registrada")
                continue

            try:
                dados = self._fontes[nome_fonte](conta.cnpj)
                if dados:
                    dados_consolidados.update(dados)
                    resultado.fonte = nome_fonte
            except Exception as e:
                resultado.erros.append(f"Erro na fonte '{nome_fonte}': {str(e)}")

        # 3. Aplicar dados
        if dados_consolidados:
            campos = self._aplicar_dados(conta, dados_consolidados)
            resultado.campos_atualizados = campos

        # 4. Regras de qualidade
        for regra in self._regras_qualidade:
            try:
                problemas = regra(conta)
                if problemas:
                    resultado.campos_faltantes.extend(problemas)
            except Exception as e:
                resultado.erros.append(f"Erro em regra de qualidade: {str(e)}")

        # 5. Marcar status
        if resultado.campos_atualizados and not resultado.erros:
            conta.marcar_verificado(fonte=resultado.fonte or "Enriquecimento")
            resultado.sucesso = True
        elif resultado.campos_atualizados:
            conta.status_dados = StatusDados.VERIFICADO
            resultado.sucesso = True
        else:
            conta.status_dados = StatusDados.ERRO_VALIDACAO

        return resultado

    def _aplicar_dados(self, conta: Conta, dados: Dict) -> List[str]:
        """Aplica dados do enriquecimento à conta. Retorna campos atualizados."""
        atualizados = []

        mapeamento = {
            'razao_social': 'razao_social',
            'nome_fantasia': 'nome_fantasia',
            'cnae_principal': 'cnae_principal',
            'cnae_descricao': 'cnae_descricao',
            'natureza_juridica': 'natureza_juridica',
            'site': 'site',
            'telefone_geral': 'telefone_geral',
            'email_geral': 'email_geral',
            'grupo_economico': 'grupo_economico',
        }

        for chave_fonte, campo_conta in mapeamento.items():
            if chave_fonte in dados and dados[chave_fonte]:
                valor_atual = getattr(conta, campo_conta, None)
                if not valor_atual or valor_atual != dados[chave_fonte]:
                    setattr(conta, campo_conta, dados[chave_fonte])
                    atualizados.append(campo_conta)

        # Situação cadastral
        if 'situacao_cadastral' in dados:
            mapa_situacao = {
                'ATIVA': SituacaoCadastral.ATIVA,
                'SUSPENSA': SituacaoCadastral.SUSPENSA,
                'INAPTA': SituacaoCadastral.INAPTA,
                'BAIXADA': SituacaoCadastral.BAIXADA,
                'NULA': SituacaoCadastral.NULA,
            }
            sit = mapa_situacao.get(dados['situacao_cadastral'].upper())
            if sit:
                conta.situacao_cadastral = sit
                atualizados.append('situacao_cadastral')

        # Porte
        if 'porte' in dados:
            mapa_porte = {
                'MEI': PorteEmpresa.MEI,
                'MICRO': PorteEmpresa.MICRO,
                'PEQUENO': PorteEmpresa.PEQUENO,
                'MEDIO': PorteEmpresa.MEDIO,
                'GRANDE': PorteEmpresa.GRANDE,
            }
            porte = mapa_porte.get(dados['porte'].upper())
            if porte:
                conta.porte = porte
                atualizados.append('porte')

        # Tipo estabelecimento
        if 'tipo_estabelecimento' in dados:
            if dados['tipo_estabelecimento'].upper() == 'MATRIZ':
                conta.tipo_estabelecimento = TipoEstabelecimento.MATRIZ
            else:
                conta.tipo_estabelecimento = TipoEstabelecimento.FILIAL
            atualizados.append('tipo_estabelecimento')

        # CNAEs secundárias
        if 'cnaes_secundarias' in dados and dados['cnaes_secundarias']:
            conta.cnaes_secundarias = dados['cnaes_secundarias']
            atualizados.append('cnaes_secundarias')

        # Endereço fiscal
        if 'endereco' in dados:
            end = dados['endereco']
            conta.endereco_fiscal = Endereco(
                tipo="Fiscal",
                logradouro=end.get('logradouro', ''),
                numero=end.get('numero', ''),
                complemento=end.get('complemento', ''),
                bairro=end.get('bairro', ''),
                cidade=end.get('cidade', ''),
                uf=end.get('uf', ''),
                cep=end.get('cep', ''),
            )
            atualizados.append('endereco_fiscal')

        # Data de abertura
        if 'data_abertura' in dados:
            conta.data_abertura = dados['data_abertura']
            atualizados.append('data_abertura')

        conta.data_atualizacao = datetime.now()
        return atualizados

    def enriquecer_lote(self, contas: List[Conta],
                        fontes: List[str] = None) -> List[ResultadoEnriquecimento]:
        """Enriquece lista de contas (batch)"""
        resultados = []
        for conta in contas:
            resultado = self.enriquecer_conta(conta, fontes)
            resultados.append(resultado)
        return resultados

    def verificar_qualidade(self, conta: Conta) -> Dict:
        """
        Verifica qualidade dos dados de uma conta.

        Retorna relatório com campos obrigatórios e sua completude.
        """
        campos_obrigatorios = {
            'cnpj_valido': conta.cnpj_valido,
            'razao_social': bool(conta.razao_social),
            'cnae_principal': bool(conta.cnae_principal),
            'porte': conta.porte is not None,
            'situacao_verificada': conta.situacao_cadastral != SituacaoCadastral.NAO_VERIFICADA,
        }

        campos_recomendados = {
            'nome_fantasia': bool(conta.nome_fantasia),
            'endereco_fiscal': conta.endereco_fiscal is not None,
            'telefone': bool(conta.telefone_geral),
            'site': bool(conta.site),
            'grupo_economico': bool(conta.grupo_economico),
        }

        obrigatorios_ok = sum(1 for v in campos_obrigatorios.values() if v)
        recomendados_ok = sum(1 for v in campos_recomendados.values() if v)

        return {
            'conta_id': conta.id,
            'cnpj': conta.cnpj,
            'campos_obrigatorios': campos_obrigatorios,
            'obrigatorios_pct': obrigatorios_ok / len(campos_obrigatorios) * 100,
            'campos_recomendados': campos_recomendados,
            'recomendados_pct': recomendados_ok / len(campos_recomendados) * 100,
            'completude_total': conta.percentual_completude,
            'status_dados': conta.status_dados.value,
        }
