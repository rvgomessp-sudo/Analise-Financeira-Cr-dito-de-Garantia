"""
Score de Fit (Conta)

Avalia a adequação da conta ao ICP (Ideal Customer Profile) da VF.

Fatores:
    - Porte (faturamento/funcionários) — peso 25
    - Setor/CNAE (fit com garantias) — peso 30
    - Histórico com seguros — peso 20
    - Complexidade do objeto recorrente — peso 15
    - Sinais de mercado ativos — peso 10
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from decimal import Decimal

from src.crm.models.conta import Conta, PorteEmpresa


@dataclass
class DetalheFit:
    """Detalhe do cálculo de um fator do score"""
    fator: str
    peso: int
    pontuacao_bruta: float  # 0-100
    pontuacao_ponderada: float  # bruta * peso / 100
    justificativa: str


@dataclass
class ResultadoScoreFit:
    """Resultado completo do scoring de fit"""
    score_total: float  # 0-100
    semaforo: str  # verde, amarelo, vermelho
    icp_fit: bool
    detalhes: List[DetalheFit] = field(default_factory=list)
    recomendacao: str = ""

    def to_dict(self) -> Dict:
        return {
            'score_total': round(self.score_total, 1),
            'semaforo': self.semaforo,
            'icp_fit': self.icp_fit,
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
            'recomendacao': self.recomendacao,
        }


class ScoreFit:
    """
    Motor de scoring de fit para contas (PJ).

    Avalia adequação da conta ao Ideal Customer Profile.
    Score 0-100, com semáforo (verde >= 70, amarelo >= 40, vermelho < 40).
    """

    # CNAEs com alto fit para garantias
    CNAES_ALTO_FIT = {
        '41': 'Construção de Edifícios',
        '42': 'Obras de Infraestrutura',
        '43': 'Serviços Especializados para Construção',
        '35': 'Energia',
        '36': 'Captação/Tratamento de Água',
        '37': 'Esgoto',
        '49': 'Transporte Terrestre',
        '50': 'Transporte Aquaviário',
        '51': 'Transporte Aéreo',
        '52': 'Armazenamento e Atividades Auxiliares',
        '71': 'Serviços de Arquitetura e Engenharia',
        '09': 'Atividades de Apoio à Extração Mineral',
    }

    CNAES_MEDIO_FIT = {
        '46': 'Comércio Atacadista',
        '25': 'Produtos de Metal',
        '26': 'Equipamentos de Informática',
        '27': 'Máquinas e Equipamentos Elétricos',
        '28': 'Máquinas e Equipamentos',
        '29': 'Veículos Automotores',
        '62': 'Atividades de TI',
        '64': 'Serviços Financeiros',
        '84': 'Administração Pública',
    }

    # Pesos dos fatores
    PESO_PORTE = 25
    PESO_SETOR = 30
    PESO_HISTORICO = 20
    PESO_COMPLEXIDADE = 15
    PESO_SINAIS = 10

    def calcular(self, conta: Conta) -> ResultadoScoreFit:
        """
        Calcula score de fit completo para uma conta.

        Returns:
            ResultadoScoreFit com score, semáforo, detalhes e recomendação.
        """
        detalhes = []

        # 1. PORTE (peso 25)
        detalhe_porte = self._avaliar_porte(conta)
        detalhes.append(detalhe_porte)

        # 2. SETOR/CNAE (peso 30)
        detalhe_setor = self._avaliar_setor(conta)
        detalhes.append(detalhe_setor)

        # 3. HISTÓRICO COM SEGUROS (peso 20)
        detalhe_historico = self._avaliar_historico(conta)
        detalhes.append(detalhe_historico)

        # 4. COMPLEXIDADE RECORRENTE (peso 15)
        detalhe_complexidade = self._avaliar_complexidade(conta)
        detalhes.append(detalhe_complexidade)

        # 5. SINAIS DE MERCADO (peso 10)
        detalhe_sinais = self._avaliar_sinais(conta)
        detalhes.append(detalhe_sinais)

        # Score total
        score_total = sum(d.pontuacao_ponderada for d in detalhes)

        # Semáforo
        if score_total >= 70:
            semaforo = "verde"
        elif score_total >= 40:
            semaforo = "amarelo"
        else:
            semaforo = "vermelho"

        # ICP fit
        icp_fit = score_total >= 60

        # Recomendação
        recomendacao = self._gerar_recomendacao(score_total, semaforo, detalhes)

        resultado = ResultadoScoreFit(
            score_total=score_total,
            semaforo=semaforo,
            icp_fit=icp_fit,
            detalhes=detalhes,
            recomendacao=recomendacao,
        )

        # Atualiza conta
        conta.score_fit = score_total
        conta.icp_fit = icp_fit

        return resultado

    def _avaliar_porte(self, conta: Conta) -> DetalheFit:
        """Avalia porte da empresa (maiores = mais fit)"""
        scores = {
            PorteEmpresa.GRANDE: 100,
            PorteEmpresa.MEDIO: 80,
            PorteEmpresa.PEQUENO: 40,
            PorteEmpresa.MICRO: 15,
            PorteEmpresa.MEI: 5,
        }
        pontuacao = scores.get(conta.porte, 30)

        # Bônus por indicadores financeiros
        if conta.indicadores_financeiros:
            ind = conta.indicadores_financeiros
            if ind.faturamento_anual and ind.faturamento_anual > Decimal('500000000'):
                pontuacao = min(100, pontuacao + 10)
            if ind.ebitda and ind.ebitda > Decimal('50000000'):
                pontuacao = min(100, pontuacao + 5)

        ponderada = pontuacao * self.PESO_PORTE / 100
        return DetalheFit(
            fator="Porte da Empresa",
            peso=self.PESO_PORTE,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=f"Porte: {conta.porte.value}",
        )

    def _avaliar_setor(self, conta: Conta) -> DetalheFit:
        """Avalia fit do setor/CNAE com garantias"""
        cnae_prefixo = conta.cnae_principal[:2] if conta.cnae_principal else ""

        if cnae_prefixo in self.CNAES_ALTO_FIT:
            pontuacao = 100
            justificativa = f"CNAE {conta.cnae_principal} - Alto fit: {self.CNAES_ALTO_FIT[cnae_prefixo]}"
        elif cnae_prefixo in self.CNAES_MEDIO_FIT:
            pontuacao = 60
            justificativa = f"CNAE {conta.cnae_principal} - Médio fit: {self.CNAES_MEDIO_FIT[cnae_prefixo]}"
        elif cnae_prefixo:
            pontuacao = 25
            justificativa = f"CNAE {conta.cnae_principal} - Fit não mapeado"
        else:
            pontuacao = 0
            justificativa = "CNAE não preenchido"

        # Verifica CNAEs secundárias
        for cnae_sec in conta.cnaes_secundarias:
            prefixo_sec = cnae_sec[:2] if cnae_sec else ""
            if prefixo_sec in self.CNAES_ALTO_FIT:
                pontuacao = min(100, pontuacao + 15)
                break

        ponderada = pontuacao * self.PESO_SETOR / 100
        return DetalheFit(
            fator="Setor / CNAE",
            peso=self.PESO_SETOR,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=justificativa,
        )

    def _avaliar_historico(self, conta: Conta) -> DetalheFit:
        """Avalia histórico com seguros/garantias"""
        pontuacao = 0
        justificativas = []

        # Limites com seguradoras
        limites = conta.limites_vigentes
        if len(limites) >= 3:
            pontuacao += 40
            justificativas.append(f"{len(limites)} limites vigentes com seguradoras")
        elif len(limites) >= 1:
            pontuacao += 25
            justificativas.append(f"{len(limites)} limite(s) vigente(s)")
        else:
            justificativas.append("Sem limites vigentes com seguradoras")

        # Historico limites expirados indica experiência
        if len(conta.limites_seguradoras) > len(limites):
            pontuacao += 15
            justificativas.append("Possui histórico de limites anteriores")

        # Sinistros abertos reduzem score
        sinistros = conta.sinistros_abertos
        if sinistros:
            pontuacao = max(0, pontuacao - 20)
            justificativas.append(f"{len(sinistros)} sinistro(s) aberto(s)")
        elif conta.sinistros:
            pontuacao += 10
            justificativas.append("Histórico de sinistros resolvidos")
        else:
            pontuacao += 20
            justificativas.append("Sem sinistros")

        # Grupo econômico é positivo
        if conta.grupo_economico:
            pontuacao = min(100, pontuacao + 15)
            justificativas.append(f"Pertence ao grupo: {conta.grupo_economico}")

        pontuacao = min(100, max(0, pontuacao))
        ponderada = pontuacao * self.PESO_HISTORICO / 100
        return DetalheFit(
            fator="Histórico com Seguros",
            peso=self.PESO_HISTORICO,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa="; ".join(justificativas),
        )

    def _avaliar_complexidade(self, conta: Conta) -> DetalheFit:
        """Avalia complexidade do objeto recorrente (infraestrutura = alto)"""
        cnae_prefixo = conta.cnae_principal[:2] if conta.cnae_principal else ""

        # Setores com objetos naturalmente complexos
        complexidade_alta = {'41', '42', '43', '35', '09', '52'}
        complexidade_media = {'71', '49', '50', '51', '28', '29'}

        if cnae_prefixo in complexidade_alta:
            pontuacao = 90
            justificativa = "Setor com objetos de alta complexidade (infraestrutura/energia)"
        elif cnae_prefixo in complexidade_media:
            pontuacao = 60
            justificativa = "Setor com objetos de complexidade média"
        elif conta.porte in (PorteEmpresa.GRANDE, PorteEmpresa.MEDIO):
            pontuacao = 45
            justificativa = "Porte sugere operações de complexidade razoável"
        else:
            pontuacao = 20
            justificativa = "Setor/porte com objetos de baixa complexidade"

        ponderada = pontuacao * self.PESO_COMPLEXIDADE / 100
        return DetalheFit(
            fator="Complexidade do Objeto Recorrente",
            peso=self.PESO_COMPLEXIDADE,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=justificativa,
        )

    def _avaliar_sinais(self, conta: Conta) -> DetalheFit:
        """Avalia sinais de mercado ativos"""
        sinais = conta.sinais_nao_processados
        total_sinais = len(sinais)

        if total_sinais >= 3:
            pontuacao = 100
            justificativa = f"{total_sinais} sinais de mercado ativos (alto potencial)"
        elif total_sinais >= 1:
            pontuacao = 60
            justificativa = f"{total_sinais} sinal(is) de mercado ativo(s)"
        else:
            pontuacao = 10
            justificativa = "Sem sinais de mercado ativos"

        # Sinais de editais valem mais
        sinais_editais = [s for s in sinais if s.tipo == "edital"]
        if sinais_editais:
            pontuacao = min(100, pontuacao + 20)
            justificativa += f" ({len(sinais_editais)} edital(is))"

        ponderada = pontuacao * self.PESO_SINAIS / 100
        return DetalheFit(
            fator="Sinais de Mercado",
            peso=self.PESO_SINAIS,
            pontuacao_bruta=pontuacao,
            pontuacao_ponderada=ponderada,
            justificativa=justificativa,
        )

    def _gerar_recomendacao(self, score: float, semaforo: str,
                            detalhes: List[DetalheFit]) -> str:
        """Gera recomendação baseada no score"""
        if semaforo == "verde":
            return ("Conta com alto fit para operações de garantia. "
                    "Priorizar prospecção ativa e cadência consultiva.")
        elif semaforo == "amarelo":
            # Identifica fatores fracos
            fracos = [d for d in detalhes if d.pontuacao_bruta < 40]
            if fracos:
                fatores = ", ".join(d.fator for d in fracos)
                return (f"Conta com fit moderado. Pontos de atenção: {fatores}. "
                        f"Avaliar caso a caso antes de investir esforço.")
            return "Conta com fit moderado. Avaliar caso a caso."
        else:
            return ("Conta com baixo fit para o ICP atual. "
                    "Não priorizar para prospecção ativa. "
                    "Manter em nurturing passivo.")
