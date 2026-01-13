"""
Modelo de Tomador - Qualificação de Risco Comercial

Este módulo implementa a gestão de tomadores com foco em:
- Risco de OPORTUNISMO (não risco de crédito)
- Histórico de comportamento
- Sinais de alerta (red flags)

Premissa: O risco não é se o tomador vai pagar a apólice,
mas se vai pagar os HONORÁRIOS após receber o trabalho.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal


class PorteTomador(Enum):
    """Porte do tomador"""
    MICRO = "Micro (até R$ 360 mil/ano)"
    PEQUENO = "Pequeno (até R$ 4,8 milhões/ano)"
    MEDIO = "Médio (até R$ 300 milhões/ano)"
    GRANDE = "Grande (acima de R$ 300 milhões/ano)"


class SetorTomador(Enum):
    """Setor de atuação"""
    CONSTRUCAO = "Construção Civil"
    TECNOLOGIA = "Tecnologia"
    TELECOM = "Telecomunicações"
    ENERGIA = "Energia"
    INFRAESTRUTURA = "Infraestrutura"
    SAUDE = "Saúde"
    INDUSTRIA = "Indústria"
    SERVICOS = "Serviços"
    COMERCIO = "Comércio"
    AGRONEGOCIO = "Agronegócio"
    FINANCEIRO = "Financeiro"
    OUTRO = "Outro"


class NivelContato(Enum):
    """Nível hierárquico do contato principal"""
    OPERACIONAL = "Operacional"
    GERENCIA = "Gerência"
    DIRETORIA = "Diretoria"
    CEO = "CEO / Presidente"
    SOCIO = "Sócio / Proprietário"


class ClassificacaoRisco(Enum):
    """Classificação de risco comercial do tomador"""
    VERDE = "Verde - Baixo Risco"
    AMARELO = "Amarelo - Atenção"
    LARANJA = "Laranja - Risco Moderado"
    VERMELHO = "Vermelho - Alto Risco"
    PRETO = "Preto - Não Operar"


@dataclass
class HistoricoOperacao:
    """Registro de operação anterior com o tomador"""
    data: datetime
    tipo: str
    valor_operacao: Decimal
    valor_honorarios: Decimal
    valor_pago: Decimal
    valor_pendente: Decimal
    status: str  # Concluída, Calote, Litígio, etc.
    observacoes: str = ""

    @property
    def pagou_integral(self) -> bool:
        return self.valor_pago >= self.valor_honorarios

    @property
    def percentual_pago(self) -> float:
        if self.valor_honorarios == 0:
            return 100.0
        return float(self.valor_pago / self.valor_honorarios * 100)


@dataclass
class HistoricoTomador:
    """Histórico completo do tomador conosco"""
    operacoes: List[HistoricoOperacao] = field(default_factory=list)

    @property
    def total_operacoes(self) -> int:
        return len(self.operacoes)

    @property
    def total_honorarios(self) -> Decimal:
        return sum(op.valor_honorarios for op in self.operacoes)

    @property
    def total_pago(self) -> Decimal:
        return sum(op.valor_pago for op in self.operacoes)

    @property
    def total_pendente(self) -> Decimal:
        return sum(op.valor_pendente for op in self.operacoes)

    @property
    def taxa_pagamento(self) -> float:
        """Percentual de honorários pagos sobre total"""
        if self.total_honorarios == 0:
            return 100.0
        return float(self.total_pago / self.total_honorarios * 100)

    @property
    def teve_calote(self) -> bool:
        """Verifica se já teve calote"""
        return any(op.status == "Calote" or op.valor_pendente > 0
                  for op in self.operacoes)

    @property
    def tem_litigio(self) -> bool:
        """Verifica se tem litígio"""
        return any(op.status == "Litígio" for op in self.operacoes)

    def adicionar_operacao(self, operacao: HistoricoOperacao) -> None:
        self.operacoes.append(operacao)


@dataclass
class RedFlagTomador:
    """Red flag identificado no tomador"""
    data_identificacao: datetime
    categoria: str
    descricao: str
    severidade: int  # 1-5
    fonte: str  # Como foi identificado
    ativo: bool = True


@dataclass
class Tomador:
    """
    Representa um tomador com foco em qualificação de risco comercial.

    IMPORTANTE: Esta qualificação NÃO é risco de crédito (capacidade
    de pagar a apólice), mas risco de COMPORTAMENTO OPORTUNISTA
    (probabilidade de calote nos honorários).
    """

    # Identificação
    id: str
    razao_social: str
    nome_fantasia: str
    cnpj: str

    # Classificação
    porte: PorteTomador
    setor: SetorTomador
    faturamento_anual: Optional[Decimal] = None

    # Contato principal
    contato_nome: str = ""
    contato_cargo: str = ""
    contato_nivel: NivelContato = NivelContato.GERENCIA
    contato_email: str = ""
    contato_telefone: str = ""

    # Situação especial
    em_recuperacao_judicial: bool = False
    tem_restricoes: bool = False
    observacoes_situacao: str = ""

    # Histórico conosco
    historico: HistoricoTomador = field(default_factory=HistoricoTomador)

    # Contexto de mercado
    corretores_conhecidos: List[str] = field(default_factory=list)
    seguradoras_com_limite: List[str] = field(default_factory=list)
    seguradoras_que_recusaram: List[str] = field(default_factory=list)

    # Red flags
    red_flags: List[RedFlagTomador] = field(default_factory=list)

    # Qualificação de risco
    score_risco: Optional[float] = None  # 0-100 (maior = mais risco)
    classificacao: ClassificacaoRisco = ClassificacaoRisco.AMARELO

    # Datas
    data_cadastro: datetime = field(default_factory=datetime.now)
    data_ultimo_contato: Optional[datetime] = None

    # Notas
    observacoes: str = ""

    def adicionar_red_flag(self, categoria: str, descricao: str,
                          severidade: int, fonte: str) -> None:
        """Adiciona um red flag ao tomador"""
        self.red_flags.append(RedFlagTomador(
            data_identificacao=datetime.now(),
            categoria=categoria,
            descricao=descricao,
            severidade=severidade,
            fonte=fonte
        ))

    def calcular_score_risco(self) -> float:
        """
        Calcula score de risco comercial (0-100).
        Maior score = MAIOR RISCO de calote/oportunismo.

        Fatores considerados:
        - Histórico de pagamentos conosco
        - Red flags identificados
        - Presença de outros corretores
        - Situação especial (RJ, restrições)
        - Nível do contato (paradoxalmente, CEO não garante nada)
        """

        score = 0.0

        # 1. HISTÓRICO DE PAGAMENTOS (peso 40)
        if self.historico.total_operacoes > 0:
            taxa_pagamento = self.historico.taxa_pagamento
            if taxa_pagamento >= 100:
                score += 0  # Pagou tudo
            elif taxa_pagamento >= 80:
                score += 10  # Quase tudo
            elif taxa_pagamento >= 50:
                score += 25  # Metade
            else:
                score += 40  # Menos da metade

            # Bônus negativo por calote ou litígio
            if self.historico.teve_calote:
                score += 15
            if self.historico.tem_litigio:
                score += 20
        else:
            # Sem histórico = risco médio
            score += 20

        # 2. RED FLAGS (peso 30)
        red_flags_ativos = [rf for rf in self.red_flags if rf.ativo]
        if red_flags_ativos:
            # Soma severidade dos red flags (máximo 30)
            soma_severidade = sum(rf.severidade for rf in red_flags_ativos)
            score += min(soma_severidade * 3, 30)

        # 3. OUTROS CORRETORES (peso 15)
        if self.corretores_conhecidos:
            # Cada corretor conhecido aumenta risco
            score += min(len(self.corretores_conhecidos) * 5, 15)

        # 4. SITUAÇÃO ESPECIAL (peso 15)
        if self.em_recuperacao_judicial:
            score += 10
        if self.tem_restricoes:
            score += 5

        # Limita entre 0 e 100
        self.score_risco = min(max(score, 0), 100)

        # Define classificação baseada no score
        self._definir_classificacao()

        return self.score_risco

    def _definir_classificacao(self) -> None:
        """Define classificação baseada no score"""
        if self.score_risco is None:
            self.classificacao = ClassificacaoRisco.AMARELO
            return

        if self.score_risco >= 80:
            self.classificacao = ClassificacaoRisco.PRETO
        elif self.score_risco >= 60:
            self.classificacao = ClassificacaoRisco.VERMELHO
        elif self.score_risco >= 40:
            self.classificacao = ClassificacaoRisco.LARANJA
        elif self.score_risco >= 20:
            self.classificacao = ClassificacaoRisco.AMARELO
        else:
            self.classificacao = ClassificacaoRisco.VERDE

    def verificar_red_flags_automaticos(self) -> List[str]:
        """
        Verifica e adiciona red flags automáticos baseado nos dados.
        Retorna lista de red flags identificados.
        """
        novos_flags = []

        # 1. Histórico de calote
        if self.historico.teve_calote:
            self.adicionar_red_flag(
                categoria="Histórico",
                descricao="Histórico de não pagamento de honorários",
                severidade=5,
                fonte="Análise automática de histórico"
            )
            novos_flags.append("Histórico de calote")

        # 2. Litígio existente
        if self.historico.tem_litigio:
            self.adicionar_red_flag(
                categoria="Histórico",
                descricao="Operação em litígio conosco",
                severidade=5,
                fonte="Análise automática de histórico"
            )
            novos_flags.append("Litígio existente")

        # 3. Múltiplos corretores
        if len(self.corretores_conhecidos) >= 2:
            self.adicionar_red_flag(
                categoria="Mercado",
                descricao=f"Trabalha com múltiplos corretores: {', '.join(self.corretores_conhecidos)}",
                severidade=3,
                fonte="Análise de mercado"
            )
            novos_flags.append("Múltiplos corretores")

        # 4. Recuperação Judicial
        if self.em_recuperacao_judicial:
            self.adicionar_red_flag(
                categoria="Situação",
                descricao="Empresa em Recuperação Judicial",
                severidade=4,
                fonte="Situação cadastral"
            )
            novos_flags.append("Recuperação Judicial")

        # 5. Muitas recusas no mercado
        if len(self.seguradoras_que_recusaram) >= 3:
            self.adicionar_red_flag(
                categoria="Mercado",
                descricao=f"Recusado por múltiplas seguradoras: {', '.join(self.seguradoras_que_recusaram[:3])}...",
                severidade=2,
                fonte="Análise de mercado"
            )
            novos_flags.append("Múltiplas recusas")

        # 6. Taxa de pagamento baixa
        if self.historico.total_operacoes > 0:
            if self.historico.taxa_pagamento < 50:
                self.adicionar_red_flag(
                    categoria="Histórico",
                    descricao=f"Taxa de pagamento de apenas {self.historico.taxa_pagamento:.1f}%",
                    severidade=5,
                    fonte="Análise de histórico"
                )
                novos_flags.append("Taxa pagamento < 50%")
            elif self.historico.taxa_pagamento < 80:
                self.adicionar_red_flag(
                    categoria="Histórico",
                    descricao=f"Taxa de pagamento de {self.historico.taxa_pagamento:.1f}%",
                    severidade=3,
                    fonte="Análise de histórico"
                )
                novos_flags.append("Taxa pagamento < 80%")

        return novos_flags

    def recomendacao_estrutura_cobranca(self) -> Dict:
        """
        Recomenda estrutura de cobrança baseada no risco.

        Retorna dicionário com:
        - percentual_antecipado: quanto cobrar de entrada
        - exigir_contrato: se deve exigir contrato formal
        - estrutura_fases: como dividir os pagamentos
        - alertas: pontos de atenção
        """

        if self.score_risco is None:
            self.calcular_score_risco()

        recomendacao = {
            'percentual_antecipado': 0,
            'exigir_contrato': True,
            'estrutura_fases': [],
            'alertas': [],
            'operar': True
        }

        if self.classificacao == ClassificacaoRisco.PRETO:
            recomendacao['operar'] = False
            recomendacao['alertas'].append(
                "NÃO RECOMENDADO OPERAR - Risco muito alto de calote"
            )
            return recomendacao

        if self.classificacao == ClassificacaoRisco.VERMELHO:
            recomendacao['percentual_antecipado'] = 100
            recomendacao['estrutura_fases'] = [
                {'fase': 'Diagnóstico', 'pagamento': '100% antecipado'},
                {'fase': 'Execução', 'pagamento': '100% antecipado'},
                {'fase': 'Emissão', 'pagamento': 'Comissão'}
            ]
            recomendacao['alertas'] = [
                "Exigir 100% antecipado em cada fase",
                "Não entregar NADA sem pagamento confirmado",
                "Documentar todas as interações",
                "Contrato com cláusula de PI reforçada"
            ]

        elif self.classificacao == ClassificacaoRisco.LARANJA:
            recomendacao['percentual_antecipado'] = 70
            recomendacao['estrutura_fases'] = [
                {'fase': 'Diagnóstico', 'pagamento': '100% antecipado'},
                {'fase': 'Execução', 'pagamento': '50% início + 50% entrega'},
                {'fase': 'Emissão', 'pagamento': 'Comissão'}
            ]
            recomendacao['alertas'] = [
                "Diagnóstico 100% antecipado",
                "Execução em duas parcelas",
                "Atenção redobrada à documentação"
            ]

        elif self.classificacao == ClassificacaoRisco.AMARELO:
            recomendacao['percentual_antecipado'] = 50
            recomendacao['estrutura_fases'] = [
                {'fase': 'Diagnóstico', 'pagamento': '100% antecipado'},
                {'fase': 'Execução', 'pagamento': '30% início + 70% entrega'},
                {'fase': 'Emissão', 'pagamento': 'Comissão'}
            ]
            recomendacao['alertas'] = [
                "Diagnóstico sempre 100% antecipado",
                "Monitorar comportamento durante execução"
            ]

        else:  # VERDE
            recomendacao['percentual_antecipado'] = 30
            recomendacao['estrutura_fases'] = [
                {'fase': 'Diagnóstico', 'pagamento': '100% antecipado'},
                {'fase': 'Execução', 'pagamento': 'Por milestones'},
                {'fase': 'Emissão', 'pagamento': 'Comissão'}
            ]
            recomendacao['alertas'] = [
                "Diagnóstico sempre 100% antecipado",
                "Perfil de baixo risco, mas manter documentação"
            ]

        return recomendacao

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'cnpj': self.cnpj,
            'porte': self.porte.value,
            'setor': self.setor.value,
            'classificacao_risco': self.classificacao.value,
            'score_risco': self.score_risco,
            'historico': {
                'total_operacoes': self.historico.total_operacoes,
                'total_honorarios': str(self.historico.total_honorarios),
                'total_pago': str(self.historico.total_pago),
                'taxa_pagamento': self.historico.taxa_pagamento
            },
            'red_flags': [
                {
                    'categoria': rf.categoria,
                    'descricao': rf.descricao,
                    'severidade': rf.severidade
                }
                for rf in self.red_flags if rf.ativo
            ],
            'corretores_conhecidos': self.corretores_conhecidos,
            'recomendacao': self.recomendacao_estrutura_cobranca()
        }


# Funções de fábrica para casos comuns

def criar_tomador_novo(
    id: str,
    razao_social: str,
    cnpj: str,
    porte: PorteTomador,
    setor: SetorTomador,
    contato_nome: str,
    contato_cargo: str,
    contato_email: str,
    nome_fantasia: str = None,
    **kwargs
) -> Tomador:
    """Cria um tomador novo (sem histórico)"""

    tomador = Tomador(
        id=id,
        razao_social=razao_social,
        nome_fantasia=nome_fantasia or razao_social,
        cnpj=cnpj,
        porte=porte,
        setor=setor,
        contato_nome=contato_nome,
        contato_cargo=contato_cargo,
        contato_email=contato_email,
        **kwargs
    )

    # Calcula score inicial
    tomador.calcular_score_risco()

    return tomador


def criar_tomador_com_historico_calote(
    id: str,
    razao_social: str,
    cnpj: str,
    porte: PorteTomador,
    setor: SetorTomador,
    valor_calote: Decimal,
    **kwargs
) -> Tomador:
    """
    Cria um tomador que já tem histórico de calote.
    Usado para registrar casos problemáticos.
    """

    tomador = Tomador(
        id=id,
        razao_social=razao_social,
        nome_fantasia=kwargs.get('nome_fantasia', razao_social),
        cnpj=cnpj,
        porte=porte,
        setor=setor,
        **{k: v for k, v in kwargs.items() if k != 'nome_fantasia'}
    )

    # Adiciona operação com calote
    tomador.historico.adicionar_operacao(HistoricoOperacao(
        data=datetime.now(),
        tipo="Operação com Calote",
        valor_operacao=valor_calote * 10,  # Estimativa
        valor_honorarios=valor_calote,
        valor_pago=Decimal('0'),
        valor_pendente=valor_calote,
        status="Calote"
    ))

    # Verifica red flags
    tomador.verificar_red_flags_automaticos()

    # Calcula score
    tomador.calcular_score_risco()

    return tomador
