"""
Modelo de Operação Comercial - Sistema de Fases e Cobrança

Este módulo implementa a estrutura de operações com fases definidas,
cada uma com entrega específica e cobrança independente.

Modelo de Negócio:
- Operações complexas de seguro garantia
- Tomadores sem limite no mercado
- Trabalho técnico especializado (boutique)
- Cobrança por fase, não por resultado final
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal


class TipoOperacao(Enum):
    """Tipos de operação de seguro garantia"""
    LICITACAO = "Licitação Pública"
    JUDICIAL = "Garantia Judicial"
    CONTRATUAL = "Garantia Contratual"
    FINANCEIRA = "Garantia Financeira"
    ADUANEIRA = "Garantia Aduaneira"
    IMOBILIARIA = "Garantia Imobiliária"
    MA = "M&A / Fusões e Aquisições"
    RECUPERACAO_JUDICIAL = "Recuperação Judicial"
    OUTRO = "Outro"


class TipoGarantia(Enum):
    """Modalidades de seguro garantia"""
    BID_BOND = "Bid Bond (Garantia de Proposta)"
    PERFORMANCE_BOND = "Performance Bond (Garantia de Execução)"
    ADVANCE_PAYMENT = "Advance Payment (Garantia de Adiantamento)"
    RETENTION_MONEY = "Retention Money (Garantia de Retenção)"
    MAINTENANCE_BOND = "Maintenance Bond (Garantia de Manutenção)"
    JUDICIAL = "Garantia Judicial"
    FINANCEIRA = "Garantia Financeira"
    ADUANEIRA = "Garantia Aduaneira"


class StatusFase(Enum):
    """Status de cada fase da operação"""
    NAO_INICIADA = "Não Iniciada"
    EM_ANDAMENTO = "Em Andamento"
    AGUARDANDO_PAGAMENTO = "Aguardando Pagamento"
    PAGO = "Pago"
    ENTREGUE = "Entregue"
    CANCELADA = "Cancelada"
    RECUSADA_CLIENTE = "Recusada pelo Cliente"


class StatusOperacao(Enum):
    """Status geral da operação"""
    TRIAGEM = "Em Triagem"
    PROPOSTA_ENVIADA = "Proposta Enviada"
    EM_DIAGNOSTICO = "Em Diagnóstico"
    EM_EXECUCAO = "Em Execução"
    AGUARDANDO_EMISSAO = "Aguardando Emissão"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"
    PERDIDA = "Perdida"
    EM_LITIGIO = "Em Litígio"


class OrigemOperacao(Enum):
    """Como a operação chegou"""
    DEMANDA_PASSIVA = "Demanda Passiva (Cliente Veio)"
    PROSPECCAO_ATIVA = "Prospecção Ativa (Buscamos)"
    INDICACAO = "Indicação"
    RETORNO_CLIENTE = "Retorno de Cliente Antigo"


@dataclass
class FaseOperacao:
    """
    Representa uma fase do trabalho com entrega e cobrança específicas.

    Princípio: Cada fase tem valor independente e cobrança própria.
    Não avança sem pagamento da fase anterior.
    """

    numero: int
    nome: str
    descricao: str
    entregaveis: List[str]
    valor_honorario: Decimal
    percentual_do_total: float  # Para referência
    status: StatusFase = StatusFase.NAO_INICIADA

    # Datas de controle
    data_inicio: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    data_entrega: Optional[datetime] = None

    # Documentação
    nota_fiscal: Optional[str] = None
    comprovante_pagamento: Optional[str] = None
    protocolo_entrega: Optional[str] = None

    # Observações
    observacoes: str = ""

    def iniciar(self) -> None:
        """Inicia a fase"""
        self.status = StatusFase.EM_ANDAMENTO
        self.data_inicio = datetime.now()

    def registrar_pagamento(self, comprovante: str, nota_fiscal: str) -> None:
        """Registra pagamento recebido"""
        self.status = StatusFase.PAGO
        self.data_pagamento = datetime.now()
        self.comprovante_pagamento = comprovante
        self.nota_fiscal = nota_fiscal

    def registrar_entrega(self, protocolo: str) -> None:
        """Registra entrega dos entregáveis"""
        self.status = StatusFase.ENTREGUE
        self.data_entrega = datetime.now()
        self.protocolo_entrega = protocolo

    def cancelar(self, motivo: str) -> None:
        """Cancela a fase"""
        self.status = StatusFase.CANCELADA
        self.observacoes = f"Cancelada: {motivo}"

    @property
    def dias_em_andamento(self) -> int:
        """Dias desde o início da fase"""
        if not self.data_inicio:
            return 0
        fim = self.data_entrega or datetime.now()
        return (fim - self.data_inicio).days

    @property
    def pago(self) -> bool:
        """Verifica se a fase foi paga"""
        return self.status in [StatusFase.PAGO, StatusFase.ENTREGUE]


def criar_fases_padrao(valor_total_operacao: Decimal,
                       valor_diagnostico: Decimal = None,
                       percentual_execucao: float = 0.6,
                       incluir_emissao: bool = True) -> List[FaseOperacao]:
    """
    Cria estrutura padrão de fases para uma operação.

    Modelo de 3-4 fases:
    - Fase 1: Diagnóstico (valor fixo, independente do resultado)
    - Fase 2: Execução (trabalho de reversão/aprovação)
    - Fase 3: Acompanhamento até Emissão (opcional)
    - Fase 4: Success Fee / Comissão (se aplicável)

    Args:
        valor_total_operacao: Valor total estimado da operação (honorários)
        valor_diagnostico: Valor fixo do diagnóstico (se None, usa 15% do total)
        percentual_execucao: Percentual do restante para execução
        incluir_emissao: Se inclui fase de acompanhamento até emissão

    Returns:
        Lista de FaseOperacao configuradas
    """

    # Fase 1: Diagnóstico - valor fixo
    if valor_diagnostico is None:
        valor_diagnostico = valor_total_operacao * Decimal('0.15')
        # Mínimo de R$ 15.000 para diagnóstico
        valor_diagnostico = max(valor_diagnostico, Decimal('15000'))

    valor_restante = valor_total_operacao - valor_diagnostico

    fases = []

    # FASE 1: DIAGNÓSTICO
    fases.append(FaseOperacao(
        numero=1,
        nome="Diagnóstico Técnico",
        descricao="""
        Análise profunda do caso para identificar:
        - Situação atual do tomador no mercado
        - Motivos das recusas anteriores
        - Obstáculos técnicos e regulatórios
        - Viabilidade de aprovação
        - Linha de trabalho proposta

        IMPORTANTE: Esta fase tem valor independente do resultado final.
        O diagnóstico entrega clareza sobre o problema, mesmo que a
        conclusão seja de inviabilidade.
        """,
        entregaveis=[
            "Relatório de Diagnóstico Técnico",
            "Análise de Recusas Anteriores",
            "Mapeamento de Obstáculos",
            "Avaliação de Viabilidade (Parecer)",
            "Linha de Trabalho Proposta (se viável)",
            "Estimativa de Prazo e Investimento para Execução"
        ],
        valor_honorario=valor_diagnostico,
        percentual_do_total=float(valor_diagnostico / valor_total_operacao * 100)
    ))

    # FASE 2: EXECUÇÃO
    if incluir_emissao:
        valor_execucao = valor_restante * Decimal(str(percentual_execucao))
        valor_emissao = valor_restante - valor_execucao
    else:
        valor_execucao = valor_restante
        valor_emissao = Decimal('0')

    fases.append(FaseOperacao(
        numero=2,
        nome="Execução Técnica",
        descricao="""
        Trabalho de reversão e aprovação:
        - Reconstrução da operação
        - Elaboração de estudos técnicos
        - Fundamentação em legislação e normativas
        - Negociação com seguradoras
        - Defesa técnica do caso
        """,
        entregaveis=[
            "Estudo de Viabilidade Econômica",
            "Dossiê Técnico Completo",
            "Parecer Fundamentado (legislação/normativas)",
            "Proposta de Estruturação",
            "Negociação com Seguradoras",
            "Aprovação de Limite"
        ],
        valor_honorario=valor_execucao,
        percentual_do_total=float(valor_execucao / valor_total_operacao * 100)
    ))

    # FASE 3: ACOMPANHAMENTO ATÉ EMISSÃO
    if incluir_emissao and valor_emissao > 0:
        fases.append(FaseOperacao(
            numero=3,
            nome="Acompanhamento até Emissão",
            descricao="""
            Finalização e emissão da apólice:
            - Formalização com seguradora
            - Revisão de condições
            - Emissão da apólice
            - Entrega ao tomador
            """,
            entregaveis=[
                "Proposta Formal da Seguradora",
                "Apólice Emitida",
                "Documentação de Fechamento"
            ],
            valor_honorario=valor_emissao,
            percentual_do_total=float(valor_emissao / valor_total_operacao * 100)
        ))

    return fases


@dataclass
class Operacao:
    """
    Representa uma operação comercial completa.

    Cada operação tem:
    - Dados do tomador e da oportunidade
    - Fases de trabalho com cobrança independente
    - Histórico de interações
    - Documentação para proteção
    """

    # Identificação
    id: str
    nome: str

    # Tomador (será referência ao objeto Tomador)
    tomador_id: str
    tomador_nome: str
    tomador_cnpj: str

    # Detalhes da operação
    tipo_operacao: TipoOperacao
    tipo_garantia: TipoGarantia
    valor_garantia: Decimal  # Valor da garantia/apólice
    valor_contrato: Decimal  # Valor do contrato principal (licitação, etc)
    descricao: str

    # Origem e contexto
    origem: OrigemOperacao
    contato_nome: str
    contato_cargo: str
    contato_email: str
    contato_telefone: str

    # Status
    status: StatusOperacao = StatusOperacao.TRIAGEM

    # Datas
    data_entrada: datetime = field(default_factory=datetime.now)
    data_limite: Optional[date] = None  # Prazo do cliente (licitação, etc)

    # Fases de trabalho
    fases: List[FaseOperacao] = field(default_factory=list)

    # Contexto do mercado
    ja_tentou_outros_corretores: bool = False
    corretores_anteriores: List[str] = field(default_factory=list)
    motivos_recusa_mercado: List[str] = field(default_factory=list)

    # Análise de risco
    score_risco_comercial: Optional[float] = None  # 0-100
    red_flags: List[str] = field(default_factory=list)

    # Valores
    valor_total_honorarios: Decimal = Decimal('0')
    valor_recebido: Decimal = Decimal('0')
    valor_pendente: Decimal = Decimal('0')

    # Documentação
    documentos: List[Dict] = field(default_factory=list)
    historico_interacoes: List[Dict] = field(default_factory=list)

    # Resultado
    seguradora_aprovadora: Optional[str] = None
    limite_aprovado: Optional[Decimal] = None
    taxa_obtida: Optional[float] = None
    comissao_esperada: Optional[Decimal] = None

    # Observações
    observacoes: str = ""

    def __post_init__(self):
        """Inicializa valores calculados"""
        self.atualizar_valores()

    def atualizar_valores(self) -> None:
        """Atualiza valores totais baseado nas fases"""
        self.valor_total_honorarios = sum(f.valor_honorario for f in self.fases)
        self.valor_recebido = sum(f.valor_honorario for f in self.fases if f.pago)
        self.valor_pendente = self.valor_total_honorarios - self.valor_recebido

    @property
    def fase_atual(self) -> Optional[FaseOperacao]:
        """Retorna a fase atual (em andamento ou aguardando)"""
        for fase in self.fases:
            if fase.status in [StatusFase.EM_ANDAMENTO, StatusFase.AGUARDANDO_PAGAMENTO]:
                return fase
        return None

    @property
    def proxima_fase(self) -> Optional[FaseOperacao]:
        """Retorna a próxima fase a ser iniciada"""
        for fase in self.fases:
            if fase.status == StatusFase.NAO_INICIADA:
                return fase
        return None

    @property
    def pode_avancar(self) -> bool:
        """Verifica se pode avançar para próxima fase"""
        fase_atual = self.fase_atual
        if not fase_atual:
            return True
        return fase_atual.status == StatusFase.ENTREGUE

    @property
    def dias_desde_entrada(self) -> int:
        """Dias desde a entrada da operação"""
        return (datetime.now() - self.data_entrada).days

    @property
    def dias_ate_limite(self) -> Optional[int]:
        """Dias até o prazo limite (se houver)"""
        if not self.data_limite:
            return None
        return (self.data_limite - date.today()).days

    @property
    def urgencia(self) -> str:
        """Nível de urgência baseado no prazo"""
        dias = self.dias_ate_limite
        if dias is None:
            return "Indefinida"
        if dias < 0:
            return "VENCIDA"
        if dias <= 7:
            return "CRÍTICA"
        if dias <= 15:
            return "ALTA"
        if dias <= 30:
            return "MÉDIA"
        return "BAIXA"

    def adicionar_fase(self, fase: FaseOperacao) -> None:
        """Adiciona uma fase à operação"""
        self.fases.append(fase)
        self.atualizar_valores()

    def iniciar_fase(self, numero_fase: int) -> bool:
        """
        Inicia uma fase específica.
        Só permite iniciar se a fase anterior foi paga.
        """
        for i, fase in enumerate(self.fases):
            if fase.numero == numero_fase:
                # Verifica se fase anterior foi paga
                if i > 0 and not self.fases[i-1].pago:
                    return False
                fase.iniciar()
                return True
        return False

    def registrar_pagamento_fase(self, numero_fase: int,
                                  comprovante: str,
                                  nota_fiscal: str) -> bool:
        """Registra pagamento de uma fase"""
        for fase in self.fases:
            if fase.numero == numero_fase:
                fase.registrar_pagamento(comprovante, nota_fiscal)
                self.atualizar_valores()
                return True
        return False

    def registrar_entrega_fase(self, numero_fase: int, protocolo: str) -> bool:
        """Registra entrega de uma fase"""
        for fase in self.fases:
            if fase.numero == numero_fase:
                # Só entrega se foi pago
                if not fase.pago:
                    return False
                fase.registrar_entrega(protocolo)
                return True
        return False

    def adicionar_interacao(self, tipo: str, descricao: str,
                           arquivo: str = None) -> None:
        """Registra uma interação no histórico"""
        self.historico_interacoes.append({
            'data': datetime.now().isoformat(),
            'tipo': tipo,
            'descricao': descricao,
            'arquivo': arquivo
        })

    def adicionar_documento(self, nome: str, tipo: str,
                           caminho: str, descricao: str = "") -> None:
        """Adiciona documento à operação"""
        self.documentos.append({
            'data': datetime.now().isoformat(),
            'nome': nome,
            'tipo': tipo,
            'caminho': caminho,
            'descricao': descricao
        })

    def adicionar_red_flag(self, flag: str) -> None:
        """Adiciona um red flag à operação"""
        if flag not in self.red_flags:
            self.red_flags.append(flag)

    def to_dict(self) -> Dict:
        """Converte para dicionário (para serialização)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tomador': {
                'id': self.tomador_id,
                'nome': self.tomador_nome,
                'cnpj': self.tomador_cnpj
            },
            'tipo_operacao': self.tipo_operacao.value,
            'tipo_garantia': self.tipo_garantia.value,
            'valor_garantia': str(self.valor_garantia),
            'valor_contrato': str(self.valor_contrato),
            'status': self.status.value,
            'origem': self.origem.value,
            'urgencia': self.urgencia,
            'fases': [
                {
                    'numero': f.numero,
                    'nome': f.nome,
                    'status': f.status.value,
                    'valor': str(f.valor_honorario),
                    'pago': f.pago
                }
                for f in self.fases
            ],
            'valores': {
                'total_honorarios': str(self.valor_total_honorarios),
                'recebido': str(self.valor_recebido),
                'pendente': str(self.valor_pendente)
            },
            'red_flags': self.red_flags,
            'score_risco': self.score_risco_comercial
        }


# Fábrica de operações com configurações pré-definidas

def criar_operacao_licitacao(
    id: str,
    nome: str,
    tomador_id: str,
    tomador_nome: str,
    tomador_cnpj: str,
    valor_garantia: Decimal,
    valor_contrato: Decimal,
    data_licitacao: date,
    contato_nome: str,
    contato_cargo: str,
    contato_email: str,
    contato_telefone: str,
    origem: OrigemOperacao,
    valor_diagnostico: Decimal = Decimal('25000'),
    **kwargs
) -> Operacao:
    """
    Cria uma operação de licitação com estrutura padrão.

    Valor de diagnóstico padrão: R$ 25.000
    (ajustável conforme complexidade)
    """

    # Estima honorários totais (2-3% do valor da garantia para operações complexas)
    valor_estimado_honorarios = valor_garantia * Decimal('0.025')
    valor_estimado_honorarios = max(valor_estimado_honorarios, Decimal('50000'))

    operacao = Operacao(
        id=id,
        nome=nome,
        tomador_id=tomador_id,
        tomador_nome=tomador_nome,
        tomador_cnpj=tomador_cnpj,
        tipo_operacao=TipoOperacao.LICITACAO,
        tipo_garantia=TipoGarantia.PERFORMANCE_BOND,
        valor_garantia=valor_garantia,
        valor_contrato=valor_contrato,
        descricao=kwargs.get('descricao', ''),
        origem=origem,
        contato_nome=contato_nome,
        contato_cargo=contato_cargo,
        contato_email=contato_email,
        contato_telefone=contato_telefone,
        data_limite=data_licitacao,
        **{k: v for k, v in kwargs.items() if k != 'descricao'}
    )

    # Cria fases padrão
    fases = criar_fases_padrao(
        valor_total_operacao=valor_estimado_honorarios,
        valor_diagnostico=valor_diagnostico
    )

    for fase in fases:
        operacao.adicionar_fase(fase)

    return operacao


def criar_operacao_ma(
    id: str,
    nome: str,
    tomador_id: str,
    tomador_nome: str,
    tomador_cnpj: str,
    valor_garantia: Decimal,
    valor_transacao: Decimal,
    contato_nome: str,
    contato_cargo: str,
    contato_email: str,
    contato_telefone: str,
    origem: OrigemOperacao,
    valor_diagnostico: Decimal = Decimal('30000'),
    **kwargs
) -> Operacao:
    """
    Cria uma operação de M&A com estrutura padrão.

    Operações de M&A são tipicamente mais complexas.
    Valor de diagnóstico padrão: R$ 30.000
    """

    valor_estimado_honorarios = valor_garantia * Decimal('0.03')
    valor_estimado_honorarios = max(valor_estimado_honorarios, Decimal('80000'))

    operacao = Operacao(
        id=id,
        nome=nome,
        tomador_id=tomador_id,
        tomador_nome=tomador_nome,
        tomador_cnpj=tomador_cnpj,
        tipo_operacao=TipoOperacao.MA,
        tipo_garantia=TipoGarantia.FINANCEIRA,
        valor_garantia=valor_garantia,
        valor_contrato=valor_transacao,
        descricao=kwargs.get('descricao', ''),
        origem=origem,
        contato_nome=contato_nome,
        contato_cargo=contato_cargo,
        contato_email=contato_email,
        contato_telefone=contato_telefone,
        **{k: v for k, v in kwargs.items() if k != 'descricao'}
    )

    fases = criar_fases_padrao(
        valor_total_operacao=valor_estimado_honorarios,
        valor_diagnostico=valor_diagnostico
    )

    for fase in fases:
        operacao.adicionar_fase(fase)

    return operacao


def criar_operacao_recuperacao_judicial(
    id: str,
    nome: str,
    tomador_id: str,
    tomador_nome: str,
    tomador_cnpj: str,
    valor_garantia: Decimal,
    valor_contrato: Decimal,
    contato_nome: str,
    contato_cargo: str,
    contato_email: str,
    contato_telefone: str,
    origem: OrigemOperacao,
    valor_diagnostico: Decimal = Decimal('35000'),
    **kwargs
) -> Operacao:
    """
    Cria uma operação de empresa em Recuperação Judicial.

    Operações em RJ são as mais complexas e arriscadas.
    Valor de diagnóstico padrão: R$ 35.000 (maior devido à complexidade)
    """

    valor_estimado_honorarios = valor_garantia * Decimal('0.04')
    valor_estimado_honorarios = max(valor_estimado_honorarios, Decimal('100000'))

    operacao = Operacao(
        id=id,
        nome=nome,
        tomador_id=tomador_id,
        tomador_nome=tomador_nome,
        tomador_cnpj=tomador_cnpj,
        tipo_operacao=TipoOperacao.RECUPERACAO_JUDICIAL,
        tipo_garantia=TipoGarantia.PERFORMANCE_BOND,
        valor_garantia=valor_garantia,
        valor_contrato=valor_contrato,
        descricao=kwargs.get('descricao', ''),
        origem=origem,
        contato_nome=contato_nome,
        contato_cargo=contato_cargo,
        contato_email=contato_email,
        contato_telefone=contato_telefone,
        **{k: v for k, v in kwargs.items() if k != 'descricao'}
    )

    # Para RJ, adiciona red flag automático
    operacao.adicionar_red_flag("Empresa em Recuperação Judicial - Complexidade elevada")

    fases = criar_fases_padrao(
        valor_total_operacao=valor_estimado_honorarios,
        valor_diagnostico=valor_diagnostico
    )

    for fase in fases:
        operacao.adicionar_fase(fase)

    return operacao
