"""
Playbook C — Recusa Técnica / Contestação

Trigger: Recusa injustificada ou genérica de seguradora.
Ação: Abrir tarefa "Contestação" com template de ofício,
      anexar estudo técnico e evidências; prazos e lembretes;
      registro de motivos e desfecho (para analytics).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.crm.models.oportunidade import (
    Oportunidade, StatusSeguradora, StatusSeguradoraOportunidade,
)
from src.crm.models.atividade import TipoAtividade, PrioridadeAtividade


# Motivos de recusa padronizados (para analytics)
MOTIVOS_RECUSA = {
    'GENERICA': 'Recusa genérica / sem justificativa técnica',
    'CAPACIDADE_FINANCEIRA': 'Capacidade financeira insuficiente',
    'HISTORICO_SINISTROS': 'Histórico de sinistros',
    'SETOR_RESTRITO': 'Setor/atividade restrita pela seguradora',
    'DOCUMENTACAO_INCOMPLETA': 'Documentação incompleta',
    'LIMITE_EXCEDIDO': 'Limite de exposição excedido',
    'OBJETO_NAO_ACEITO': 'Tipo de objeto/garantia não aceito',
    'CONTRAGARANTIA_INSUFICIENTE': 'Contragarantia insuficiente',
    'PRAZO_EXCESSIVO': 'Prazo de vigência excessivo',
    'RECUPERACAO_JUDICIAL': 'Empresa em Recuperação Judicial',
    'OUTRO': 'Outro motivo',
}

# Motivos que justificam contestação
MOTIVOS_CONTESTAVEIS = {
    'GENERICA', 'CAPACIDADE_FINANCEIRA', 'SETOR_RESTRITO',
    'LIMITE_EXCEDIDO', 'CONTRAGARANTIA_INSUFICIENTE',
}


@dataclass
class AcaoContestacao:
    """Ação de contestação gerada pelo playbook"""
    tipo: str
    descricao: str
    dados: Dict = field(default_factory=dict)
    prioridade: str = "alta"
    prazo_horas: int = 48


@dataclass
class ResultadoContestacao:
    """Resultado da análise de contestação"""
    playbook: str = "Playbook C - Recusa Técnica / Contestação"
    oportunidade_id: str = ""
    seguradora: str = ""
    motivo_recusa: str = ""
    motivo_classificado: str = ""
    contestavel: bool = False
    acoes_geradas: List[AcaoContestacao] = field(default_factory=list)
    template_oficio: str = ""
    data_execucao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'playbook': self.playbook,
            'oportunidade_id': self.oportunidade_id,
            'seguradora': self.seguradora,
            'motivo_recusa': self.motivo_recusa,
            'motivo_classificado': self.motivo_classificado,
            'contestavel': self.contestavel,
            'total_acoes': len(self.acoes_geradas),
        }


class PlaybookContestacao:
    """
    Playbook C — Recusa Técnica / Contestação

    Analisa recusas de seguradoras e, quando identificada recusa
    injustificada ou genérica, gera fluxo de contestação:
        1. Classificar motivo da recusa
        2. Abrir tarefa "Contestação" com prazo de 48h
        3. Gerar template de ofício
        4. Vincular estudos técnicos e evidências
        5. Configurar lembretes e follow-up
        6. Registrar para analytics
    """

    NOME = "Playbook C - Recusa Técnica / Contestação"

    def analisar_recusa(self, oportunidade: Oportunidade,
                         seguradora_nome: str) -> ResultadoContestacao:
        """
        Analisa recusa de uma seguradora e determina se é contestável.
        """
        resultado = ResultadoContestacao(
            oportunidade_id=oportunidade.id,
            seguradora=seguradora_nome,
        )

        # Encontrar a seguradora na oportunidade
        seg = None
        for s in oportunidade.seguradoras:
            if s.nome == seguradora_nome and s.status == StatusSeguradoraOportunidade.RECUSADA:
                seg = s
                break

        if not seg:
            resultado.motivo_recusa = "Seguradora não encontrada ou não recusou"
            return resultado

        resultado.motivo_recusa = seg.razao_recusa

        # Classificar motivo
        resultado.motivo_classificado = self._classificar_motivo(seg.razao_recusa)

        # Verificar se é contestável
        resultado.contestavel = resultado.motivo_classificado in MOTIVOS_CONTESTAVEIS

        if resultado.contestavel:
            self._gerar_acoes_contestacao(resultado, oportunidade, seg)
            resultado.template_oficio = self._gerar_template_oficio(
                oportunidade, seg, resultado.motivo_classificado
            )

        return resultado

    def analisar_todas_recusas(self, oportunidade: Oportunidade) -> List[ResultadoContestacao]:
        """Analisa todas as recusas de uma oportunidade"""
        resultados = []
        for seg in oportunidade.seguradoras_recusadas:
            resultado = self.analisar_recusa(oportunidade, seg.nome)
            resultados.append(resultado)
        return resultados

    def _classificar_motivo(self, razao_recusa: str) -> str:
        """Classifica o motivo da recusa em categoria padronizada"""
        razao_lower = razao_recusa.lower() if razao_recusa else ""

        if not razao_lower or razao_lower in ('recusado', 'não aprovado', 'negado'):
            return 'GENERICA'

        mapeamento_keywords = {
            'CAPACIDADE_FINANCEIRA': [
                'financeira', 'capacidade', 'balanço', 'patrimônio',
                'faturamento', 'liquidez', 'endividamento',
            ],
            'HISTORICO_SINISTROS': [
                'sinistro', 'sinistralidade', 'histórico', 'ocorrência',
            ],
            'SETOR_RESTRITO': [
                'setor', 'atividade', 'cnae', 'restrit', 'não opera',
            ],
            'DOCUMENTACAO_INCOMPLETA': [
                'document', 'incompleta', 'faltando', 'pendente',
            ],
            'LIMITE_EXCEDIDO': [
                'limite', 'exposição', 'concentração', 'excedido',
            ],
            'OBJETO_NAO_ACEITO': [
                'objeto', 'modalidade', 'tipo de garantia', 'não aceita',
            ],
            'CONTRAGARANTIA_INSUFICIENTE': [
                'contragarantia', 'garantia adicional', 'colateral',
            ],
            'PRAZO_EXCESSIVO': [
                'prazo', 'vigência', 'longo prazo',
            ],
            'RECUPERACAO_JUDICIAL': [
                'recuperação judicial', 'rj', 'falência', 'recuperação',
            ],
        }

        for motivo, keywords in mapeamento_keywords.items():
            if any(kw in razao_lower for kw in keywords):
                return motivo

        return 'GENERICA'

    def _gerar_acoes_contestacao(self, resultado: ResultadoContestacao,
                                  oportunidade: Oportunidade,
                                  seg: StatusSeguradora) -> None:
        """Gera ações de contestação"""

        # 1. Abrir tarefa de contestação
        resultado.acoes_geradas.append(AcaoContestacao(
            tipo="criar_atividade",
            descricao=f"Contestação: {seg.nome} - {oportunidade.nome}",
            dados={
                'tipo': TipoAtividade.CONTESTACAO.value,
                'titulo': f"Contestação {seg.nome} - {oportunidade.nome}",
                'descricao': (
                    f"Recusa da {seg.nome} classificada como contestável.\n"
                    f"Motivo informado: {seg.razao_recusa}\n"
                    f"Classificação: {MOTIVOS_RECUSA.get(resultado.motivo_classificado, 'N/A')}\n\n"
                    "Ações necessárias:\n"
                    "1. Redigir ofício de contestação\n"
                    "2. Anexar estudo técnico com evidências\n"
                    "3. Protocolar contestação\n"
                    "4. Registrar prazo de resposta\n"
                    "5. Agendar follow-up"
                ),
                'oportunidade_id': oportunidade.id,
                'prioridade': PrioridadeAtividade.ALTA.value,
                'sla_horas': 48,
                'checklist': [
                    "Ofício de contestação redigido",
                    "Estudo técnico anexado",
                    "Evidências documentais compiladas",
                    "Contestação protocolada",
                    "Follow-up agendado",
                ],
            },
            prioridade="alta",
            prazo_horas=48,
        ))

        # 2. Alerta no canal de operações
        resultado.acoes_geradas.append(AcaoContestacao(
            tipo="alerta",
            descricao=f"Postar no Teams: Recusa contestável - {seg.nome}",
            dados={
                'canal': 'teams',
                'canal_nome': 'Operações Críticas',
                'mensagem': (
                    f"Recusa contestável detectada:\n"
                    f"Seguradora: {seg.nome}\n"
                    f"Oportunidade: {oportunidade.nome}\n"
                    f"Motivo: {MOTIVOS_RECUSA.get(resultado.motivo_classificado, seg.razao_recusa)}\n"
                    f"Prazo para contestação: 48 horas"
                ),
                'oportunidade_id': oportunidade.id,
            },
            prioridade="alta",
            prazo_horas=24,
        ))

        # 3. Atualizar status da seguradora
        resultado.acoes_geradas.append(AcaoContestacao(
            tipo="atualizar_seguradora",
            descricao=f"Mudar status para 'Em Contestação' - {seg.nome}",
            dados={
                'seguradora_nome': seg.nome,
                'novo_status': StatusSeguradoraOportunidade.EM_CONTESTACAO.value,
                'oportunidade_id': oportunidade.id,
            },
            prioridade="alta",
        ))

        # 4. Follow-up em 7 dias
        resultado.acoes_geradas.append(AcaoContestacao(
            tipo="criar_atividade",
            descricao=f"Follow-up contestação {seg.nome} (7 dias)",
            dados={
                'tipo': TipoAtividade.FOLLOW_UP.value,
                'titulo': f"Follow-up contestação {seg.nome} - {oportunidade.nome}",
                'descricao': "Verificar resposta da seguradora à contestação.",
                'oportunidade_id': oportunidade.id,
                'data_agendada': (datetime.now() + timedelta(days=7)).isoformat(),
                'prioridade': PrioridadeAtividade.ALTA.value,
            },
            prioridade="media",
            prazo_horas=168,
        ))

    def _gerar_template_oficio(self, oportunidade: Oportunidade,
                                seg: StatusSeguradora,
                                motivo_classificado: str) -> str:
        """Gera template de ofício de contestação"""

        argumentos_por_motivo = {
            'GENERICA': (
                "Conforme legislação vigente e normativas da SUSEP, a recusa "
                "de emissão de garantia deve ser fundamentada em critérios técnicos "
                "objetivos. A recusa genérica, sem apresentação de justificativa "
                "técnica detalhada, contraria os princípios de boa-fé e transparência "
                "que regem as relações securitárias."
            ),
            'CAPACIDADE_FINANCEIRA': (
                "Os indicadores financeiros da empresa demonstram capacidade "
                "adequada para a operação em questão, conforme análise técnica "
                "em anexo. Os parâmetros de solvência, liquidez e endividamento "
                "encontram-se dentro dos limites aceitáveis pelo mercado."
            ),
            'SETOR_RESTRITO': (
                "A restrição setorial aplicada não encontra respaldo nas normas "
                "da SUSEP para o mercado de seguro garantia. O setor de atuação "
                "da empresa é regularmente atendido por outras seguradoras do mercado, "
                "não havendo impedimento técnico ou regulatório."
            ),
            'LIMITE_EXCEDIDO': (
                "O limite de exposição alegado pode ser mitigado pelas contragarantias "
                "propostas e pela estrutura de resseguro disponível. "
                "Solicitamos reavaliação considerando os mitigadores apresentados."
            ),
            'CONTRAGARANTIA_INSUFICIENTE': (
                "As contragarantias propostas são compatíveis com o risco da operação "
                "e atendem aos requisitos de mercado. Apresentamos alternativas "
                "complementares para avaliação."
            ),
        }

        argumento = argumentos_por_motivo.get(
            motivo_classificado,
            "Solicitamos reavaliação da recusa com base nos fundamentos técnicos apresentados."
        )

        template = f"""OFÍCIO DE CONTESTAÇÃO

À
{seg.nome}
Departamento de Subscrição / Seguro Garantia

Ref.: Contestação de recusa — Operação: {oportunidade.nome}

Prezados Senhores,

Pela presente, vimos contestar formalmente a recusa de emissão de seguro garantia
referente à operação acima identificada, cujo motivo informado foi:

"{seg.razao_recusa}"

FUNDAMENTAÇÃO TÉCNICA:

{argumento}

DOCUMENTAÇÃO EM ANEXO:

Seguem em anexo os seguintes documentos que fundamentam esta contestação:
1. Estudo Técnico de Viabilidade (versão atualizada)
2. Análise de Indicadores Financeiros
3. Proposta de Contragarantias e Mitigadores
4. Parecer Técnico sobre o Objeto Contratual

CONCLUSÃO:

Diante do exposto, solicitamos a reavaliação da operação com base nos
fundamentos técnicos e documentais apresentados, nos termos das normas
aplicáveis ao mercado de seguro garantia brasileiro.

Permanecemos à disposição para esclarecimentos adicionais e reunião técnica.

Atenciosamente,

_________________________________
[Nome do Responsável]
[Cargo]
[Contato]

Data: {datetime.now().strftime('%d/%m/%Y')}
"""
        return template

    def estatisticas_recusas(self, oportunidades: List[Oportunidade]) -> Dict:
        """Gera estatísticas de recusas para analytics"""
        todas_recusas = []
        for op in oportunidades:
            for seg in op.seguradoras_recusadas:
                motivo = self._classificar_motivo(seg.razao_recusa)
                todas_recusas.append({
                    'oportunidade_id': op.id,
                    'seguradora': seg.nome,
                    'motivo_original': seg.razao_recusa,
                    'motivo_classificado': motivo,
                    'contestavel': motivo in MOTIVOS_CONTESTAVEIS,
                    'dias_analise': seg.dias_em_analise,
                })

        # Contagem por motivo
        contagem_motivos = {}
        for recusa in todas_recusas:
            motivo = recusa['motivo_classificado']
            contagem_motivos[motivo] = contagem_motivos.get(motivo, 0) + 1

        # Contagem por seguradora
        contagem_seguradoras = {}
        for recusa in todas_recusas:
            seg = recusa['seguradora']
            contagem_seguradoras[seg] = contagem_seguradoras.get(seg, 0) + 1

        total = len(todas_recusas)
        contestaveis = len([r for r in todas_recusas if r['contestavel']])

        return {
            'total_recusas': total,
            'contestaveis': contestaveis,
            'taxa_contestacao': contestaveis / total * 100 if total > 0 else 0,
            'por_motivo': contagem_motivos,
            'por_seguradora': contagem_seguradoras,
            'detalhes': todas_recusas,
        }
