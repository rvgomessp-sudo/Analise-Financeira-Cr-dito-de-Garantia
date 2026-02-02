"""
Agendador de Jobs

Jobs automáticos (diários/semanais):
    - Validação de CNPJ e situação cadastral
    - Detecção de novas obras/contratos públicos
    - Alterações societárias, notícias materiais
    - Deduplicação
    - Alertas de certidões e documentos vencendo
    - Monitoramento de marcos contratuais
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Callable

from src.crm.models.conta import Conta
from src.crm.models.oportunidade import Oportunidade, EtapaOportunidade
from src.crm.models.documento import Documento
from src.crm.enriquecimento.validador_cnpj import ValidadorCNPJ
from src.crm.enriquecimento.deduplicacao import Deduplicador


class FrequenciaJob:
    """Frequências de execução"""
    DIARIO = "diario"
    SEMI_SEMANAL = "semi_semanal"  # 2x por semana
    SEMANAL = "semanal"
    MENSAL = "mensal"


@dataclass
class ResultadoJob:
    """Resultado da execução de um job"""
    nome: str
    sucesso: bool
    registros_processados: int = 0
    registros_atualizados: int = 0
    erros: List[str] = field(default_factory=list)
    detalhes: Dict = field(default_factory=dict)
    data_execucao: datetime = field(default_factory=datetime.now)
    duracao_ms: int = 0

    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'sucesso': self.sucesso,
            'processados': self.registros_processados,
            'atualizados': self.registros_atualizados,
            'erros': self.erros,
            'data': self.data_execucao.isoformat(),
        }


@dataclass
class JobAgendado:
    """Definição de um job agendado"""
    id: str
    nome: str
    descricao: str
    frequencia: str
    funcao: Callable
    ativo: bool = True
    ultima_execucao: Optional[datetime] = None
    proxima_execucao: Optional[datetime] = None
    historico: List[ResultadoJob] = field(default_factory=list)


class AgendadorJobs:
    """
    Agendador de jobs automáticos do CRM.

    Gerencia jobs periódicos de manutenção, enriquecimento e monitoramento.
    """

    def __init__(self):
        self.jobs: Dict[str, JobAgendado] = {}
        self.validador_cnpj = ValidadorCNPJ()
        self.deduplicador = Deduplicador()
        self._registrar_jobs_padrao()

    def _registrar_jobs_padrao(self) -> None:
        """Registra jobs padrão do sistema"""

        self.registrar_job(JobAgendado(
            id="J001",
            nome="Validação de CNPJs",
            descricao="Valida CNPJs de todas as contas não verificadas",
            frequencia=FrequenciaJob.DIARIO,
            funcao=self.job_validar_cnpjs,
        ))

        self.registrar_job(JobAgendado(
            id="J002",
            nome="Deduplicação de Contas",
            descricao="Analisa e detecta contas duplicadas",
            frequencia=FrequenciaJob.SEMANAL,
            funcao=self.job_deduplicacao,
        ))

        self.registrar_job(JobAgendado(
            id="J003",
            nome="Alertas de Certidões",
            descricao="Verifica certidões próximas do vencimento e gera alertas",
            frequencia=FrequenciaJob.DIARIO,
            funcao=self.job_alertas_certidoes,
        ))

        self.registrar_job(JobAgendado(
            id="J004",
            nome="Alertas de Documentos",
            descricao="Verifica documentos próximos do vencimento",
            frequencia=FrequenciaJob.DIARIO,
            funcao=self.job_alertas_documentos,
        ))

        self.registrar_job(JobAgendado(
            id="J005",
            nome="Monitoramento de Renovações",
            descricao="Verifica oportunidades com vigência próxima ao vencimento",
            frequencia=FrequenciaJob.DIARIO,
            funcao=self.job_monitorar_renovacoes,
        ))

        self.registrar_job(JobAgendado(
            id="J006",
            nome="Qualidade de Dados",
            descricao="Gera relatório de qualidade de dados das contas",
            frequencia=FrequenciaJob.SEMANAL,
            funcao=self.job_qualidade_dados,
        ))

    def registrar_job(self, job: JobAgendado) -> None:
        """Registra um novo job"""
        self.jobs[job.id] = job

    def executar_job(self, job_id: str, **kwargs) -> Optional[ResultadoJob]:
        """Executa um job específico"""
        job = self.jobs.get(job_id)
        if not job or not job.ativo:
            return None

        inicio = datetime.now()
        try:
            resultado = job.funcao(**kwargs)
            resultado.duracao_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            job.ultima_execucao = datetime.now()
            job.historico.append(resultado)
            return resultado
        except Exception as e:
            resultado = ResultadoJob(
                nome=job.nome,
                sucesso=False,
                erros=[str(e)],
            )
            job.historico.append(resultado)
            return resultado

    def executar_todos_diarios(self, **kwargs) -> List[ResultadoJob]:
        """Executa todos os jobs diários"""
        resultados = []
        for job in self.jobs.values():
            if job.ativo and job.frequencia == FrequenciaJob.DIARIO:
                resultado = self.executar_job(job.id, **kwargs)
                if resultado:
                    resultados.append(resultado)
        return resultados

    def executar_todos_semanais(self, **kwargs) -> List[ResultadoJob]:
        """Executa todos os jobs semanais"""
        resultados = []
        for job in self.jobs.values():
            if job.ativo and job.frequencia == FrequenciaJob.SEMANAL:
                resultado = self.executar_job(job.id, **kwargs)
                if resultado:
                    resultados.append(resultado)
        return resultados

    # === Implementação dos Jobs ===

    def job_validar_cnpjs(self, contas: List[Conta] = None, **kwargs) -> ResultadoJob:
        """Job: Valida CNPJs de contas não verificadas"""
        resultado = ResultadoJob(nome="Validação de CNPJs", sucesso=True)

        if not contas:
            resultado.erros.append("Nenhuma conta fornecida")
            resultado.sucesso = False
            return resultado

        nao_verificadas = [c for c in contas if not c.dados_verificados]
        resultado.registros_processados = len(nao_verificadas)

        for conta in nao_verificadas:
            validacao = self.validador_cnpj.validar(conta.cnpj)
            if validacao.valido:
                resultado.registros_atualizados += 1
            else:
                resultado.erros.append(
                    f"CNPJ inválido: {conta.cnpj} ({conta.razao_social}) - {validacao.erro}"
                )

        resultado.sucesso = len(resultado.erros) == 0 or resultado.registros_atualizados > 0
        return resultado

    def job_deduplicacao(self, contas: List[Conta] = None, **kwargs) -> ResultadoJob:
        """Job: Detecta contas duplicadas"""
        resultado = ResultadoJob(nome="Deduplicação de Contas", sucesso=True)

        if not contas:
            resultado.erros.append("Nenhuma conta fornecida")
            resultado.sucesso = False
            return resultado

        resultado.registros_processados = len(contas)
        analise = self.deduplicador.analisar(contas)

        resultado.registros_atualizados = analise.total_duplicatas
        resultado.detalhes = {
            'duplicatas': [d.to_dict() for d in analise.duplicatas_encontradas],
        }

        return resultado

    def job_alertas_certidoes(self, contas: List[Conta] = None, **kwargs) -> ResultadoJob:
        """Job: Verifica certidões vencendo"""
        resultado = ResultadoJob(nome="Alertas de Certidões", sucesso=True)

        if not contas:
            resultado.erros.append("Nenhuma conta fornecida")
            resultado.sucesso = False
            return resultado

        alertas = []
        for conta in contas:
            resultado.registros_processados += len(conta.certidoes)
            for cert in conta.certidoes:
                if cert.vencendo_em_30_dias:
                    alertas.append({
                        'conta_id': conta.id,
                        'razao_social': conta.razao_social,
                        'tipo_certidao': cert.tipo,
                        'data_validade': cert.data_validade.isoformat(),
                        'dias_para_vencer': cert.dias_para_vencer,
                    })
                    resultado.registros_atualizados += 1

        resultado.detalhes = {'alertas': alertas}
        return resultado

    def job_alertas_documentos(self, documentos: List[Documento] = None,
                                **kwargs) -> ResultadoJob:
        """Job: Verifica documentos vencendo"""
        resultado = ResultadoJob(nome="Alertas de Documentos", sucesso=True)

        if not documentos:
            resultado.erros.append("Nenhum documento fornecido")
            resultado.sucesso = False
            return resultado

        alertas = []
        resultado.registros_processados = len(documentos)

        for doc in documentos:
            if doc.dias_para_vencer is not None and 0 <= doc.dias_para_vencer <= 30:
                alertas.append({
                    'documento_id': doc.id,
                    'titulo': doc.titulo,
                    'tipo': doc.tipo.value,
                    'dias_para_vencer': doc.dias_para_vencer,
                })
                resultado.registros_atualizados += 1

        resultado.detalhes = {'alertas': alertas}
        return resultado

    def job_monitorar_renovacoes(self, oportunidades: List[Oportunidade] = None,
                                  **kwargs) -> ResultadoJob:
        """Job: Monitora renovações de apólices"""
        resultado = ResultadoJob(nome="Monitoramento de Renovações", sucesso=True)

        if not oportunidades:
            resultado.erros.append("Nenhuma oportunidade fornecida")
            resultado.sucesso = False
            return resultado

        pos_emissao = [
            o for o in oportunidades
            if o.etapa == EtapaOportunidade.POS_EMISSAO
            and o.data_fim_vigencia is not None
        ]
        resultado.registros_processados = len(pos_emissao)

        alertas = {'90d': [], '60d': [], '30d': [], 'vencidas': []}
        hoje = date.today()

        for op in pos_emissao:
            dias = (op.data_fim_vigencia - hoje).days
            item = {
                'oportunidade_id': op.id,
                'nome': op.nome,
                'dias_restantes': dias,
                'data_fim_vigencia': op.data_fim_vigencia.isoformat(),
            }

            if dias < 0:
                alertas['vencidas'].append(item)
            elif dias <= 30:
                alertas['30d'].append(item)
            elif dias <= 60:
                alertas['60d'].append(item)
            elif dias <= 90:
                alertas['90d'].append(item)

            if dias <= 90:
                resultado.registros_atualizados += 1

        resultado.detalhes = {'alertas': alertas}
        return resultado

    def job_qualidade_dados(self, contas: List[Conta] = None, **kwargs) -> ResultadoJob:
        """Job: Relatório de qualidade de dados"""
        resultado = ResultadoJob(nome="Qualidade de Dados", sucesso=True)

        if not contas:
            resultado.erros.append("Nenhuma conta fornecida")
            resultado.sucesso = False
            return resultado

        resultado.registros_processados = len(contas)

        completudes = [c.percentual_completude for c in contas]
        media_completude = sum(completudes) / len(completudes) if completudes else 0

        faixas = {
            'excelente': len([c for c in completudes if c > 80]),
            'bom': len([c for c in completudes if 60 < c <= 80]),
            'regular': len([c for c in completudes if 40 < c <= 60]),
            'ruim': len([c for c in completudes if c <= 40]),
        }

        cnpj_invalidos = [c for c in contas if not c.cnpj_valido]
        sem_cnae = [c for c in contas if not c.cnae_principal]
        sem_verificacao = [c for c in contas if not c.dados_verificados]

        resultado.detalhes = {
            'media_completude': round(media_completude, 1),
            'faixas': faixas,
            'cnpj_invalidos': len(cnpj_invalidos),
            'sem_cnae': len(sem_cnae),
            'sem_verificacao': len(sem_verificacao),
        }

        resultado.registros_atualizados = len([c for c in completudes if c < 60])
        return resultado

    def listar_jobs(self) -> List[Dict]:
        """Lista todos os jobs registrados"""
        return [
            {
                'id': j.id,
                'nome': j.nome,
                'frequencia': j.frequencia,
                'ativo': j.ativo,
                'ultima_execucao': j.ultima_execucao.isoformat() if j.ultima_execucao else None,
                'execucoes': len(j.historico),
            }
            for j in self.jobs.values()
        ]
