"""
Qualificador de Operação - Sistema de Decisão

Este módulo implementa a análise de viabilidade comercial de uma operação,
respondendo à pergunta: "Vale a pena entrar nessa operação?"

Considera:
- Risco do tomador (probabilidade de calote)
- Complexidade da operação
- Retorno esperado vs. esforço
- Estrutura de cobrança recomendada
- Capacidade de proteção
"""

from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Tuple
from decimal import Decimal

from .operacao import Operacao, TipoOperacao, OrigemOperacao
from .tomador import Tomador, ClassificacaoRisco


class DecisaoOperacao(Enum):
    """Decisão sobre entrar ou não na operação"""
    ENTRAR = "Entrar na Operação"
    ENTRAR_COM_RESTRICOES = "Entrar com Restrições"
    AVALIAR_MELHOR = "Avaliar Melhor"
    NAO_ENTRAR = "Não Entrar"
    RECUSAR = "Recusar Imediatamente"


class NivelComplexidade(Enum):
    """Nível de complexidade da operação"""
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    MUITO_ALTA = "Muito Alta"
    EXTREMA = "Extrema"


@dataclass
class AnaliseViabilidade:
    """Resultado da análise de viabilidade de uma operação"""

    # Decisão
    decisao: DecisaoOperacao
    confianca: float  # 0-100%

    # Scores componentes
    score_risco_tomador: float  # 0-100 (maior = mais risco)
    score_complexidade: float  # 0-100 (maior = mais complexo)
    score_retorno: float  # 0-100 (maior = melhor retorno)
    score_protecao: float  # 0-100 (maior = mais protegido)

    # Score final
    score_viabilidade: float  # 0-100 (maior = mais viável)

    # Detalhes
    complexidade: NivelComplexidade
    valor_minimo_diagnostico: Decimal
    valor_recomendado_diagnostico: Decimal
    estrutura_cobranca: Dict

    # Alertas e recomendações
    red_flags: List[str]
    pontos_atencao: List[str]
    recomendacoes: List[str]

    # Justificativa
    justificativa: str

    # Timestamp
    data_analise: datetime


class QualificadorOperacao:
    """
    Sistema de qualificação de operações comerciais.

    Responde: "Devo entrar nessa operação?"
    E se sim: "Com qual estrutura de cobrança?"
    """

    # Configurações de thresholds
    VALOR_MINIMO_DIAGNOSTICO = Decimal('15000')
    VALOR_DIAGNOSTICO_RJ = Decimal('35000')
    VALOR_DIAGNOSTICO_MA = Decimal('30000')
    VALOR_DIAGNOSTICO_PADRAO = Decimal('25000')

    # Multiplicadores por complexidade
    MULTIPLICADOR_COMPLEXIDADE = {
        NivelComplexidade.BAIXA: 1.0,
        NivelComplexidade.MEDIA: 1.2,
        NivelComplexidade.ALTA: 1.5,
        NivelComplexidade.MUITO_ALTA: 2.0,
        NivelComplexidade.EXTREMA: 2.5
    }

    def __init__(self):
        self.historico_analises: List[AnaliseViabilidade] = []

    def qualificar(self, operacao: Operacao, tomador: Tomador) -> AnaliseViabilidade:
        """
        Realiza análise completa de viabilidade da operação.

        Args:
            operacao: Operação a ser analisada
            tomador: Tomador da operação

        Returns:
            AnaliseViabilidade com decisão e recomendações
        """

        # 1. Calcula scores componentes
        score_risco = self._calcular_score_risco(tomador)
        score_complexidade, complexidade = self._calcular_score_complexidade(operacao, tomador)
        score_retorno = self._calcular_score_retorno(operacao, complexidade)
        score_protecao = self._calcular_score_protecao(operacao, tomador)

        # 2. Calcula score de viabilidade final
        # Pesos: Retorno (30%), Risco invertido (30%), Proteção (25%), Complexidade invertida (15%)
        score_viabilidade = (
            score_retorno * 0.30 +
            (100 - score_risco) * 0.30 +
            score_protecao * 0.25 +
            (100 - score_complexidade) * 0.15
        )

        # 3. Identifica red flags
        red_flags = self._identificar_red_flags(operacao, tomador)

        # 4. Define estrutura de cobrança
        valor_min_diag, valor_rec_diag = self._calcular_valores_diagnostico(
            operacao, complexidade
        )
        estrutura_cobranca = self._definir_estrutura_cobranca(
            tomador, complexidade, valor_rec_diag
        )

        # 5. Toma decisão
        decisao, confianca, justificativa = self._tomar_decisao(
            score_viabilidade, score_risco, red_flags, tomador
        )

        # 6. Gera recomendações
        pontos_atencao = self._gerar_pontos_atencao(operacao, tomador, complexidade)
        recomendacoes = self._gerar_recomendacoes(decisao, tomador, operacao)

        analise = AnaliseViabilidade(
            decisao=decisao,
            confianca=confianca,
            score_risco_tomador=score_risco,
            score_complexidade=score_complexidade,
            score_retorno=score_retorno,
            score_protecao=score_protecao,
            score_viabilidade=score_viabilidade,
            complexidade=complexidade,
            valor_minimo_diagnostico=valor_min_diag,
            valor_recomendado_diagnostico=valor_rec_diag,
            estrutura_cobranca=estrutura_cobranca,
            red_flags=red_flags,
            pontos_atencao=pontos_atencao,
            recomendacoes=recomendacoes,
            justificativa=justificativa,
            data_analise=datetime.now()
        )

        self.historico_analises.append(analise)
        return analise

    def _calcular_score_risco(self, tomador: Tomador) -> float:
        """Calcula score de risco do tomador (0-100, maior = mais risco)"""
        if tomador.score_risco is None:
            tomador.calcular_score_risco()
        return tomador.score_risco or 50.0

    def _calcular_score_complexidade(self, operacao: Operacao,
                                      tomador: Tomador) -> Tuple[float, NivelComplexidade]:
        """
        Calcula score de complexidade da operação.
        Retorna (score, nivel).
        """
        score = 0.0

        # Tipo de operação
        complexidade_tipo = {
            TipoOperacao.LICITACAO: 20,
            TipoOperacao.JUDICIAL: 30,
            TipoOperacao.CONTRATUAL: 25,
            TipoOperacao.FINANCEIRA: 35,
            TipoOperacao.ADUANEIRA: 25,
            TipoOperacao.IMOBILIARIA: 30,
            TipoOperacao.MA: 50,
            TipoOperacao.RECUPERACAO_JUDICIAL: 60,
            TipoOperacao.OUTRO: 30
        }
        score += complexidade_tipo.get(operacao.tipo_operacao, 30)

        # Valor da garantia (quanto maior, mais complexo)
        if operacao.valor_garantia > Decimal('100000000'):  # > 100M
            score += 20
        elif operacao.valor_garantia > Decimal('50000000'):  # > 50M
            score += 15
        elif operacao.valor_garantia > Decimal('10000000'):  # > 10M
            score += 10
        elif operacao.valor_garantia > Decimal('1000000'):  # > 1M
            score += 5

        # Situação do tomador
        if tomador.em_recuperacao_judicial:
            score += 15

        # Múltiplas recusas no mercado
        if len(tomador.seguradoras_que_recusaram) >= 3:
            score += 10
        elif len(tomador.seguradoras_que_recusaram) >= 1:
            score += 5

        # Urgência (prazo apertado aumenta complexidade operacional)
        if operacao.dias_ate_limite is not None:
            if operacao.dias_ate_limite <= 7:
                score += 10
            elif operacao.dias_ate_limite <= 15:
                score += 5

        # Limita a 100
        score = min(score, 100)

        # Define nível
        if score >= 80:
            nivel = NivelComplexidade.EXTREMA
        elif score >= 60:
            nivel = NivelComplexidade.MUITO_ALTA
        elif score >= 40:
            nivel = NivelComplexidade.ALTA
        elif score >= 20:
            nivel = NivelComplexidade.MEDIA
        else:
            nivel = NivelComplexidade.BAIXA

        return score, nivel

    def _calcular_score_retorno(self, operacao: Operacao,
                                 complexidade: NivelComplexidade) -> float:
        """
        Calcula score de retorno esperado (0-100, maior = melhor).
        Considera valor vs. esforço estimado.
        """

        # Retorno base pelo valor da garantia
        valor = float(operacao.valor_garantia)

        if valor >= 100_000_000:  # >= 100M
            score_base = 100
        elif valor >= 50_000_000:  # >= 50M
            score_base = 85
        elif valor >= 10_000_000:  # >= 10M
            score_base = 70
        elif valor >= 1_000_000:  # >= 1M
            score_base = 55
        elif valor >= 500_000:  # >= 500K
            score_base = 40
        else:
            score_base = 25

        # Ajusta pela complexidade (mais complexo = precisa de mais retorno para valer)
        multiplicador = self.MULTIPLICADOR_COMPLEXIDADE[complexidade]
        score_ajustado = score_base / multiplicador

        return min(score_ajustado, 100)

    def _calcular_score_protecao(self, operacao: Operacao,
                                  tomador: Tomador) -> float:
        """
        Calcula capacidade de proteção (0-100, maior = mais protegido).
        Quanto mais podemos nos proteger, melhor.
        """
        score = 50.0  # Base

        # Origem da operação
        if operacao.origem == OrigemOperacao.DEMANDA_PASSIVA:
            score += 20  # Cliente veio com urgência = mais leverage
        elif operacao.origem == OrigemOperacao.INDICACAO:
            score += 10
        elif operacao.origem == OrigemOperacao.PROSPECCAO_ATIVA:
            score += 0  # Menos leverage

        # Urgência do tomador
        if operacao.dias_ate_limite is not None and operacao.dias_ate_limite <= 15:
            score += 15  # Urgência = leverage

        # Tomador sem alternativas
        if len(tomador.seguradoras_que_recusaram) >= 3:
            score += 10  # Sem opções = precisa de nós

        # Histórico positivo
        if tomador.historico.taxa_pagamento >= 100:
            score += 10
        elif tomador.historico.taxa_pagamento < 50:
            score -= 20

        return min(max(score, 0), 100)

    def _identificar_red_flags(self, operacao: Operacao,
                                tomador: Tomador) -> List[str]:
        """Identifica red flags da operação"""
        flags = []

        # Do tomador
        flags.extend(operacao.red_flags)
        flags.extend([rf.descricao for rf in tomador.red_flags if rf.ativo])

        # Da operação
        if operacao.ja_tentou_outros_corretores:
            flags.append(f"Já trabalhou com outros corretores: {', '.join(operacao.corretores_anteriores)}")

        if tomador.historico.teve_calote:
            flags.append("HISTÓRICO DE CALOTE - Tomador já não pagou honorários anteriormente")

        if tomador.historico.tem_litigio:
            flags.append("EM LITÍGIO - Temos processo judicial contra este tomador")

        if tomador.classificacao == ClassificacaoRisco.PRETO:
            flags.append("CLASSIFICAÇÃO PRETA - Risco extremo de calote")

        if tomador.classificacao == ClassificacaoRisco.VERMELHO:
            flags.append("CLASSIFICAÇÃO VERMELHA - Alto risco de calote")

        return flags

    def _calcular_valores_diagnostico(self, operacao: Operacao,
                                       complexidade: NivelComplexidade) -> Tuple[Decimal, Decimal]:
        """
        Calcula valores mínimo e recomendado para diagnóstico.
        """

        # Base por tipo de operação
        if operacao.tipo_operacao == TipoOperacao.RECUPERACAO_JUDICIAL:
            valor_base = self.VALOR_DIAGNOSTICO_RJ
        elif operacao.tipo_operacao == TipoOperacao.MA:
            valor_base = self.VALOR_DIAGNOSTICO_MA
        else:
            valor_base = self.VALOR_DIAGNOSTICO_PADRAO

        # Multiplica pela complexidade
        multiplicador = Decimal(str(self.MULTIPLICADOR_COMPLEXIDADE[complexidade]))
        valor_recomendado = valor_base * multiplicador

        # Ajusta pelo valor da garantia (garantias maiores = diagnóstico mais caro)
        if operacao.valor_garantia > Decimal('100000000'):  # > 100M
            valor_recomendado *= Decimal('1.5')
        elif operacao.valor_garantia > Decimal('50000000'):  # > 50M
            valor_recomendado *= Decimal('1.3')

        # Mínimo absoluto
        valor_minimo = max(self.VALOR_MINIMO_DIAGNOSTICO, valor_base * Decimal('0.6'))

        return valor_minimo, valor_recomendado

    def _definir_estrutura_cobranca(self, tomador: Tomador,
                                     complexidade: NivelComplexidade,
                                     valor_diagnostico: Decimal) -> Dict:
        """
        Define estrutura de cobrança recomendada.
        """

        recomendacao = tomador.recomendacao_estrutura_cobranca()

        # Ajusta valores com base na complexidade
        estrutura = {
            'diagnostico': {
                'valor': str(valor_diagnostico),
                'condicao': '100% antecipado - NÃO NEGOCIÁVEL',
                'entrega_condicional': 'Entrega apenas após confirmação de pagamento'
            },
            'execucao': recomendacao['estrutura_fases'][1] if len(recomendacao['estrutura_fases']) > 1 else {},
            'emissao': recomendacao['estrutura_fases'][2] if len(recomendacao['estrutura_fases']) > 2 else {},
            'alertas': recomendacao['alertas'],
            'regra_ouro': 'NUNCA entregar trabalho sem pagamento da fase correspondente'
        }

        # Se complexidade muito alta, exige mais antecipado
        if complexidade in [NivelComplexidade.MUITO_ALTA, NivelComplexidade.EXTREMA]:
            estrutura['execucao'] = {
                'fase': 'Execução',
                'pagamento': '70% início + 30% entrega'
            }
            estrutura['alertas'].append(
                f"Complexidade {complexidade.value}: exigir maior antecipação na execução"
            )

        return estrutura

    def _tomar_decisao(self, score_viabilidade: float,
                       score_risco: float,
                       red_flags: List[str],
                       tomador: Tomador) -> Tuple[DecisaoOperacao, float, str]:
        """
        Toma decisão final sobre a operação.
        Retorna (decisao, confianca, justificativa).
        """

        # Vetos automáticos
        if tomador.classificacao == ClassificacaoRisco.PRETO:
            return (
                DecisaoOperacao.RECUSAR,
                95.0,
                "Tomador com classificação PRETA. Histórico indica risco inaceitável de calote. "
                "Recomendação: não operar sob nenhuma circunstância sem pagamento 100% antecipado "
                "e garantias adicionais."
            )

        if tomador.historico.tem_litigio:
            return (
                DecisaoOperacao.RECUSAR,
                90.0,
                "Tomador em litígio conosco. Não devemos realizar novas operações até "
                "resolução do processo judicial existente."
            )

        # Decisão baseada no score
        if score_viabilidade >= 70:
            return (
                DecisaoOperacao.ENTRAR,
                min(score_viabilidade, 95),
                f"Operação viável. Score {score_viabilidade:.1f}/100. "
                f"Retorno esperado justifica o esforço e risco."
            )

        elif score_viabilidade >= 50:
            if score_risco >= 60:
                return (
                    DecisaoOperacao.ENTRAR_COM_RESTRICOES,
                    score_viabilidade,
                    f"Operação viável com ressalvas. Score {score_viabilidade:.1f}/100. "
                    f"Risco do tomador elevado ({score_risco:.1f}). "
                    f"Exigir 100% antecipado em todas as fases."
                )
            else:
                return (
                    DecisaoOperacao.ENTRAR,
                    score_viabilidade,
                    f"Operação viável. Score {score_viabilidade:.1f}/100. "
                    f"Seguir estrutura de cobrança padrão."
                )

        elif score_viabilidade >= 30:
            if len(red_flags) >= 3:
                return (
                    DecisaoOperacao.NAO_ENTRAR,
                    70,
                    f"Operação de alto risco. Score {score_viabilidade:.1f}/100. "
                    f"Múltiplos red flags identificados. "
                    f"Retorno não justifica o risco."
                )
            else:
                return (
                    DecisaoOperacao.AVALIAR_MELHOR,
                    50,
                    f"Operação marginal. Score {score_viabilidade:.1f}/100. "
                    f"Recomendado avaliar melhor antes de decidir. "
                    f"Se entrar, exigir estrutura rígida de cobrança."
                )

        else:
            return (
                DecisaoOperacao.NAO_ENTRAR,
                80,
                f"Operação não recomendada. Score {score_viabilidade:.1f}/100. "
                f"Risco muito alto para o retorno esperado."
            )

    def _gerar_pontos_atencao(self, operacao: Operacao,
                              tomador: Tomador,
                              complexidade: NivelComplexidade) -> List[str]:
        """Gera lista de pontos de atenção"""
        pontos = []

        if complexidade in [NivelComplexidade.MUITO_ALTA, NivelComplexidade.EXTREMA]:
            pontos.append(f"Complexidade {complexidade.value} - Considere aumentar valor do diagnóstico")

        if operacao.ja_tentou_outros_corretores:
            pontos.append("Outros corretores já trabalharam este caso - risco de desvio")

        if operacao.origem == OrigemOperacao.PROSPECCAO_ATIVA:
            pontos.append("Prospecção ativa - Menor leverage para exigir antecipação")

        if operacao.dias_ate_limite is not None and operacao.dias_ate_limite <= 7:
            pontos.append("Prazo crítico - Use a urgência como leverage para cobrar antecipado")

        if tomador.historico.total_operacoes > 0 and not tomador.historico.teve_calote:
            pontos.append("Histórico positivo - MAS não garantia de pagamento futuro (vide caso Citra)")

        return pontos

    def _gerar_recomendacoes(self, decisao: DecisaoOperacao,
                             tomador: Tomador,
                             operacao: Operacao) -> List[str]:
        """Gera recomendações específicas"""
        recomendacoes = []

        # Sempre recomendar diagnóstico pago
        recomendacoes.append(
            "REGRA #1: Diagnóstico sempre 100% antecipado, sem exceção"
        )

        if decisao in [DecisaoOperacao.ENTRAR, DecisaoOperacao.ENTRAR_COM_RESTRICOES]:
            recomendacoes.append(
                "Enviar proposta comercial formal com estrutura de fases"
            )
            recomendacoes.append(
                "Documentar todas as interações por escrito"
            )

            if tomador.classificacao in [ClassificacaoRisco.VERMELHO, ClassificacaoRisco.LARANJA]:
                recomendacoes.append(
                    "Contrato de prestação de serviços com cláusula de PI reforçada"
                )
                recomendacoes.append(
                    "Não entregar NENHUM documento sem pagamento confirmado"
                )

        if decisao == DecisaoOperacao.AVALIAR_MELHOR:
            recomendacoes.append(
                "Solicitar mais informações antes de decidir"
            )
            recomendacoes.append(
                "Avaliar se tomador aceita estrutura rígida de cobrança"
            )

        if operacao.origem == OrigemOperacao.PROSPECCAO_ATIVA:
            recomendacoes.append(
                "Apresentar valor do diagnóstico como investimento do tomador"
            )
            recomendacoes.append(
                "Usar abordagem de 'problema identificado' para criar urgência"
            )

        return recomendacoes

    def gerar_resumo_executivo(self, analise: AnaliseViabilidade) -> str:
        """
        Gera resumo executivo da análise para apresentação.
        """

        decisao_emoji = {
            DecisaoOperacao.ENTRAR: "✅",
            DecisaoOperacao.ENTRAR_COM_RESTRICOES: "⚠️",
            DecisaoOperacao.AVALIAR_MELHOR: "🔍",
            DecisaoOperacao.NAO_ENTRAR: "❌",
            DecisaoOperacao.RECUSAR: "🚫"
        }

        resumo = f"""
╔══════════════════════════════════════════════════════════════════╗
║  ANÁLISE DE VIABILIDADE - RESUMO EXECUTIVO                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DECISÃO: {decisao_emoji.get(analise.decisao, '')} {analise.decisao.value:<45} ║
║  Confiança: {analise.confianca:.0f}%                                              ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  SCORES                                                          ║
║  ├─ Viabilidade Geral: {analise.score_viabilidade:>5.1f}/100                        ║
║  ├─ Risco do Tomador:  {analise.score_risco_tomador:>5.1f}/100 (maior = pior)       ║
║  ├─ Complexidade:      {analise.score_complexidade:>5.1f}/100 ({analise.complexidade.value})      ║
║  ├─ Retorno Esperado:  {analise.score_retorno:>5.1f}/100                        ║
║  └─ Capacidade Proteção:{analise.score_protecao:>5.1f}/100                        ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  VALORES DIAGNÓSTICO                                             ║
║  ├─ Mínimo:      R$ {analise.valor_minimo_diagnostico:>15,.2f}                   ║
║  └─ Recomendado: R$ {analise.valor_recomendado_diagnostico:>15,.2f}                   ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  RED FLAGS: {len(analise.red_flags)} identificados                                    ║
"""

        for flag in analise.red_flags[:3]:
            resumo += f"║  • {flag[:58]:<58} ║\n"

        if len(analise.red_flags) > 3:
            resumo += f"║  ... e mais {len(analise.red_flags) - 3} flags                                         ║\n"

        resumo += """║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  JUSTIFICATIVA                                                   ║
"""

        # Quebra justificativa em linhas
        justificativa = analise.justificativa
        while len(justificativa) > 60:
            resumo += f"║  {justificativa[:60]:<60} ║\n"
            justificativa = justificativa[60:]
        if justificativa:
            resumo += f"║  {justificativa:<60} ║\n"

        resumo += """║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

        return resumo
