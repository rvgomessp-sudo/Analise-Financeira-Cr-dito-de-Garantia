"""
CRM de Prospecção e Operações de Garantia — Aplicação Principal

Demonstração completa do sistema CRM PJ-first com:
    1. Modelo de dados PJ-first (Conta, Contato, Oportunidade, etc.)
    2. Pipeline comercial com 8 etapas e checklists
    3. Scoring de Fit (conta) e Propensão (oportunidade)
    4. Enriquecimento e validação de CNPJ
    5. Playbooks de prospecção (Editais, Renovação, Contestação)
    6. KPIs e Dashboard executivo
    7. Segurança RBAC e LGPD
    8. Motor de regras e automação
    9. Orquestrador de integrações

OKRs alvo:
    Obj 1: Prospecção de Alta Precisão (B2B)
    Obj 2: Conversão em Operações de Garantia
    Obj 3: Inteligência & Governança
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crm.models.conta import (
    Conta, PorteEmpresa, SituacaoCadastral, TipoEstabelecimento,
    IndicadoresFinanceiros, Endereco, SinalMercado, CertidaoDocumento,
    LimiteSeguradora,
)
from src.crm.models.contato import (
    Contato, AreaContato, NivelInfluencia, CanalPreferido,
)
from src.crm.models.oportunidade import (
    Oportunidade, TipoGarantiaOportunidade, EtapaOportunidade,
    ObjetoContratual, MatrizRisco, CategoriaRisco, NivelRisco,
    TipoContragarantia, EconomiaOperacao, StatusSeguradoraOportunidade,
)
from src.crm.models.atividade import (
    Atividade, TipoAtividade, StatusAtividade,
    criar_cadencia_prospeccao_consultiva,
)
from src.crm.models.documento import Documento, TipoDocumento

from src.crm.pipeline.etapas import Pipeline
from src.crm.pipeline.validador import ValidadorEtapa

from src.crm.scoring.score_fit import ScoreFit
from src.crm.scoring.score_propensao import ScorePropensao

from src.crm.enriquecimento.validador_cnpj import ValidadorCNPJ
from src.crm.enriquecimento.enriquecedor import Enriquecedor
from src.crm.enriquecimento.deduplicacao import Deduplicador

from src.crm.playbooks.playbook_editais import PlaybookEditais
from src.crm.playbooks.playbook_renovacao import PlaybookRenovacao
from src.crm.playbooks.playbook_contestacao import PlaybookContestacao

from src.crm.dashboards.kpis import MotorKPIs
from src.crm.dashboards.dashboard import DashboardExecutivo

from src.crm.seguranca.controle_acesso import ControleAcesso, Permissao
from src.crm.seguranca.lgpd import GestorLGPD

from src.crm.automacao.regras import MotorRegras, Evento, TipoEvento
from src.crm.automacao.jobs import AgendadorJobs

from src.crm.integracoes.orquestrador import OrquestradorIntegracoes


def separador(titulo: str) -> None:
    """Imprime separador visual"""
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print(f"{'='*70}\n")


def subsecao(titulo: str) -> None:
    """Imprime subsecao"""
    print(f"\n--- {titulo} ---\n")


def criar_dados_demonstracao():
    """Cria dados de demonstração para todas as funcionalidades"""

    # === CONTAS ===
    contas = []

    # Conta 1: Construtora Grande (alto fit)
    conta1 = Conta(
        id="C001",
        cnpj="12345678000195",
        razao_social="Construtora Nacional S.A.",
        nome_fantasia="CN Engenharia",
        situacao_cadastral=SituacaoCadastral.ATIVA,
        porte=PorteEmpresa.GRANDE,
        cnae_principal="4120400",
        cnae_descricao="Construção de edifícios",
        cnaes_secundarias=["4211101", "4213800"],
        tipo_estabelecimento=TipoEstabelecimento.MATRIZ,
        grupo_economico="Grupo CN Holdings",
        data_abertura=date(2005, 3, 15),
        endereco_fiscal=Endereco(
            tipo="Fiscal", logradouro="Av. Paulista", numero="1000",
            bairro="Bela Vista", cidade="São Paulo", uf="SP", cep="01310100",
        ),
        site="www.cnengenharia.com.br",
        telefone_geral="(11) 3000-0000",
        email_geral="contato@cnengenharia.com.br",
        indicadores_financeiros=IndicadoresFinanceiros(
            data_referencia=date(2024, 12, 31),
            faturamento_anual=Decimal('850000000'),
            ebitda=Decimal('120000000'),
            patrimonio_liquido=Decimal('500000000'),
            divida_bruta=Decimal('200000000'),
            divida_liquida=Decimal('150000000'),
            ativo_total=Decimal('1200000000'),
        ),
        rating_interno="AA",
        dados_verificados=True,
        segmento="Construção Civil",
        proprietario="joao.silva",
    )
    conta1.dados_verificados = True
    conta1.adicionar_limite("Zurich", Decimal('50000000'), date(2024, 6, 1), date(2025, 6, 1))
    conta1.adicionar_limite("Junto Seguros", Decimal('30000000'), date(2024, 8, 1), date(2025, 8, 1))
    conta1.adicionar_sinal_mercado(
        tipo="edital", fonte="PNCP",
        titulo="Edital Obra Rodoviária BR-101/SC - Lote 3",
        descricao="Obra de duplicação da BR-101, lote 3, valor estimado R$ 200M",
        relevancia=5,
        id_externo="PNCP-2025-00123",
    )
    conta1.certidoes.append(CertidaoDocumento(
        tipo="CND Federal", numero="CND-2025-001",
        data_emissao=date(2025, 1, 15), data_validade=date(2025, 7, 15),
    ))
    contas.append(conta1)

    # Conta 2: Empresa Média (médio fit)
    conta2 = Conta(
        id="C002",
        cnpj="98765432000187",
        razao_social="Infratech Engenharia Ltda.",
        nome_fantasia="Infratech",
        situacao_cadastral=SituacaoCadastral.ATIVA,
        porte=PorteEmpresa.MEDIO,
        cnae_principal="4221902",
        cnae_descricao="Construção de estações e redes de distribuição de energia elétrica",
        grupo_economico="",
        dados_verificados=True,
        proprietario="maria.santos",
        segmento="Energia",
    )
    contas.append(conta2)

    # Conta 3: Empresa sem enriquecimento
    conta3 = Conta(
        id="C003",
        cnpj="55566677000199",
        razao_social="Transportadora Rápida Ltda.",
        nome_fantasia="TransRápida",
        porte=PorteEmpresa.PEQUENO,
        cnae_principal="4930202",
        proprietario="joao.silva",
    )
    contas.append(conta3)

    # Conta 4: Potencial duplicata da conta 1
    conta4 = Conta(
        id="C004",
        cnpj="12345678000276",  # Mesma raiz, filial diferente
        razao_social="CN Engenharia - Filial Nordeste",
        nome_fantasia="CN Engenharia NE",
        porte=PorteEmpresa.GRANDE,
        cnae_principal="4120400",
        site="www.cnengenharia.com.br",
        dados_verificados=True,
    )
    contas.append(conta4)

    # === CONTATOS ===
    contatos = []

    contato1 = Contato(
        id="CT001",
        conta_id="C001",
        nome="Carlos Mendes",
        cargo="Diretor de Engenharia",
        area=AreaContato.ENGENHARIA,
        nivel_influencia=NivelInfluencia.DECISOR,
        email="carlos.mendes@cnengenharia.com.br",
        telefone="(11) 3000-0001",
        canal_preferido=CanalPreferido.EMAIL,
        principal=True,
    )
    contato1.registrar_consentimento("Comunicação Comercial", "E-mail")
    contato1.registrar_consentimento("Envio de Propostas", "E-mail")
    contatos.append(contato1)

    contato2 = Contato(
        id="CT002",
        conta_id="C001",
        nome="Ana Paula Rodrigues",
        cargo="Gerente de Compras",
        area=AreaContato.COMPRAS,
        nivel_influencia=NivelInfluencia.INFLUENCIADOR,
        email="ana.rodrigues@cnengenharia.com.br",
        canal_preferido=CanalPreferido.WHATSAPP,
    )
    contatos.append(contato2)

    contato3 = Contato(
        id="CT003",
        conta_id="C002",
        nome="Roberto Lima",
        cargo="CEO",
        area=AreaContato.DIRETORIA,
        nivel_influencia=NivelInfluencia.DECISOR,
        email="roberto@infratech.com.br",
        principal=True,
    )
    contato3.registrar_consentimento("Comunicação Comercial", "Formulário")
    contatos.append(contato3)

    # === OPORTUNIDADES ===
    oportunidades = []

    # Oportunidade 1: Performance Bond em estágio avançado
    op1 = Oportunidade(
        id="OP001",
        conta_id="C001",
        nome="Performance Bond - BR-101/SC Lote 3",
        tipo_garantia=TipoGarantiaOportunidade.PERFORMANCE,
        etapa=EtapaOportunidade.ESTRUTURACAO_SUBMISSAO,
        objeto_contratual=ObjetoContratual(
            descricao_resumida="Duplicação da BR-101/SC, Lote 3 - 45km",
            escopo_tecnico="Terraplenagem, pavimentação, drenagem, sinalização e obras de arte correntes",
            cronograma_fisico_financeiro="24 meses, desembolso progressivo trimestral",
            kpis=["IRI < 2,5", "Prazo de execução", "Qualidade do pavimento"],
            clausulas_criticas=["Multa de 2% por mês de atraso", "Reajuste IPCA anual", "Retomada após 90 dias"],
        ),
        valor_contrato=Decimal('200000000'),
        valor_garantia=Decimal('40000000'),
        vigencia_meses=30,
        data_previsao_fechamento=date.today() + timedelta(days=20),
        proprietario="joao.silva",
        contatos_ids=["CT001", "CT002"],
    )

    # Matriz de risco
    op1.matriz_risco = MatrizRisco(lgd_assumida=25.0, responsavel="equipe_tecnica")
    op1.matriz_risco.adicionar_risco(
        CategoriaRisco.ENGENHARIA, "Complexidade geotécnica no trecho 15-25km",
        NivelRisco.MODERADO, 3, 3,
        mitigacao="Laudo geotécnico complementar e solução alternativa de fundação",
    )
    op1.matriz_risco.adicionar_risco(
        CategoriaRisco.FINANCEIRO, "Exposição acima do limite padrão da seguradora",
        NivelRisco.ALTO, 2, 5,
        mitigacao="Contragarantia via cessão de recebíveis do contrato",
    )
    op1.matriz_risco.adicionar_risco(
        CategoriaRisco.JURIDICO, "Cláusula de retomada após 90 dias é agressiva",
        NivelRisco.MODERADO, 2, 4,
        mitigacao="Negociação para extensão do prazo de retomada para 120 dias",
    )

    # Contragarantias
    op1.adicionar_contragarantia(
        TipoContragarantia.CESSAO_RECEBIVEIS,
        "Cessão de 30% dos recebíveis do contrato BR-101",
        valor=Decimal('60000000'), garantidor="CN Engenharia",
    )
    op1.adicionar_contragarantia(
        TipoContragarantia.FIANCA_CORPORATIVA,
        "Fiança do Grupo CN Holdings",
        garantidor="CN Holdings S.A.",
    )

    # Seguradoras
    seg_zurich = op1.adicionar_seguradora("Zurich Seguros", "Seguradora")
    seg_zurich.status = StatusSeguradoraOportunidade.EM_ANALISE
    seg_zurich.data_submissao = date.today() - timedelta(days=10)

    seg_junto = op1.adicionar_seguradora("Junto Seguros", "Seguradora")
    seg_junto.status = StatusSeguradoraOportunidade.RECUSADA
    seg_junto.data_submissao = date.today() - timedelta(days=15)
    seg_junto.data_resposta = date.today() - timedelta(days=5)
    seg_junto.razao_recusa = "Limite de exposição excedido para o setor rodoviário"

    # Estudo técnico
    op1.adicionar_estudo_tecnico(
        "ET001", "Estudo de Viabilidade - BR-101 Lote 3",
        "/docs/estudos/ET001_BR101_v1.pdf",
        "abc123hash", autor="equipe_tecnica",
        resumo="Análise de viabilidade técnica e financeira da operação",
    )

    # Economia
    op1.economia = EconomiaOperacao(
        taxa_praticada=1.8,
        premio_anual=Decimal('720000'),
        premio_total=Decimal('1800000'),
        comissao_percentual=20.0,
        comissao_valor=Decimal('360000'),
        custos_operacionais=Decimal('80000'),
        honorarios=Decimal('150000'),
    )

    oportunidades.append(op1)

    # Oportunidade 2: Bid Bond (início do pipeline)
    op2 = Oportunidade(
        id="OP002",
        conta_id="C002",
        nome="Bid Bond - Subestação Energia SE",
        tipo_garantia=TipoGarantiaOportunidade.PARTICIPACAO,
        etapa=EtapaOportunidade.QUALIFICACAO_PJ,
        valor_contrato=Decimal('80000000'),
        valor_garantia=Decimal('4000000'),
        vigencia_meses=6,
        proprietario="maria.santos",
    )
    oportunidades.append(op2)

    # Oportunidade 3: Pós-emissão (para monitoramento de renovação)
    op3 = Oportunidade(
        id="OP003",
        conta_id="C001",
        nome="Performance Bond - Metro SP Linha 6",
        tipo_garantia=TipoGarantiaOportunidade.PERFORMANCE,
        etapa=EtapaOportunidade.POS_EMISSAO,
        valor_contrato=Decimal('500000000'),
        valor_garantia=Decimal('100000000'),
        data_inicio_vigencia=date.today() - timedelta(days=300),
        data_fim_vigencia=date.today() + timedelta(days=65),
        data_fechamento_real=date.today() - timedelta(days=300),
        proprietario="joao.silva",
        economia=EconomiaOperacao(
            taxa_praticada=1.5,
            premio_total=Decimal('3750000'),
            comissao_valor=Decimal('750000'),
            custos_operacionais=Decimal('120000'),
            honorarios=Decimal('200000'),
        ),
    )
    seg_zurich3 = op3.adicionar_seguradora("Zurich Seguros")
    seg_zurich3.status = StatusSeguradoraOportunidade.APROVADA
    oportunidades.append(op3)

    return contas, contatos, oportunidades


def demo_modelo_dados(contas, contatos, oportunidades):
    """Demonstra modelo de dados PJ-first"""
    separador("1. MODELO DE DADOS PJ-FIRST")

    subsecao("Contas (PJ)")
    for conta in contas:
        print(f"  {conta}")
        print(f"    CNPJ: {conta.cnpj_formatado}")
        print(f"    Dados verificados: {conta.dados_verificados}")
        print(f"    Completude: {conta.percentual_completude:.0f}%")
        print(f"    Limites vigentes: {len(conta.limites_vigentes)}")
        print(f"    Sinais pendentes: {len(conta.sinais_nao_processados)}")
        print()

    subsecao("Contatos")
    for contato in contatos:
        print(f"  {contato}")
        print(f"    Conta: {contato.conta_id} | LGPD: {contato.tem_consentimento_comercial}")
        print()

    subsecao("Oportunidades")
    for op in oportunidades:
        print(f"  {op}")
        print(f"    Valor garantia: R$ {op.valor_garantia:,.2f}" if op.valor_garantia else "    Valor: N/D")
        print(f"    Dias no pipeline: {op.dias_no_pipeline}")
        print(f"    Tem objeto: {op.tem_objeto_contratual} | Tem risco: {op.tem_matriz_risco}")
        print()


def demo_pipeline():
    """Demonstra pipeline com checklists"""
    separador("2. PIPELINE COMERCIAL (8 ETAPAS)")

    pipeline = Pipeline()
    for etapa in pipeline.etapas:
        status = "OK" if etapa.pode_avancar() else "PENDENTE"
        print(f"  Etapa {etapa.numero}: {etapa.nome}")
        print(f"    Saída: {etapa.saida_esperada}")
        print(f"    Checklist: {len(etapa.checklist)} itens | Status: {status}")
        for item in etapa.checklist[:3]:
            obr = "*" if item.obrigatorio else " "
            print(f"      [{obr}] {item.descricao}")
        if len(etapa.checklist) > 3:
            print(f"      ... e mais {len(etapa.checklist) - 3} item(ns)")
        print()


def demo_validacao_pipeline(oportunidades, contas, contatos):
    """Demonstra validação de avanço de etapa"""
    separador("3. VALIDAÇÃO DE ETAPA (GOVERNANÇA)")

    validador = ValidadorEtapa()
    op = oportunidades[0]
    conta = contas[0]
    ctts = [c for c in contatos if c.conta_id == conta.id]

    resultado = validador.validar_transicao(op, conta, ctts, op.etapa_numero + 1)
    print(f"  Oportunidade: {op.nome}")
    print(f"  Etapa atual: {resultado.etapa_atual}")
    print(f"  Etapa destino: {resultado.etapa_destino}")
    print(f"  Pode avançar: {resultado.pode_avancar}")
    if resultado.erros:
        print(f"  Erros:")
        for e in resultado.erros:
            print(f"    X {e}")
    if resultado.avisos:
        print(f"  Avisos:")
        for a in resultado.avisos:
            print(f"    ! {a}")


def demo_scoring(contas, oportunidades):
    """Demonstra scoring de fit e propensão"""
    separador("4. SCORING & PRIORIZAÇÃO")

    subsecao("Score de Fit (Conta)")
    score_fit = ScoreFit()
    for conta in contas[:2]:
        resultado = score_fit.calcular(conta)
        print(f"  {conta.razao_social}")
        print(f"    Score: {resultado.score_total:.1f}/100 | Semáforo: {resultado.semaforo.upper()}")
        print(f"    ICP Fit: {resultado.icp_fit}")
        for detalhe in resultado.detalhes:
            print(f"      {detalhe.fator}: {detalhe.pontuacao_bruta:.0f} (peso {detalhe.peso})")
        print(f"    Recomendação: {resultado.recomendacao[:80]}...")
        print()

    subsecao("Score de Propensão (Oportunidade)")
    score_prop = ScorePropensao()
    for op in oportunidades[:2]:
        resultado = score_prop.calcular(op)
        print(f"  {op.nome}")
        print(f"    Score: {resultado.score_total:.1f}/100 | Semáforo: {resultado.semaforo.upper()}")
        print(f"    Probabilidade fechamento: {resultado.probabilidade_fechamento:.1f}%")
        print(f"    Próxima ação: {resultado.proxima_melhor_acao[:80]}")
        print()


def demo_enriquecimento(contas):
    """Demonstra validação de CNPJ e enriquecimento"""
    separador("5. ENRIQUECIMENTO DE DADOS")

    subsecao("Validação de CNPJ")
    validador = ValidadorCNPJ()
    cnpjs_teste = ["12345678000195", "11222333000181", "00000000000000", "123"]
    for cnpj in cnpjs_teste:
        resultado = validador.validar(cnpj)
        status = "VÁLIDO" if resultado.valido else f"INVÁLIDO ({resultado.erro})"
        print(f"  {cnpj} → {status}")

    subsecao("Verificação de Matriz/Filial")
    print(f"  12345678000195 → Matriz: {validador.eh_matriz('12345678000195')}")
    print(f"  12345678000276 → Matriz: {validador.eh_matriz('12345678000276')}")
    print(f"  Mesma empresa: {validador.mesma_empresa('12345678000195', '12345678000276')}")

    subsecao("Deduplicação")
    deduplicador = Deduplicador()
    resultado = deduplicador.analisar(contas)
    print(f"  Contas analisadas: {resultado.total_contas_analisadas}")
    print(f"  Duplicatas encontradas: {resultado.total_duplicatas}")
    for dup in resultado.duplicatas_encontradas:
        print(f"    Par: {dup.conta_a_id} <-> {dup.conta_b_id}")
        print(f"      Score: {dup.score_similaridade:.0f}% | Critérios: {', '.join(dup.criterios_match)}")
        print(f"      Recomendação: {dup.recomendacao}")


def demo_playbooks(contas, contatos, oportunidades):
    """Demonstra playbooks de prospecção"""
    separador("6. PLAYBOOKS DE PROSPECÇÃO CONSULTIVA")

    subsecao("Playbook A — Editais/Obras")
    playbook_editais = PlaybookEditais()

    lista_quente = playbook_editais.gerar_lista_quente(contas)
    print(f"  Lista quente: {len(lista_quente)} conta(s)")

    if lista_quente:
        contato_principal = next(
            (c for c in contatos if c.conta_id == lista_quente[0].id and c.principal),
            None
        )
        resultado = playbook_editais.executar(lista_quente[0], contato_principal)
        print(f"  Trigger ativado: {resultado.trigger_ativado}")
        print(f"  Ações geradas: {len(resultado.acoes_geradas)}")
        for acao in resultado.acoes_geradas[:5]:
            print(f"    [{acao.prioridade.upper()}] {acao.tipo}: {acao.descricao[:60]}")

    subsecao("Playbook B — Renovação/Performance")
    playbook_renovacao = PlaybookRenovacao()
    resultado_ren = playbook_renovacao.executar(oportunidades)
    resumo = playbook_renovacao.resumo_renovacoes(oportunidades)
    print(f"  Monitoradas: {resumo['total_monitoradas']}")
    print(f"  Vencendo 90d: {resumo['vencendo_90d']}")
    print(f"  Vencendo 60d: {resumo['vencendo_60d']}")
    print(f"  Vencendo 30d: {resumo['vencendo_30d']}")
    print(f"  Ações geradas: {resumo['total_acoes_pendentes']}")

    subsecao("Playbook C — Recusa Técnica / Contestação")
    playbook_contestacao = PlaybookContestacao()
    stats = playbook_contestacao.estatisticas_recusas(oportunidades)
    print(f"  Total recusas: {stats['total_recusas']}")
    print(f"  Contestáveis: {stats['contestaveis']}")
    print(f"  Por motivo:")
    for motivo, count in stats.get('por_motivo', {}).items():
        print(f"    {motivo}: {count}")

    # Executar contestação específica
    if oportunidades[0].seguradoras_recusadas:
        recusa = oportunidades[0].seguradoras_recusadas[0]
        resultado_cont = playbook_contestacao.analisar_recusa(oportunidades[0], recusa.nome)
        print(f"\n  Análise recusa {recusa.nome}:")
        print(f"    Motivo classificado: {resultado_cont.motivo_classificado}")
        print(f"    Contestável: {resultado_cont.contestavel}")
        print(f"    Ações: {len(resultado_cont.acoes_geradas)}")


def demo_dashboard(contas, oportunidades):
    """Demonstra dashboard executivo"""
    separador("7. DASHBOARD EXECUTIVO")

    dashboard = DashboardExecutivo()
    dados = dashboard.gerar(contas, oportunidades)

    # Versão texto
    print(dashboard.gerar_resumo_texto(dados))


def demo_seguranca(contatos):
    """Demonstra controle de acesso e LGPD"""
    separador("8. SEGURANÇA, LGPD & GOVERNANÇA")

    subsecao("Controle de Acesso (RBAC)")
    controle = ControleAcesso()

    # Registrar usuários
    controle.registrar_usuario("U001", "João Silva", "joao@vf.com", "comercial")
    controle.registrar_usuario("U002", "Ana Tech", "ana@vf.com", "tecnico")
    controle.registrar_usuario("U003", "Dir. Carlos", "carlos@vf.com", "diretoria")
    controle.registrar_usuario("U004", "Parceiro X", "parceiro@ext.com", "parceiro")

    # Verificar permissões
    testes = [
        ("U001", Permissao.CONTA_CRIAR, "Comercial criar conta"),
        ("U001", Permissao.ESTUDO_EDITAR, "Comercial editar estudo"),
        ("U002", Permissao.RISCO_CRIAR, "Técnico criar risco"),
        ("U002", Permissao.OPORTUNIDADE_FECHAR, "Técnico fechar oportunidade"),
        ("U003", Permissao.ADMIN_AUDITORIA, "Diretoria ver auditoria"),
        ("U004", Permissao.DOCUMENTO_EDITAR, "Parceiro editar documento"),
    ]

    for user_id, perm, desc in testes:
        permitido = controle.verificar_permissao(user_id, perm)
        status = "PERMITIDO" if permitido else "NEGADO"
        print(f"  {desc}: {status}")

    subsecao("LGPD")
    gestor_lgpd = GestorLGPD()
    relatorio = gestor_lgpd.verificar_conformidade(contatos)
    print(f"  Total contatos: {relatorio.total_contatos}")
    print(f"  Com consentimento: {relatorio.com_consentimento}")
    print(f"  Sem consentimento: {relatorio.sem_consentimento}")
    print(f"  Taxa conformidade: {relatorio.taxa_conformidade:.1f}%")
    if relatorio.alertas:
        print(f"  Alertas:")
        for alerta in relatorio.alertas:
            print(f"    ! {alerta}")


def demo_automacao():
    """Demonstra motor de regras e automação"""
    separador("9. AUTOMAÇÃO & REGRAS")

    motor = MotorRegras()

    subsecao("Regras Registradas")
    for regra in motor.listar_regras():
        print(f"  [{regra['id']}] {regra['nome']} (trigger: {regra['evento']})")

    subsecao("Simulação de Eventos")

    # Evento 1: Conta criada
    evento1 = Evento(
        tipo=TipoEvento.CONTA_CRIADA,
        dados={'conta_id': 'C005', 'cnpj': '11222333000181'},
        usuario="joao.silva",
    )
    resultado1 = motor.processar_evento(evento1)
    print(f"  Evento: Conta Criada")
    print(f"    Regras avaliadas: {resultado1.regras_avaliadas}")
    print(f"    Regras ativadas: {resultado1.regras_ativadas}")
    print(f"    Ações geradas: {len(resultado1.acoes_geradas)}")
    for acao in resultado1.acoes_geradas:
        print(f"      -> {acao.tipo}: {acao.descricao[:60]}")

    # Evento 2: Recusa registrada
    evento2 = Evento(
        tipo=TipoEvento.RECUSA_REGISTRADA,
        dados={
            'oportunidade_id': 'OP001',
            'oportunidade_nome': 'Performance Bond - BR-101',
            'seguradora': 'Junto Seguros',
            'motivo_recusa': 'Limite excedido',
        },
        usuario="maria.santos",
    )
    resultado2 = motor.processar_evento(evento2)
    print(f"\n  Evento: Recusa Registrada")
    print(f"    Regras ativadas: {resultado2.regras_ativadas}")
    print(f"    Ações geradas: {len(resultado2.acoes_geradas)}")
    for acao in resultado2.acoes_geradas:
        print(f"      -> {acao.tipo}: {acao.descricao[:60]}")


def demo_integracoes():
    """Demonstra orquestrador de integrações"""
    separador("10. INTEGRAÇÕES")

    orquestrador = OrquestradorIntegracoes()

    subsecao("Integrações Configuradas")
    for integ in orquestrador.status_integracoes():
        print(f"  [{integ['status']}] {integ['nome']}")
        print(f"    Tipo: {integ['tipo']} | Frequência: {integ['frequencia'] or 'N/A'}")

    subsecao("Saúde Geral")
    saude = orquestrador.saude_integracoes()
    print(f"  Total: {saude['total_integracoes']}")
    print(f"  Ativas: {saude['ativas']}")
    print(f"  Com erro: {saude['com_erro']}")
    print(f"  Saúde: {saude['saude'].upper()}")


def demo_roadmap():
    """Exibe roadmap de 90 dias"""
    separador("11. ROADMAP DE 90 DIAS")

    roadmap = {
        "Dias 0-15 — Fundamentos": [
            "Modelo de dados implementado (Conta/Contato/Oportunidade/Documentos)",
            "Regras de deduplicação e campos obrigatórios por etapa",
            "Pipeline com checklists mínimos (objeto/cronograma/mitigações)",
            "Integração de e-mail/calendário + repositório de documentos",
        ],
        "Dias 16-30 — Enriquecimento & Prospecção": [
            "Conector de validação CNPJ/CNAE/porte + job diário",
            "Primeiros playbooks (Editais/Obras e Renovação/Performance)",
            "Listas ICP + cadências (outbound consultivo)",
        ],
        "Dias 31-60 — Risco & Contestação": [
            "Matriz de risco padronizada, templates de dossiê e ofício",
            "Registro obrigatório de motivo de recusa e SLA de follow-up",
            "Dashboard executivo v1 (pipeline, taxas, motivos de recusa)",
        ],
        "Dias 61-90 — Otimização & BI": [
            "Score de Fit/Propensão e priorização por próxima melhor ação",
            "Automação de renovações e alertas de marcos contratuais",
            "Power BI com insights semanais e metas por produtor/parceiro",
        ],
    }

    for fase, itens in roadmap.items():
        print(f"  {fase}")
        for item in itens:
            print(f"    [x] {item}")
        print()


def main():
    """Execução principal - demonstração completa do CRM"""
    print("""
    ===============================================================
     CRM DE PROSPECÇÃO E OPERAÇÕES DE GARANTIA
     Sistema completo PJ-first para seguro garantia
    ===============================================================

     OKRs:
       Obj 1: Prospecção de Alta Precisão (B2B)
         KR1: 80% contas com CNPJ validado e CNAE/porte enriquecidos
         KR2: +30% taxa de resposta em cadências consultivas (90 dias)
         KR3: Qualificação de 10 para 3 dias

       Obj 2: Conversão em Operações de Garantia
         KR1: +20% win rate com objeto contratual analisado
         KR2: 100% oportunidades com risco e contragarantias
         KR3: Tempo ciclo reduzido em 25%

       Obj 3: Inteligência & Governança
         KR1: 100% dados PJ com deduplicação e campos obrigatórios
         KR2: Dashboard executivo atualizado diariamente
         KR3: Estudos técnicos vinculados com controle de acesso
    """)

    # Criar dados de demonstração
    contas, contatos, oportunidades = criar_dados_demonstracao()

    # Executar demonstrações
    demo_modelo_dados(contas, contatos, oportunidades)
    demo_pipeline()
    demo_validacao_pipeline(oportunidades, contas, contatos)
    demo_scoring(contas, oportunidades)
    demo_enriquecimento(contas)
    demo_playbooks(contas, contatos, oportunidades)
    demo_dashboard(contas, oportunidades)
    demo_seguranca(contatos)
    demo_automacao()
    demo_integracoes()
    demo_roadmap()

    separador("SISTEMA CRM COMPLETO")
    print("  Todos os módulos implementados e demonstrados:")
    print("    1. Modelo de Dados PJ-first (Conta, Contato, Oportunidade, Atividade, Documento)")
    print("    2. Pipeline Comercial (8 etapas com checklists)")
    print("    3. Scoring (Fit + Propensão + Semáforos)")
    print("    4. Enriquecimento (CNPJ, API, Deduplicação)")
    print("    5. Playbooks (Editais, Renovação, Contestação)")
    print("    6. Dashboard Executivo (KPIs + Insights)")
    print("    7. Segurança (RBAC + LGPD)")
    print("    8. Automação (Regras + Jobs)")
    print("    9. Integrações (8 conectores configurados)")
    print("   10. Roadmap 90 dias")
    print()


if __name__ == "__main__":
    main()
