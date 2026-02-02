"""
Score de Propensão (Oportunidade)

Avalia a probabilidade de fechamento de uma oportunidade.

Fatores:
    - Qualidade do dossiê (completude) — peso 25
    - Mitigadores / Contragarantias — peso 20
    - Urgência / Cronograma — peso 15
    - Histórico de resposta das seguradoras — peso 20
    - Racional econômico (taxa/prêmio) — peso 10
    - Etapa no pipeline (mais avançada = mais provável) — peso 10
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict
from decimal import Decimal

from src.crm.models.oportunidade import (
    Oportunidade, EtapaOportunidade, StatusSeguradoraOportunidade,
)
from src.crm.models.conta import Conta


@dataclass
class DetalhePropensao:
    """Detalhe do cálculo de um fator do score"""
    fator: str
    peso: int
    pontuacao_bruta: float
    pontuacao_ponderada: float
    justificativa: str


@dataclass
class ResultadoScorePropensao:
    """Resultado completo do scoring de propensão"""
    score_total: float  # 0-100
    semaforo: str  # verde, amarelo, vermelho
    probabilidade_fechamento: float  # % estimado
    proxima_melhor_acao: str
    detalhes: List[DetalhePropensao] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'score_total': round(self.score_total, 1),
            'semaforo': self.semaforo,
            'probabilidade_fechamento': round(self.probabilidade_fechamento, 1),
            'proxima_melhor_acao': self.proxima_melhor_acao,
            'detalhes': [
                {
                    'fator': d.fator,
                    'peso': d.peso,
                    'pontuacao': round(d.pontuacao_bruta, 1),
                    'contribuicao': round(d.pontuacao_ponderada, 1),
                    'justificativa': d.justificativa,
                }
                for d in self.detalhes
            ],
        }


class ScorePropensao:
    """
    Motor de scoring de propensão para oportunidades.

    Avalia probabilidade de fechamento e sugere próxima melhor ação.
    Score 0-100, mapeado para probabilidade de fechamento.
    """

    PESO_DOSSIE = 25
    PESO_MITIGADORES = 20
    PESO_URGENCIA = 15
    PESO_SEGURADORAS = 20
    PESO_ECONOMIA = 10
    PESO_ETAPA = 10

    def calcular(self, oportunidade: Oportunidade,
                 conta: Optional[Conta] = None) -> ResultadoScorePropensao:
        """Calcula score de propensão completo"""
        detalhes = []

        # 1. Qualidade do dossiê
        detalhes.append(self._avaliar_dossie(oportunidade))

        # 2. Mitigadores / Contragarantias
        detalhes.append(self._avaliar_mitigadores(oportunidade))

        # 3. Urgência / Cronograma
        detalhes.append(self._avaliar_urgencia(oportunidade))

        # 4. Histórico seguradoras
        detalhes.append(self._avaliar_seguradoras(oportunidade))

        # 5. Racional econômico
        detalhes.append(self._avaliar_economia(oportunidade))

        # 6. Etapa no pipeline
        detalhes.append(self._avaliar_etapa(oportunidade))

        score_total = sum(d.pontuacao_ponderada for d in detalhes)

        # Semáforo
        if score_total >= 70:
            semaforo = "verde"
        elif score_total >= 40:
            semaforo = "amarelo"
        else:
            semaforo = "vermelho"

        # Probabilidade de fechamento (calibração)
        probabilidade = self._calcular_probabilidade(score_total, oportunidade)

        # Próxima melhor ação
        proxima_acao = self._determinar_proxima_acao(oportunidade, detalhes)

        resultado = ResultadoScorePropensao(
            score_total=score_total,
            semaforo=semaforo,
            probabilidade_fechamento=probabilidade,
            proxima_melhor_acao=proxima_acao,
            detalhes=detalhes,
        )

        # Atualiza oportunidade
        oportunidade.score_propensao = score_total
        oportunidade.probabilidade_fechamento = probabilidade

        return resultado

    def _avaliar_dossie(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia completude do dossiê"""
        pontuacao = 0
        justificativas = []

        if oportunidade.tem_objeto_contratual:
            pontuacao += 30
            justificativas.append("Objeto contratual preenchido")

        if oportunidade.valor_garantia:
            pontuacao += 15
            justificativas.append("Valor de garantia definido")

        if oportunidade.vigencia_meses:
            pontuacao += 10
            justificativas.append("Vigência definida")

        if oportunidade.estudos_tecnicos:
            pontuacao += 25
            justificativas.append(f"{len(oportunidade.estudos_tecnicos)} estudo(s) técnico(s)")

        if oportunidade.objeto_contratual and oportunidade.objeto_contratual.cronograma_fisico_financeiro:
            pontuacao += 10
            justificativas.append("Cronograma preenchido")

        if oportunidade.objeto_contratual and oportunidade.objeto_contratual.clausulas_criticas:
            pontuacao += 10
            justificativas.append("Cláusulas críticas mapeadas")

        pontuacao = min(100, pontuacao)
        ponderada = pontuacao * self.PESO_DOSSIE / 100
        return DetalhePropensao(
            fator="Qualidade do Dossiê",
            peso=self.PESO_DOSSIE,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa="; ".join(justificativas) if justificativas else "Dossiê incompleto",
        )

    def _avaliar_mitigadores(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia contragarantias e mitigadores"""
        pontuacao = 0
        justificativas = []

        # Contragarantias
        if oportunidade.contragarantias:
            formalizadas = [c for c in oportunidade.contragarantias if c.status == "Formalizada"]
            aceitas = [c for c in oportunidade.contragarantias if c.status == "Aceita"]

            if formalizadas:
                pontuacao += 50
                justificativas.append(f"{len(formalizadas)} contragarantia(s) formalizada(s)")
            elif aceitas:
                pontuacao += 35
                justificativas.append(f"{len(aceitas)} contragarantia(s) aceita(s)")
            else:
                pontuacao += 20
                justificativas.append(f"{len(oportunidade.contragarantias)} contragarantia(s) proposta(s)")
        else:
            justificativas.append("Sem contragarantias")

        # Matriz de risco com mitigações
        if oportunidade.matriz_risco:
            if oportunidade.matriz_risco.tem_mitigacoes_completas:
                pontuacao += 40
                justificativas.append("Todos os riscos com mitigadores")
            elif oportunidade.matriz_risco.itens:
                mitigados = sum(1 for i in oportunidade.matriz_risco.itens if i.mitigacao)
                total = len(oportunidade.matriz_risco.itens)
                pontuacao += 20
                justificativas.append(f"{mitigados}/{total} riscos com mitigadores")

            # Riscos críticos sem mitigação penalizam
            criticos_sem_mitigacao = [
                i for i in oportunidade.matriz_risco.riscos_criticos
                if not i.mitigacao
            ]
            if criticos_sem_mitigacao:
                pontuacao = max(0, pontuacao - 25)
                justificativas.append(
                    f"{len(criticos_sem_mitigacao)} risco(s) crítico(s) sem mitigação"
                )

        pontuacao = min(100, max(0, pontuacao))
        ponderada = pontuacao * self.PESO_MITIGADORES / 100
        return DetalhePropensao(
            fator="Mitigadores / Contragarantias",
            peso=self.PESO_MITIGADORES,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa="; ".join(justificativas) if justificativas else "Sem dados",
        )

    def _avaliar_urgencia(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia urgência e cronograma"""
        pontuacao = 50  # Base

        if oportunidade.data_previsao_fechamento:
            dias = (oportunidade.data_previsao_fechamento - date.today()).days
            if dias < 0:
                pontuacao = 20  # Atrasada
                justificativa = "Previsão de fechamento ultrapassada"
            elif dias <= 15:
                pontuacao = 90  # Urgente, iminente
                justificativa = f"Fechamento previsto em {dias} dias"
            elif dias <= 30:
                pontuacao = 80
                justificativa = f"Fechamento previsto em {dias} dias"
            elif dias <= 60:
                pontuacao = 65
                justificativa = f"Fechamento previsto em {dias} dias"
            elif dias <= 90:
                pontuacao = 50
                justificativa = f"Fechamento previsto em {dias} dias"
            else:
                pontuacao = 35
                justificativa = f"Fechamento previsto em {dias} dias (longo prazo)"
        else:
            pontuacao = 30
            justificativa = "Sem previsão de fechamento definida"

        # Renovações têm urgência natural
        if oportunidade.renovacao_prevista:
            pontuacao = min(100, pontuacao + 15)
            justificativa += "; Renovação prevista (urgência natural)"

        ponderada = pontuacao * self.PESO_URGENCIA / 100
        return DetalhePropensao(
            fator="Urgência / Cronograma",
            peso=self.PESO_URGENCIA,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=justificativa,
        )

    def _avaliar_seguradoras(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia resposta das seguradoras"""
        if not oportunidade.seguradoras:
            return DetalhePropensao(
                fator="Histórico Seguradoras",
                peso=self.PESO_SEGURADORAS,
                pontuacao_bruta=30,
                pontuacao_ponderada=30 * self.PESO_SEGURADORAS / 100,
                justificativa="Nenhuma seguradora abordada ainda",
            )

        aprovadas = len(oportunidade.seguradoras_aprovadas)
        recusadas = len(oportunidade.seguradoras_recusadas)
        em_analise = len([
            s for s in oportunidade.seguradoras
            if s.status == StatusSeguradoraOportunidade.EM_ANALISE
        ])
        em_contestacao = len(oportunidade.seguradoras_em_contestacao)
        total = len(oportunidade.seguradoras)

        pontuacao = 0
        justificativas = []

        if aprovadas > 0:
            pontuacao = 90 + min(10, aprovadas * 5)
            justificativas.append(f"{aprovadas} seguradora(s) aprovou(aram)")
        elif em_analise > 0:
            pontuacao = 50 + min(20, em_analise * 10)
            justificativas.append(f"{em_analise} em análise")
        elif em_contestacao > 0:
            pontuacao = 40
            justificativas.append(f"{em_contestacao} em contestação")

        if recusadas > 0:
            penalidade = min(30, recusadas * 10)
            pontuacao = max(0, pontuacao - penalidade)
            justificativas.append(f"{recusadas} recusa(s)")

        if recusadas == total and total > 0:
            pontuacao = 10
            justificativas.append("Todas seguradoras recusaram")

        pontuacao = min(100, max(0, pontuacao))
        ponderada = pontuacao * self.PESO_SEGURADORAS / 100
        return DetalhePropensao(
            fator="Histórico Seguradoras",
            peso=self.PESO_SEGURADORAS,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa="; ".join(justificativas),
        )

    def _avaliar_economia(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia racional econômico"""
        if not oportunidade.economia:
            return DetalhePropensao(
                fator="Racional Econômico",
                peso=self.PESO_ECONOMIA,
                pontuacao_bruta=30,
                pontuacao_ponderada=30 * self.PESO_ECONOMIA / 100,
                justificativa="Economia da operação não definida",
            )

        eco = oportunidade.economia
        pontuacao = 40  # Base se tem dados
        justificativas = []

        if eco.taxa_praticada:
            pontuacao += 20
            justificativas.append(f"Taxa: {eco.taxa_praticada}% a.a.")

        if eco.margem_percentual is not None:
            if eco.margem_percentual >= 30:
                pontuacao += 30
                justificativas.append(f"Margem atrativa: {eco.margem_percentual:.1f}%")
            elif eco.margem_percentual >= 15:
                pontuacao += 20
                justificativas.append(f"Margem adequada: {eco.margem_percentual:.1f}%")
            elif eco.margem_percentual > 0:
                pontuacao += 10
                justificativas.append(f"Margem baixa: {eco.margem_percentual:.1f}%")
            else:
                justificativas.append("Margem negativa")

        if eco.premio_total and eco.premio_total > Decimal('100000'):
            pontuacao = min(100, pontuacao + 10)
            justificativas.append("Prêmio relevante")

        pontuacao = min(100, pontuacao)
        ponderada = pontuacao * self.PESO_ECONOMIA / 100
        return DetalhePropensao(
            fator="Racional Econômico",
            peso=self.PESO_ECONOMIA,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa="; ".join(justificativas) if justificativas else "Dados econômicos parciais",
        )

    def _avaliar_etapa(self, oportunidade: Oportunidade) -> DetalhePropensao:
        """Avalia posição no pipeline (mais avançada = mais provável)"""
        etapa_num = oportunidade.etapa_numero
        scores_etapa = {
            1: 10, 2: 20, 3: 35, 4: 50,
            5: 65, 6: 80, 7: 95, 8: 100,
        }
        pontuacao = scores_etapa.get(etapa_num, 0)
        justificativa = f"Etapa {etapa_num}: {oportunidade.etapa.value}"

        ponderada = pontuacao * self.PESO_ETAPA / 100
        return DetalhePropensao(
            fator="Posição no Pipeline",
            peso=self.PESO_ETAPA,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=justificativa,
        )

    def _calcular_probabilidade(self, score: float,
                                oportunidade: Oportunidade) -> float:
        """Mapeia score para probabilidade de fechamento"""
        # Base pelo score
        base = score * 0.8

        # Ajuste pela etapa (etapas avançadas têm histórico melhor)
        ajuste_etapa = {
            1: -5, 2: -3, 3: 0, 4: 3,
            5: 5, 6: 10, 7: 15, 8: 0,
        }
        base += ajuste_etapa.get(oportunidade.etapa_numero, 0)

        return min(95, max(5, base))

    def _determinar_proxima_acao(self, oportunidade: Oportunidade,
                                 detalhes: List[DetalhePropensao]) -> str:
        """Determina próxima melhor ação baseada nos fatores mais fracos"""
        # Encontra fator mais fraco
        mais_fraco = min(detalhes, key=lambda d: d.pontuacao_bruta)

        acoes = {
            "Qualidade do Dossiê": "Completar dossiê: adicionar estudo técnico, "
                                   "cronograma e cláusulas críticas",
            "Mitigadores / Contragarantias": "Propor contragarantias e documentar "
                                             "mitigadores para todos os riscos",
            "Urgência / Cronograma": "Definir previsão de fechamento e validar "
                                     "cronograma com o cliente",
            "Histórico Seguradoras": "Submeter dossiê a mais seguradoras ou "
                                     "contestar recusas existentes",
            "Racional Econômico": "Calcular economia da operação (taxa, prêmio, margem)",
            "Posição no Pipeline": "Completar requisitos da etapa atual para avançar",
        }

        acao_base = acoes.get(mais_fraco.fator, "Revisar oportunidade")

        # Ações específicas por etapa
        etapa_acoes = {
            EtapaOportunidade.PESQUISA_SINAIS: "Validar e enriquecer dados da conta (CNPJ, CNAE, porte)",
            EtapaOportunidade.QUALIFICACAO_PJ: "Mapear decisores e calcular score de fit",
            EtapaOportunidade.DESCOBERTA_OBJETO: "Capturar objeto contratual e escopo da garantia",
            EtapaOportunidade.PRE_RISCO: "Elaborar matriz de risco e propor contragarantias",
            EtapaOportunidade.ESTRUTURACAO_SUBMISSAO: "Montar e submeter dossiê para seguradoras",
            EtapaOportunidade.NEGOCIACAO: "Negociar taxa e condições com seguradora aprovadora",
            EtapaOportunidade.FECHAMENTO_EMISSAO: "Formalizar emissão da apólice",
            EtapaOportunidade.POS_EMISSAO: "Configurar monitoramento de marcos e renovação",
        }

        etapa_acao = etapa_acoes.get(oportunidade.etapa, "")

        if mais_fraco.pontuacao_bruta < 30:
            return f"PRIORIDADE: {acao_base}"
        return etapa_acao or acao_base
