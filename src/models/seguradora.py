"""
Modelos de dados para representar informações financeiras de seguradoras
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class BalancoPatrimonial:
    """Representa o Balanço Patrimonial de uma seguradora"""

    # ATIVO
    # Ativo Circulante
    disponibilidades: float = 0.0
    aplicacoes_financeiras_cp: float = 0.0
    premios_a_receber: float = 0.0
    creditos_operacionais: float = 0.0
    outros_creditos_cp: float = 0.0

    # Ativo Não Circulante
    aplicacoes_financeiras_lp: float = 0.0
    investimentos: float = 0.0
    imobilizado: float = 0.0
    intangivel: float = 0.0
    outros_ativos_lp: float = 0.0

    # PASSIVO
    # Passivo Circulante
    provisoes_tecnicas_cp: float = 0.0
    debitos_operacionais: float = 0.0
    depositos_terceiros: float = 0.0
    emprestimos_cp: float = 0.0
    outras_obrigacoes_cp: float = 0.0

    # Passivo Não Circulante
    provisoes_tecnicas_lp: float = 0.0
    emprestimos_lp: float = 0.0
    outras_obrigacoes_lp: float = 0.0

    # Patrimônio Líquido
    capital_social: float = 0.0
    reservas_capital: float = 0.0
    reservas_lucros: float = 0.0
    ajustes_avaliacao: float = 0.0
    lucros_acumulados: float = 0.0

    @property
    def ativo_circulante(self) -> float:
        """Total do Ativo Circulante"""
        return (self.disponibilidades +
                self.aplicacoes_financeiras_cp +
                self.premios_a_receber +
                self.creditos_operacionais +
                self.outros_creditos_cp)

    @property
    def ativo_nao_circulante(self) -> float:
        """Total do Ativo Não Circulante"""
        return (self.aplicacoes_financeiras_lp +
                self.investimentos +
                self.imobilizado +
                self.intangivel +
                self.outros_ativos_lp)

    @property
    def ativo_total(self) -> float:
        """Total do Ativo"""
        return self.ativo_circulante + self.ativo_nao_circulante

    @property
    def passivo_circulante(self) -> float:
        """Total do Passivo Circulante"""
        return (self.provisoes_tecnicas_cp +
                self.debitos_operacionais +
                self.depositos_terceiros +
                self.emprestimos_cp +
                self.outras_obrigacoes_cp)

    @property
    def passivo_nao_circulante(self) -> float:
        """Total do Passivo Não Circulante"""
        return (self.provisoes_tecnicas_lp +
                self.emprestimos_lp +
                self.outras_obrigacoes_lp)

    @property
    def passivo_exigivel(self) -> float:
        """Total do Passivo Exigível"""
        return self.passivo_circulante + self.passivo_nao_circulante

    @property
    def patrimonio_liquido(self) -> float:
        """Total do Patrimônio Líquido"""
        return (self.capital_social +
                self.reservas_capital +
                self.reservas_lucros +
                self.ajustes_avaliacao +
                self.lucros_acumulados)

    @property
    def passivo_total(self) -> float:
        """Total do Passivo + Patrimônio Líquido"""
        return self.passivo_exigivel + self.patrimonio_liquido

    @property
    def provisoes_tecnicas_total(self) -> float:
        """Total de Provisões Técnicas"""
        return self.provisoes_tecnicas_cp + self.provisoes_tecnicas_lp


@dataclass
class DRE:
    """Demonstração do Resultado do Exercício"""

    # Receitas
    premios_emitidos: float = 0.0
    premios_cedidos_resseguro: float = 0.0
    variacoes_provisoes_tecnicas: float = 0.0
    premios_ganhos: float = 0.0

    # Sinistros
    sinistros_ocorridos: float = 0.0
    custos_aquisicao: float = 0.0
    outras_despesas_operacionais: float = 0.0

    # Resultado Financeiro
    receitas_financeiras: float = 0.0
    despesas_financeiras: float = 0.0

    # Despesas Administrativas
    despesas_administrativas: float = 0.0
    despesas_tributarias: float = 0.0

    # Resultado
    resultado_operacional: float = 0.0
    resultado_nao_operacional: float = 0.0

    # Impostos
    irpj_csll: float = 0.0

    @property
    def premios_retidos(self) -> float:
        """Prêmios retidos (líquido de resseguro)"""
        return self.premios_emitidos - self.premios_cedidos_resseguro

    @property
    def resultado_financeiro(self) -> float:
        """Resultado financeiro líquido"""
        return self.receitas_financeiras - self.despesas_financeiras

    @property
    def resultado_tecnico(self) -> float:
        """Resultado técnico (operação de seguros)"""
        return (self.premios_ganhos -
                self.sinistros_ocorridos -
                self.custos_aquisicao -
                self.outras_despesas_operacionais)

    @property
    def lucro_bruto(self) -> float:
        """Lucro bruto"""
        return self.resultado_tecnico + self.resultado_financeiro

    @property
    def lucro_antes_impostos(self) -> float:
        """Lucro antes do IR/CSLL"""
        return (self.lucro_bruto -
                self.despesas_administrativas -
                self.despesas_tributarias +
                self.resultado_nao_operacional)

    @property
    def lucro_liquido(self) -> float:
        """Lucro líquido do exercício"""
        return self.lucro_antes_impostos - self.irpj_csll


@dataclass
class IndicadoresFinanceiros:
    """Indicadores financeiros calculados para análise"""

    # Identificação
    nome_seguradora: str = ""
    data_referencia: Optional[date] = None

    # Indicadores de Solvência
    indice_solvencia: float = 0.0  # PL / Passivo Exigível
    margem_solvencia: float = 0.0  # Capital excedente regulatório
    cobertura_provisoes: float = 0.0  # Ativos garantidores / Provisões

    # Indicadores de Liquidez
    liquidez_corrente: float = 0.0  # AC / PC
    liquidez_seca: float = 0.0  # (AC - Estoques) / PC
    liquidez_imediata: float = 0.0  # Disponibilidades / PC

    # Indicadores de Rentabilidade
    roe: float = 0.0  # Return on Equity - Lucro / PL
    roa: float = 0.0  # Return on Assets - Lucro / Ativo Total
    margem_liquida: float = 0.0  # Lucro / Prêmios Ganhos
    margem_operacional: float = 0.0  # Resultado Operacional / Prêmios

    # Indicadores de Sinistralidade
    indice_sinistralidade: float = 0.0  # Sinistros / Prêmios Ganhos
    indice_despesas: float = 0.0  # Despesas Adm / Prêmios
    indice_combinado: float = 0.0  # Sinistralidade + Despesas
    indice_combinado_ampliado: float = 0.0  # Combinado + Resultado Financeiro

    # Indicadores de Estrutura
    endividamento: float = 0.0  # Passivo Exigível / Ativo Total
    imobilizacao_pl: float = 0.0  # Imobilizado / PL
    alavancagem: float = 0.0  # Prêmios / PL

    # Rating e Score
    score_forca_financeira: float = 0.0  # Score calculado (0-100)
    classificacao_risco: str = ""  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D


@dataclass
class Seguradora:
    """Representa uma seguradora com todos os dados financeiros"""

    # Identificação
    codigo_susep: str = ""
    nome: str = ""
    cnpj: str = ""
    grupo_economico: str = ""

    # Dados de referência
    ano_exercicio: int = 0
    data_balanco: Optional[date] = None

    # Demonstrações Financeiras
    balanco: BalancoPatrimonial = field(default_factory=BalancoPatrimonial)
    dre: DRE = field(default_factory=DRE)

    # Indicadores calculados
    indicadores: IndicadoresFinanceiros = field(default_factory=IndicadoresFinanceiros)

    # Informações adicionais
    capital_minimo_requerido: float = 0.0
    patrimonio_liquido_ajustado: float = 0.0
    ativo_liquido_regulatorio: float = 0.0

    def __post_init__(self):
        """Inicializa valores padrão se necessário"""
        if self.indicadores.nome_seguradora == "":
            self.indicadores.nome_seguradora = self.nome
        if self.indicadores.data_referencia is None and self.data_balanco:
            self.indicadores.data_referencia = self.data_balanco

    def to_dict(self) -> dict:
        """Converte a seguradora para dicionário"""
        return {
            'codigo_susep': self.codigo_susep,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'grupo_economico': self.grupo_economico,
            'ano_exercicio': self.ano_exercicio,
            'ativo_total': self.balanco.ativo_total,
            'passivo_total': self.balanco.passivo_total,
            'patrimonio_liquido': self.balanco.patrimonio_liquido,
            'premios_emitidos': self.dre.premios_emitidos,
            'lucro_liquido': self.dre.lucro_liquido,
            'score_forca_financeira': self.indicadores.score_forca_financeira,
            'classificacao_risco': self.indicadores.classificacao_risco
        }
