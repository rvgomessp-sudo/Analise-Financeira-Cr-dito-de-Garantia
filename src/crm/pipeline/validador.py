"""
Validador de Etapas do Pipeline

Valida se uma oportunidade pode avançar de etapa, verificando
campos obrigatórios na conta, contatos e oportunidade.
Implementa governança de dados no pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

from src.crm.models.conta import Conta
from src.crm.models.contato import Contato, NivelInfluencia
from src.crm.models.oportunidade import Oportunidade, EtapaOportunidade


@dataclass
class ResultadoValidacao:
    """Resultado de uma validação de etapa"""
    pode_avancar: bool
    etapa_atual: str
    etapa_destino: str
    erros: List[str] = field(default_factory=list)
    avisos: List[str] = field(default_factory=list)
    campos_faltantes: List[str] = field(default_factory=list)
    data_validacao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'pode_avancar': self.pode_avancar,
            'etapa_atual': self.etapa_atual,
            'etapa_destino': self.etapa_destino,
            'erros': self.erros,
            'avisos': self.avisos,
            'campos_faltantes': self.campos_faltantes,
        }


class ValidadorEtapa:
    """
    Valida transições de etapa no pipeline.

    Cada transição tem regras específicas que verificam
    campos obrigatórios na conta, contatos e oportunidade.
    """

    NOMES_ETAPAS = {
        1: "Pesquisa & Sinais",
        2: "Qualificação PJ",
        3: "Descoberta / Objeto",
        4: "Pré-Risco",
        5: "Estruturação / Submissão",
        6: "Negociação",
        7: "Fechamento / Emissão",
        8: "Pós-Emissão / Monitoramento",
    }

    def validar_transicao(
        self,
        oportunidade: Oportunidade,
        conta: Conta,
        contatos: List[Contato],
        etapa_destino: int,
    ) -> ResultadoValidacao:
        """
        Valida se a oportunidade pode transitar para a etapa destino.

        Verifica regras da etapa atual (campo obrigatório para sair)
        e pré-requisitos da etapa destino.
        """
        etapa_atual = oportunidade.etapa_numero
        resultado = ResultadoValidacao(
            pode_avancar=True,
            etapa_atual=self.NOMES_ETAPAS.get(etapa_atual, "Desconhecida"),
            etapa_destino=self.NOMES_ETAPAS.get(etapa_destino, "Desconhecida"),
        )

        if etapa_destino != etapa_atual + 1:
            if etapa_destino > etapa_atual + 1:
                resultado.pode_avancar = False
                resultado.erros.append(
                    f"Não é permitido pular etapas. "
                    f"Etapa atual: {etapa_atual}, destino: {etapa_destino}"
                )
                return resultado

        validadores = {
            1: self._validar_saida_pesquisa,
            2: self._validar_saida_qualificacao,
            3: self._validar_saida_descoberta,
            4: self._validar_saida_pre_risco,
            5: self._validar_saida_estruturacao,
            6: self._validar_saida_negociacao,
            7: self._validar_saida_fechamento,
        }

        validador = validadores.get(etapa_atual)
        if validador:
            validador(resultado, oportunidade, conta, contatos)

        resultado.pode_avancar = len(resultado.erros) == 0
        return resultado

    def _validar_saida_pesquisa(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Pesquisa & Sinais → Qualificação PJ"""
        if not conta.cnpj_valido:
            resultado.erros.append("CNPJ inválido ou não preenchido")
            resultado.campos_faltantes.append("conta.cnpj")

        if not conta.razao_social:
            resultado.erros.append("Razão social não preenchida")
            resultado.campos_faltantes.append("conta.razao_social")

        if not conta.cnae_principal:
            resultado.erros.append("CNAE principal não preenchido")
            resultado.campos_faltantes.append("conta.cnae_principal")

        if conta.situacao_cadastral.value == "Não Verificada":
            resultado.avisos.append(
                "Situação cadastral não verificada. "
                "Recomenda-se verificar antes de qualificar."
            )

        if not conta.dados_verificados:
            resultado.avisos.append("Dados da conta não foram enriquecidos/verificados")

    def _validar_saida_qualificacao(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Qualificação PJ → Descoberta / Objeto"""
        decisores = [
            c for c in contatos
            if c.conta_id == conta.id
            and c.nivel_influencia in (
                NivelInfluencia.DECISOR,
                NivelInfluencia.CHAMPION,
                NivelInfluencia.INFLUENCIADOR,
            )
        ]
        if not decisores:
            resultado.erros.append(
                "Nenhum decisor/influenciador mapeado. "
                "Mapeie pelo menos 1 contato com nível Decisor, "
                "Champion ou Influenciador."
            )
            resultado.campos_faltantes.append("contatos.decisor")

        if conta.score_fit is None:
            resultado.erros.append("Score de fit não calculado")
            resultado.campos_faltantes.append("conta.score_fit")

        if not conta.segmento:
            resultado.avisos.append("Segmento da conta não definido")

    def _validar_saida_descoberta(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Descoberta / Objeto → Pré-Risco"""
        if not oportunidade.tem_objeto_contratual:
            resultado.erros.append(
                "Objeto contratual não preenchido. "
                "É obrigatório ter descrição resumida do objeto."
            )
            resultado.campos_faltantes.append("oportunidade.objeto_contratual")

        if oportunidade.objeto_contratual and not oportunidade.objeto_contratual.cronograma_fisico_financeiro:
            resultado.erros.append(
                "Cronograma físico-financeiro não preenchido. "
                "Defina pelo menos cronograma básico."
            )
            resultado.campos_faltantes.append("oportunidade.cronograma")

        if not oportunidade.valor_garantia:
            resultado.erros.append("Valor estimado da garantia não definido")
            resultado.campos_faltantes.append("oportunidade.valor_garantia")

        if not oportunidade.vigencia_meses:
            resultado.avisos.append("Vigência estimada não definida")

    def _validar_saida_pre_risco(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Pré-Risco → Estruturação / Submissão"""
        if not oportunidade.tem_matriz_risco:
            resultado.erros.append(
                "Matriz de risco não elaborada. "
                "Necessário identificar riscos de engenharia, financeiro e jurídico."
            )
            resultado.campos_faltantes.append("oportunidade.matriz_risco")

        if not oportunidade.tem_contragarantias:
            resultado.avisos.append(
                "Nenhuma contragarantia proposta. "
                "Recomenda-se definir contragarantias antes da submissão."
            )

        if oportunidade.matriz_risco and oportunidade.matriz_risco.riscos_criticos:
            resultado.avisos.append(
                f"Existem {len(oportunidade.matriz_risco.riscos_criticos)} "
                f"riscos críticos (vermelho) na matriz. "
                f"Certifique-se de que existem mitigadores adequados."
            )

    def _validar_saida_estruturacao(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Estruturação / Submissão → Negociação"""
        if not oportunidade.estudos_tecnicos:
            resultado.erros.append("Nenhum estudo técnico vinculado à oportunidade")
            resultado.campos_faltantes.append("oportunidade.estudos_tecnicos")

        seguradoras_abordadas = [
            s for s in oportunidade.seguradoras
            if s.status.value != "Não Abordada"
        ]
        if not seguradoras_abordadas:
            resultado.erros.append(
                "Nenhuma seguradora foi abordada. "
                "Submeta o dossiê a pelo menos 1 seguradora."
            )
            resultado.campos_faltantes.append("oportunidade.seguradoras")

        if oportunidade.matriz_risco and not oportunidade.matriz_risco.tem_mitigacoes_completas:
            resultado.avisos.append(
                "Nem todos os riscos possuem mitigadores documentados"
            )

    def _validar_saida_negociacao(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Negociação → Fechamento / Emissão"""
        if not oportunidade.seguradoras_aprovadas:
            resultado.erros.append(
                "Nenhuma seguradora aprovou a operação. "
                "Necessário pelo menos 1 aprovação para fechar."
            )
            resultado.campos_faltantes.append("oportunidade.aprovacao_seguradora")

        if not oportunidade.economia or not oportunidade.economia.taxa_praticada:
            resultado.erros.append("Taxa praticada não definida")
            resultado.campos_faltantes.append("oportunidade.economia.taxa")

        if not oportunidade.economia or not oportunidade.economia.premio_total:
            resultado.erros.append("Prêmio total não calculado")
            resultado.campos_faltantes.append("oportunidade.economia.premio")

    def _validar_saida_fechamento(
        self, resultado: ResultadoValidacao,
        oportunidade: Oportunidade, conta: Conta,
        contatos: List[Contato],
    ) -> None:
        """Validação: Fechamento / Emissão → Pós-Emissão"""
        if not oportunidade.data_fechamento_real:
            resultado.erros.append("Data de fechamento não registrada")
            resultado.campos_faltantes.append("oportunidade.data_fechamento_real")

        if not oportunidade.economia:
            resultado.erros.append("Economia da operação não registrada")
            resultado.campos_faltantes.append("oportunidade.economia")

        if not oportunidade.data_inicio_vigencia or not oportunidade.data_fim_vigencia:
            resultado.avisos.append("Datas de vigência da apólice não configuradas")

    def relatorio_completo(
        self,
        oportunidade: Oportunidade,
        conta: Conta,
        contatos: List[Contato],
    ) -> Dict:
        """
        Gera relatório completo de validação para todas as etapas.
        Útil para dashboard de qualidade de dados.
        """
        etapa_atual = oportunidade.etapa_numero
        relatorio = {
            'oportunidade_id': oportunidade.id,
            'etapa_atual': etapa_atual,
            'etapa_nome': self.NOMES_ETAPAS.get(etapa_atual, "Desconhecida"),
            'validacoes': [],
        }

        for num_etapa in range(1, etapa_atual + 1):
            if num_etapa < 8:
                val = ResultadoValidacao(
                    pode_avancar=True,
                    etapa_atual=self.NOMES_ETAPAS.get(num_etapa, ""),
                    etapa_destino=self.NOMES_ETAPAS.get(num_etapa + 1, ""),
                )
                validadores = {
                    1: self._validar_saida_pesquisa,
                    2: self._validar_saida_qualificacao,
                    3: self._validar_saida_descoberta,
                    4: self._validar_saida_pre_risco,
                    5: self._validar_saida_estruturacao,
                    6: self._validar_saida_negociacao,
                    7: self._validar_saida_fechamento,
                }
                validador = validadores.get(num_etapa)
                if validador:
                    validador(val, oportunidade, conta, contatos)
                    val.pode_avancar = len(val.erros) == 0
                    relatorio['validacoes'].append(val.to_dict())

        return relatorio
