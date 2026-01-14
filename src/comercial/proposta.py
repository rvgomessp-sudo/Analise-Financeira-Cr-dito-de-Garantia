"""
Gerador de Propostas Comerciais e Abordagens

Este módulo implementa:
1. Geração de propostas comerciais estruturadas por fase
2. Scripts de abordagem para DEMANDA PASSIVA (cliente vem)
3. Scripts de abordagem para PROSPECÇÃO ATIVA (buscamos o cliente)
4. Argumentação técnica para justificar cobrança antecipada

Princípio Central:
- Diagnóstico SEMPRE 100% antecipado
- Cada fase tem valor independente
- Nunca entregar sem pagamento
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal
from string import Template

from .operacao import Operacao, TipoOperacao, FaseOperacao
from .tomador import Tomador, ClassificacaoRisco
from .qualificador import AnaliseViabilidade, NivelComplexidade


class TipoAbordagem(Enum):
    """Tipo de abordagem comercial"""
    DEMANDA_PASSIVA = "Demanda Passiva"
    PROSPECCAO_ATIVA = "Prospecção Ativa"
    RETORNO_CLIENTE = "Retorno de Cliente"


@dataclass
class PropostaComercial:
    """Proposta comercial estruturada"""

    # Identificação
    numero: str
    data: datetime

    # Partes
    tomador_nome: str
    tomador_cnpj: str
    contato_nome: str

    # Operação
    descricao_operacao: str
    valor_garantia: Decimal
    tipo_operacao: str

    # Fases e valores
    fases: List[Dict]
    valor_total: Decimal

    # Condições
    condicoes_gerais: List[str]
    condicoes_pagamento: List[str]

    # Validade
    validade_dias: int = 15

    # Observações
    observacoes: str = ""

    def gerar_texto(self) -> str:
        """Gera texto formatado da proposta"""

        texto = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PROPOSTA COMERCIAL                                   ║
║                         Nº {self.numero:<20}                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Data: {self.data.strftime('%d/%m/%Y'):<72} ║
║ Validade: {self.validade_dias} dias                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TOMADOR                                                                      ║
║ Razão Social: {self.tomador_nome:<62} ║
║ CNPJ: {self.tomador_cnpj:<70} ║
║ Contato: {self.contato_nome:<67} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ OPERAÇÃO                                                                     ║
║ Tipo: {self.tipo_operacao:<70} ║
║ Valor da Garantia: R$ {self.valor_garantia:>15,.2f}                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ DESCRIÇÃO                                                                    ║
"""
        # Adiciona descrição
        for linha in self.descricao_operacao.split('\n'):
            linha = linha.strip()
            if linha:
                texto += f"║ {linha:<76} ║\n"

        texto += """╠══════════════════════════════════════════════════════════════════════════════╣
║ ESTRUTURA DE TRABALHO E INVESTIMENTO                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""

        # Adiciona fases
        for fase in self.fases:
            texto += f"""║                                                                              ║
║ FASE {fase['numero']}: {fase['nome']:<66} ║
║ {'─' * 76} ║
║ Descrição: {fase['descricao'][:65]:<65} ║
"""
            if len(fase['descricao']) > 65:
                resto = fase['descricao'][65:]
                while resto:
                    texto += f"║            {resto[:65]:<65} ║\n"
                    resto = resto[65:]

            texto += f"""║                                                                              ║
║ Entregáveis:                                                                 ║
"""
            for entregavel in fase['entregaveis'][:5]:
                texto += f"║   • {entregavel[:71]:<71} ║\n"

            texto += f"""║                                                                              ║
║ Investimento: R$ {fase['valor']:>15,.2f}                                            ║
║ Condição: {fase['condicao_pagamento']:<66} ║
"""

        # Total
        texto += f"""╠══════════════════════════════════════════════════════════════════════════════╣
║ INVESTIMENTO TOTAL: R$ {self.valor_total:>15,.2f}                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CONDIÇÕES GERAIS                                                             ║
"""
        for condicao in self.condicoes_gerais:
            texto += f"║ • {condicao[:73]:<73} ║\n"

        texto += """╠══════════════════════════════════════════════════════════════════════════════╣
║ CONDIÇÕES DE PAGAMENTO                                                       ║
"""
        for condicao in self.condicoes_pagamento:
            texto += f"║ • {condicao[:73]:<73} ║\n"

        if self.observacoes:
            texto += """╠══════════════════════════════════════════════════════════════════════════════╣
║ OBSERVAÇÕES                                                                  ║
"""
            for linha in self.observacoes.split('\n'):
                linha = linha.strip()
                if linha:
                    texto += f"║ {linha[:76]:<76} ║\n"

        texto += """╠══════════════════════════════════════════════════════════════════════════════╣
║ ACEITE                                                                       ║
║                                                                              ║
║ Declaro que li e aceito os termos desta proposta.                            ║
║                                                                              ║
║ Data: ___/___/______                                                         ║
║                                                                              ║
║ ___________________________________                                          ║
║ Assinatura do Responsável                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return texto


class GeradorProposta:
    """
    Gera propostas comerciais e scripts de abordagem.
    """

    def __init__(self):
        pass

    def gerar_proposta(self, operacao: Operacao,
                       tomador: Tomador,
                       analise: AnaliseViabilidade,
                       numero_proposta: str = None) -> PropostaComercial:
        """
        Gera proposta comercial completa baseada na análise.
        """

        if not numero_proposta:
            numero_proposta = f"PC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Monta fases com valores da análise
        fases = []
        valor_total = Decimal('0')

        # Fase 1: Diagnóstico (sempre presente)
        valor_diagnostico = analise.valor_recomendado_diagnostico
        fases.append({
            'numero': 1,
            'nome': 'DIAGNÓSTICO TÉCNICO',
            'descricao': (
                'Análise profunda do caso para identificar a situação atual, '
                'motivos de recusas anteriores, obstáculos técnicos e regulatórios, '
                'viabilidade de aprovação e linha de trabalho proposta. '
                'Esta fase tem valor independente do resultado final.'
            ),
            'entregaveis': [
                'Relatório de Diagnóstico Técnico',
                'Análise de Recusas Anteriores',
                'Mapeamento de Obstáculos',
                'Parecer de Viabilidade',
                'Plano de Trabalho (se viável)'
            ],
            'valor': valor_diagnostico,
            'condicao_pagamento': '100% ANTECIPADO - Início dos trabalhos após confirmação'
        })
        valor_total += valor_diagnostico

        # Fase 2: Execução (se diagnóstico indicar viabilidade)
        valor_execucao = valor_diagnostico * Decimal('2.5')  # Estimativa
        fases.append({
            'numero': 2,
            'nome': 'EXECUÇÃO TÉCNICA',
            'descricao': (
                'Trabalho técnico de estruturação e aprovação. Inclui reconstrução '
                'da operação, elaboração de estudos técnicos, fundamentação em '
                'legislação e normativas, e negociação com seguradoras.'
            ),
            'entregaveis': [
                'Estudo de Viabilidade Econômica',
                'Dossiê Técnico Completo',
                'Parecer Fundamentado',
                'Proposta de Estruturação',
                'Aprovação de Limite'
            ],
            'valor': valor_execucao,
            'condicao_pagamento': self._definir_condicao_execucao(tomador)
        })
        valor_total += valor_execucao

        # Fase 3: Emissão (opcional)
        valor_emissao = valor_diagnostico * Decimal('0.5')
        fases.append({
            'numero': 3,
            'nome': 'ACOMPANHAMENTO ATÉ EMISSÃO',
            'descricao': (
                'Acompanhamento do processo até a emissão final da apólice, '
                'incluindo revisão de condições e formalização.'
            ),
            'entregaveis': [
                'Proposta Formal da Seguradora',
                'Apólice Emitida',
                'Documentação de Fechamento'
            ],
            'valor': valor_emissao,
            'condicao_pagamento': 'Mediante entrega ou comissão de corretagem'
        })
        valor_total += valor_emissao

        # Condições gerais
        condicoes_gerais = [
            'Os trabalhos serão realizados em fases independentes',
            'Cada fase tem valor próprio, independente do resultado da operação',
            'O diagnóstico entrega clareza sobre o problema, mesmo se inviável',
            'Não há garantia de aprovação, mas sim de análise técnica profunda',
            'Todos os estudos e pareceres são de propriedade intelectual exclusiva',
            'É vedada a reprodução ou compartilhamento sem autorização expressa'
        ]

        # Condições de pagamento
        condicoes_pagamento = [
            'Fase 1 (Diagnóstico): 100% antecipado via boleto ou transferência',
            'Fase 2 (Execução): Conforme estrutura definida para cada caso',
            'Fase 3 (Emissão): Conforme acordo ou comissão de corretagem',
            'Não iniciamos fase sem pagamento da fase correspondente',
            'Não entregamos documentos sem confirmação de pagamento'
        ]

        # Observações baseadas no risco
        observacoes = self._gerar_observacoes(tomador, analise)

        return PropostaComercial(
            numero=numero_proposta,
            data=datetime.now(),
            tomador_nome=tomador.razao_social,
            tomador_cnpj=tomador.cnpj,
            contato_nome=tomador.contato_nome,
            descricao_operacao=operacao.descricao or f"{operacao.tipo_operacao.value} - {operacao.nome}",
            valor_garantia=operacao.valor_garantia,
            tipo_operacao=operacao.tipo_operacao.value,
            fases=fases,
            valor_total=valor_total,
            condicoes_gerais=condicoes_gerais,
            condicoes_pagamento=condicoes_pagamento,
            observacoes=observacoes
        )

    def _definir_condicao_execucao(self, tomador: Tomador) -> str:
        """Define condição de pagamento da execução baseada no risco"""

        if tomador.classificacao == ClassificacaoRisco.VERMELHO:
            return '100% ANTECIPADO - Alto risco identificado'
        elif tomador.classificacao == ClassificacaoRisco.LARANJA:
            return '70% início + 30% entrega'
        elif tomador.classificacao == ClassificacaoRisco.AMARELO:
            return '50% início + 50% entrega'
        else:
            return '30% início + 70% entrega'

    def _gerar_observacoes(self, tomador: Tomador,
                          analise: AnaliseViabilidade) -> str:
        """Gera observações baseadas na análise"""

        obs = []

        if analise.complexidade in [NivelComplexidade.MUITO_ALTA, NivelComplexidade.EXTREMA]:
            obs.append(
                f"Operação de complexidade {analise.complexidade.value}. "
                "O valor do diagnóstico reflete a profundidade da análise necessária."
            )

        if len(analise.red_flags) > 0:
            obs.append(
                "Esta proposta considera fatores de risco identificados na análise prévia. "
                "As condições de pagamento refletem o perfil da operação."
            )

        obs.append(
            "O valor do diagnóstico NÃO é reembolsável e NÃO depende do resultado. "
            "Você está contratando nossa análise técnica especializada, não uma garantia de aprovação."
        )

        return '\n'.join(obs)

    # ══════════════════════════════════════════════════════════════════════════
    # SCRIPTS DE ABORDAGEM - DEMANDA PASSIVA
    # ══════════════════════════════════════════════════════════════════════════

    def script_demanda_passiva(self, operacao: Operacao,
                                tomador: Tomador,
                                analise: AnaliseViabilidade) -> Dict[str, str]:
        """
        Gera scripts de abordagem para DEMANDA PASSIVA.

        Contexto: O cliente veio até nós com urgência.
        Leverage: Alta - ele precisa de nós.
        Estratégia: Usar a urgência para estabelecer cobrança antecipada.
        """

        valor_diag = analise.valor_recomendado_diagnostico

        scripts = {}

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 1: Resposta Inicial à Solicitação
        # ─────────────────────────────────────────────────────────────────────
        scripts['resposta_inicial'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: RESPOSTA INICIAL À SOLICITAÇÃO DE COTAÇÃO
Contexto: Cliente pediu cotação de seguro garantia
══════════════════════════════════════════════════════════════════════════════

Prezado(a) {tomador.contato_nome},

Obrigado pelo contato. Analisamos preliminarmente a solicitação de
{operacao.tipo_operacao.value} no valor de R$ {operacao.valor_garantia:,.2f}.

Antes de avançarmos, preciso ser transparente:

Após uma análise inicial, identificamos que este caso apresenta
complexidade que vai além de uma simples cotação de mercado.
{self._motivo_complexidade(operacao, tomador)}

O que isso significa na prática?

Casos como este exigem um trabalho técnico aprofundado para identificar:
• Por que o mercado está recusando (ou recusaria)
• Quais são os obstáculos técnicos e regulatórios
• Se existe um caminho viável para aprovação
• Qual estratégia de estruturação pode funcionar

Este tipo de análise não é uma cotação - é um DIAGNÓSTICO TÉCNICO
especializado que demanda tempo, expertise e pesquisa.

Nossa proposta:

Realizamos o Diagnóstico Técnico por um investimento de
R$ {valor_diag:,.2f}, que inclui:

✓ Análise completa da situação do tomador
✓ Mapeamento de obstáculos no mercado
✓ Parecer de viabilidade fundamentado
✓ Plano de trabalho (se viável)

IMPORTANTE: Este valor é pelo diagnóstico, não pelo resultado.
Você terá clareza sobre o problema independente de conseguirmos
ou não aprovar a operação.

Se houver interesse em prosseguir, envio a proposta formal.

Atenciosamente,
[Seu nome]

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Não entregar análise sem pagamento. A resposta inicial
já posiciona que não é uma simples cotação.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 2: Objeção "Muito Caro"
        # ─────────────────────────────────────────────────────────────────────
        scripts['objecao_preco'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: RESPOSTA À OBJEÇÃO "MUITO CARO" / "OUTROS NÃO COBRAM"
══════════════════════════════════════════════════════════════════════════════

Entendo sua preocupação com o investimento.

Permita-me explicar a diferença:

O que outros corretores fazem:
• Enviam sua documentação para várias seguradoras
• Esperam a resposta (geralmente recusa)
• Informam que "não conseguiram"
• Você fica sem saber o porquê e sem solução

O que nós fazemos:
• Análise técnica profunda ANTES de ir ao mercado
• Identificação das causas reais das recusas
• Estruturação criativa da operação
• Fundamentação em legislação e normativas
• Defesa técnica junto às seguradoras

Nosso trabalho não é "pedir cotação" - é CONSTRUIR a solução.

Sobre o valor:

O diagnóstico de R$ {valor_diag:,.2f} representa uma fração
do que você perderia se:
• Perder a licitação por falta de garantia
• Ficar meses tentando sem sucesso
• Contratar alguém que não resolve

Casos como o seu - {operacao.tipo_operacao.value} de
R$ {operacao.valor_garantia:,.2f} - não se resolvem com
cotação de balcão. Requerem expertise.

Se preferir tentar o caminho tradicional primeiro, sem problema.
Estaremos aqui quando precisar de uma abordagem diferente.

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Não reduzir preço. Se ele não valoriza o diagnóstico,
provavelmente não vai pagar a execução também. Melhor não entrar.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 3: Objeção "Pago no Final"
        # ─────────────────────────────────────────────────────────────────────
        scripts['objecao_pagar_final'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: RESPOSTA À OBJEÇÃO "PREFIRO PAGAR QUANDO CONSEGUIR"
══════════════════════════════════════════════════════════════════════════════

Entendo. Seria confortável pagar só pelo resultado.

Mas deixa eu explicar por que não trabalhamos assim:

1. O diagnóstico TEM VALOR independente do resultado

   Mesmo que a conclusão seja "não é viável", você terá:
   • Clareza sobre por que o mercado recusa
   • O que precisaria mudar para conseguir no futuro
   • Documentação técnica do problema

   Isso tem valor. Clientes já usaram nossos diagnósticos
   para negociar com bancos, ajustar operações, ou
   planejar para o próximo ciclo.

2. Nosso trabalho acontece ANTES do resultado

   Vamos investir dezenas de horas de análise, pesquisa,
   elaboração de estudos. Esse trabalho existe
   independente de aprovar ou não.

3. Histórico de mercado

   Infelizmente, quando cobramos no final, uma parte
   significativa dos clientes "desaparece" após receber
   o trabalho. Não por má-fé necessariamente, mas porque
   a urgência passou e outras prioridades surgem.

   Não podemos mais assumir esse risco.

O que posso oferecer:

O diagnóstico é R$ {valor_diag:,.2f} - 100% antecipado.
Se o diagnóstico indicar viabilidade e você quiser prosseguir
para a execução, discutimos a estrutura de pagamento dessa fase.

É um compromisso mútuo: você investe no diagnóstico,
nós investimos nosso melhor trabalho técnico.

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Não ceder. Se o cliente não aceita pagar pelo diagnóstico,
ele não valoriza seu trabalho e provavelmente dará problema depois.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 4: Fechamento com Urgência
        # ─────────────────────────────────────────────────────────────────────
        scripts['fechamento_urgencia'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: FECHAMENTO USANDO A URGÊNCIA
Contexto: Cliente tem prazo apertado (licitação, contrato, etc.)
══════════════════════════════════════════════════════════════════════════════

{tomador.contato_nome}, vou ser direto:

Você tem {operacao.dias_ate_limite or 'poucos'} dias até o prazo.
O mercado já recusou. Você precisa de uma solução.

Nós podemos ajudar, mas preciso da sua decisão AGORA.

O diagnóstico custa R$ {valor_diag:,.2f}.
Com o pagamento confirmado hoje, iniciamos amanhã.

Se houver viabilidade (e geralmente encontramos caminhos
que outros não veem), partimos para a execução imediatamente.

O que eu preciso de você:
1. Confirmação de interesse
2. Pagamento do diagnóstico
3. Documentação completa

O que você recebe:
1. Análise técnica em até 5 dias úteis
2. Parecer fundamentado
3. Plano de ação (se viável)
4. Prioridade total da equipe

O tempo está contra nós. Cada dia que passa reduz
nossas opções. Vamos resolver isso?

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: A urgência é SUA moeda de troca. Use-a para fechar
o diagnóstico. Não deixe o cliente "pensar" - urgência é agora.
──────────────────────────────────────────────────────────────────────────────
"""

        return scripts

    # ══════════════════════════════════════════════════════════════════════════
    # SCRIPTS DE ABORDAGEM - PROSPECÇÃO ATIVA
    # ══════════════════════════════════════════════════════════════════════════

    def script_prospeccao_ativa(self, operacao: Operacao,
                                 tomador: Tomador,
                                 analise: AnaliseViabilidade) -> Dict[str, str]:
        """
        Gera scripts de abordagem para PROSPECÇÃO ATIVA.

        Contexto: Nós estamos buscando o cliente.
        Leverage: Baixa - ele não estava procurando.
        Estratégia: Criar urgência identificando um PROBLEMA que ele não sabia que tinha.
        """

        valor_diag = analise.valor_recomendado_diagnostico

        scripts = {}

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 1: Abordagem Inicial - Criar Problema
        # ─────────────────────────────────────────────────────────────────────
        scripts['abordagem_inicial'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: ABORDAGEM INICIAL - PROSPECÇÃO ATIVA
Estratégia: Identificar um problema que o cliente não sabe que tem
══════════════════════════════════════════════════════════════════════════════

Prezado(a) {tomador.contato_nome},

Meu nome é [Seu Nome], sou especialista em operações complexas
de seguro garantia.

Estou entrando em contato porque identifiquei uma situação que
pode impactar as operações da {tomador.razao_social}.

[ESCOLHA O GANCHO APROPRIADO]

─────────────────────────────────────────────────────────────────
GANCHO A: Se você sabe de uma licitação/contrato futuro
─────────────────────────────────────────────────────────────────
Tomei conhecimento de que a {tomador.razao_social} participa
frequentemente de [licitações / contratos de grande porte].

Analisando o perfil da empresa, identifiquei alguns pontos que
podem dificultar a obtenção de seguro garantia quando precisar:
• [Ponto específico baseado em pesquisa]
• [Outro ponto]

Isso pode significar perder oportunidades de negócio ou
pagar muito mais caro do que deveria.

─────────────────────────────────────────────────────────────────
GANCHO B: Se a empresa está em situação especial (RJ, etc.)
─────────────────────────────────────────────────────────────────
Sei que a {tomador.razao_social} está em [Recuperação Judicial /
situação especial]. Isso tipicamente fecha as portas do
mercado de seguro garantia.

No entanto, tenho experiência em estruturar operações para
empresas nessa situação. Já viabilizamos garantias para
casos que o mercado dava como impossíveis.

─────────────────────────────────────────────────────────────────
GANCHO C: Se você sabe de uma recusa recente
─────────────────────────────────────────────────────────────────
Soube que recentemente a {tomador.razao_social} teve
dificuldades em obter seguro garantia para [operação].

Isso aconteceu porque [motivo provável]. Mas existe
uma forma de contornar esse obstáculo.

─────────────────────────────────────────────────────────────────

FECHAMENTO (para todos os ganchos):

Gostaria de fazer uma análise preliminar (sem compromisso)
para identificar exatamente qual é a situação e se existe
um caminho viável.

Podemos agendar uma conversa de 20 minutos esta semana?

Atenciosamente,
[Seu nome]

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Na prospecção ativa, você precisa CRIAR o problema na
cabeça do cliente. Ele não estava procurando solução. Faça ele perceber
que tem um problema que precisa resolver.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 2: Reunião de Qualificação
        # ─────────────────────────────────────────────────────────────────────
        scripts['reuniao_qualificacao'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: REUNIÃO DE QUALIFICAÇÃO (Prospecção Ativa)
Objetivo: Transformar curiosidade em necessidade percebida
══════════════════════════════════════════════════════════════════════════════

ABERTURA (5 min):

"Obrigado pelo tempo. Vou ser direto e objetivo.

Meu trabalho é resolver operações de seguro garantia que
o mercado tradicional não consegue. Casos complexos.

Entrei em contato porque identifiquei [o problema/gancho].
Quero entender melhor a situação de vocês."

─────────────────────────────────────────────────────────────────
PERGUNTAS DE DIAGNÓSTICO (10 min):
─────────────────────────────────────────────────────────────────

1. "Vocês participam de licitações ou contratos que exigem
    seguro garantia com frequência?"

2. "Já tiveram dificuldade em obter garantia em algum momento?"
   [Se sim]: "O que aconteceu? Como resolveram?"

3. "Qual é o volume típico de garantias que precisam por ano?"

4. "Têm alguma operação específica no radar para os próximos meses?"

5. "Trabalham com algum corretor fixo ou buscam no mercado?"

6. "Já foram recusados por alguma seguradora? Sabem o motivo?"

─────────────────────────────────────────────────────────────────
CRIAÇÃO DE URGÊNCIA (5 min):
─────────────────────────────────────────────────────────────────

"Com base no que você me contou, vejo alguns pontos de atenção:

[Baseado nas respostas, identifique 2-3 riscos]

• Se X acontecer, vocês podem ter dificuldade em conseguir garantia
• O perfil de vocês sugere que [problema potencial]
• Empresas com características similares costumam enfrentar [obstáculo]

Não estou dizendo que isso VAI acontecer, mas é um risco real.
E quando acontece, geralmente é na pior hora - quando há
uma licitação importante ou um contrato urgente."

─────────────────────────────────────────────────────────────────
PROPOSTA DE DIAGNÓSTICO PREVENTIVO (5 min):
─────────────────────────────────────────────────────────────────

"Minha sugestão é fazermos um Diagnóstico Preventivo.

Não é para resolver um problema urgente (que vocês não têm agora),
mas para MAPEAR a situação e identificar:

• Qual é a real capacidade de vocês no mercado de garantia
• Quais seguradoras têm apetite para o perfil de vocês
• Quais obstáculos podem surgir e como evitá-los
• Como se preparar para operações futuras

O investimento é de R$ {valor_diag * Decimal('0.7'):,.2f}
[Valor menor porque não há urgência]

Com esse mapeamento em mãos, vocês:
1. Sabem exatamente onde estão
2. Podem se preparar para oportunidades
3. Não são pegos de surpresa

É um investimento em inteligência de mercado."

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Na prospecção ativa, você não tem urgência como leverage.
Precisa criar VALOR PERCEBIDO no diagnóstico como "seguro" contra
problemas futuros. O valor pode ser menor porque a demanda é menor.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 3: Follow-up - Sem Resposta
        # ─────────────────────────────────────────────────────────────────────
        scripts['followup_sem_resposta'] = """
══════════════════════════════════════════════════════════════════════════════
SCRIPT: FOLLOW-UP QUANDO NÃO HÁ RESPOSTA
══════════════════════════════════════════════════════════════════════════════

FOLLOW-UP 1 (3-5 dias depois):

"[Nome], tudo bem?

Não tive retorno sobre minha mensagem anterior.

Entendo que talvez não seja prioridade agora - e está tudo bem.

Só quero deixar claro: quando surgir uma licitação ou contrato
que exija seguro garantia e o mercado disser 'não', me procure.

Casos 'impossíveis' são nossa especialidade.

Fico à disposição.
[Seu nome]"

─────────────────────────────────────────────────────────────────
FOLLOW-UP 2 (2-3 semanas depois):
─────────────────────────────────────────────────────────────────

"[Nome],

Passando para compartilhar um caso recente:

Uma empresa do setor [setor do prospecto] nos procurou depois
de ser recusada por [número] seguradoras. Licitação de [valor].
Prazo de [X] dias.

Conseguimos aprovar a garantia. [Breve descrição de como]

Se em algum momento enfrentar situação similar, estamos aqui.

[Seu nome]"

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Na prospecção ativa, a maioria não vai responder.
O objetivo é PLANTAR A SEMENTE para quando precisarem.
Não insista demais - gera rejeição. Seja presente sem ser inconveniente.
──────────────────────────────────────────────────────────────────────────────
"""

        # ─────────────────────────────────────────────────────────────────────
        # SCRIPT 4: Conversão de Interesse em Venda
        # ─────────────────────────────────────────────────────────────────────
        scripts['conversao_interesse'] = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: CONVERSÃO DE INTERESSE EM VENDA (Prospecção Ativa)
Contexto: O prospecto demonstrou interesse, quer saber mais
══════════════════════════════════════════════════════════════════════════════

"Ótimo que tenha interesse em entender melhor.

Deixa eu explicar como trabalhamos:

1. DIAGNÓSTICO TÉCNICO (primeira fase)

   Antes de qualquer coisa, fazemos uma análise profunda
   da situação. Não é uma cotação - é um estudo técnico.

   Nesse diagnóstico, identificamos:
   • Sua real posição no mercado de garantia
   • Obstáculos existentes e potenciais
   • Caminhos possíveis para aprovação
   • Estimativa de prazo e investimento

   O investimento no diagnóstico é de R$ {valor_diag:,.2f}.

2. POR QUE COBRAMOS PELO DIAGNÓSTICO?

   Porque ele tem valor independente. Mesmo que a conclusão
   seja 'não é viável agora', você terá:

   • Clareza sobre sua situação
   • O que precisaria mudar
   • Documentação técnica

   Muitos clientes usam o diagnóstico para outras finalidades:
   negociar com bancos, ajustar operações, planejar.

3. E SE FOR VIÁVEL?

   Se o diagnóstico indicar viabilidade, apresentamos proposta
   para a fase de execução. Aí sim trabalhamos para aprovar
   a garantia.

   A decisão de prosseguir é sua. Sem compromisso automático.

4. PRÓXIMO PASSO

   Se quiser avançar, preciso de:
   • Documentação básica da empresa
   • Detalhes da operação (se houver específica)
   • Pagamento do diagnóstico

   Com isso, iniciamos a análise em 48 horas.

Faz sentido para você?"

──────────────────────────────────────────────────────────────────────────────
PONTO-CHAVE: Mesmo sem urgência, o diagnóstico precisa ser pago antes.
Se o cliente não valoriza o diagnóstico preventivo, ele não é seu cliente.
Não reduza o preço para "fechar" - isso desvaloriza seu trabalho.
──────────────────────────────────────────────────────────────────────────────
"""

        return scripts

    def _motivo_complexidade(self, operacao: Operacao, tomador: Tomador) -> str:
        """Gera texto explicando a complexidade do caso"""

        motivos = []

        if tomador.em_recuperacao_judicial:
            motivos.append("empresa em Recuperação Judicial")

        if len(tomador.seguradoras_que_recusaram) > 0:
            motivos.append(f"recusas anteriores no mercado")

        if operacao.tipo_operacao == TipoOperacao.MA:
            motivos.append("operação de M&A com estrutura complexa")

        if operacao.tipo_operacao == TipoOperacao.FINANCEIRA:
            motivos.append("garantia financeira (modalidade restritiva)")

        if operacao.valor_garantia > Decimal('50000000'):
            motivos.append("valor elevado da garantia")

        if len(motivos) == 0:
            motivos.append("características específicas do caso")

        return "Identificamos: " + ", ".join(motivos) + "."

    # ══════════════════════════════════════════════════════════════════════════
    # GERAÇÃO DE DOCUMENTOS
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_contrato_fase(self, fase: int, operacao: Operacao,
                           tomador: Tomador, valor: Decimal) -> str:
        """
        Gera modelo de contrato para fase específica.
        """

        nomes_fase = {
            1: "DIAGNÓSTICO TÉCNICO",
            2: "EXECUÇÃO TÉCNICA",
            3: "ACOMPANHAMENTO ATÉ EMISSÃO"
        }

        nome_fase = nomes_fase.get(fase, f"FASE {fase}")

        contrato = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            CONTRATO DE PRESTAÇÃO DE SERVIÇOS - {nome_fase:<24} ║
╚══════════════════════════════════════════════════════════════════════════════╝

CONTRATANTE: {tomador.razao_social}
CNPJ: {tomador.cnpj}
Representado por: {tomador.contato_nome}

CONTRATADA: [Sua Empresa]
CNPJ: [Seu CNPJ]

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 1 - OBJETO
════════════════════════════════════════════════════════════════════════════════

O presente contrato tem por objeto a prestação de serviços de {nome_fase}
relacionados à operação de {operacao.tipo_operacao.value} descrita abaixo:

• Valor da Garantia: R$ {operacao.valor_garantia:,.2f}
• Tipo: {operacao.tipo_garantia.value if hasattr(operacao, 'tipo_garantia') else 'Seguro Garantia'}

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 2 - VALOR E PAGAMENTO
════════════════════════════════════════════════════════════════════════════════

2.1. O valor dos serviços objeto deste contrato é de R$ {valor:,.2f}
     ({self._valor_por_extenso(valor)}).

2.2. O pagamento deverá ser realizado INTEGRALMENTE E ANTECIPADAMENTE,
     antes do início dos trabalhos.

2.3. Os trabalhos somente serão iniciados após confirmação do pagamento
     na conta bancária da CONTRATADA.

2.4. O valor NÃO É REEMBOLSÁVEL, independente do resultado do trabalho.

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 3 - PROPRIEDADE INTELECTUAL
════════════════════════════════════════════════════════════════════════════════

3.1. Todos os estudos, análises, pareceres, relatórios e demais documentos
     produzidos pela CONTRATADA são de sua PROPRIEDADE INTELECTUAL EXCLUSIVA.

3.2. A CONTRATANTE recebe LICENÇA DE USO dos materiais exclusivamente para
     a finalidade da operação objeto deste contrato.

3.3. É EXPRESSAMENTE VEDADO à CONTRATANTE:
     a) Compartilhar os materiais com terceiros, incluindo outros corretores
     b) Utilizar os materiais para outras operações
     c) Reproduzir, total ou parcialmente, os materiais
     d) Apresentar os materiais como de sua autoria

3.4. A violação desta cláusula sujeitará a CONTRATANTE ao pagamento de
     multa equivalente a 10 (dez) vezes o valor deste contrato, sem
     prejuízo de perdas e danos.

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 4 - CONFIDENCIALIDADE
════════════════════════════════════════════════════════════════════════════════

4.1. As partes se comprometem a manter sigilo sobre todas as informações
     trocadas durante a execução deste contrato.

4.2. A CONTRATANTE autoriza a CONTRATADA a mencionar a realização do
     trabalho em seu portfólio, sem revelar detalhes confidenciais.

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 5 - EXCLUSIVIDADE
════════════════════════════════════════════════════════════════════════════════

5.1. Durante a vigência deste contrato, a CONTRATANTE se compromete a
     não contratar outros profissionais para a mesma finalidade.

5.2. Caso a CONTRATANTE viole esta cláusula, deverá pagar à CONTRATADA
     multa equivalente ao valor total dos honorários contratados para
     todas as fases da operação.

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 6 - LIMITAÇÃO DE RESPONSABILIDADE
════════════════════════════════════════════════════════════════════════════════

6.1. A CONTRATADA NÃO GARANTE a aprovação da operação, mas sim a
     realização do trabalho técnico com diligência e expertise.

6.2. A responsabilidade da CONTRATADA limita-se ao valor efetivamente
     pago pela CONTRATANTE.

════════════════════════════════════════════════════════════════════════════════
CLÁUSULA 7 - FORO
════════════════════════════════════════════════════════════════════════════════

7.1. Fica eleito o foro da Comarca de [Sua Cidade] para dirimir quaisquer
     questões oriundas deste contrato.


Data: ____/____/________

_________________________________    _________________________________
CONTRATANTE                          CONTRATADA
{tomador.razao_social[:30]}

"""
        return contrato

    def _valor_por_extenso(self, valor: Decimal) -> str:
        """Converte valor para extenso (simplificado)"""
        # Implementação simplificada
        valor_int = int(valor)
        if valor_int >= 1000000:
            return f"{valor_int/1000000:.1f} milhão(ões) de reais"
        elif valor_int >= 1000:
            return f"{valor_int/1000:.0f} mil reais"
        else:
            return f"{valor_int} reais"
