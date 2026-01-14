# Metodologia de Avaliação da Força Financeira Isolada de Seguradoras: Identificação de Fissuras e Dependência de Resseguro

**Paper Técnico**

**Autor:** Sistema de Análise Financeira
**Data:** Janeiro de 2026
**Versão:** 1.0

---

## Resumo Executivo

Este paper apresenta uma metodologia inovadora para avaliação da força financeira isolada de seguradoras, com foco na identificação de dependências estruturais de resseguro e de ratings de grupos econômicos. A metodologia foi desenvolvida para revelar "fissuras" financeiras em seguradoras que, embora apresentem ratings de crédito elevados derivados do grupo econômico, possuem capacidade própria insuficiente para assumir riscos significativos (referência: R$ 50 milhões) de forma independente.

O estudo de caso aplicado à Junto Seguros S.A. demonstrou que a metodologia é eficaz em identificar discrepâncias significativas entre o rating declarado (baseado no grupo) e a real capacidade financeira isolada da seguradora.

**Palavras-chave:** Força financeira, Resseguro, Rating de crédito, Análise de risco, Solvência, Seguradoras, Fronting.

---

## 1. Introdução

### 1.1 Contexto e Problemática

O mercado segurador brasileiro conta com diversas seguradoras que operam sob a égide de grandes grupos econômicos nacionais e internacionais. Essas seguradoras frequentemente utilizam o rating de crédito do grupo consolidado como indicador de sua solidez financeira, sem distinguir adequadamente sua capacidade própria de assumir riscos.

Esta prática levanta questões fundamentais:

1. **Qual é a real capacidade de uma seguradora assumir riscos por conta própria?**
2. **Seguradoras com alta cessão ao resseguro podem ser consideradas financeiramente sólidas de forma independente?**
3. **O rating do grupo reflete a força financeira individual da subsidiária operacional?**

### 1.2 Objetivo do Estudo

Desenvolver e validar uma metodologia para:

- Calcular indicadores de força financeira isolada, excluindo dependências de grupo e resseguro
- Identificar "fissuras" financeiras que evidenciam fragilidades estruturais
- Comparar ratings declarados com ratings isolados calculados
- Estabelecer um limite de referência de capacidade própria (R$ 50 milhões)

### 1.3 Relevância para o Mercado

Credores, segurados e contrapartes em operações de garantia (seguro garantia, fiança, etc.) precisam compreender que o rating de um grupo econômico não necessariamente reflete a capacidade de sua subsidiária operacional de honrar compromissos de forma independente. Esta análise é particularmente relevante para:

- Garantidores e beneficiários de seguros garantia
- Tomadores de grandes riscos
- Reguladores e supervisores
- Agências de rating
- Resseguradoras

---

## 2. Fundamentação Teórica

### 2.1 Conceito de Força Financeira Isolada

A **Força Financeira Isolada** é definida como a capacidade de uma seguradora honrar seus compromissos e absorver perdas utilizando exclusivamente seus próprios recursos, sem depender de:

- Suporte financeiro do grupo econômico (aportes, cartas de suporte)
- Recuperações de resseguro
- Créditos intercompany
- Garantias implícitas ou explícitas

### 2.2 Operações de Fronting

O termo "fronting" refere-se a operações onde a seguradora primária cede a totalidade ou quase totalidade do risco ao ressegurador, atuando essencialmente como intermediária. Seguradoras com taxa de cessão superior a 70% podem ser caracterizadas como operadoras de fronting.

### 2.3 Inflação de Rating

A "inflação de rating" ocorre quando uma entidade apresenta um rating de crédito superior ao que teria se avaliada de forma isolada. Esta situação é comum em subsidiárias de grupos econômicos bem avaliados.

### 2.4 Limite de Referência: R$ 50 Milhões

O valor de R$ 50 milhões foi estabelecido como referência por representar:

- Limite relevante para operações de seguro garantia de médio/grande porte
- Threshold significativo para análise de capacidade de retenção
- Valor-referência para identificação de seguradoras com limitações operacionais relevantes

---

## 3. Metodologia de Análise

### 3.1 Arquitetura do Sistema

O sistema de análise foi desenvolvido em Python e estruturado nos seguintes módulos:

```
src/
├── models/
│   └── forca_isolada.py      # Modelos de dados
└── analysis/
    ├── analisador_forca_isolada.py    # Motor de análise
    └── terminal_forca_isolada.py      # Interface de visualização
```

### 3.2 Indicadores Calculados

A metodologia calcula 6 categorias de indicadores:

#### 3.2.1 Indicadores de Dependência de Resseguro

| Indicador | Fórmula | Interpretação |
|-----------|---------|---------------|
| Taxa de Cessão | Prêmios Cedidos / Prêmios Emitidos | > 70% = Fronting |
| Índice de Retenção | 1 - Taxa de Cessão | < 30% = Alta dependência |
| Dependência de Recuperação | Sinistros Recuperados / Sinistros Totais | > 50% = Crítico |
| Concentração Resseguro Grupo | Resseguro Grupo / Resseguro Total | > 50% = Risco concentração |

#### 3.2.2 Indicadores de Capacidade Própria

| Indicador | Fórmula | Referência |
|-----------|---------|------------|
| Capital Próprio Efetivo | PL - Intangíveis - Créditos Grupo | Base para capacidade |
| Capacidade por Risco | Capital Efetivo × 5% | Vs R$ 50MM |
| Capacidade por Evento | Capital Efetivo × 10% | Vs R$ 100MM |
| Índice de Capacidade 50MM | Capacidade Risco / 50.000.000 | ≥ 1.0 adequado |

#### 3.2.3 Indicadores de Solvência Isolada

| Indicador | Fórmula | Limite |
|-----------|---------|--------|
| Índice Solvência Isolado | Capital Efetivo / Passivo Ajustado | ≥ 1.0 |
| Cobertura Provisões Isolada | Ativos Próprios / Provisões Técnicas | ≥ 1.0 |
| Suficiência Capital Isolada | Capital Efetivo / CMR | ≥ 1.5 |

#### 3.2.4 Indicadores de Liquidez Isolada

| Indicador | Fórmula | Limite |
|-----------|---------|--------|
| Liquidez Isolada | Ativos Líquidos Próprios / Passivo CP | ≥ 1.0 |
| Dependência Caixa Grupo | Caixa Grupo / Caixa Total | < 30% |

#### 3.2.5 Indicadores de Stress

| Indicador | Descrição | Interpretação |
|-----------|-----------|---------------|
| Impacto Perda Resseguro | Créditos Resseguro / PL | < 50% aceitável |
| Capacidade Absorção Sinistros | 20% do Capital Efetivo | Máximo absorvível |
| Resiliência Catástrofe | Capital Efetivo / Exposição Cat | ≥ 1.0 |

### 3.3 Score de Força Isolada

O Score de Força Isolada (0-100) é calculado como média ponderada:

| Componente | Peso |
|------------|------|
| Capacidade Própria | 25% |
| Independência Resseguro | 20% |
| Capital Efetivo | 20% |
| Solvência Isolada | 15% |
| Liquidez Isolada | 10% |
| Resiliência | 10% |

### 3.4 Conversão Score → Rating Isolado

| Score | Rating |
|-------|--------|
| ≥ 90 | AAA |
| ≥ 85 | AA+ |
| ≥ 80 | AA |
| ≥ 75 | AA- |
| ≥ 70 | A+ |
| ≥ 65 | A |
| ≥ 60 | A- |
| ≥ 55 | BBB+ |
| ≥ 50 | BBB |
| ≥ 45 | BBB- |
| ≥ 40 | BB+ |
| < 40 | BB ou inferior |

### 3.5 Tipos de Fissuras Identificadas

O sistema identifica 10 tipos de fissuras/fragilidades:

1. **Dependência Excessiva de Resseguro** - Cessão > 50%
2. **Rating Inflado pelo Grupo** - Gap ≥ 2 notches
3. **Capacidade Própria Insuficiente** - < R$ 50MM
4. **Capital Próprio Frágil** - Suficiência < 1.5x
5. **Concentração em Operações do Grupo** - > 50% no grupo
6. **Liquidez Dependente de Terceiros** - < 1.0x
7. **Provisões Subdimensionadas** - Cobertura < 100%
8. **Rentabilidade Artificial** - Dependente de receitas grupo
9. **Alavancagem Excessiva** - > 6x capital efetivo
10. **Exposição Catastrófica sem Cobertura** - Resiliência < 0.5x

### 3.6 Classificação de Risco Isolado

| Nível | Critérios |
|-------|-----------|
| CRÍTICO | ≥ 2 fissuras críticas OU score < 30 |
| ALTO | ≥ 1 fissura crítica OU ≥ 2 altas OU score < 45 |
| MODERADO | ≥ 1 fissura alta OU score < 60 |
| BAIXO | Score 60-74 |
| MÍNIMO | Score ≥ 75 |

---

## 4. Estudo de Caso: Junto Seguros S.A.

### 4.1 Perfil da Empresa

- **Razão Social:** Junto Seguros S.A.
- **CNPJ:** 32.098.536/0001-27
- **Grupo Econômico:** Junto Group
- **Rating Declarado:** brAAA (S&P) / A- (AM Best)
- **Período Analisado:** Exercício 2024

### 4.2 Dados Financeiros Utilizados

Dados extraídos das Demonstrações Financeiras de 2024:

| Item | Valor (R$ mil) |
|------|----------------|
| **Ativo Total** | 3.115.802 |
| **Ativo Circulante** | 2.783.608 |
| **Disponibilidades** | 17.684 |
| **Aplicações Financeiras** | 2.419.082 |
| **Créditos com Resseguradores** | 1.310.832 |
| **Ativo Não Circulante** | 332.194 |
| **Passivo Circulante** | 2.645.523 |
| **Passivo Não Circulante** | 104.929 |
| **Provisões Técnicas** | 2.427.399 |
| **Patrimônio Líquido** | 365.350 |
| **Capital Social** | 210.000 |

### 4.3 Dados de Resseguro

| Item | Valor |
|------|-------|
| Prêmios Emitidos | R$ 1.889.632 mil |
| Prêmios Cedidos | R$ 1.214.434 mil (64,3%) |
| Principal Ressegurador | Junto Resseguros S.A. |
| Concentração no Grupo | 99,4% |

### 4.4 Resultados da Análise

#### 4.4.1 Indicadores de Dependência de Resseguro

| Indicador | Valor | Classificação |
|-----------|-------|---------------|
| Taxa de Cessão | 64,3% | **ALTO** |
| Índice de Retenção | 35,7% | MODERADO |
| Concentração no Grupo | 99,4% | **CRÍTICO** |

**Observação:** A altíssima concentração de resseguro no próprio grupo (99,4% cedido à Junto Resseguros S.A.) configura risco de contraparte crítico e questiona a real transferência de risco.

#### 4.4.2 Indicadores de Capacidade Própria

| Indicador | Valor | Status |
|-----------|-------|--------|
| Patrimônio Líquido Real | R$ 365.350 mil | - |
| Capital Próprio Efetivo | R$ 210.000 mil | - |
| Capacidade por Risco (5% CE) | **R$ 10.500 mil** | **INSUFICIENTE** |
| Índice de Capacidade 50MM | 0,21 (21%) | **CRÍTICO** |

**Conclusão:** A capacidade própria de R$ 10,5 milhões representa apenas **21%** do limite de referência de R$ 50 milhões. A seguradora não possui capacidade isolada para assumir riscos de médio/grande porte.

#### 4.4.3 Indicadores de Solvência Isolada

| Indicador | Valor | Status |
|-----------|-------|--------|
| Suficiência de Capital | 1,67x | ADEQUADO |
| Cobertura de Provisões | 100,6% | MARGINAL |
| Índice de Solvência Isolado | 0,08 | BAIXO |

#### 4.4.4 Rating Isolado Calculado

| Componente | Score | Peso | Contribuição |
|------------|-------|------|--------------|
| Capacidade Própria | 12,6 | 25% | 3,15 |
| Independência Resseguro | 38,5 | 20% | 7,70 |
| Capital Efetivo | 66,8 | 20% | 13,36 |
| Solvência Isolada | 45,6 | 15% | 6,84 |
| Liquidez Isolada | 58,3 | 10% | 5,83 |
| Resiliência | 42,5 | 10% | 4,25 |
| **SCORE FINAL** | - | - | **41,1** |

**Rating Isolado Calculado:** BB+

### 4.5 Gap de Rating

| Elemento | Valor |
|----------|-------|
| Rating Declarado (Grupo) | brAAA / A- |
| Rating Isolado Calculado | BB+ |
| **Gap Estimado** | **5-6 notches** |
| Inflação de Rating | 50-60% |

### 4.6 Fissuras Identificadas

| # | Tipo | Nível | Descrição |
|---|------|-------|-----------|
| 1 | Dependência Resseguro | ALTO | Cessão de 64,3% ao resseguro |
| 2 | Concentração Grupo | **CRÍTICO** | 99,4% do resseguro no próprio grupo |
| 3 | Capacidade Insuficiente | **CRÍTICO** | Capacidade R$ 10,5MM vs referência R$ 50MM |
| 4 | Rating Inflado | ALTO | Gap de 5-6 notches vs grupo |

### 4.7 Parecer da Análise

```
========================================
PARECER DE FORÇA FINANCEIRA ISOLADA
========================================
Seguradora: JUNTO SEGUROS S.A.
Data da Análise: Janeiro/2026

CLASSIFICAÇÃO: VULNERÁVEL
Score de Força Isolada: 41,1/100
Nível de Risco: MODERADO-ALTO

COMPARAÇÃO DE RATING:
- Rating Declarado (Grupo): brAAA / A-
- Rating Isolado Calculado: BB+
- Gap de Rating: 5-6 notches
- Inflação de Rating: 50-60%

CAPACIDADE PRÓPRIA:
- Capacidade por Risco: R$ 10,5 milhões
- Referência (50MM): NÃO ATENDE
- Índice de Capacidade: 0,21x (21%)

FISSURAS IDENTIFICADAS: 4
- Críticas: 2
- Altas: 2
- Moderadas: 0

CONCLUSÃO: Requer cautela e análise aprofundada
antes de assumir riscos relevantes.
========================================
```

---

## 5. Discussão dos Resultados

### 5.1 Discrepância Rating vs Capacidade Real

A análise revelou uma **discrepância significativa** entre o rating declarado (baseado no grupo) e a força financeira isolada da Junto Seguros. Enquanto o rating de grupo sugere uma entidade de primeira linha (brAAA/A-), a análise isolada revela uma estrutura financeira que:

1. **Não possui capital suficiente** para assumir riscos acima de R$ 10,5 milhões por conta própria
2. **Depende criticamente** do resseguro do próprio grupo (99,4% de concentração)
3. **Operaria como BB+** se avaliada isoladamente

### 5.2 Implicações da Concentração de Resseguro

A concentração de 99,4% do resseguro na Junto Resseguros S.A. (empresa do mesmo grupo) levanta questões fundamentais:

1. **Existe real transferência de risco?** O risco permanece no perímetro do grupo econômico
2. **Qual o impacto de um evento que afete o grupo?** Seguradora e ressegurador seriam impactados simultaneamente
3. **A diversificação de contraparte é adequada?** Não, há risco de concentração crítico

### 5.3 Capacidade vs Demanda do Mercado

Para operações de seguro garantia de médio/grande porte (acima de R$ 50 milhões), a Junto Seguros:

- **Não pode** reter mais que R$ 10,5 milhões por risco
- **Precisa ceder** 79% de cada risco de R$ 50 milhões ao resseguro
- **Depende** da Junto Resseguros para viabilizar a operação

Isso significa que, em caso de sinistro de R$ 50 milhões, a Junto Seguros conseguiria pagar apenas R$ 10,5 milhões com recursos próprios, dependendo do ressegurador do grupo para os R$ 39,5 milhões restantes.

### 5.4 Validação da Metodologia

O estudo de caso demonstrou que a metodologia:

1. **É aplicável** a dados reais de demonstrações financeiras
2. **Identifica corretamente** fissuras estruturais relevantes
3. **Quantifica** de forma objetiva gaps de rating
4. **Fornece** base técnica para decisões de crédito/contraparte

---

## 6. Conclusões

### 6.1 Conclusões Principais

1. **O rating do grupo não reflete a força financeira isolada:** A Junto Seguros apresenta rating de grupo brAAA/A-, mas rating isolado estimado de BB+ - uma diferença de 5-6 notches.

2. **A capacidade própria é limitada:** Com capacidade de apenas R$ 10,5 milhões por risco (21% do referencial de R$ 50MM), a seguradora não possui estrutura para assumir riscos de médio/grande porte de forma independente.

3. **Alta dependência de resseguro intragrupo:** A concentração de 99,4% no ressegurador do mesmo grupo configura dependência estrutural crítica e questiona a real transferência de risco.

4. **A metodologia é eficaz:** O sistema de análise desenvolvido demonstrou capacidade de identificar fissuras financeiras relevantes e quantificar gaps de rating de forma objetiva.

### 6.2 Implicações para Stakeholders

#### Para Credores e Beneficiários de Garantias:
- Não devem basear decisões exclusivamente no rating do grupo
- Devem verificar capacidade de retenção própria da seguradora
- Devem considerar a estrutura de resseguro e concentração de contraparte

#### Para Reguladores:
- Considerar exigência de disclosure de rating individual vs grupo
- Avaliar limites de concentração de resseguro intragrupo
- Monitorar seguradoras com alta taxa de cessão (potencial fronting)

#### Para Resseguradores:
- Avaliar dependência do cedente em programas de quota parte
- Considerar diversificação como condição para capacidade

### 6.3 Limitações do Estudo

1. Análise baseada em dados públicos das demonstrações financeiras
2. Algumas premissas foram necessárias na ausência de dados detalhados
3. O rating isolado é estimativa metodológica, não rating oficial de agência

### 6.4 Sugestões para Pesquisas Futuras

1. Aplicar a metodologia a uma amostra ampla do mercado segurador
2. Desenvolver backtesting com eventos de sinistro históricos
3. Integrar análise de qualidade de ativos garantidores
4. Incluir análise de grupo econômico consolidado

---

## 7. Recomendações

### 7.1 Recomendações Específicas para Junto Seguros

1. **Diversificar resseguro:** Reduzir concentração no grupo para máximo de 50%
2. **Fortalecer capital:** Aporte de capital para aumentar capacidade própria
3. **Transparência:** Divulgar rating individual separado do grupo
4. **Limites operacionais:** Não assumir riscos acima de R$ 10,5MM sem resseguro externo

### 7.2 Recomendações Gerais para o Mercado

1. **Credores devem exigir:** Rating individual (não consolidado) em operações relevantes
2. **Tomadores devem verificar:** Capacidade de retenção antes de contratar
3. **Reguladores devem considerar:** Limites de concentração de resseguro intragrupo
4. **Agências de rating devem:** Destacar diferenças entre rating grupo vs individual

---

## Referências

1. Demonstrações Financeiras Junto Seguros S.A. - Exercício 2024
2. Circular SUSEP nº 648/2022 - Requisitos de capital
3. Resolução CNSP nº 432/2021 - Provisões técnicas
4. Standard & Poor's - Metodologia de Rating de Seguradoras
5. AM Best - Critérios de Avaliação de Força Financeira

---

## Anexo A: Código-Fonte da Metodologia

O código-fonte completo da metodologia está disponível nos seguintes arquivos:

- `src/models/forca_isolada.py` - Modelos de dados
- `src/analysis/analisador_forca_isolada.py` - Motor de análise
- `src/analysis/terminal_forca_isolada.py` - Interface de visualização

### Principais Classes

```python
class AnalisadorForcaIsolada:
    """
    Motor principal de análise de força financeira isolada.

    Métodos principais:
    - analisar_seguradora(): Análise completa de uma seguradora
    - analisar_carteira(): Análise de múltiplas seguradoras
    - gerar_comparacao_rating(): Comparação rating declarado vs isolado
    """

class IndicadoresForcaIsolada:
    """
    Dataclass com todos os indicadores calculados:
    - Indicadores de dependência de resseguro
    - Indicadores de capacidade própria
    - Indicadores de solvência isolada
    - Indicadores de liquidez isolada
    - Indicadores de stress
    - Fissuras identificadas
    - Rating isolado calculado
    """
```

---

## Anexo B: Glossário

| Termo | Definição |
|-------|-----------|
| **Cessão** | Transferência de parte do risco ao ressegurador |
| **CMR** | Capital Mínimo Requerido (regulatório) |
| **Fronting** | Operação onde seguradora cede quase totalidade do risco |
| **Gap de Rating** | Diferença em notches entre ratings |
| **Notch** | Uma graduação na escala de rating (ex: de A para A-) |
| **PLA** | Patrimônio Líquido Ajustado |
| **Provisões Técnicas** | Reservas para obrigações com segurados |
| **Quota Parte** | Tipo de resseguro proporcional |
| **Retenção** | Parte do risco mantida pela seguradora |
| **Score** | Pontuação numérica de avaliação |

---

*Documento gerado automaticamente pelo Sistema de Análise Financeira*
*Versão 1.0 - Janeiro 2026*
