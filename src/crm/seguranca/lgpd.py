"""
Gestão LGPD

Gerencia consentimentos, mascaramento de dados pessoais,
e políticas de retenção/descarte conforme LGPD.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional

from src.crm.models.contato import Contato, ConsentimentoLGPD
from src.crm.models.documento import Documento


@dataclass
class RelatorioLGPD:
    """Relatório de conformidade LGPD"""
    total_contatos: int = 0
    com_consentimento: int = 0
    sem_consentimento: int = 0
    consentimentos_revogados: int = 0
    documentos_vencidos: int = 0
    documentos_para_descarte: int = 0
    alertas: List[str] = field(default_factory=list)
    data_geracao: datetime = field(default_factory=datetime.now)

    @property
    def taxa_conformidade(self) -> float:
        if self.total_contatos == 0:
            return 100.0
        return self.com_consentimento / self.total_contatos * 100

    def to_dict(self) -> Dict:
        return {
            'total_contatos': self.total_contatos,
            'com_consentimento': self.com_consentimento,
            'sem_consentimento': self.sem_consentimento,
            'consentimentos_revogados': self.consentimentos_revogados,
            'taxa_conformidade': round(self.taxa_conformidade, 1),
            'documentos_vencidos': self.documentos_vencidos,
            'documentos_para_descarte': self.documentos_para_descarte,
            'alertas': self.alertas,
        }


class GestorLGPD:
    """
    Gestor de conformidade LGPD.

    Responsabilidades:
        - Verificar consentimentos ativos
        - Mascarar dados pessoais (quando necessário)
        - Gerenciar políticas de retenção
        - Gerar relatórios de conformidade
        - Processar solicitações de titulares
    """

    PROPOSITOS_PADRAO = [
        "Comunicação Comercial",
        "Envio de Propostas",
        "Análise de Crédito",
        "Compartilhamento com Seguradoras",
    ]

    def verificar_conformidade(self, contatos: List[Contato],
                                documentos: List[Documento] = None) -> RelatorioLGPD:
        """Gera relatório de conformidade LGPD"""
        relatorio = RelatorioLGPD(total_contatos=len(contatos))

        for contato in contatos:
            tem_consentimento = any(c.ativo for c in contato.consentimentos)
            if tem_consentimento:
                relatorio.com_consentimento += 1
            else:
                relatorio.sem_consentimento += 1
                if contato.interacoes:
                    relatorio.alertas.append(
                        f"Contato '{contato.nome}' tem interações mas sem consentimento ativo"
                    )

            revogados = [c for c in contato.consentimentos if c.data_revogacao is not None]
            relatorio.consentimentos_revogados += len(revogados)

        if documentos:
            for doc in documentos:
                if doc.vencido:
                    relatorio.documentos_vencidos += 1
                if doc.data_descarte and doc.data_descarte <= date.today():
                    relatorio.documentos_para_descarte += 1
                    relatorio.alertas.append(
                        f"Documento '{doc.titulo}' atingiu prazo de descarte"
                    )

        if relatorio.taxa_conformidade < 80:
            relatorio.alertas.append(
                f"Taxa de conformidade abaixo de 80%: {relatorio.taxa_conformidade:.1f}%"
            )

        return relatorio

    def mascarar_contato(self, contato: Contato) -> Dict:
        """Retorna dados do contato com dados pessoais mascarados"""
        return contato.to_dict(mascarar_dados=True)

    def mascarar_contatos_sem_consentimento(self, contatos: List[Contato],
                                              proposito: str = "Comunicação Comercial") -> List[Dict]:
        """Mascara dados de contatos sem consentimento para um propósito"""
        resultado = []
        for contato in contatos:
            tem_consentimento = any(
                c.ativo and c.proposito == proposito
                for c in contato.consentimentos
            )
            if tem_consentimento:
                resultado.append(contato.to_dict(mascarar_dados=False))
            else:
                resultado.append(contato.to_dict(mascarar_dados=True))
        return resultado

    def solicitar_exclusao(self, contato: Contato) -> Dict:
        """
        Processa solicitação de exclusão de dados (direito ao esquecimento).
        Retorna relatório do que foi/será excluído.
        """
        dados_excluidos = []
        dados_retidos = []

        # Revoga todos os consentimentos
        for consent in contato.consentimentos:
            if consent.ativo:
                consent.revogar()
                dados_excluidos.append(f"Consentimento: {consent.proposito}")

        # Dados que podem ser excluídos
        campos_pessoais = {
            'email': contato.email,
            'telefone': contato.telefone,
            'celular': contato.celular,
            'linkedin': contato.linkedin,
        }

        for campo, valor in campos_pessoais.items():
            if valor:
                dados_excluidos.append(f"Campo: {campo}")

        # Dados retidos por obrigação legal
        dados_retidos.append("Nome (retido por obrigação contratual)")
        dados_retidos.append("Cargo (retido por legítimo interesse)")
        dados_retidos.append("Histórico de interações (retido por 5 anos - obrigação legal)")

        # Limpar dados pessoais
        contato.email = ""
        contato.telefone = ""
        contato.celular = ""
        contato.linkedin = ""
        contato.notas_relacionamento = ""
        contato.status = contato.status  # Mantém status

        return {
            'contato_id': contato.id,
            'dados_excluidos': dados_excluidos,
            'dados_retidos': dados_retidos,
            'data_processamento': datetime.now().isoformat(),
            'observacao': "Dados pessoais removidos. Dados retidos por obrigação legal.",
        }

    def verificar_retencao_documentos(self, documentos: List[Documento]) -> List[Dict]:
        """Verifica documentos que atingiram prazo de retenção"""
        para_descarte = []
        hoje = date.today()

        for doc in documentos:
            if doc.data_descarte and doc.data_descarte <= hoje:
                para_descarte.append({
                    'documento_id': doc.id,
                    'titulo': doc.titulo,
                    'tipo': doc.tipo.value,
                    'data_descarte_prevista': doc.data_descarte.isoformat(),
                    'dias_apos_vencimento': (hoje - doc.data_descarte).days,
                    'acao': 'Avaliar para descarte ou renovação de retenção',
                })

        return para_descarte

    def gerar_relatorio_titular(self, contato: Contato) -> Dict:
        """
        Gera relatório de dados do titular (atendendo ao direito de acesso).
        """
        return {
            'titular': {
                'nome': contato.nome,
                'cargo': contato.cargo,
                'empresa': contato.conta_id,
            },
            'dados_pessoais_armazenados': {
                'email': bool(contato.email),
                'telefone': bool(contato.telefone),
                'celular': bool(contato.celular),
                'linkedin': bool(contato.linkedin),
            },
            'consentimentos': [
                {
                    'proposito': c.proposito,
                    'ativo': c.ativo,
                    'data_consentimento': c.data_consentimento.isoformat(),
                    'base_legal': c.base_legal,
                    'data_revogacao': c.data_revogacao.isoformat() if c.data_revogacao else None,
                }
                for c in contato.consentimentos
            ],
            'total_interacoes': len(contato.interacoes),
            'data_geracao': datetime.now().isoformat(),
            'informacoes': "Relatório gerado conforme Art. 18 da LGPD (Lei 13.709/2018).",
        }
