# Análise Financeira - Crédito de Garantia

Sistema para análise comparativa da força financeira de seguradoras, gerando relatórios detalhados com indicadores de solvência, liquidez, rentabilidade e sinistralidade.

## Funcionalidades

- **Análise de Indicadores Financeiros**: Calcula automaticamente indicadores de solvência, liquidez, rentabilidade, sinistralidade e estrutura de capital
- **Score de Força Financeira**: Sistema de pontuação de 0 a 100 que avalia a saúde financeira geral
- **Rating de Risco**: Classificação de AAA (excelente) a D (inadimplente)
- **Comparação entre Seguradoras**: Rankings por categoria e análise comparativa completa
- **Relatórios em Múltiplos Formatos**: HTML interativo, Excel e PDF
- **Análise de Pontos Fortes e Fracos**: Identificação automática de áreas de destaque e atenção

## Estrutura do Projeto

```
.
├── main.py                          # Script principal
├── requirements.txt                 # Dependências
├── README.md                        # Documentação
├── output/                          # Relatórios gerados
└── src/
    ├── models/
    │   └── seguradora.py            # Modelos de dados
    ├── analysis/
    │   ├── indicadores.py           # Cálculo de indicadores
    │   └── comparador.py            # Comparação entre seguradoras
    ├── reports/
    │   └── gerador_relatorios.py    # Geração de relatórios
    └── data/
        └── dados_exemplo.py         # Dados de exemplo
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

## Licença

MIT License
