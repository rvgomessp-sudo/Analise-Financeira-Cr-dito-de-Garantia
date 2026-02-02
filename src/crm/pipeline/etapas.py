"""
Pipeline Comercial - Etapas com checklists

8 etapas do pipeline com saídas objetivas:
    1. Pesquisa & Sinais → conta criada c/ CNPJ + CNAE + porte
    2. Qualificação PJ → decisores mapeados, score de fit
    3. Descoberta / Objeto → objeto contratual e escopo capturados
    4. Pré-Risco → matriz de risco inicial, documentos solicitados
    5. Estruturação / Submissão → dossiê para seguradoras
    6. Negociação → taxa/condições validadas
    7. Fechamento / Emissão → apólice emitida
    8. Pós-Emissão / Monitoramento → renovações, alertas

Cada etapa tem checklist de campos obrigatórios para avançar.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Callable


@dataclass
class ChecklistItem:
    """Item do checklist de uma etapa"""
    id: str
    descricao: str
    campo_validacao: str  # Caminho do campo a validar (ex: "conta.cnpj_valido")
    obrigatorio: bool = True
    concluido: bool = False
    data_conclusao: Optional[datetime] = None
    observacao: str = ""

    def marcar_concluido(self, observacao: str = "") -> None:
        self.concluido = True
        self.data_conclusao = datetime.now()
        self.observacao = observacao


@dataclass
class EtapaPipeline:
    """Definição de uma etapa do pipeline"""
    numero: int
    nome: str
    descricao: str
    saida_esperada: str
    checklist: List[ChecklistItem] = field(default_factory=list)

    @property
    def todos_obrigatorios_concluidos(self) -> bool:
        obrigatorios = [c for c in self.checklist if c.obrigatorio]
        return all(c.concluido for c in obrigatorios)

    @property
    def percentual_concluido(self) -> float:
        if not self.checklist:
            return 100.0
        concluidos = sum(1 for c in self.checklist if c.concluido)
        return concluidos / len(self.checklist) * 100

    @property
    def itens_pendentes(self) -> List[ChecklistItem]:
        return [c for c in self.checklist if not c.concluido and c.obrigatorio]

    def pode_avancar(self) -> bool:
        """Verifica se pode avançar para próxima etapa"""
        return self.todos_obrigatorios_concluidos

    def to_dict(self) -> Dict:
        return {
            'numero': self.numero,
            'nome': self.nome,
            'saida_esperada': self.saida_esperada,
            'percentual_concluido': self.percentual_concluido,
            'pode_avancar': self.pode_avancar(),
            'itens_pendentes': [
                {'id': c.id, 'descricao': c.descricao}
                for c in self.itens_pendentes
            ],
        }


class Pipeline:
    """
    Pipeline comercial completo com 8 etapas.

    Gerencia o avanço de oportunidades, validando checklists
    em cada transição de etapa (governança de dados).
    """

    def __init__(self):
        self.etapas = self._criar_etapas_padrao()

    def _criar_etapas_padrao(self) -> List[EtapaPipeline]:
        """Cria as 8 etapas padrão do pipeline de garantias"""

        etapas = []

        # ETAPA 1: Pesquisa & Sinais
        etapas.append(EtapaPipeline(
            numero=1,
            nome="Pesquisa & Sinais",
            descricao="Identificação de prospect via sinais de mercado",
            saida_esperada="Conta criada com CNPJ + CNAE + porte verificados",
            checklist=[
                ChecklistItem(
                    id="1.1", descricao="CNPJ válido e verificado",
                    campo_validacao="conta.cnpj_valido",
                ),
                ChecklistItem(
                    id="1.2", descricao="CNAE principal preenchido",
                    campo_validacao="conta.cnae_principal",
                ),
                ChecklistItem(
                    id="1.3", descricao="Porte definido",
                    campo_validacao="conta.porte",
                ),
                ChecklistItem(
                    id="1.4", descricao="Situação cadastral verificada",
                    campo_validacao="conta.situacao_cadastral",
                ),
                ChecklistItem(
                    id="1.5", descricao="Razão social preenchida",
                    campo_validacao="conta.razao_social",
                ),
            ],
        ))

        # ETAPA 2: Qualificação PJ
        etapas.append(EtapaPipeline(
            numero=2,
            nome="Qualificação PJ",
            descricao="Qualificação da conta: decisores, fit, segmento",
            saida_esperada="Decisores mapeados, score de fit calculado",
            checklist=[
                ChecklistItem(
                    id="2.1", descricao="Pelo menos 1 decisor mapeado",
                    campo_validacao="contatos.decisor_mapeado",
                ),
                ChecklistItem(
                    id="2.2", descricao="Score de fit calculado",
                    campo_validacao="conta.score_fit",
                ),
                ChecklistItem(
                    id="2.3", descricao="Segmento definido",
                    campo_validacao="conta.segmento",
                ),
                ChecklistItem(
                    id="2.4", descricao="Fit com ICP avaliado",
                    campo_validacao="conta.icp_fit",
                ),
                ChecklistItem(
                    id="2.5", descricao="Canais de contato do decisor",
                    campo_validacao="contatos.canais",
                    obrigatorio=False,
                ),
            ],
        ))

        # ETAPA 3: Descoberta / Objeto
        etapas.append(EtapaPipeline(
            numero=3,
            nome="Descoberta / Objeto",
            descricao="Captura do objeto contratual, escopo e premissas de garantia",
            saida_esperada="Objeto contratual e escopo capturados; premissas de garantia definidas",
            checklist=[
                ChecklistItem(
                    id="3.1", descricao="Objeto contratual resumido",
                    campo_validacao="oportunidade.objeto_contratual.descricao_resumida",
                ),
                ChecklistItem(
                    id="3.2", descricao="Cronograma básico definido",
                    campo_validacao="oportunidade.objeto_contratual.cronograma_fisico_financeiro",
                ),
                ChecklistItem(
                    id="3.3", descricao="Tipo de garantia definido",
                    campo_validacao="oportunidade.tipo_garantia",
                ),
                ChecklistItem(
                    id="3.4", descricao="Valor estimado da garantia",
                    campo_validacao="oportunidade.valor_garantia",
                ),
                ChecklistItem(
                    id="3.5", descricao="Vigência estimada",
                    campo_validacao="oportunidade.vigencia_meses",
                ),
            ],
        ))

        # ETAPA 4: Pré-Risco
        etapas.append(EtapaPipeline(
            numero=4,
            nome="Pré-Risco",
            descricao="Análise de risco inicial, solicitação de documentos, "
                      "proposta de contragarantias",
            saida_esperada="Matriz de risco inicial, documentos solicitados, "
                          "contragarantias propostas",
            checklist=[
                ChecklistItem(
                    id="4.1", descricao="Matriz de risco elaborada",
                    campo_validacao="oportunidade.tem_matriz_risco",
                ),
                ChecklistItem(
                    id="4.2", descricao="Documentos solicitados ao cliente",
                    campo_validacao="oportunidade.documentos_solicitados",
                ),
                ChecklistItem(
                    id="4.3", descricao="Contragarantias propostas",
                    campo_validacao="oportunidade.tem_contragarantias",
                ),
                ChecklistItem(
                    id="4.4", descricao="LGD assumida definida",
                    campo_validacao="oportunidade.matriz_risco.lgd_assumida",
                    obrigatorio=False,
                ),
            ],
        ))

        # ETAPA 5: Estruturação / Submissão
        etapas.append(EtapaPipeline(
            numero=5,
            nome="Estruturação / Submissão",
            descricao="Montagem e envio do dossiê para seguradoras com "
                      "argumentos e mitigadores",
            saida_esperada="Dossiê para seguradoras montado e submetido",
            checklist=[
                ChecklistItem(
                    id="5.1", descricao="Dossiê técnico completo",
                    campo_validacao="oportunidade.estudos_tecnicos",
                ),
                ChecklistItem(
                    id="5.2", descricao="Pelo menos 1 seguradora abordada",
                    campo_validacao="oportunidade.seguradoras_abordadas",
                ),
                ChecklistItem(
                    id="5.3", descricao="Mitigadores documentados",
                    campo_validacao="oportunidade.matriz_risco.tem_mitigacoes_completas",
                ),
                ChecklistItem(
                    id="5.4", descricao="Contragarantias formalizadas",
                    campo_validacao="oportunidade.contragarantias_formalizadas",
                    obrigatorio=False,
                ),
            ],
        ))

        # ETAPA 6: Negociação
        etapas.append(EtapaPipeline(
            numero=6,
            nome="Negociação",
            descricao="Negociação de taxa e condições; contestações se necessário",
            saida_esperada="Taxa/condições validadas; contestações protocoladas",
            checklist=[
                ChecklistItem(
                    id="6.1", descricao="Pelo menos 1 aprovação de seguradora",
                    campo_validacao="oportunidade.seguradoras_aprovadas",
                ),
                ChecklistItem(
                    id="6.2", descricao="Taxa praticada definida",
                    campo_validacao="oportunidade.economia.taxa_praticada",
                ),
                ChecklistItem(
                    id="6.3", descricao="Condições comerciais validadas",
                    campo_validacao="oportunidade.economia.premio_total",
                ),
                ChecklistItem(
                    id="6.4", descricao="Contestações protocoladas (se houver)",
                    campo_validacao="oportunidade.contestacoes_protocoladas",
                    obrigatorio=False,
                ),
            ],
        ))

        # ETAPA 7: Fechamento / Emissão
        etapas.append(EtapaPipeline(
            numero=7,
            nome="Fechamento / Emissão",
            descricao="Emissão da apólice, controle de prazos e obrigações",
            saida_esperada="Apólice emitida, controle de prazos e obrigações configurado",
            checklist=[
                ChecklistItem(
                    id="7.1", descricao="Apólice emitida (documento)",
                    campo_validacao="oportunidade.apolice_emitida",
                ),
                ChecklistItem(
                    id="7.2", descricao="Data de fechamento registrada",
                    campo_validacao="oportunidade.data_fechamento_real",
                ),
                ChecklistItem(
                    id="7.3", descricao="Economia da operação registrada",
                    campo_validacao="oportunidade.economia",
                ),
                ChecklistItem(
                    id="7.4", descricao="Prazos de vigência configurados",
                    campo_validacao="oportunidade.vigencia_configurada",
                ),
            ],
        ))

        # ETAPA 8: Pós-Emissão / Monitoramento
        etapas.append(EtapaPipeline(
            numero=8,
            nome="Pós-Emissão / Monitoramento",
            descricao="Monitoramento de renovações, liberações e alertas de marcos",
            saida_esperada="Renovações monitoradas, liberações controladas, alertas ativos",
            checklist=[
                ChecklistItem(
                    id="8.1", descricao="Marcos contratuais mapeados",
                    campo_validacao="oportunidade.marcos_contratuais",
                    obrigatorio=False,
                ),
                ChecklistItem(
                    id="8.2", descricao="Alertas de renovação configurados",
                    campo_validacao="oportunidade.alertas_renovacao",
                    obrigatorio=False,
                ),
                ChecklistItem(
                    id="8.3", descricao="Cronograma de liberações registrado",
                    campo_validacao="oportunidade.cronograma_liberacoes",
                    obrigatorio=False,
                ),
            ],
        ))

        return etapas

    def obter_etapa(self, numero: int) -> Optional[EtapaPipeline]:
        """Obtém etapa por número"""
        for etapa in self.etapas:
            if etapa.numero == numero:
                return etapa
        return None

    def validar_avanço(self, numero_etapa_atual: int) -> Dict:
        """
        Valida se pode avançar da etapa atual.
        Retorna dicionário com resultado e pendências.
        """
        etapa = self.obter_etapa(numero_etapa_atual)
        if not etapa:
            return {'pode_avancar': False, 'erro': 'Etapa não encontrada'}

        pendentes = etapa.itens_pendentes
        return {
            'pode_avancar': etapa.pode_avancar(),
            'etapa_atual': etapa.nome,
            'percentual_concluido': etapa.percentual_concluido,
            'pendentes': [
                {'id': p.id, 'descricao': p.descricao}
                for p in pendentes
            ],
        }

    def resumo_pipeline(self) -> List[Dict]:
        """Retorna resumo de todas as etapas"""
        return [etapa.to_dict() for etapa in self.etapas]

    def __repr__(self) -> str:
        return f"Pipeline(etapas={len(self.etapas)})"
