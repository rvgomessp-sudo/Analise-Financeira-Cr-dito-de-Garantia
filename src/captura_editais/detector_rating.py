"""
Detector de exigências de rating em editais de licitação.

Este módulo analisa textos de editais para identificar exigências de
rating/classificação de risco para seguradoras emitentes de seguro garantia.
"""

import re
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .modelos import (
    ExigenciaRating,
    NivelRating,
    AgenciaRating,
    TipoGarantia
)


@dataclass
class PadraoDeteccao:
    """Padrão de detecção com regex e metadados."""
    nome: str
    regex: str
    peso: int  # 1-10, quanto maior mais relevante
    categoria: str


class DetectorRating:
    """
    Detecta exigências de rating em textos de editais.

    Esta classe utiliza uma combinação de expressões regulares e
    análise contextual para identificar quando um edital exige
    rating/classificação de risco para seguradoras.
    """

    # Padrões para detectar exigência de rating
    PADROES_RATING = [
        # Padrões diretos de exigência de rating
        PadraoDeteccao(
            "rating_direto",
            r"(?:rating|classificação\s+de\s+risco)\s+(?:mínimo|igual\s+ou\s+superior|no\s+mínimo)",
            10,
            "exigencia_direta"
        ),
        PadraoDeteccao(
            "rating_nivel",
            r"(?:rating|classificação)\s+(?:de\s+)?(?:pelo\s+menos\s+)?[\"']?([A-D][A-D]?[\+\-]?|(?:AA|BBB|BB|B)[\+\-]?)[\"']?",
            10,
            "nivel_especifico"
        ),
        PadraoDeteccao(
            "grau_investimento",
            r"(?:grau\s+de\s+investimento|investment\s+grade)",
            9,
            "grau_investimento"
        ),

        # Padrões com agências específicas
        PadraoDeteccao(
            "agencia_sp",
            r"(?:standard\s*(?:and|&)?\s*poor'?s?|s&p|s\s*&\s*p)",
            8,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_moody",
            r"moody'?s?",
            8,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_fitch",
            r"fitch\s*(?:ratings?)?",
            8,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_ambest",
            r"a\.?\s*m\.?\s*best",
            8,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_austin",
            r"austin\s*(?:rating)?",
            7,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_lf",
            r"lf\s*rating",
            7,
            "agencia"
        ),
        PadraoDeteccao(
            "agencia_sr",
            r"sr\s*rating",
            7,
            "agencia"
        ),

        # Padrões contextuais sobre seguradora
        PadraoDeteccao(
            "seguradora_rating",
            r"seguradora\s+(?:que\s+)?(?:possua|tenha|detenha|apresente)\s+(?:rating|classificação)",
            9,
            "contexto_seguradora"
        ),
        PadraoDeteccao(
            "classificacao_financeira",
            r"classificação\s+(?:financeira|de\s+solidez|de\s+capacidade)",
            7,
            "contexto_financeiro"
        ),
        PadraoDeteccao(
            "forca_financeira",
            r"(?:força|solidez|capacidade)\s+financeira\s+(?:classificada|avaliada|certificada)",
            7,
            "contexto_financeiro"
        ),

        # Padrões sobre escala
        PadraoDeteccao(
            "escala_nacional",
            r"escala\s+(?:nacional|brasileira|local)",
            6,
            "escala"
        ),
        PadraoDeteccao(
            "escala_global",
            r"escala\s+(?:global|internacional)",
            6,
            "escala"
        ),

        # Padrões sobre seguro garantia
        PadraoDeteccao(
            "seguro_garantia_rating",
            r"seguro\s+garantia\s+(?:emitido|expedido)?\s*(?:por)?\s+(?:seguradora\s+)?(?:com\s+)?(?:rating|classificação)",
            9,
            "seguro_garantia"
        ),
        PadraoDeteccao(
            "apólice_rating",
            r"apólice\s+(?:de\s+seguro\s+garantia\s+)?(?:emitida)?\s*(?:por)?\s+(?:seguradora\s+)?(?:com\s+)?(?:rating|classificação)",
            9,
            "seguro_garantia"
        ),

        # Padrões sobre exigência em garantias
        PadraoDeteccao(
            "garantia_contratual_rating",
            r"garantia\s+(?:contratual|de\s+execução|de\s+proposta)\s+[\s\S]{0,100}(?:rating|classificação)",
            8,
            "garantia"
        ),
        PadraoDeteccao(
            "caucao_rating",
            r"caução\s+[\s\S]{0,100}(?:seguradora\s+)?(?:com\s+)?(?:rating|classificação)",
            7,
            "garantia"
        ),
    ]

    # Padrões para detectar níveis de rating
    PADROES_NIVEL = {
        r'\bAAA\b': NivelRating.AAA,
        r'\bAA\+': NivelRating.AA_PLUS,
        r'\bAA(?![\+\-])': NivelRating.AA,
        r'\bAA\-': NivelRating.AA_MINUS,
        r'\bA\+': NivelRating.A_PLUS,
        r'\bA(?![\+\-A])': NivelRating.A,
        r'\bA\-': NivelRating.A_MINUS,
        r'\bBBB\+': NivelRating.BBB_PLUS,
        r'\bBBB(?![\+\-])': NivelRating.BBB,
        r'\bBBB\-': NivelRating.BBB_MINUS,
        r'\bBB\+': NivelRating.BB_PLUS,
        r'\bBB(?![\+\-B])': NivelRating.BB,
        r'grau\s+de\s+investimento': NivelRating.INVESTIMENTO,
        r'investment\s+grade': NivelRating.INVESTIMENTO,
    }

    # Mapeamento de agências
    MAPA_AGENCIAS = {
        r'standard\s*(?:and|&)?\s*poor': AgenciaRating.SP,
        r's\s*&\s*p': AgenciaRating.SP,
        r'moody': AgenciaRating.MOODYS,
        r'fitch': AgenciaRating.FITCH,
        r'a\.?\s*m\.?\s*best': AgenciaRating.AM_BEST,
        r'austin': AgenciaRating.AUSTIN,
        r'lf\s*rating': AgenciaRating.LF_RATING,
        r'sr\s*rating': AgenciaRating.SR_RATING,
    }

    def __init__(self):
        """Inicializa o detector."""
        # Compila os padrões regex para melhor performance
        self._padroes_compilados = [
            (p, re.compile(p.regex, re.IGNORECASE | re.MULTILINE))
            for p in self.PADROES_RATING
        ]

        self._niveis_compilados = {
            re.compile(p, re.IGNORECASE): n
            for p, n in self.PADROES_NIVEL.items()
        }

        self._agencias_compiladas = {
            re.compile(p, re.IGNORECASE): a
            for p, a in self.MAPA_AGENCIAS.items()
        }

    def detectar(self, texto: str) -> ExigenciaRating:
        """
        Detecta exigências de rating em um texto.

        Args:
            texto: Texto do edital para análise

        Returns:
            ExigenciaRating com os detalhes encontrados
        """
        if not texto:
            return ExigenciaRating(encontrada=False)

        texto_normalizado = self._normalizar_texto(texto)

        # Coleta todas as correspondências
        correspondencias = self._encontrar_correspondencias(texto_normalizado)

        if not correspondencias:
            return ExigenciaRating(encontrada=False)

        # Calcula pontuação total
        pontuacao = sum(c['peso'] for c in correspondencias)

        # Se pontuação suficiente, consideramos que há exigência
        if pontuacao >= 8:  # Threshold configurável
            return self._construir_exigencia(texto_normalizado, correspondencias)

        return ExigenciaRating(encontrada=False)

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza o texto para análise."""
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        # Remove caracteres especiais problemáticos
        texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', texto)
        return texto

    def _encontrar_correspondencias(self, texto: str) -> List[Dict]:
        """Encontra todas as correspondências de padrões."""
        correspondencias = []

        for padrao, regex in self._padroes_compilados:
            matches = regex.finditer(texto)
            for match in matches:
                correspondencias.append({
                    'padrao': padrao,
                    'match': match,
                    'texto': match.group(),
                    'posicao': match.start(),
                    'peso': padrao.peso,
                    'categoria': padrao.categoria
                })

        return correspondencias

    def _construir_exigencia(
        self,
        texto: str,
        correspondencias: List[Dict]
    ) -> ExigenciaRating:
        """Constrói objeto ExigenciaRating a partir das correspondências."""

        # Extrai o contexto das correspondências
        textos_relevantes = self._extrair_contexto(texto, correspondencias)
        texto_original = ' [...] '.join(textos_relevantes[:3])

        # Detecta nível de rating
        nivel_minimo = self._detectar_nivel(texto)

        # Detecta agências aceitas
        agencias = self._detectar_agencias(texto)

        # Detecta escala (nacional vs global)
        escala_nacional = self._detectar_escala_nacional(texto)

        # Detecta se permite rating do grupo
        permite_grupo = self._detectar_permite_grupo(texto)

        # Tenta identificar cláusula de referência
        clausula = self._encontrar_clausula(texto, correspondencias)

        # Gera observações
        observacoes = self._gerar_observacoes(correspondencias)

        return ExigenciaRating(
            encontrada=True,
            nivel_minimo=nivel_minimo,
            agencias_aceitas=agencias,
            texto_original=texto_original[:500],  # Limita tamanho
            clausula_referencia=clausula,
            escala_nacional=escala_nacional,
            permite_grupo=permite_grupo,
            observacoes=observacoes
        )

    def _extrair_contexto(
        self,
        texto: str,
        correspondencias: List[Dict],
        tamanho_contexto: int = 200
    ) -> List[str]:
        """Extrai contexto ao redor das correspondências."""
        contextos = []

        for c in correspondencias:
            inicio = max(0, c['posicao'] - tamanho_contexto // 2)
            fim = min(len(texto), c['posicao'] + len(c['texto']) + tamanho_contexto // 2)
            contexto = texto[inicio:fim].strip()

            # Adiciona elipses se truncado
            if inicio > 0:
                contexto = '...' + contexto
            if fim < len(texto):
                contexto = contexto + '...'

            contextos.append(contexto)

        # Remove duplicatas mantendo ordem
        vistos = set()
        unicos = []
        for c in contextos:
            if c not in vistos:
                vistos.add(c)
                unicos.append(c)

        return unicos

    def _detectar_nivel(self, texto: str) -> NivelRating:
        """Detecta o nível de rating exigido."""
        for regex, nivel in self._niveis_compilados.items():
            if regex.search(texto):
                return nivel
        return NivelRating.NAO_ESPECIFICADO

    def _detectar_agencias(self, texto: str) -> List[AgenciaRating]:
        """Detecta agências de rating mencionadas."""
        agencias = []

        for regex, agencia in self._agencias_compiladas.items():
            if regex.search(texto):
                if agencia not in agencias:
                    agencias.append(agencia)

        # Se menciona "agência reconhecida" genericamente
        if re.search(r'agência\s+(?:de\s+)?(?:rating|classificação)\s+(?:reconhecida|autorizada)', texto, re.IGNORECASE):
            if AgenciaRating.QUALQUER not in agencias and not agencias:
                agencias.append(AgenciaRating.QUALQUER)

        return agencias if agencias else [AgenciaRating.NAO_ESPECIFICADO]

    def _detectar_escala_nacional(self, texto: str) -> Optional[bool]:
        """Detecta se aceita escala nacional ou exige global."""
        # Padrões que indicam escala nacional
        if re.search(r'escala\s+(?:nacional|brasileira|local|br)', texto, re.IGNORECASE):
            return True

        # Padrões que indicam escala global
        if re.search(r'escala\s+(?:global|internacional)', texto, re.IGNORECASE):
            return False

        # Se menciona .br nos ratings (ex: brAA, brAAA)
        if re.search(r'br[A-D]{1,3}[\+\-]?', texto, re.IGNORECASE):
            return True

        return None  # Não especificado

    def _detectar_permite_grupo(self, texto: str) -> Optional[bool]:
        """Detecta se permite usar rating do grupo econômico."""
        # Padrões que indicam aceitação de rating do grupo
        if re.search(r'(?:rating|classificação)\s+(?:do\s+)?grupo(?:\s+econômico)?', texto, re.IGNORECASE):
            return True

        # Padrões que exigem rating próprio/isolado
        if re.search(r'(?:rating|classificação)\s+(?:próprio|própria|isolado|isolada|individual)', texto, re.IGNORECASE):
            return False

        return None  # Não especificado

    def _encontrar_clausula(
        self,
        texto: str,
        correspondencias: List[Dict]
    ) -> str:
        """Tenta identificar a cláusula que contém a exigência."""
        # Procura padrões de numeração de cláusulas próximos às correspondências
        for c in correspondencias:
            posicao = c['posicao']

            # Busca cláusula/item antes da posição
            trecho = texto[max(0, posicao - 500):posicao]

            # Padrões de identificação de cláusulas
            padroes_clausula = [
                r'(\d+\.\d+(?:\.\d+)?)\s*[-–]',  # 10.1 ou 10.1.1
                r'(?:cláusula|item|artigo)\s+(\d+(?:\.\d+)?)',
                r'(?:seção|capítulo)\s+([IVX]+|\d+)',
                r'([a-z]\))\s+',  # a), b), etc
                r'(\d+(?:º|ª)?)\s*[-–]',  # 1º, 2ª
            ]

            for padrao in padroes_clausula:
                match = re.search(padrao, trecho, re.IGNORECASE)
                if match:
                    return match.group(1)

        return ""

    def _gerar_observacoes(self, correspondencias: List[Dict]) -> str:
        """Gera observações sobre a detecção."""
        categorias = set(c['categoria'] for c in correspondencias)

        observacoes = []

        if 'exigencia_direta' in categorias:
            observacoes.append("Exigência direta de rating identificada")

        if 'nivel_especifico' in categorias:
            observacoes.append("Nível específico de rating mencionado")

        if 'grau_investimento' in categorias:
            observacoes.append("Exige grau de investimento")

        if 'agencia' in categorias:
            observacoes.append("Agências específicas mencionadas")

        if 'seguro_garantia' in categorias:
            observacoes.append("Contexto de seguro garantia")

        return "; ".join(observacoes)

    def detectar_tipo_garantia(self, texto: str) -> TipoGarantia:
        """Detecta o tipo de garantia mencionado no edital."""
        texto_lower = texto.lower()

        tipos_encontrados = []

        if re.search(r'seguro\s+garantia', texto_lower):
            tipos_encontrados.append(TipoGarantia.SEGURO_GARANTIA)

        if re.search(r'fian[çc]a\s+banc[áa]ria', texto_lower):
            tipos_encontrados.append(TipoGarantia.FIANCA_BANCARIA)

        if re.search(r'cau[çc][ãa]o\s+(?:em\s+)?dinheiro', texto_lower):
            tipos_encontrados.append(TipoGarantia.CAUCAO_DINHEIRO)

        if re.search(r't[ií]tulo(?:s)?\s+(?:da\s+)?d[ií]vida\s+p[úu]blica', texto_lower):
            tipos_encontrados.append(TipoGarantia.TITULO_DIVIDA_PUBLICA)

        if len(tipos_encontrados) > 1:
            return TipoGarantia.MULTIPLA
        elif len(tipos_encontrados) == 1:
            return tipos_encontrados[0]
        else:
            return TipoGarantia.NAO_ESPECIFICADO

    def detectar_percentual_garantia(self, texto: str) -> Optional[float]:
        """Detecta o percentual de garantia exigido."""
        # Padrões comuns de percentual de garantia
        padroes = [
            r'garantia\s+(?:de\s+)?(\d+(?:[,\.]\d+)?)\s*%',
            r'(\d+(?:[,\.]\d+)?)\s*%\s+(?:de\s+)?(?:garantia|do\s+valor)',
            r'percentual\s+(?:de\s+)?(\d+(?:[,\.]\d+)?)\s*%',
            r'correspond(?:ente|er)\s+a\s+(\d+(?:[,\.]\d+)?)\s*%',
        ]

        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                valor = match.group(1).replace(',', '.')
                try:
                    return float(valor)
                except ValueError:
                    pass

        return None

    def analisar_completo(self, texto: str) -> Dict:
        """
        Realiza análise completa do texto.

        Returns:
            Dicionário com todos os resultados da análise
        """
        exigencia = self.detectar(texto)
        tipo_garantia = self.detectar_tipo_garantia(texto)
        percentual = self.detectar_percentual_garantia(texto)

        return {
            'exigencia_rating': exigencia,
            'tipo_garantia': tipo_garantia,
            'percentual_garantia': percentual,
            'tem_exigencia': exigencia.encontrada,
            'resumo': self._gerar_resumo_analise(exigencia, tipo_garantia, percentual)
        }

    def _gerar_resumo_analise(
        self,
        exigencia: ExigenciaRating,
        tipo_garantia: TipoGarantia,
        percentual: Optional[float]
    ) -> str:
        """Gera resumo textual da análise."""
        linhas = []

        if exigencia.encontrada:
            linhas.append("✅ EXIGÊNCIA DE RATING DETECTADA")
            linhas.append(f"   Nível mínimo: {exigencia.nivel_minimo.value}")
            linhas.append(f"   Agências: {', '.join(a.value for a in exigencia.agencias_aceitas)}")

            if exigencia.escala_nacional is not None:
                escala = "Nacional" if exigencia.escala_nacional else "Global"
                linhas.append(f"   Escala: {escala}")

            if exigencia.permite_grupo is not None:
                grupo = "Sim" if exigencia.permite_grupo else "Não"
                linhas.append(f"   Permite rating de grupo: {grupo}")
        else:
            linhas.append("❌ Nenhuma exigência de rating detectada")

        linhas.append(f"\nTipo de Garantia: {tipo_garantia.value}")

        if percentual:
            linhas.append(f"Percentual de Garantia: {percentual}%")

        return '\n'.join(linhas)


# Função de conveniência
def detectar_rating(texto: str) -> ExigenciaRating:
    """
    Função de conveniência para detectar exigências de rating.

    Args:
        texto: Texto do edital

    Returns:
        ExigenciaRating com os detalhes encontrados
    """
    detector = DetectorRating()
    return detector.detectar(texto)


def analisar_edital(texto: str) -> Dict:
    """
    Função de conveniência para análise completa.

    Args:
        texto: Texto do edital

    Returns:
        Dicionário com resultados completos da análise
    """
    detector = DetectorRating()
    return detector.analisar_completo(texto)
