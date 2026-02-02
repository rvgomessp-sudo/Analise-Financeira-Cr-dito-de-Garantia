"""
Motor de Deduplicação

Regras de deduplicação para contas PJ.
Match por CNPJ, e-mail, site e similaridade de nome fantasia.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import re

from src.crm.models.conta import Conta


@dataclass
class ParDuplicata:
    """Par de contas potencialmente duplicadas"""
    conta_a_id: str
    conta_b_id: str
    score_similaridade: float  # 0-100
    criterios_match: List[str]
    recomendacao: str  # "mesclar", "revisar", "falso_positivo"
    conta_master_sugerida: str = ""  # ID da conta sugerida como master
    data_deteccao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'conta_a_id': self.conta_a_id,
            'conta_b_id': self.conta_b_id,
            'score_similaridade': round(self.score_similaridade, 1),
            'criterios_match': self.criterios_match,
            'recomendacao': self.recomendacao,
            'conta_master_sugerida': self.conta_master_sugerida,
        }


@dataclass
class ResultadoDeduplicacao:
    """Resultado da análise de deduplicação"""
    total_contas_analisadas: int
    duplicatas_encontradas: List[ParDuplicata]
    total_duplicatas: int = 0
    data_analise: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self.total_duplicatas = len(self.duplicatas_encontradas)

    def to_dict(self) -> Dict:
        return {
            'total_analisadas': self.total_contas_analisadas,
            'total_duplicatas': self.total_duplicatas,
            'duplicatas': [d.to_dict() for d in self.duplicatas_encontradas],
        }


class Deduplicador:
    """
    Motor de deduplicação de contas PJ.

    Critérios de match (por prioridade):
        1. CNPJ idêntico (match exato) - score 100
        2. Mesma raiz CNPJ (matriz/filial) - score 80
        3. E-mail corporativo idêntico - score 70
        4. Site idêntico - score 60
        5. Nome fantasia similar (>80% similaridade) - score 50

    Regras:
        - Score >= 80: recomenda mesclar automaticamente
        - Score 50-79: recomenda revisão manual
        - Score < 50: descarta como falso positivo
    """

    LIMIAR_MESCLAR = 80
    LIMIAR_REVISAR = 50

    def analisar(self, contas: List[Conta]) -> ResultadoDeduplicacao:
        """
        Analisa lista de contas para encontrar duplicatas.

        Usa indexação por CNPJ/e-mail/site para performance.
        """
        duplicatas = []

        # Índice por CNPJ (match exato)
        indice_cnpj: Dict[str, List[Conta]] = {}
        for conta in contas:
            cnpj = conta.cnpj
            if cnpj not in indice_cnpj:
                indice_cnpj[cnpj] = []
            indice_cnpj[cnpj].append(conta)

        # Match exato por CNPJ
        for cnpj, grupo in indice_cnpj.items():
            if len(grupo) > 1:
                for i in range(len(grupo)):
                    for j in range(i + 1, len(grupo)):
                        par = ParDuplicata(
                            conta_a_id=grupo[i].id,
                            conta_b_id=grupo[j].id,
                            score_similaridade=100,
                            criterios_match=["CNPJ idêntico"],
                            recomendacao="mesclar",
                            conta_master_sugerida=self._sugerir_master(grupo[i], grupo[j]),
                        )
                        duplicatas.append(par)

        # Índice por raiz CNPJ (matriz/filial)
        indice_raiz: Dict[str, List[Conta]] = {}
        for conta in contas:
            raiz = conta.cnpj[:8] if len(conta.cnpj) >= 8 else ""
            if raiz and raiz not in indice_raiz:
                indice_raiz[raiz] = []
            if raiz:
                indice_raiz[raiz].append(conta)

        for raiz, grupo in indice_raiz.items():
            if len(grupo) > 1:
                # Só reporta se não são mesmo CNPJ (já capturado acima)
                for i in range(len(grupo)):
                    for j in range(i + 1, len(grupo)):
                        if grupo[i].cnpj != grupo[j].cnpj:
                            ja_reportado = any(
                                (d.conta_a_id == grupo[i].id and d.conta_b_id == grupo[j].id)
                                or (d.conta_a_id == grupo[j].id and d.conta_b_id == grupo[i].id)
                                for d in duplicatas
                            )
                            if not ja_reportado:
                                par = ParDuplicata(
                                    conta_a_id=grupo[i].id,
                                    conta_b_id=grupo[j].id,
                                    score_similaridade=80,
                                    criterios_match=["Mesma raiz CNPJ (matriz/filial)"],
                                    recomendacao="revisar",
                                    conta_master_sugerida=self._sugerir_master(grupo[i], grupo[j]),
                                )
                                duplicatas.append(par)

        # Índice por e-mail
        indice_email: Dict[str, List[Conta]] = {}
        for conta in contas:
            if conta.email_geral:
                email_norm = conta.email_geral.lower().strip()
                if email_norm not in indice_email:
                    indice_email[email_norm] = []
                indice_email[email_norm].append(conta)

        for email, grupo in indice_email.items():
            if len(grupo) > 1:
                for i in range(len(grupo)):
                    for j in range(i + 1, len(grupo)):
                        if grupo[i].cnpj != grupo[j].cnpj:
                            ja_reportado = any(
                                (d.conta_a_id == grupo[i].id and d.conta_b_id == grupo[j].id)
                                or (d.conta_a_id == grupo[j].id and d.conta_b_id == grupo[i].id)
                                for d in duplicatas
                            )
                            if not ja_reportado:
                                par = ParDuplicata(
                                    conta_a_id=grupo[i].id,
                                    conta_b_id=grupo[j].id,
                                    score_similaridade=70,
                                    criterios_match=["E-mail corporativo idêntico"],
                                    recomendacao="revisar",
                                )
                                duplicatas.append(par)

        # Índice por site
        indice_site: Dict[str, List[Conta]] = {}
        for conta in contas:
            if conta.site:
                site_norm = self._normalizar_url(conta.site)
                if site_norm and site_norm not in indice_site:
                    indice_site[site_norm] = []
                if site_norm:
                    indice_site[site_norm].append(conta)

        for site, grupo in indice_site.items():
            if len(grupo) > 1:
                for i in range(len(grupo)):
                    for j in range(i + 1, len(grupo)):
                        if grupo[i].cnpj != grupo[j].cnpj:
                            ja_reportado = any(
                                (d.conta_a_id == grupo[i].id and d.conta_b_id == grupo[j].id)
                                or (d.conta_a_id == grupo[j].id and d.conta_b_id == grupo[i].id)
                                for d in duplicatas
                            )
                            if not ja_reportado:
                                par = ParDuplicata(
                                    conta_a_id=grupo[i].id,
                                    conta_b_id=grupo[j].id,
                                    score_similaridade=60,
                                    criterios_match=["Site idêntico"],
                                    recomendacao="revisar",
                                )
                                duplicatas.append(par)

        # Similaridade por nome fantasia (O(n²) - apenas para lotes pequenos)
        if len(contas) <= 500:
            for i in range(len(contas)):
                for j in range(i + 1, len(contas)):
                    if contas[i].cnpj == contas[j].cnpj:
                        continue
                    ja_reportado = any(
                        (d.conta_a_id == contas[i].id and d.conta_b_id == contas[j].id)
                        or (d.conta_a_id == contas[j].id and d.conta_b_id == contas[i].id)
                        for d in duplicatas
                    )
                    if ja_reportado:
                        continue

                    nome_a = contas[i].nome_fantasia or contas[i].razao_social
                    nome_b = contas[j].nome_fantasia or contas[j].razao_social
                    sim = self._similaridade_nomes(nome_a, nome_b)

                    if sim >= 0.8:
                        par = ParDuplicata(
                            conta_a_id=contas[i].id,
                            conta_b_id=contas[j].id,
                            score_similaridade=sim * 60,
                            criterios_match=[f"Nome fantasia similar ({sim*100:.0f}%)"],
                            recomendacao="revisar" if sim >= 0.9 else "revisar",
                        )
                        duplicatas.append(par)

        return ResultadoDeduplicacao(
            total_contas_analisadas=len(contas),
            duplicatas_encontradas=duplicatas,
        )

    def verificar_conta_individual(self, conta_nova: Conta,
                                    contas_existentes: List[Conta]) -> List[ParDuplicata]:
        """
        Verifica se uma conta nova é duplicata de alguma existente.
        Útil para validação em tempo real (ao criar conta).
        """
        duplicatas = []

        for existente in contas_existentes:
            criterios = []
            score = 0

            # CNPJ idêntico
            if conta_nova.cnpj == existente.cnpj:
                criterios.append("CNPJ idêntico")
                score = 100

            # Mesma raiz
            elif (len(conta_nova.cnpj) >= 8 and len(existente.cnpj) >= 8
                  and conta_nova.cnpj[:8] == existente.cnpj[:8]):
                criterios.append("Mesma raiz CNPJ (matriz/filial)")
                score = max(score, 80)

            # E-mail
            if (conta_nova.email_geral and existente.email_geral
                    and conta_nova.email_geral.lower() == existente.email_geral.lower()):
                criterios.append("E-mail corporativo idêntico")
                score = max(score, 70)

            # Site
            if conta_nova.site and existente.site:
                site_a = self._normalizar_url(conta_nova.site)
                site_b = self._normalizar_url(existente.site)
                if site_a and site_b and site_a == site_b:
                    criterios.append("Site idêntico")
                    score = max(score, 60)

            # Nome similar
            nome_a = conta_nova.nome_fantasia or conta_nova.razao_social
            nome_b = existente.nome_fantasia or existente.razao_social
            sim = self._similaridade_nomes(nome_a, nome_b)
            if sim >= 0.8:
                criterios.append(f"Nome fantasia similar ({sim*100:.0f}%)")
                score = max(score, sim * 60)

            if criterios and score >= self.LIMIAR_REVISAR:
                recomendacao = "mesclar" if score >= self.LIMIAR_MESCLAR else "revisar"
                duplicatas.append(ParDuplicata(
                    conta_a_id=conta_nova.id,
                    conta_b_id=existente.id,
                    score_similaridade=score,
                    criterios_match=criterios,
                    recomendacao=recomendacao,
                    conta_master_sugerida=self._sugerir_master(conta_nova, existente),
                ))

        return duplicatas

    def _sugerir_master(self, conta_a: Conta, conta_b: Conta) -> str:
        """Sugere qual conta deve ser a master (mais completa/antiga)"""
        score_a = conta_a.percentual_completude
        score_b = conta_b.percentual_completude
        if score_a > score_b:
            return conta_a.id
        elif score_b > score_a:
            return conta_b.id
        # Se igual, a mais antiga
        if conta_a.data_criacao <= conta_b.data_criacao:
            return conta_a.id
        return conta_b.id

    @staticmethod
    def _normalizar_url(url: str) -> str:
        """Normaliza URL para comparação"""
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        return url

    @staticmethod
    def _similaridade_nomes(nome_a: str, nome_b: str) -> float:
        """
        Calcula similaridade entre dois nomes usando coeficiente de Jaccard
        sobre trigramas (simples, sem dependências externas).
        """
        if not nome_a or not nome_b:
            return 0.0

        nome_a = re.sub(r'[^a-z0-9\s]', '', nome_a.lower().strip())
        nome_b = re.sub(r'[^a-z0-9\s]', '', nome_b.lower().strip())

        if nome_a == nome_b:
            return 1.0

        def trigramas(s: str) -> set:
            s = f"  {s} "
            return {s[i:i+3] for i in range(len(s) - 2)}

        tri_a = trigramas(nome_a)
        tri_b = trigramas(nome_b)

        if not tri_a or not tri_b:
            return 0.0

        intersecao = tri_a & tri_b
        uniao = tri_a | tri_b

        return len(intersecao) / len(uniao)
