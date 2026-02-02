"""
Playbook A — Editais/Obras

Trigger: Empresa com CNAE/porte alvo + sinal de participação em editais.
Ação: Criar lista quente, abrir oportunidade "Participação",
      solicitar escopo/cronograma e cláusulas; enviar checklist documental;
      agendar call técnico.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.crm.models.conta import Conta, PorteEmpresa
from src.crm.models.contato import Contato
from src.crm.models.oportunidade import (
    Oportunidade, TipoGarantiaOportunidade, EtapaOportunidade,
    ObjetoContratual,
)
from src.crm.models.atividade import (
    Atividade, TipoAtividade, StatusAtividade, PrioridadeAtividade,
    Cadencia, EtapaCadencia, criar_cadencia_prospeccao_consultiva,
)


@dataclass
class AcaoPlaybook:
    """Ação gerada pelo playbook"""
    tipo: str  # criar_oportunidade, criar_atividade, criar_cadencia, alerta
    descricao: str
    dados: Dict = field(default_factory=dict)
    prioridade: str = "media"


@dataclass
class ResultadoPlaybook:
    """Resultado da execução do playbook"""
    playbook: str
    conta_id: str
    trigger_ativado: bool
    acoes_geradas: List[AcaoPlaybook] = field(default_factory=list)
    motivo: str = ""
    data_execucao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'playbook': self.playbook,
            'conta_id': self.conta_id,
            'trigger_ativado': self.trigger_ativado,
            'total_acoes': len(self.acoes_geradas),
            'acoes': [
                {'tipo': a.tipo, 'descricao': a.descricao, 'prioridade': a.prioridade}
                for a in self.acoes_geradas
            ],
            'motivo': self.motivo,
        }


class PlaybookEditais:
    """
    Playbook A — Editais/Obras

    Trigger: CNAE alvo + porte >= Pequeno + sinal de edital ativo
    Ações automáticas:
        1. Criar lista quente (marcar conta)
        2. Abrir oportunidade "Participação"
        3. Criar atividade de solicitação de escopo
        4. Enviar checklist documental
        5. Agendar call técnico
        6. Iniciar cadência de prospecção consultiva
    """

    # CNAEs alvo para este playbook
    CNAES_ALVO = {
        '41', '42', '43',  # Construção
        '35',              # Energia
        '49', '50', '51',  # Transporte
        '71',              # Engenharia
        '09',              # Mineração
        '36', '37',        # Saneamento
        '52',              # Armazenamento
    }

    PORTES_ALVO = {
        PorteEmpresa.PEQUENO,
        PorteEmpresa.MEDIO,
        PorteEmpresa.GRANDE,
    }

    NOME = "Playbook A - Editais/Obras"

    def verificar_trigger(self, conta: Conta) -> bool:
        """Verifica se a conta atende aos critérios de trigger"""
        # CNAE alvo
        cnae_prefixo = conta.cnae_principal[:2] if conta.cnae_principal else ""
        if cnae_prefixo not in self.CNAES_ALVO:
            return False

        # Porte adequado
        if conta.porte not in self.PORTES_ALVO:
            return False

        # Sinal de edital ativo
        sinais_editais = [
            s for s in conta.sinais_mercado
            if s.tipo == "edital" and not s.processado
        ]
        if not sinais_editais:
            return False

        return True

    def executar(self, conta: Conta,
                 contato_principal: Optional[Contato] = None) -> ResultadoPlaybook:
        """
        Executa o playbook para uma conta.

        Retorna lista de ações a serem criadas no CRM.
        """
        resultado = ResultadoPlaybook(
            playbook=self.NOME,
            conta_id=conta.id,
            trigger_ativado=self.verificar_trigger(conta),
        )

        if not resultado.trigger_ativado:
            resultado.motivo = "Conta não atende critérios de trigger"
            return resultado

        sinais_editais = [
            s for s in conta.sinais_mercado
            if s.tipo == "edital" and not s.processado
        ]

        # 1. Marcar conta como lista quente
        resultado.acoes_geradas.append(AcaoPlaybook(
            tipo="atualizar_conta",
            descricao="Marcar conta como 'Lista Quente - Editais'",
            dados={
                'tags_adicionar': ['lista_quente', 'editais', 'playbook_a'],
                'icp_fit': True,
            },
            prioridade="alta",
        ))

        # 2. Abrir oportunidade para cada edital detectado
        for sinal in sinais_editais[:3]:  # Máximo 3 oportunidades por vez
            resultado.acoes_geradas.append(AcaoPlaybook(
                tipo="criar_oportunidade",
                descricao=f"Criar oportunidade: {sinal.titulo}",
                dados={
                    'conta_id': conta.id,
                    'nome': f"Participação - {sinal.titulo[:80]}",
                    'tipo_garantia': TipoGarantiaOportunidade.PARTICIPACAO.value,
                    'etapa': EtapaOportunidade.PESQUISA_SINAIS.value,
                    'sinal_id': sinal.id_externo,
                    'fonte': sinal.fonte,
                },
                prioridade="alta",
            ))

        # 3. Criar atividade de solicitação de escopo
        resultado.acoes_geradas.append(AcaoPlaybook(
            tipo="criar_atividade",
            descricao="Solicitar escopo/cronograma e cláusulas do edital",
            dados={
                'tipo': TipoAtividade.TAREFA.value,
                'titulo': f"Solicitar escopo e cronograma - {conta.nome_fantasia or conta.razao_social}",
                'descricao': (
                    "Solicitar ao prospect:\n"
                    "1. Escopo técnico do edital/contrato\n"
                    "2. Cronograma físico-financeiro\n"
                    "3. Cláusulas críticas (reajuste, multas, retomada)\n"
                    "4. Valor estimado do contrato e da garantia\n"
                    "5. Prazo de vigência necessário"
                ),
                'prioridade': PrioridadeAtividade.ALTA.value,
                'sla_horas': 48,
                'checklist': [
                    "Escopo técnico obtido",
                    "Cronograma obtido",
                    "Valor estimado confirmado",
                    "Prazo de vigência definido",
                    "Cláusulas críticas identificadas",
                ],
            },
            prioridade="alta",
        ))

        # 4. Enviar checklist documental
        resultado.acoes_geradas.append(AcaoPlaybook(
            tipo="criar_atividade",
            descricao="Enviar checklist documental ao prospect",
            dados={
                'tipo': TipoAtividade.EMAIL.value,
                'titulo': f"Enviar checklist documental - {conta.nome_fantasia or conta.razao_social}",
                'descricao': (
                    "Enviar checklist de documentos necessários:\n"
                    "- Contrato social / Estatuto\n"
                    "- Certidões negativas (Federal, Estadual, Municipal, FGTS, Trabalhista)\n"
                    "- Balanço patrimonial dos últimos 3 exercícios\n"
                    "- DRE dos últimos 3 exercícios\n"
                    "- Relação de contratos em andamento\n"
                    "- Edital completo com anexos\n"
                    "- Cronograma da obra/projeto"
                ),
                'prioridade': PrioridadeAtividade.MEDIA.value,
                'sla_horas': 72,
            },
            prioridade="media",
        ))

        # 5. Agendar call técnico
        resultado.acoes_geradas.append(AcaoPlaybook(
            tipo="criar_atividade",
            descricao="Agendar call técnico com decisor",
            dados={
                'tipo': TipoAtividade.LIGACAO.value,
                'titulo': f"Call técnico - {conta.nome_fantasia or conta.razao_social}",
                'descricao': (
                    "Call técnico para:\n"
                    "1. Entender necessidade específica de garantia\n"
                    "2. Mapear histórico com seguradoras\n"
                    "3. Identificar desafios/recusas anteriores\n"
                    "4. Apresentar abordagem consultiva VF\n"
                    "5. Definir próximos passos"
                ),
                'prioridade': PrioridadeAtividade.ALTA.value,
                'data_agendada': (datetime.now() + timedelta(days=3)).isoformat(),
                'contato_id': contato_principal.id if contato_principal else None,
            },
            prioridade="alta",
        ))

        # 6. Iniciar cadência consultiva
        if contato_principal:
            resultado.acoes_geradas.append(AcaoPlaybook(
                tipo="criar_cadencia",
                descricao="Iniciar cadência de prospecção consultiva (90 dias)",
                dados={
                    'conta_id': conta.id,
                    'contato_id': contato_principal.id,
                    'nome': f"Cadência Editais - {conta.nome_fantasia or conta.razao_social}",
                },
                prioridade="media",
            ))

        # Marcar sinais como processados
        for sinal in sinais_editais:
            sinal.processado = True

        resultado.motivo = (
            f"Trigger ativado: CNAE {conta.cnae_principal}, "
            f"Porte {conta.porte.value}, "
            f"{len(sinais_editais)} edital(is) detectado(s)"
        )

        return resultado

    def gerar_lista_quente(self, contas: List[Conta]) -> List[Conta]:
        """
        Filtra contas que atendem ao trigger do playbook.
        Retorna lista quente ordenada por relevância.
        """
        lista = [c for c in contas if self.verificar_trigger(c)]

        # Ordena por: número de sinais (desc), score_fit (desc), porte (desc)
        prioridade_porte = {
            PorteEmpresa.GRANDE: 4,
            PorteEmpresa.MEDIO: 3,
            PorteEmpresa.PEQUENO: 2,
            PorteEmpresa.MICRO: 1,
            PorteEmpresa.MEI: 0,
        }

        lista.sort(key=lambda c: (
            len([s for s in c.sinais_mercado if s.tipo == "edital" and not s.processado]),
            c.score_fit or 0,
            prioridade_porte.get(c.porte, 0),
        ), reverse=True)

        return lista
