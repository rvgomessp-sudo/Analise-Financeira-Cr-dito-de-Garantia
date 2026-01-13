# Análise Financeira - Crédito de Garantia

Sistema completo para análise financeira de seguradoras e **análise jurídica de licitações**, com foco em:
- Análise comparativa da força financeira de seguradoras
- Cruzamento de dados entre editais, Lei 14.133/2021 e jurisprudência do TCU
- Identificação de irregularidades em processos licitatórios
- Geração de notificações jurídicas e representações

## Funcionalidades

### Módulo de Análise Financeira
- **Análise de Indicadores Financeiros**: Calcula automaticamente indicadores de solvência, liquidez, rentabilidade, sinistralidade e estrutura de capital
- **Score de Força Financeira**: Sistema de pontuação de 0 a 100 que avalia a saúde financeira geral
- **Rating de Risco**: Classificação de AAA (excelente) a D (inadimplente)
- **Comparação entre Seguradoras**: Rankings por categoria e análise comparativa completa
- **Relatórios em Múltiplos Formatos**: HTML interativo, Excel e PDF
- **Análise de Pontos Fortes e Fracos**: Identificação automática de áreas de destaque e atenção

### Módulo de Análise Jurídica (NOVO)
- **Base Legal Lei 14.133/2021**: Artigos sobre garantias, habilitação, qualificação econômica
- **Jurisprudência TCU**: Acórdãos, súmulas e boas práticas sobre licitações
- **Análise de Irregularidades**: Identificação automática de não-conformidades
- **Cruzamento de Dados**: Edital x Lei x TCU x Estudos de Rating
- **Gerador de Notificações**: Notificações de irregularidades, representações ao TCE, pareceres jurídicos

## Estrutura do Projeto

```
.
├── main.py                          # Script principal (análise financeira)
├── terminal_app.py                  # Aplicação interativa financeira
├── analise_juridica_cc17.py         # Sistema de Análise Jurídica CC17/2025
├── requirements.txt                 # Dependências
├── README.md                        # Documentação
├── output/                          # Relatórios gerados
└── src/
    ├── models/
    │   └── seguradora.py            # Modelos de dados financeiros
    ├── analysis/
    │   ├── indicadores.py           # Cálculo de indicadores
    │   └── comparador.py            # Comparação entre seguradoras
    ├── reports/
    │   └── gerador_relatorios.py    # Geração de relatórios
    ├── data/
    │   └── dados_exemplo.py         # Dados de exemplo
    └── juridico/                    # MÓDULO JURÍDICO (NOVO)
        ├── __init__.py              # Inicialização do módulo
        ├── base_legal.py            # Lei 14.133/2021 - artigos relevantes
        ├── referencias_tcu.py       # Acórdãos, súmulas e boas práticas TCU
        ├── analisador_irregularidades.py  # Análise de irregularidades
        ├── cruzamento_dados.py      # Motor de cruzamento de dados
        └── gerador_notificacao.py   # Gerador de documentos jurídicos
```

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd Analise-Financeira-Cr-dito-de-Garantia

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Uso

### Linha de Comando

```bash
# Gera relatório completo com dados de exemplo
python main.py

# Especifica pasta de saída
python main.py --output minha_pasta

# Gera apenas em formato específico
python main.py --formato html
python main.py --formato excel

# Exibe apenas resumo no terminal
python main.py --resumo

# Gera relatórios individuais para cada seguradora
python main.py --individual
```

### Análise Jurídica (CC17/2025 - SEAP Manaus)

```bash
# Executa o sistema de análise jurídica interativo
python analise_juridica_cc17.py
```

O sistema oferece:
1. **Visualização de Dados**: Edital, estudo de rating, seguradoras
2. **Consulta à Base Legal**: Lei 14.133/2021 por categoria
3. **Consulta ao TCU**: Acórdãos, súmulas e boas práticas
4. **Análise Completa**: Cruzamento de dados e identificação de irregularidades
5. **Geração de Documentos**: Notificações, representações e pareceres

### Uso Programático

```python
from src.models.seguradora import Seguradora, BalancoPatrimonial, DRE
from src.analysis.indicadores import AnalisadorIndicadores
from src.analysis.comparador import ComparadorSeguradora
from src.reports.gerador_relatorios import GeradorRelatorios
from datetime import date

# Cria uma seguradora
seguradora = Seguradora(
    codigo_susep="12345",
    nome="Minha Seguradora S.A.",
    cnpj="11.222.333/0001-44",
    ano_exercicio=2024,
    balanco=BalancoPatrimonial(
        disponibilidades=30_000_000,
        aplicacoes_financeiras_cp=150_000_000,
        # ... outros campos
    ),
    dre=DRE(
        premios_emitidos=200_000_000,
        sinistros_ocorridos=-81_000_000,
        # ... outros campos
    )
)

# Calcula indicadores
analisador = AnalisadorIndicadores()
indicadores = analisador.calcular_indicadores(seguradora)

print(f"Score: {indicadores.score_forca_financeira}")
print(f"Rating: {indicadores.classificacao_risco}")
print(f"ROE: {indicadores.roe:.1%}")
```

### Uso do Módulo Jurídico

```python
from src.juridico.cruzamento_dados import MotorCruzamento, DadosEdital, DadosRating
from src.juridico.gerador_notificacao import GeradorNotificacao, Destinatario

# Criar motor de cruzamento
motor = MotorCruzamento()

# Configurar dados do edital
dados_edital = DadosEdital(
    numero="CC17/2025",
    processo="CC17/2025 - CSC",
    objeto="Contratação de Seguro-Garantia",
    valor_estimado=50_000_000.00,
    # ... outros campos
)

# Executar análise completa
resultado = motor.executar_analise_completa(dados_edital, dados_rating)

# Gerar notificação
gerador = GeradorNotificacao()
notificacao = gerador.gerar_notificacao_irregularidades(
    resultado_cruzamento=resultado,
    irregularidades=resultado.irregularidades_encontradas,
    destinatarios=[Destinatario(nome="...", cargo="...", orgao="...")],
    notificante="Empresa XYZ",
    qualificacao_notificante="participante do certame"
)
```

## Indicadores Calculados

### Solvência
- **Índice de Solvência**: PL / Passivo Exigível
- **Cobertura de Provisões**: Ativos Garantidores / Provisões Técnicas
- **Margem de Solvência**: PLA - Capital Mínimo Requerido

### Liquidez
- **Liquidez Corrente**: AC / PC
- **Liquidez Seca**: (AC - Prêmios a Receber) / PC
- **Liquidez Imediata**: (Disponibilidades + Aplicações CP) / PC

### Rentabilidade
- **ROE**: Lucro Líquido / Patrimônio Líquido
- **ROA**: Lucro Líquido / Ativo Total
- **Margem Líquida**: Lucro Líquido / Prêmios Ganhos
- **Margem Operacional**: Resultado Técnico / Prêmios Ganhos

### Sinistralidade
- **Índice de Sinistralidade**: Sinistros / Prêmios Ganhos
- **Índice de Despesas**: (Custos Aquisição + Despesas Adm) / Prêmios
- **Índice Combinado**: Sinistralidade + Índice de Despesas
- **Índice Combinado Ampliado**: Combinado - Resultado Financeiro/Prêmios

### Estrutura
- **Endividamento**: Passivo Exigível / Ativo Total
- **Imobilização do PL**: (Imobilizado + Intangível) / PL
- **Alavancagem**: Prêmios Emitidos / PL

## Sistema de Rating

| Score | Rating | Classificação |
|-------|--------|---------------|
| 90-100 | AAA | Excepcional |
| 80-89 | AA | Muito Forte |
| 70-79 | A | Forte |
| 60-69 | BBB | Adequado |
| 50-59 | BB | Menos Vulnerável |
| 40-49 | B | Mais Vulnerável |
| 30-39 | CCC | Vulnerável |
| 20-29 | CC | Altamente Vulnerável |
| 10-19 | C | Falência Iminente |
| 0-9 | D | Inadimplente |

## Relatórios Gerados

### HTML
- Relatório interativo com gráficos
- Rankings por categoria
- Matriz comparativa
- Análise individual de cada seguradora

### Excel
- Múltiplas abas com dados detalhados
- Resumo executivo
- Rankings específicos por indicador
- Análise de pontos fortes/fracos

### PDF
- Versão para impressão do relatório HTML
- Requer WeasyPrint ou pdfkit instalados

## Exemplos de Saída

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RESUMO EXECUTIVO - ANÁLISE COMPARATIVA                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 VISÃO GERAL DO SETOR ANALISADO
────────────────────────────────────────────────────────────────────────────────
• Total de Seguradoras Analisadas: 6
• Ativo Total do Setor: R$ 4,325.00 milhões
• Patrimônio Líquido Total: R$ 2,475.00 milhões

🏆 RANKING DE FORÇA FINANCEIRA
────────────────────────────────────────────────────────────────────────────────
  1º - Alpha Garantias S.A.: Score 87.5 (Rating AA)
  2º - Zeta Crédito Garantido S.A.: Score 82.3 (Rating AA)
  3º - Beta Crédito S.A.: Score 73.8 (Rating A)
```

## Módulo Jurídico - Análise de Licitações

### Funcionalidades Principais

1. **Base Legal (Lei 14.133/2021)**
   - Artigos sobre garantias (Arts. 96-102)
   - Habilitação e qualificação (Arts. 62-72)
   - Sanções e penalidades (Arts. 155-156)
   - Princípios norteadores (Art. 5º, 11)

2. **Jurisprudência TCU**
   - Acórdãos sobre seguro-garantia
   - Acórdãos sobre rating e solidez financeira
   - Súmulas aplicáveis
   - Boas práticas em contratações

3. **Tipos de Irregularidades Detectadas**
   - Omissão de documentos obrigatórios
   - Garantia contratual inadequada
   - Descarte de melhor rating por custo
   - Viés financeiro na seleção
   - Risco regulatório e jurídico
   - Violação de princípios licitatórios

4. **Documentos Jurídicos Gerados**
   - Notificação de Irregularidades
   - Representação ao TCE
   - Parecer Jurídico
   - Relatório de Análise

### Caso de Uso: CC17/2025 - SEAP/AM

O sistema foi desenvolvido para análise do certame CC17/2025 da SEAP Manaus,
identificando irregularidades na seleção de seguradora para garantia contratual
com base em estudos de rating financeiro.

**Principais Irregularidades Identificadas:**
- Descarte de seguradora com rating superior (AA) em favor de outra com rating inferior (BBB+)
- Seleção baseada exclusivamente em menor preço
- Desconsideração de estudo técnico de rating
- Exposição do Estado a risco regulatório

## Licença

MIT License
