#!/usr/bin/env python3
"""
Demonstração do Sistema Comercial (não interativo)
"""

from datetime import datetime, date, timedelta
from decimal import Decimal

# Importações do sistema
from src.comercial.operacao import (
    Operacao, TipoOperacao, TipoGarantia, OrigemOperacao
)
from src.comercial.tomador import (
    Tomador, PorteTomador, SetorTomador, NivelContato,
    ClassificacaoRisco, criar_tomador_novo, HistoricoOperacao
)
from src.comercial.qualificador import QualificadorOperacao
from src.comercial.proposta import GeradorProposta


print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     SISTEMA COMERCIAL DE OPERAÇÕES - DEMONSTRAÇÃO                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# ══════════════════════════════════════════════════════════════════════════════
# 1. CRIANDO TOMADOR - DISTRIBUIDORA
# ══════════════════════════════════════════════════════════════════════════════

print("""
════════════════════════════════════════════════════════════════════════════════
  1. CADASTRO DE TOMADOR - DISTRIBUIDORA DE ALIMENTOS
════════════════════════════════════════════════════════════════════════════════
""")

tomador = criar_tomador_novo(
    id="DIST001",
    razao_social="Distribuidora de Alimentos S.A.",
    cnpj="12.345.678/0001-90",
    porte=PorteTomador.GRANDE,
    setor=SetorTomador.COMERCIO,
    contato_nome="Maria Silva",
    contato_cargo="Chefe do Jurídico",
    contato_email="maria.silva@distribuidora.com.br",
    nome_fantasia="Distribuidora Alimentos",
    contato_nivel=NivelContato.DIRETORIA,
    faturamento_anual=Decimal('10000000000')
)

# Adiciona histórico positivo
tomador.historico.adicionar_operacao(HistoricoOperacao(
    data=datetime(2024, 1, 1),
    tipo="Emissão anterior",
    valor_operacao=Decimal('50000000'),
    valor_honorarios=Decimal('100000'),
    valor_pago=Decimal('100000'),
    valor_pendente=Decimal('0'),
    status="Concluída"
))

# Adiciona RED FLAGS
tomador.corretores_conhecidos = ["Geo Seguros"]
tomador.adicionar_red_flag(
    categoria="Concorrência",
    descricao="Corretor atual é Geo - família dona da Pottencial",
    severidade=5,
    fonte="Informação do caso"
)

tomador.calcular_score_risco()

print(f"""
TOMADOR CADASTRADO:

  Razão Social:  {tomador.razao_social}
  CNPJ:          {tomador.cnpj}
  Faturamento:   R$ 10 bilhões/ano
  Setor:         {tomador.setor.value}
  Contato:       {tomador.contato_nome} ({tomador.contato_cargo})

ANÁLISE DE RISCO:

  Score de Risco:    {tomador.score_risco:.0f}/100 (maior = pior)
  Classificação:     {tomador.classificacao.value}

HISTÓRICO:

  Operações:         {tomador.historico.total_operacoes}
  Taxa de Pagamento: {tomador.historico.taxa_pagamento:.0f}%

RED FLAGS:
""")

for rf in tomador.red_flags:
    print(f"  🚩 {rf.descricao} (severidade: {rf.severidade}/5)")

print(f"\nCorretores conhecidos: {', '.join(tomador.corretores_conhecidos)}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. QUALIFICAÇÃO DE OPERAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

print("""

════════════════════════════════════════════════════════════════════════════════
  2. QUALIFICAÇÃO DA OPERAÇÃO - VALE A PENA ENTRAR?
════════════════════════════════════════════════════════════════════════════════
""")

operacao = Operacao(
    id="OP001",
    nome="Garantia de Pagamento ICMS - Anglo Americana",
    tomador_id=tomador.id,
    tomador_nome=tomador.razao_social,
    tomador_cnpj=tomador.cnpj,
    tipo_operacao=TipoOperacao.FINANCEIRA,
    tipo_garantia=TipoGarantia.FINANCEIRA,
    valor_garantia=Decimal('10000000'),
    valor_contrato=Decimal('10000000'),
    descricao="Garantia de pagamento para compra de ICMS",
    origem=OrigemOperacao.RETORNO_CLIENTE,
    contato_nome=tomador.contato_nome,
    contato_cargo=tomador.contato_cargo,
    contato_email=tomador.contato_email,
    contato_telefone="",
    ja_tentou_outros_corretores=True,
    corretores_anteriores=["Geo Seguros"]
)

qualificador = QualificadorOperacao()
analise = qualificador.qualificar(operacao, tomador)

print(qualificador.gerar_resumo_executivo(analise))

print("\nRECOMENDAÇÕES DO SISTEMA:\n")

for i, rec in enumerate(analise.recomendacoes, 1):
    print(f"  {i}. {rec}")

print(f"""

ESTRUTURA DE COBRANÇA RECOMENDADA:

  DIAGNÓSTICO:
    Valor mínimo:      R$ {analise.valor_minimo_diagnostico:,.2f}
    Valor recomendado: R$ {analise.valor_recomendado_diagnostico:,.2f}
    Condição:          100% ANTECIPADO - NÃO NEGOCIÁVEL
""")


# ══════════════════════════════════════════════════════════════════════════════
# 3. PROPOSTA COMERCIAL
# ══════════════════════════════════════════════════════════════════════════════

print("""
════════════════════════════════════════════════════════════════════════════════
  3. PROPOSTA COMERCIAL GERADA
════════════════════════════════════════════════════════════════════════════════
""")

gerador = GeradorProposta()
proposta = gerador.gerar_proposta(operacao, tomador, analise)

print(f"""
PROPOSTA GERADA:

  Número:    {proposta.numero}
  Data:      {proposta.data.strftime('%d/%m/%Y')}
  Validade:  {proposta.validade_dias} dias

ESTRUTURA DE FASES:
""")

for fase in proposta.fases:
    print(f"""
  FASE {fase['numero']}: {fase['nome']}
  Valor:     R$ {fase['valor']:,.2f}
  Condição:  {fase['condicao_pagamento']}
""")

print(f"""
  ════════════════════════════════════════
  TOTAL: R$ {proposta.valor_total:,.2f}
  ════════════════════════════════════════
""")


# ══════════════════════════════════════════════════════════════════════════════
# 4. SCRIPT DE ABORDAGEM
# ══════════════════════════════════════════════════════════════════════════════

print("""
════════════════════════════════════════════════════════════════════════════════
  4. SCRIPT DE ABORDAGEM - DEMANDA PASSIVA
════════════════════════════════════════════════════════════════════════════════

Scripts disponíveis:

  [1] Resposta Inicial à Solicitação
  [2] Objeção: "Muito Caro"
  [3] Objeção: "Prefiro Pagar no Final"
  [4] Fechamento com Urgência

EXEMPLO - RESPOSTA INICIAL:
───────────────────────────────────────────────────────────────────────────────
""")

print(f"""
Prezada(o) {tomador.contato_nome},

Obrigado pelo contato. Analisamos preliminarmente a solicitação de
{operacao.tipo_operacao.value} no valor de R$ {operacao.valor_garantia:,.2f}.

Antes de avançarmos, preciso ser transparente:

Após uma análise inicial, identificamos que este caso apresenta
complexidade que vai além de uma simples cotação de mercado.
Identificamos: garantia financeira (modalidade restritiva).

O que isso significa na prática?

Casos como este exigem um trabalho técnico aprofundado para identificar:
• Por que o mercado está recusando
• Quais são os obstáculos técnicos e regulatórios
• Se existe um caminho viável para aprovação

Este diagnóstico tem um investimento de R$ {analise.valor_recomendado_diagnostico:,.2f}.

IMPORTANTE: Este valor é pelo diagnóstico, não pelo resultado.
Você terá clareza sobre o problema independente de conseguirmos
ou não aprovar a operação.

Se houver interesse em prosseguir, envio a proposta formal.

───────────────────────────────────────────────────────────────────────────────
""")


# ══════════════════════════════════════════════════════════════════════════════
# 5. COMPARATIVO COM AGRONEGÓCIO
# ══════════════════════════════════════════════════════════════════════════════

print("""
════════════════════════════════════════════════════════════════════════════════
  5. COMPARATIVO - DISTRIBUIDORA vs AGRONEGÓCIO
════════════════════════════════════════════════════════════════════════════════
""")

tomador2 = criar_tomador_novo(
    id="AGRO001",
    razao_social="Trading Exportadora de Grãos Ltda",
    cnpj="98.765.432/0001-10",
    porte=PorteTomador.GRANDE,
    setor=SetorTomador.AGRONEGOCIO,
    contato_nome="João Oliveira",
    contato_cargo="Diretor Comercial",
    contato_email="joao@trading.com.br",
    nome_fantasia="Trading Grãos",
    contato_nivel=NivelContato.DIRETORIA
)

tomador2.calcular_score_risco()

operacao2 = Operacao(
    id="OP002",
    nome="Estruturação Exportação de Grãos",
    tomador_id=tomador2.id,
    tomador_nome=tomador2.razao_social,
    tomador_cnpj=tomador2.cnpj,
    tipo_operacao=TipoOperacao.OUTRO,
    tipo_garantia=TipoGarantia.FINANCEIRA,
    valor_garantia=Decimal('50000000'),
    valor_contrato=Decimal('100000000'),
    descricao="Estruturação de exportação com garantia internacional",
    origem=OrigemOperacao.DEMANDA_PASSIVA,
    contato_nome=tomador2.contato_nome,
    contato_cargo=tomador2.contato_cargo,
    contato_email=tomador2.contato_email,
    contato_telefone=""
)

analise2 = qualificador.qualificar(operacao2, tomador2)

print(f"""
COMPARATIVO DOS DOIS CASOS:

┌─────────────────────────────┬──────────────────────┬──────────────────────┐
│                             │ DISTRIBUIDORA        │ AGRONEGÓCIO          │
├─────────────────────────────┼──────────────────────┼──────────────────────┤
│ Valor Garantia              │ R$ 10 milhões        │ R$ 50 milhões        │
│ Diagnóstico Recomendado     │ R$ 37.500            │ R$ 50.000            │
│ Score Viabilidade           │ {analise.score_viabilidade:.1f}/100             │ {analise2.score_viabilidade:.1f}/100             │
│ Score Risco Tomador         │ {analise.score_risco_tomador:.1f}/100             │ {analise2.score_risco_tomador:.1f}/100              │
│ Red Flags                   │ {len(analise.red_flags)} (GEO!)              │ 0                    │
│ Decisão                     │ {analise.decisao.value[:20]:<20} │ {analise2.decisao.value[:20]:<20} │
└─────────────────────────────┴──────────────────────┴──────────────────────┘

⚠️  ALERTA DISTRIBUIDORA: Geo é corretor atual (família dona da Pottencial)
                          Risco de desvio da operação é ALTO

✓  AGRONEGÓCIO: Caso limpo, sem corretor concorrente
                Complexidade internacional justifica R$ 50K
""")


# ══════════════════════════════════════════════════════════════════════════════
# RESUMO FINAL
# ══════════════════════════════════════════════════════════════════════════════

print("""
════════════════════════════════════════════════════════════════════════════════
  RESUMO - SISTEMA COMERCIAL
════════════════════════════════════════════════════════════════════════════════

O QUE O SISTEMA FAZ:

  ✓ Qualifica operações (vale a pena entrar?)
  ✓ Calcula risco de oportunismo do tomador
  ✓ Define valor do diagnóstico baseado em complexidade
  ✓ Gera propostas comerciais estruturadas
  ✓ Fornece scripts para demanda passiva
  ✓ Fornece scripts para prospecção ativa
  ✓ Gera contratos por fase com proteção de PI

PRINCÍPIOS IMPLEMENTADOS:

  1. Diagnóstico SEMPRE 100% antecipado
  2. Cada fase tem valor independente
  3. Nunca entregar sem pagamento
  4. Documentar tudo para proteção

ARQUIVOS DO SISTEMA:

  src/comercial/
  ├── operacao.py      # Modelo de operações e fases
  ├── tomador.py       # Modelo de tomadores e risco
  ├── qualificador.py  # Sistema de decisão
  └── proposta.py      # Propostas e scripts

PARA USAR INTERATIVAMENTE:

  python comercial_app.py

════════════════════════════════════════════════════════════════════════════════
                         FIM DA DEMONSTRAÇÃO
════════════════════════════════════════════════════════════════════════════════
""")
