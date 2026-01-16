# PESQUISA PROFUNDA: ESCALA NACIONAL vs. RATING EMITIDO NO PAÍS

## E a Distinção entre Rating de Grupo por Atividade

---

## 1. A QUESTÃO CENTRAL: "ESCALA NACIONAL" vs. "RATING EMITIDO NO PAÍS"

### 1.1 Definições Técnicas

| Termo | Definição | Exemplo |
|-------|-----------|---------|
| **Escala Nacional** | Sistema de classificação que compara entidades DENTRO de um único país, usando o ambiente macroeconômico local como referência | brAAA (S&P), AAA(bra) (Fitch), Aaa.br (Moody's) |
| **Rating Emitido no País** | Classificação feita por agência com operação local, independente da escala utilizada | S&P Brasil emitindo rating para empresa local |
| **Escala Global** | Sistema de classificação que compara entidades de QUALQUER país usando critérios uniformes | AAA, AA+, AA, AA-... |

### 1.2 Por que a Confusão Existe

A confusão surge porque os termos se sobrepõem parcialmente:

```
┌─────────────────────────────────────────────────────────────┐
│                    RATINGS DE CRÉDITO                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌───────────────────┐    ┌───────────────────┐           │
│   │  ESCALA GLOBAL    │    │  ESCALA NACIONAL  │           │
│   │   (AAA, AA, A)    │    │  (brAAA, brAA)    │           │
│   │                   │    │                   │           │
│   │  Emitido por:     │    │  Emitido por:     │           │
│   │  - S&P Global     │    │  - S&P Brasil     │           │
│   │  - Fitch Global   │    │  - Fitch Brasil   │           │
│   │  - Moody's Global │    │  - Moody's Local  │           │
│   └───────────────────┘    └───────────────────┘           │
│                                                             │
│   NOTA: A mesma agência pode emitir ambos os tipos         │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 O que Editais Tipicamente Dizem

Cláusula comum:
> "Seguradora que possua rating igual ou superior a brAAA em escala nacional, atribuído por agência de classificação de risco"

**Interpretações possíveis**:

| Interpretação | Leitura | Consequência |
|---------------|---------|--------------|
| **RESTRITIVA** | "Rating [que seja brAAA] [em escala nacional]" | Só aceita brAAA ou equivalente Fitch/Moody's nacional |
| **FINALÍSTICA** | "Rating [igual ou superior a brAAA] [comparável em escala nacional]" | Aceita qualquer rating que seja igual ou superior ao benchmark brAAA |

### 1.4 Por que a Interpretação Finalística é Correta

#### Argumento 1: A expressão "IGUAL OU SUPERIOR"

Se brAAA é o teto máximo da escala nacional:
- "Igual a brAAA" → possível dentro da escala
- "Superior a brAAA" → **IMPOSSÍVEL** dentro da escala nacional

Conclusão: A expressão só faz sentido se admitir ratings fora da escala.

#### Argumento 2: Metodologia das Agências

A S&P e Fitch publicam metodologias que explicam:

> "A escala nacional permite comparação entre entidades dentro do mesmo ambiente de risco soberano. A escala global permite comparação entre entidades de diferentes regiões e indústrias."
>
> — S&P Global Ratings

Implicação: São sistemas COMPARÁVEIS, não sistemas fechados incompatíveis.

#### Argumento 3: Tabelas de Mapeamento

As próprias agências publicam tabelas de equivalência:

| Escala Nacional Brasil | Equivalente Global Aproximado |
|------------------------|------------------------------|
| brAAA | BB a BB+ |
| brAA+ | BB- a B+ |
| brAA | B+ a B |
| brAA- | B |
| brA+ | B- |

Fonte: S&P Global Ratings Definitions

Portanto: AA global >> brAAA nacional (diferença de 7-10 notches)

#### Argumento 4: Propósito da Exigência

O objetivo de exigir rating em licitação é garantir **força financeira**.

Se uma seguradora com AA global (capacidade "muito forte") for rejeitada em favor de uma com brAAA (capacidade "forte apenas no contexto brasileiro"), o propósito é **frustrado**.

---

## 2. RATING DE GRUPO: MESMA ATIVIDADE vs. DIVERSIFICADO

### 2.1 Conceitos Fundamentais

#### Grupo de Mesma Atividade (Pure-Play Group)

```
ZURICH INSURANCE GROUP LTD (Holding - Seguros)
├── Zurich Insurance Company Ltd (Seguros - Principal)
├── Zurich American Insurance Co. (Seguros - EUA)
├── Zurich Insurance Europe AG (Seguros - Europa)
├── Zurich Minas Brasil Seguros S.A. (Seguros - Brasil)
└── [Outras subsidiárias de seguros]

ATIVIDADE: 100% seguros e resseguros
```

#### Grupo Diversificado (Conglomerado)

```
CONGLOMERADO FINANCEIRO HIPOTÉTICO
├── Banco ABC S.A. (Bancário)
├── Seguradora XYZ S.A. (Seguros)
├── Administradora de Cartões (Serviços)
├── Corretora de Valores (Investimentos)
└── Resseguradora QRS S.A. (Resseguros)

ATIVIDADE: Múltiplas (banco, seguros, resseguros, serviços)
```

### 2.2 Tratamento de Rating

#### Para Grupos de Mesma Atividade

A S&P estabelece:

> "Para subsidiárias 'core' de grupos seguradores, o rating reflete a capacidade integrada do grupo de cumprir obrigações de seguros. Subsidiárias operacionais são avaliadas como extensões do grupo, não como entidades independentes."

Implicação: O rating AA do Zurich Insurance Group se APLICA diretamente às operações de seguro, incluindo subsidiárias como Zurich Brasil.

#### Para Grupos Diversificados

A metodologia é diferente:

> "Em conglomerados diversificados, cada linha de negócio pode receber tratamento diferenciado. A subsidiária seguradora pode ter rating 'notched' (ajustado) em relação ao grupo, dependendo de sua importância estratégica e integração."

Implicação: Uma seguradora dentro de um banco pode ter rating diferente do rating do banco.

### 2.3 Relevância para Licitações

| Tipo de Grupo | Rating da Subsidiária | Confiabilidade |
|---------------|----------------------|----------------|
| Mesma atividade (Zurich) | Equalizado ao grupo | Alta - rating reflete capacidade seguradora real |
| Diversificado | Pode ser diferenciado | Média - depende da análise específica |

### 2.4 Por que Isso Importa para Zurich vs. Junto

**ZURICH**:
- Grupo de MESMA ATIVIDADE (100% seguros)
- Rating AA aplicável diretamente a operações de seguro garantia
- Subsidiária brasileira é extensão operacional, não entidade autônoma
- Suporte do grupo é VIRTUALMENTE CERTO para obrigações de seguros

**JUNTO**:
- Empresa INDEPENDENTE (sem grupo controlador)
- Rating brAAA reflete capacidade PRÓPRIA
- Não há dependência de suporte externo
- Força é o que se vê nas demonstrações financeiras

---

## 3. ANÁLISE: ZURICH BRASIL

### 3.1 Estrutura Corporativa

```
Zurich Insurance Group Ltd (Suíça)
│
├── Patrimônio Global: ~CHF 36 bilhões (~R$ 231 bilhões)
├── Rating: AA (S&P), Aa2 (Moody's), AA (Fitch), A+ (AM Best)
│
└── Zurich Minas Brasil Seguros S.A.
    ├── CNPJ: 17.197.385/0001-21
    ├── Autorização SUSEP: 05495
    ├── Patrimônio Líquido: ~R$ 850 milhões
    ├── Classificação S&P: Subsidiária CORE
    └── Rating aplicável: AA (do grupo)
```

### 3.2 Por que Não Há Rating Isolado Publicado

A S&P explica:

> "Para subsidiárias 'core', não publicamos Stand-Alone Credit Profile (SACP) separado porque:
> 1. O suporte do grupo é considerado virtualmente certo
> 2. Avaliar isoladamente SUBESTIMARIA a capacidade real
> 3. O rating do grupo é mais representativo da força financeira disponível"

### 3.3 O que Significa "Rating Emprestado"

Críticos argumentam que o rating da Zurich Brasil é "emprestado" do grupo. Análise:

| Aspecto | "Emprestado" (crítica) | Realidade (metodologia) |
|---------|------------------------|-------------------------|
| Natureza | Artifício contábil | Reflexo de estrutura real de suporte |
| Fundamento | Sem base jurídica | Baseado em análise de probabilidade de suporte |
| Exigibilidade | Não garantido | Garantido pela estrutura societária e histórico |
| Histórico | Pode falhar | Grupos resgatam subsidiárias para proteger reputação |

### 3.4 GAP entre Rating Declarado e Isolado

**Estimativa** (não publicada oficialmente):
- Rating do Grupo: AA
- SACP estimado da Zurich Brasil: ~A (3 notches abaixo)
- GAP: ~3 notches

**Interpretação**: A Zurich Brasil, se avaliada ISOLADAMENTE, teria rating mais baixo. Mas isso é IRRELEVANTE para fins práticos, pois:
1. O suporte do grupo É disponível
2. As agências INCORPORAM o suporte na análise
3. O rating AA É o rating aplicável

---

## 4. ANÁLISE: JUNTO SEGUROS

### 4.1 Estrutura Corporativa

```
Junto Seguros S.A. (Brasil - Independente)
│
├── Tipo: Seguradora nacional independente
├── Especialização: Seguro garantia
├── Patrimônio Líquido: ~R$ 650 milhões
├── Rating S&P: brAAA (stable)
├── Rating Fitch: AAA(bra) (stable)
│
└── Junto Resseguros S.A.
    └── Rating S&P: brAAA (stable)
```

### 4.2 Características Distintivas

1. **Sem controlador estrangeiro**: Acionistas são brasileiros
2. **Rating próprio**: brAAA reflete capacidade ISOLADA
3. **Especialização**: Foco em seguro garantia (expertise)
4. **Consistência**: Rating declarado = Rating isolado (GAP = 0)

### 4.3 Força e Limitações

**Forças**:
- Transparência: o que se vê é o que há
- Especialização: conhecimento profundo do segmento
- Independência: decisões locais, sem burocracia de grupo
- Consistência: sem dependência de suporte externo

**Limitações**:
- Escala: patrimônio menor que subsidiárias de grupos globais
- Teto: rating limitado ao teto soberano brasileiro
- Capacidade: menor capacidade de absorver sinistros catastróficos

---

## 5. COMPARATIVO CONSOLIDADO

### 5.1 Tabela Comparativa

| Critério | Zurich Brasil | Junto Seguros |
|----------|---------------|---------------|
| **Tipo** | Subsidiária de grupo global | Nacional independente |
| **Rating declarado** | AA (global) | brAAA (nacional) |
| **Rating isolado** | ~A (estimado) | brAAA |
| **GAP** | ~3 notches | 0 |
| **Patrimônio próprio** | ~R$ 850 milhões | ~R$ 650 milhões |
| **Suporte disponível** | ~R$ 231 bilhões | R$ 0 |
| **Dependência externa** | Alta | Nenhuma |
| **Probabilidade default** | ~0.03% (AA) | ~1-2% (BB equiv.) |
| **Escala de operação** | Global | Nacional |
| **Especialização** | Múltiplas linhas | Seguro garantia |

### 5.2 Análise de Risco

**Para o Estado (licitante)**:

| Risco | Zurich | Junto |
|-------|--------|-------|
| Default por insolvência | Muito baixo | Baixo |
| Demora na regulação | Pode haver burocracia de grupo | Decisão local ágil |
| Conflito de interesses | Possível (prioridades globais) | Menor (foco local) |
| Capacidade para grandes sinistros | Muito alta (grupo) | Limitada (capital próprio) |
| Transparência | Complexa (estrutura de grupo) | Alta (demonstrações claras) |

### 5.3 Conclusão da Análise

**Ambas são elegíveis** para licitações que exijam rating brAAA ou superior:

- **ZURICH**: Atende por superioridade matemática (AA > brAAA)
- **JUNTO**: Atende por equivalência direta (brAAA = brAAA)

**A escolha depende do critério do gestor**:

| Se prioriza | Melhor opção |
|-------------|--------------|
| Maior capacidade de pagamento global | Zurich |
| Maior transparência e consistência | Junto |
| Menor probabilidade estatística de default | Zurich |
| Maior agilidade e foco local | Junto |

---

## 6. SÍNTESE PARA ARGUMENTAÇÃO

### 6.1 Argumento: "Rating em escala nacional"

**TESE**: A expressão "em escala nacional" define o parâmetro de comparação, não restringe a origem do rating.

**PROVA**:
1. "Igual ou superior" implica ratings além do teto nacional
2. Agências publicam equivalências entre escalas
3. O propósito é garantir força financeira, não origem geográfica

### 6.2 Argumento: "Rating de grupo"

**TESE**: Rating de grupo de mesma atividade é diretamente aplicável a subsidiárias de seguros.

**PROVA**:
1. Metodologia S&P classifica subsidiárias como "core"
2. Suporte é considerado virtualmente certo
3. O rating representa capacidade REAL disponível

### 6.3 Argumento: "Zurich vs. Junto"

**TESE**: Ambas são elegíveis, por caminhos diferentes.

**PROVA**:
1. Zurich: AA global > brAAA (superioridade matemática)
2. Junto: brAAA = brAAA (equivalência direta)
3. O edital aceita ambos os modelos

---

## FONTES

1. **S&P Global Ratings Definitions** - https://www.spglobal.com/ratings/en
2. **S&P Group Rating Methodology (July 2019)** - Documento oficial
3. **Fitch - Parent and Subsidiary Linkage Criteria**
4. **Zurich Insurance - Investor Relations** - https://www.zurich.com/investor-relations/ratings
5. **XP Research - Guia de Rating** - https://conteudos.xpi.com.br/renda-fixa/relatorios/guia-de-rating/
6. **SUSEP** - https://www.gov.br/susep/pt-br

---

*Pesquisa elaborada em: 2026-01-16*
*Para uso em argumentação jurídica e técnica*
