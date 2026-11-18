#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estudo de rating e capacidade: Zurich Minas Brasil x Junto Seguros
Certame CC17/2025 - CSC/SEAP Amazonas (cogestão prisional)

Roda sem dependências externas (Python 3.8+), inclusive no Google Colab.
Gera o relatório no terminal e o arquivo dados_analise_completa_cc17_2025.json.
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Dict, List, Optional, Tuple

# =============================================================================
# 1. TABELA OFICIAL DE CONVERSÃO S&P (escala global -> escala nacional Brasil)
# Fonte: S&P Global Ratings, "National And Regional Scale Credit Ratings
# Methodology", 19/12/2023, Tabela 3 - Brazil mapping specification, p. 3.
# =============================================================================

ESCALA_GLOBAL_SP = [
    "AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-",
    "BB+", "BB", "BB-", "B+", "B", "B-", "CCC+", "CCC", "CCC-", "CC", "C",
]

TABELA_3_SP_BRASIL_2023: List[Tuple[str, List[str]]] = [
    ("BB+ e acima", ["brAAA"]),
    ("BB", ["brAAA", "brAA+"]),
    ("BB-", ["brAA+", "brAA"]),
    ("B+", ["brAA", "brAA-", "brA+"]),
    ("B", ["brA+", "brA", "brA-"]),
    ("B-", ["brBBB+", "brBBB", "brBBB-", "brBB+"]),
    ("CCC+", ["brBB+", "brBB", "brBB-"]),
    ("CCC", ["brB+", "brB", "brB-"]),
    ("CCC-", ["brCCC+", "brCCC", "brCCC-"]),
    ("CC", ["brCC"]),
    ("C", ["brC"]),
]

# Versão anterior (S&P, 25/06/2018, Tabela 3): "BB e acima -> brAAA".
LIMIAR_BRAAA_2018 = "BB"
LIMIAR_BRAAA_2023 = "BB+"


def posicao(rating_global: str) -> int:
    """Quanto menor, melhor (AAA = 0)."""
    return ESCALA_GLOBAL_SP.index(rating_global)


def degraus_entre(melhor: str, pior: str) -> int:
    return posicao(pior) - posicao(melhor)


def converter_para_escala_nacional(rating_global: str) -> List[str]:
    """Aplica a Tabela 3 da S&P (dez/2023) a um rating global em moeda local."""
    if posicao(rating_global) <= posicao(LIMIAR_BRAAA_2023):
        return ["brAAA"]
    for faixa, nacionais in TABELA_3_SP_BRASIL_2023[1:]:
        if faixa == rating_global:
            return nacionais
    raise ValueError(f"Rating fora da tabela: {rating_global}")


def atende_braaa(rating_global: str) -> Dict[str, object]:
    nacionais = converter_para_escala_nacional(rating_global)
    return {
        "rating_global": rating_global,
        "escala_nacional_indicativa": nacionais,
        "atende_igual_ou_superior_a_brAAA": nacionais == ["brAAA"],
        "degraus_acima_do_limiar_brAAA": degraus_entre(rating_global, LIMIAR_BRAAA_2023),
    }


# =============================================================================
# 2. DADOS DOCUMENTADOS DAS SEGURADORAS
# Valores em R$ mil, como publicados nas demonstrações financeiras.
# =============================================================================

@dataclass
class Fonte:
    documento: str
    localizacao: str


@dataclass
class Seguradora:
    nome: str
    cnpj: str
    codigo_susep: Optional[str]
    controlador: str
    participacao_controlador: str
    data_base: str
    patrimonio_liquido: float
    pla: float
    capital_minimo_requerido: float
    ativos_garantidores: Optional[float]
    ratings: Dict[str, str]
    rating_global_sp_aplicavel: Optional[str]
    fontes: List[Fonte] = field(default_factory=list)

    @property
    def suficiencia_capital(self) -> float:
        return self.pla - self.capital_minimo_requerido

    @property
    def indice_solvencia(self) -> float:
        return self.pla / self.capital_minimo_requerido


ZURICH_MINAS = Seguradora(
    nome="Zurich Minas Brasil Seguros S.A.",
    cnpj="17.197.385/0001-21",
    codigo_susep="05495",
    controlador="Zurich Insurance Company Ltd (Suíça)",
    participacao_controlador="99,9999% (0,0001% Zurich Life Insurance Company Ltd)",
    data_base="30/06/2024",
    patrimonio_liquido=2_324_494,
    pla=1_063_478,
    capital_minimo_requerido=679_402,
    ativos_garantidores=2_706_645,
    ratings={
        "S&P (controladora Zurich Insurance Company Ltd)": "AA/estável",
        "Moody's (controladora)": "Aa2/estável",
        "AM Best (controladora)": "A+ (Superior)/estável",
    },
    rating_global_sp_aplicavel="AA",
    fontes=[
        Fonte("DFs intermediárias Zurich Minas Brasil Seguros S.A., 30/06/2024",
              "Nota 1 (acionistas); Nota 20.c (PLA e CMR); quadro de cobertura das provisões técnicas"),
        Fonte("Condições gerais Seguro Garantia Zurich (Circular SUSEP 662/2022)",
              "Qualificação da seguradora: 'devidamente autorizada pela SUSEP sob o código nº 05495'"),
        Fonte("Zurich Insurance Group, Annual results 2024 - Consolidated financial statements",
              "Nota 27, Tabela 27.1, p. 132 (subsidiária significativa, 100% de voto e capital)"),
        Fonte("zurich.com/investor-relations/ratings (capturado em 03/01/2026)",
              "Tabela de ratings de força financeira"),
    ],
)

JUNTO = Seguradora(
    nome="Junto Seguros S.A. (antiga J. Malucelli Seguradora)",
    cnpj="84.948.157/0001-33",
    codigo_susep=None,
    controlador="Junto Holding Brasil S.A. (joint venture Paraná Banco / Travelers 49,5%)",
    participacao_controlador="100% (acionista única)",
    data_base="31/12/2024",
    patrimonio_liquido=271_674,
    pla=294_901,
    capital_minimo_requerido=76_344,
    ativos_garantidores=None,
    ratings={
        "S&P Brasil": "brAAA",
        "AM Best (DFs 2024)": "A- (Excelente)",
        "AM Best (12/11/2026, Junto Re e Junto Seg em conjunto)": "A (Excellent)",
    },
    rating_global_sp_aplicavel=None,
    fontes=[
        Fonte("DFs Junto Seguros S.A. 2024 (publicadas em 28/02/2025)",
              "Relatório da Administração; Nota 21 (suficiência do PLA e capital)"),
        Fonte("AM Best, 12/11/2026 (Business Wire)",
              "Ratings de Junto Re e Junto Seg em conjunto; apoio da controladora Travelers"),
    ],
)


# =============================================================================
# 3. TESE DA RH MULTI E REFUTAÇÕES
# =============================================================================

TESE_RH = (
    "A Zurich não atenderia ao edital porque o rating AA é global e não em "
    "escala nacional, e porque a subsidiária brasileira não tem rating próprio."
)

REFUTACOES = [
    {
        "numero": 1,
        "titulo": "O edital exige uma NOTA na escala nacional, não um rating EMITIDO no Brasil",
        "argumento": (
            "A cláusula pede rating 'igual ou superior a brAAA em escala nacional'. "
            "Ela fixa um patamar de qualidade, medido na régua nacional. Não exige "
            "que a classificação tenha sido emitida por escritório brasileiro nem "
            "que a seguradora tenha relatório nacional próprio."
        ),
        "prova": "Texto da cláusula do edital (conferir redação literal no edital CC17/2025).",
    },
    {
        "numero": 2,
        "titulo": "A própria S&P converte o AA global em brAAA",
        "argumento": (
            "Pela Tabela 3 da metodologia S&P (dez/2023), toda qualidade de crédito "
            "global 'BB+ e acima' corresponde a brAAA. O AA está 8 degraus acima "
            "desse limiar. Convertido pela régua oficial, o AA dá brAAA: atende ao "
            "'igual'. brAAA é o teto da escala: não existe nota nacional superior, "
            "então o 'superior' só pode ser demonstrado pela escala global."
        ),
        "prova": "S&P, National And Regional Scale Credit Ratings Methodology, 19/12/2023, Tabela 3, p. 3.",
    },
    {
        "numero": 3,
        "titulo": "A Zurich Minas é autorizada pela SUSEP e mantém os ativos garantidores no Brasil",
        "argumento": (
            "A Zurich Minas Brasil Seguros S.A. é sociedade anônima brasileira, "
            "autorizada pela SUSEP (código 05495) e opera seguro-garantia sob a "
            "Circular SUSEP 662/2022. Em 30/06/2024 tinha R$ 2,71 bilhões em ativos "
            "oferecidos em garantia das provisões técnicas, majoritariamente títulos "
            "do Tesouro Nacional, com suficiência de R$ 150 milhões. Pela Resolução "
            "CMN 4.993/2022 (Regulamento, art. 4º), só valem como garantidores ativos "
            "registrados ou custodiados em instituições autorizadas pelo BCB ou pela CVM."
        ),
        "prova": "Condições gerais Zurich (código SUSEP 05495); DFs Zurich Minas 30/06/2024; Res. CMN 4.993/2022.",
    },
    {
        "numero": 4,
        "titulo": "A subsidiária é controlada diretamente pela entidade que tem o AA",
        "argumento": (
            "O AA (S&P), Aa2 (Moody's) e A+ (AM Best) são da Zurich Insurance Company "
            "Ltd. Essa mesma empresa detém 99,9999% das ações da Zurich Minas. O "
            "relatório anual do grupo lista a Zurich Minas como subsidiária "
            "significativa, com 100% de voto e capital e capital social de R$ 2,3 "
            "bilhões. Não há intermediário entre a seguradora brasileira e a "
            "entidade classificada."
        ),
        "prova": "DFs Zurich Minas 30/06/2024, Nota 1; Zurich Annual results 2024, Nota 27, Tabela 27.1, p. 132.",
    },
    {
        "numero": 5,
        "titulo": "A Junto também tem rating derivado do grupo: a tese da RH a desqualificaria",
        "argumento": (
            "A Junto descreve seus ratings como 'equivalentes a brAAA'. A AM Best "
            "classifica Junto Seguros e Junto Resseguros em conjunto e atribui a "
            "perspectiva ao 'apoio contínuo da controladora, The Travelers Companies'. "
            "A Junto cede 99,4% do resseguro à resseguradora do próprio grupo. E em "
            "2016 a S&P rebaixou a então J. Malucelli Seguradora de brAA- para brA "
            "por ação sobre o controlador, o Paraná Banco. Se rating apoiado no grupo "
            "não valesse, o da Junto também não valeria."
        ),
        "prova": "DFs Junto 2024 (Relatório da Administração e nota de resseguro); AM Best 12/11/2026; S&P 2016 (Grupo Amanhã).",
    },
]

PONTOS_DE_ATENCAO = [
    (
        "Rating próprio da Zurich Minas",
        "Nenhuma das fontes levantadas mostra rating S&P, Fitch ou Moody's emitido "
        "para a Zurich Minas Brasil isoladamente. O estudo se apoia no rating da "
        "controladora direta. Vale pedir à Zurich uma declaração formal de que a "
        "subsidiária é 'core' na metodologia das agências, ou carta-conforto da matriz.",
    ),
    (
        "Limitação pelo risco-país",
        "Pela metodologia de grupos da S&P, a nota global de uma subsidiária pode ser "
        "limitada pelo risco do país onde opera (soberano Brasil: BB). Mesmo nesse "
        "cenário, a Tabela 3 converte BB+ e acima em brAAA. No limite exato de BB, a "
        "tabela indica 'brAAA ou brAA+'. As DFs da Zurich Minas, porém, informam a "
        "Zurich Resseguradora Brasil S.A. com S&P AA-, o que indica que o grupo não "
        "tem suas entidades brasileiras rebaixadas ao nível do soberano.",
    ),
    (
        "Versão da tabela S&P",
        "A tabela usada é a de dezembro de 2023. Antes de protocolar, confirmar no "
        "site da S&P se há versão mais recente.",
    ),
    (
        "Índice de solvência",
        "Em índice relativo (PLA / CMR), a Junto (386%) supera a Zurich Minas (157%). "
        "O índice mede folga em relação ao próprio risco, não capacidade absoluta. "
        "Para um contrato de R$ 1 bilhão, o que protege o Estado é o volume de "
        "capital e o respaldo do grupo, onde a Zurich é muito superior.",
    ),
    (
        "Redação do edital",
        "Os três requisitos foram transcritos a partir do relato do cliente. "
        "Citar a cláusula literal do edital CC17/2025 na peça final.",
    ),
]


# =============================================================================
# 4. GARANTIA CONCORRENTE (Art. 23 da Circular SUSEP 662/2022) - fatos relatados
# =============================================================================

ART_23 = (
    "É vedada a utilização de mais de um Seguro Garantia para cobrir a mesma "
    "obrigação do objeto principal, salvo no caso de apólices complementares."
)

FATOS_RELATADOS = {
    "zurich": {"bid_bond_premio": 136_000.00, "limite_performance": 50_000_000.00,
               "premio_performance": 980_000.00, "situacao": "emitida e vigente"},
    "junto": {"bid_bond_premio": 9_000.00, "limite_performance": None,
              "situacao": "emitida 48h antes do certame"},
}


# =============================================================================
# 5. CÁLCULOS
# =============================================================================

VALOR_CONTRATO = 1_000_000_000.00


def exposicao_sobre_pl(seg: Seguradora, percentual_garantia: float) -> float:
    garantia_mil = VALOR_CONTRATO * percentual_garantia / 1000
    return garantia_mil / seg.patrimonio_liquido * 100


def _br(texto: str) -> str:
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(valor: float) -> str:
    return _br(f"R$ {valor:,.0f}")


def brl_mi(valor_mil: float) -> str:
    return _br(f"R$ {valor_mil / 1000:,.1f} mi")


def linha(c: str = "=", n: int = 92) -> str:
    return c * n


def gerar_relatorio() -> dict:
    print(linha())
    print("ESTUDO: A ZURICH ATENDE AO REQUISITO DE RATING DO EDITAL CC17/2025")
    print("Contrato de cogestão prisional - SEAP/AM - valor de referência R$ 1 bilhão")
    print(linha())

    print("\nTESE DA RH MULTI\n  " + TESE_RH)

    print("\n" + linha("-"))
    print("1. TABELA OFICIAL S&P - ESCALA GLOBAL -> ESCALA NACIONAL BRASIL (dez/2023)")
    print(linha("-"))
    for faixa, nacionais in TABELA_3_SP_BRASIL_2023[:6]:
        print(f"  {faixa:<14} -> {', '.join(nacionais)}")
    print("  (...)  Fonte: S&P, Tabela 3, p. 3. Versão 2018: 'BB e acima -> brAAA'.")

    conv = atende_braaa("AA")
    print(f"\n  Zurich Insurance Company Ltd: S&P {conv['rating_global']}")
    print(f"  Escala nacional indicativa: {', '.join(conv['escala_nacional_indicativa'])}")
    print(f"  Degraus acima do limiar de brAAA (BB+): {conv['degraus_acima_do_limiar_brAAA']}")
    print(f"  Atende 'igual ou superior a brAAA': {'SIM' if conv['atende_igual_ou_superior_a_brAAA'] else 'NÃO'}")
    print(f"  Junto: brAAA na escala nacional; qualidade global equivalente pode ser "
          f"qualquer nota de BB+ a AAA ({degraus_entre('AA', 'BB+')} degraus abaixo do AA no piso).")

    print("\n" + linha("-"))
    print("2. COMPARAÇÃO DAS SEGURADORAS BRASILEIRAS (mesmo critério: CNSP 432/2021)")
    print(linha("-"))
    print(f"  {'':<34}{'Zurich Minas':>22}{'Junto Seguros':>22}")
    print(f"  {'Data-base':<34}{ZURICH_MINAS.data_base:>22}{JUNTO.data_base:>22}")
    for rotulo, attr in [("Patrimônio líquido", "patrimonio_liquido"),
                         ("PLA", "pla"),
                         ("Capital mínimo requerido (CMR)", "capital_minimo_requerido"),
                         ("Suficiência de capital", "suficiencia_capital")]:
        print(f"  {rotulo:<34}{brl_mi(getattr(ZURICH_MINAS, attr)):>22}{brl_mi(getattr(JUNTO, attr)):>22}")
    print(f"  {'Índice de solvência (PLA/CMR)':<34}{ZURICH_MINAS.indice_solvencia:>21.0%}{JUNTO.indice_solvencia:>21.0%}")
    print(f"  {'Ativos garantidores':<34}{brl_mi(ZURICH_MINAS.ativos_garantidores):>22}{'n/d':>22}")
    razao_pl = ZURICH_MINAS.patrimonio_liquido / JUNTO.patrimonio_liquido
    print(f"\n  Patrimônio líquido: Zurich Minas = {_br(f'{razao_pl:.1f}')}x a Junto Seguros.")
    print("  Grupo: Zurich Insurance Group USD 26,5 bi de PL (2024).")

    print("\n  Exposição de uma garantia sobre o PL da seguradora:")
    for pct in (0.05, 0.10, 0.30):
        print(_br(f"    {pct:>4.0%} de R$ 1 bi -> Zurich Minas {exposicao_sobre_pl(ZURICH_MINAS, pct):5.1f}% | "
                  f"Junto {exposicao_sobre_pl(JUNTO, pct):6.1f}%"))

    print("\n" + linha("-"))
    print("3. REFUTAÇÕES")
    print(linha("-"))
    for r in REFUTACOES:
        print(f"\n  [{r['numero']}] {r['titulo']}")
        print(f"      {r['argumento']}")
        print(f"      Prova: {r['prova']}")

    print("\n" + linha("-"))
    print("4. GARANTIA CONCORRENTE - ART. 23 CIRCULAR SUSEP 662/2022 (fatos relatados)")
    print(linha("-"))
    print(f"  \"{ART_23}\"")
    z, j = FATOS_RELATADOS["zurich"], FATOS_RELATADOS["junto"]
    print(f"  Zurich: bid bond {brl(z['bid_bond_premio'])}; limite performance {brl(z['limite_performance'])}; {z['situacao']}")
    print(f"  Junto:  bid bond {brl(j['bid_bond_premio'])}; limite performance não demonstrado; {j['situacao']}")

    print("\n" + linha("-"))
    print("5. PONTOS DE ATENÇÃO (onde a RH pode contra-atacar)")
    print(linha("-"))
    for titulo, texto in PONTOS_DE_ATENCAO:
        print(f"\n  - {titulo}: {texto}")

    print("\n" + linha())
    print("CONCLUSÃO: pela régua oficial da S&P, o AA da controladora direta da Zurich")
    print("Minas equivale a brAAA na escala nacional. A seguradora é brasileira, autorizada")
    print("pela SUSEP e com ativos garantidores no país. Recusá-la por ter 'rating global'")
    print("exigiria recusar também a Junto, cujo rating igualmente decorre do grupo.")
    print(linha())

    dados = {
        "data_estudo": date.today().isoformat(),
        "certame": "CC17/2025 - CSC/SEAP Amazonas",
        "tabela_sp_brasil_2023": [{"global": f, "nacional": n} for f, n in TABELA_3_SP_BRASIL_2023],
        "conversao_zurich": conv,
        "seguradoras": {
            "zurich_minas": {**asdict(ZURICH_MINAS),
                             "suficiencia_capital": ZURICH_MINAS.suficiencia_capital,
                             "indice_solvencia": round(ZURICH_MINAS.indice_solvencia, 4)},
            "junto": {**asdict(JUNTO),
                      "suficiencia_capital": JUNTO.suficiencia_capital,
                      "indice_solvencia": round(JUNTO.indice_solvencia, 4)},
        },
        "razao_patrimonio_liquido": round(razao_pl, 2),
        "refutacoes": REFUTACOES,
        "pontos_de_atencao": [{"titulo": t, "texto": x} for t, x in PONTOS_DE_ATENCAO],
        "art_23_circular_susep_662": ART_23,
        "fatos_relatados": FATOS_RELATADOS,
    }
    with open("dados_analise_completa_cc17_2025.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print("\nDados salvos em: dados_analise_completa_cc17_2025.json")
    return dados


if __name__ == "__main__":
    gerar_relatorio()
