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
# 1. PATAMAR EXIGIDO PELO EDITAL
# Conforme a solicitação formal enviada à Zurich em 17/12/2025. Conferir com a
# redação literal da cláusula do edital antes de protocolar.
# =============================================================================

EXIGENCIA_EDITAL = {"S&P": "brAA-", "Fitch": "A-(bra)", "Moody's": "A1.br"}
FONTE_EXIGENCIA = "Solicitação de parecer técnico à Zurich, 17/12/2025 (transcreve o edital)"

# =============================================================================
# 2. ESCALAS GLOBAIS E TABELAS OFICIAIS DE CONVERSÃO
# =============================================================================

ESCALA_SP = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-",
             "BB+", "BB", "BB-", "B+", "B", "B-", "CCC+", "CCC", "CCC-", "CC", "C"]
ESCALA_MOODYS = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
                 "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]

# S&P Global Ratings, "National And Regional Scale Credit Ratings Methodology",
# 19/12/2023, Tabela 3 - Brazil mapping specification, p. 3.
TABELA_SP_2023: List[Tuple[str, List[str]]] = [
    ("BB+ e acima", ["brAAA"]),
    ("BB", ["brAAA", "brAA+"]),
    ("BB-", ["brAA+", "brAA"]),
    ("B+", ["brAA", "brAA-", "brA+"]),
    ("B", ["brA+", "brA", "brA-"]),
    ("B-", ["brBBB+", "brBBB", "brBBB-", "brBB+"]),
    ("CCC+", ["brBB+", "brBB", "brBB-"]),
]

# S&P, "National And Regional Scale Mapping Specifications", 25/06/2018, Tabela 3.
TABELA_SP_2018: List[Tuple[str, List[str]]] = [
    ("BB e acima", ["brAAA"]),
    ("BB-", ["brAAA", "brAA+"]),
    ("B+", ["brAA+", "brAA", "brAA-"]),
    ("B", ["brA+", "brA", "brA-"]),
    ("B-", ["brBBB+", "brBBB", "brBBB-"]),
]

# Moody's América Latina, Formulário de Referência (data-base 31/12/2020),
# "Mapas de Equivalência de Ratings na Escala Nacional por País - Brasil",
# vigente a partir de 20/11/2020.
TABELA_MOODYS_2020: List[Tuple[str, List[str]]] = [
    ("Ba1 e acima", ["Aaa.br"]),
    ("Ba2", ["Aa1.br", "Aa2.br", "Aa3.br"]),
    ("Ba3", ["A1.br", "A2.br", "A3.br"]),
    ("B1", ["Baa1.br", "Baa2.br", "Baa3.br"]),
    ("B2", ["Ba1.br", "Ba2.br"]),
]


def _faixa_global(faixa: str) -> str:
    return faixa.replace(" e acima", "")


def menor_global_que_alcanca(tabela, nota_nacional: str) -> str:
    """Pior nota global cuja faixa na tabela ainda inclui a nota nacional exigida."""
    resultado = None
    for faixa, nacionais in tabela:
        if nota_nacional in nacionais:
            resultado = _faixa_global(faixa)
    if resultado is None:
        raise ValueError(f"{nota_nacional} não consta da tabela")
    return resultado


def degraus(escala: List[str], melhor: str, pior: str) -> int:
    return escala.index(pior) - escala.index(melhor)


def converter(tabela, escala: List[str], nota_global: str) -> List[str]:
    for faixa, nacionais in tabela:
        topo = _faixa_global(faixa)
        if faixa.endswith("e acima") and escala.index(nota_global) <= escala.index(topo):
            return nacionais
        if topo == nota_global:
            return nacionais
    raise ValueError(nota_global)


# =============================================================================
# 3. RATINGS DA ZURICH
# =============================================================================

# Página oficial de RI (capturada em 03/01/2026), entidade Zurich Insurance Company Ltd.
RATINGS_ZURICH_OFICIAIS = {"S&P": "AA", "Moody's": "Aa2", "AM Best": "A+ (Superior)"}
# Notas citadas na carta da Zurich de 18/12/2025 (anteriores às elevações recentes).
RATINGS_ZURICH_CARTA = {"S&P": "AA-", "Moody's": "Aa3", "Fitch": "AA-"}


def margem_de_seguranca() -> List[Dict[str, object]]:
    linhas = []
    for nome, tabela, escala, exig, nota_zurich, fonte in [
        ("S&P (tabela 2023)", TABELA_SP_2023, ESCALA_SP, EXIGENCIA_EDITAL["S&P"],
         RATINGS_ZURICH_OFICIAIS["S&P"], "S&P, 19/12/2023, Tabela 3"),
        ("S&P (tabela 2018)", TABELA_SP_2018, ESCALA_SP, EXIGENCIA_EDITAL["S&P"],
         RATINGS_ZURICH_OFICIAIS["S&P"], "S&P, 25/06/2018, Tabela 3"),
        ("Moody's (mapa 2020)", TABELA_MOODYS_2020, ESCALA_MOODYS, EXIGENCIA_EDITAL["Moody's"],
         RATINGS_ZURICH_OFICIAIS["Moody's"], "Moody's América Latina, Form. Referência 2020"),
    ]:
        piso = menor_global_que_alcanca(tabela, exig)
        linhas.append({
            "agencia": nome,
            "exigencia_edital": exig,
            "equivale_na_escala_global_a_partir_de": piso,
            "nota_zurich": nota_zurich,
            "nota_zurich_na_escala_nacional": converter(tabela, escala, nota_zurich),
            "degraus_de_folga": degraus(escala, nota_zurich, piso),
            "fonte": fonte,
        })
    return linhas


# =============================================================================
# 4. DADOS DOCUMENTADOS DAS SEGURADORAS (R$ mil)
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
        "Moody's (controladora; elevado de Aa3 em set/2024)": "Aa2/estável",
        "AM Best (controladora)": "A+ (Superior)/estável",
    },
    fontes=[
        Fonte("DFs intermediárias Zurich Minas Brasil Seguros S.A., 30/06/2024",
              "Nota 1 (acionistas); Nota 20.c (PLA e CMR); cobertura das provisões técnicas"),
        Fonte("Condições gerais Seguro Garantia Zurich (Circular SUSEP 662/2022)",
              "'devidamente autorizada pela SUSEP sob o código nº 05495'"),
        Fonte("Zurich Insurance Group, Annual results 2024", "Nota 27, Tabela 27.1, p. 132"),
        Fonte("zurich.com/investor-relations/ratings (03/01/2026)", "Tabela de ratings"),
        Fonte("Carta da Zurich (Head of Surety LatAm), 18/12/2025", "Itens 1 a 3"),
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
    fontes=[
        Fonte("DFs Junto Seguros S.A. 2024 (publicadas em 28/02/2025)",
              "Relatório da Administração; Nota 21"),
        Fonte("AM Best, 12/11/2026", "Ratings conjuntos; apoio da controladora Travelers"),
    ],
)


# =============================================================================
# 5. TESE DA RH MULTI E REFUTAÇÕES
# =============================================================================

TESE_RH = (
    "A Zurich não atenderia ao edital porque seu rating é global e não em escala "
    "nacional, e porque a subsidiária brasileira não tem rating próprio."
)

REFUTACOES = [
    {
        "numero": 1,
        "titulo": "O edital fixa um patamar de qualidade, medido na régua nacional",
        "argumento": (
            "A cláusula exige rating igual ou superior, em escala nacional, a brAA- (S&P), "
            "A-(bra) (Fitch) ou A1.br (Moody's). Ela define a régua de medida, não o país "
            "de emissão da nota nem a existência de relatório nacional próprio da seguradora."
        ),
        "prova": FONTE_EXIGENCIA + "; conferir a redação literal do edital.",
    },
    {
        "numero": 2,
        "titulo": "As tabelas oficiais das agências convertem a nota global em nacional",
        "argumento": (
            "S&P (2018 e 2023) e Moody's (2020) publicam tabelas que derivam a nota nacional "
            "da qualidade de crédito global. Em todas, o patamar do edital corresponde a uma "
            "nota global na faixa B/BB. A Zurich está em AA (S&P) e Aa2 (Moody's): 10 a 11 "
            "degraus acima, e convertida dá a nota máxima (brAAA / Aaa.br)."
        ),
        "prova": "S&P 19/12/2023 Tab. 3; S&P 25/06/2018 Tab. 3; Moody's Form. Referência 2020.",
    },
    {
        "numero": 3,
        "titulo": "A Zurich Minas é brasileira, autorizada pela SUSEP, com ativos no país",
        "argumento": (
            "Sociedade anônima brasileira, código SUSEP 05495, opera seguro-garantia sob a "
            "Circular SUSEP 662/2022. Em 30/06/2024 tinha R$ 2,71 bilhões em ativos garantidores, "
            "quase todos títulos do Tesouro Nacional. Pela Res. CMN 4.993/2022 (Regulamento, "
            "art. 4º), só valem ativos custodiados em instituições autorizadas pelo BCB ou CVM."
        ),
        "prova": "Condições gerais Zurich; DFs Zurich Minas 30/06/2024; Res. CMN 4.993/2022.",
    },
    {
        "numero": 4,
        "titulo": "A controladora direta é a própria entidade classificada",
        "argumento": (
            "Os ratings AA / Aa2 / A+ são da Zurich Insurance Company Ltd, que detém 99,9999% "
            "da Zurich Minas. O grupo a lista como subsidiária significativa, 100% de voto e "
            "capital. A própria Zurich declarou por escrito (18/12/2025) que a subsidiária está "
            "plenamente vinculada ao conglomerado, cuja solidez sustenta a operação brasileira."
        ),
        "prova": "DFs Zurich Minas, Nota 1; Annual results 2024, Nota 27, p. 132; carta Zurich 18/12/2025.",
    },
    {
        "numero": 5,
        "titulo": "A tese da RH desqualificaria a própria Junto",
        "argumento": (
            "A AM Best classifica Junto Seguros e Junto Resseguros em conjunto, com apoio da "
            "controladora Travelers; a Junto cede 99,4% do resseguro à resseguradora do grupo; "
            "e em 2016 a S&P rebaixou a então J. Malucelli por ação sobre o controlador Paraná "
            "Banco. Se rating apoiado no grupo não valesse, o da Junto também não valeria."
        ),
        "prova": "DFs Junto 2024; AM Best 12/11/2026; S&P 2016 (Grupo Amanhã).",
    },
]

PONTOS_DE_ATENCAO = [
    ("Carta da Zurich com notas desatualizadas",
     "A carta de 18/12/2025 cita S&P AA-, Moody's Aa3 e Fitch AA-. A página oficial de RI "
     "mostra S&P AA e Moody's Aa2 (elevado em set/2024), e não lista Fitch. As notas da carta "
     "também superam o patamar com folga, mas convém pedir à Zurich uma versão com as notas "
     "vigentes, para que a RH não explore a divergência."),
    ("Nova estrutura da S&P no Brasil",
     "Desde 18/08/2025 as notas 'br' são emitidas pela S&P National Ratings, com metodologias "
     "próprias; em 16/12/2025 a S&P global retirou o Brasil da sua tabela de prefixos. As "
     "metodologias novas não puderam ser baixadas para este estudo. A conclusão não depende "
     "delas: a folga de 11 degraus excede qualquer recalibração já registrada."),
    ("Rating próprio da Zurich Minas",
     "Não foi localizado rating S&P, Fitch ou Moody's emitido para a Zurich Minas isoladamente. "
     "O estudo se apoia no rating da controladora direta e na declaração da Zurich."),
    ("Índice de solvência",
     "Em índice relativo (PLA/CMR), a Junto (386%) supera a Zurich Minas (157%). O índice mede "
     "folga relativa ao próprio risco, não capacidade absoluta para um contrato de R$ 1 bilhão."),
    ("Redação do edital",
     "O patamar (brAA- / A-(bra) / A1.br) foi extraído da solicitação de 17/12/2025. Em mensagem "
     "anterior foi citado brAAA. A conclusão vale para os dois, mas a peça deve citar a cláusula literal."),
]

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

VALOR_CONTRATO = 1_000_000_000.00


# =============================================================================
# 6. RELATÓRIO
# =============================================================================

def _br(texto: str) -> str:
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(valor: float) -> str:
    return _br(f"R$ {valor:,.0f}")


def brl_mi(valor_mil: float) -> str:
    return _br(f"R$ {valor_mil / 1000:,.1f} mi")


def exposicao_sobre_pl(seg: Seguradora, percentual_garantia: float) -> float:
    return VALOR_CONTRATO * percentual_garantia / 1000 / seg.patrimonio_liquido * 100


def linha(c: str = "=", n: int = 92) -> str:
    return c * n


def gerar_relatorio() -> dict:
    print(linha())
    print("ESTUDO: A ZURICH ATENDE AO REQUISITO DE RATING DO EDITAL CC17/2025")
    print(linha())
    print("\nTese da RH Multi: " + TESE_RH)
    print("Exigência do edital: " + ", ".join(f"{k} {v}" for k, v in EXIGENCIA_EDITAL.items()))

    print("\n" + linha("-"))
    print("1. MARGEM DE SEGURANÇA PELAS TABELAS OFICIAIS")
    print(linha("-"))
    margem = margem_de_seguranca()
    print(f"  {'Tabela':<22}{'Exige':<9}{'= global a partir de':<22}{'Zurich':<8}{'Zurich nacional':<17}{'Folga'}")
    for m in margem:
        print(f"  {m['agencia']:<22}{m['exigencia_edital']:<9}{m['equivale_na_escala_global_a_partir_de']:<22}"
              f"{m['nota_zurich']:<8}{', '.join(m['nota_zurich_na_escala_nacional']):<17}{m['degraus_de_folga']} degraus")

    print("\n" + linha("-"))
    print("2. SEGURADORAS BRASILEIRAS (CNSP 432/2021)")
    print(linha("-"))
    print(f"  {'':<34}{'Zurich Minas':>20}{'Junto Seguros':>20}")
    for rotulo, attr in [("Patrimônio líquido", "patrimonio_liquido"), ("PLA", "pla"),
                         ("Capital mínimo requerido", "capital_minimo_requerido"),
                         ("Suficiência de capital", "suficiencia_capital")]:
        print(f"  {rotulo:<34}{brl_mi(getattr(ZURICH_MINAS, attr)):>20}{brl_mi(getattr(JUNTO, attr)):>20}")
    print(f"  {'Índice PLA/CMR':<34}{ZURICH_MINAS.indice_solvencia:>19.0%}{JUNTO.indice_solvencia:>19.0%}")
    razao_pl = ZURICH_MINAS.patrimonio_liquido / JUNTO.patrimonio_liquido
    print(f"\n  PL Zurich Minas = {_br(f'{razao_pl:.1f}')}x o da Junto.")
    for pct in (0.05, 0.10, 0.30):
        print(_br(f"  Garantia de {pct:.0%} de R$ 1 bi: {exposicao_sobre_pl(ZURICH_MINAS, pct):.1f}% do PL Zurich Minas | "
                  f"{exposicao_sobre_pl(JUNTO, pct):.1f}% do PL Junto"))

    print("\n" + linha("-"))
    print("3. REFUTAÇÕES")
    print(linha("-"))
    for r in REFUTACOES:
        print(f"\n  [{r['numero']}] {r['titulo']}\n      {r['argumento']}\n      Prova: {r['prova']}")

    print("\n" + linha("-"))
    print("4. PONTOS DE ATENÇÃO")
    print(linha("-"))
    for titulo, texto in PONTOS_DE_ATENCAO:
        print(f"\n  - {titulo}: {texto}")

    dados = {
        "data_estudo": date.today().isoformat(),
        "certame": "CC17/2025 - CSC/SEAP Amazonas",
        "exigencia_edital": EXIGENCIA_EDITAL,
        "margem_de_seguranca": margem,
        "tabelas": {"sp_2023": TABELA_SP_2023, "sp_2018": TABELA_SP_2018, "moodys_2020": TABELA_MOODYS_2020},
        "ratings_zurich_oficiais": RATINGS_ZURICH_OFICIAIS,
        "ratings_zurich_carta_18_12_2025": RATINGS_ZURICH_CARTA,
        "seguradoras": {
            "zurich_minas": {**asdict(ZURICH_MINAS), "suficiencia_capital": ZURICH_MINAS.suficiencia_capital,
                             "indice_solvencia": round(ZURICH_MINAS.indice_solvencia, 4)},
            "junto": {**asdict(JUNTO), "suficiencia_capital": JUNTO.suficiencia_capital,
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
