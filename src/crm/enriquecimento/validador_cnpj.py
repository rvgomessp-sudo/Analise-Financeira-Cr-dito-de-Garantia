"""
Validador de CNPJ

Valida dígitos verificadores e formato do CNPJ.
Em produção, integra com APIs da Receita Federal para validação completa.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
import re


@dataclass
class ResultadoValidacao:
    """Resultado da validação de CNPJ"""
    cnpj: str
    valido: bool
    formatado: str = ""
    erro: str = ""
    dados_receita: Optional[Dict] = None
    data_validacao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'cnpj': self.cnpj,
            'valido': self.valido,
            'formatado': self.formatado,
            'erro': self.erro,
            'data_validacao': self.data_validacao.isoformat(),
        }


class ValidadorCNPJ:
    """
    Validador de CNPJ com verificação de dígitos.

    Métodos:
        validar(cnpj) - Valida formato e dígitos verificadores
        normalizar(cnpj) - Remove formatação, mantém 14 dígitos
        formatar(cnpj) - Aplica formatação XX.XXX.XXX/XXXX-XX
        validar_lote(cnpjs) - Valida lista de CNPJs
    """

    CNPJS_INVALIDOS = {
        '00000000000000', '11111111111111', '22222222222222',
        '33333333333333', '44444444444444', '55555555555555',
        '66666666666666', '77777777777777', '88888888888888',
        '99999999999999',
    }

    @staticmethod
    def normalizar(cnpj: str) -> str:
        """Remove formatação do CNPJ, mantém 14 dígitos"""
        return re.sub(r'[^0-9]', '', cnpj)

    @staticmethod
    def formatar(cnpj: str) -> str:
        """Formata CNPJ: XX.XXX.XXX/XXXX-XX"""
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_limpo) != 14:
            return cnpj
        return (f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/"
                f"{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}")

    def validar(self, cnpj: str) -> ResultadoValidacao:
        """
        Valida CNPJ verificando formato e dígitos verificadores.

        Args:
            cnpj: CNPJ em qualquer formato

        Returns:
            ResultadoValidacao com status e detalhes
        """
        cnpj_limpo = self.normalizar(cnpj)

        # Verifica tamanho
        if len(cnpj_limpo) != 14:
            return ResultadoValidacao(
                cnpj=cnpj_limpo,
                valido=False,
                erro=f"CNPJ deve ter 14 dígitos. Recebido: {len(cnpj_limpo)}",
            )

        # Verifica se é numérico
        if not cnpj_limpo.isdigit():
            return ResultadoValidacao(
                cnpj=cnpj_limpo,
                valido=False,
                erro="CNPJ deve conter apenas dígitos",
            )

        # Verifica sequências inválidas
        if cnpj_limpo in self.CNPJS_INVALIDOS:
            return ResultadoValidacao(
                cnpj=cnpj_limpo,
                valido=False,
                erro="CNPJ com sequência inválida",
            )

        # Verifica dígitos verificadores
        if not self._verificar_digitos(cnpj_limpo):
            return ResultadoValidacao(
                cnpj=cnpj_limpo,
                valido=False,
                erro="Dígitos verificadores inválidos",
            )

        return ResultadoValidacao(
            cnpj=cnpj_limpo,
            valido=True,
            formatado=self.formatar(cnpj_limpo),
        )

    def _verificar_digitos(self, cnpj: str) -> bool:
        """Verifica os dois dígitos verificadores do CNPJ"""
        # Primeiro dígito
        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
        resto = soma % 11
        digito_1 = 0 if resto < 2 else 11 - resto

        if int(cnpj[12]) != digito_1:
            return False

        # Segundo dígito
        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
        resto = soma % 11
        digito_2 = 0 if resto < 2 else 11 - resto

        return int(cnpj[13]) == digito_2

    def validar_lote(self, cnpjs: List[str]) -> List[ResultadoValidacao]:
        """Valida uma lista de CNPJs"""
        return [self.validar(cnpj) for cnpj in cnpjs]

    def extrair_raiz(self, cnpj: str) -> str:
        """Extrai os 8 primeiros dígitos (raiz/base) do CNPJ"""
        cnpj_limpo = self.normalizar(cnpj)
        return cnpj_limpo[:8]

    def extrair_filial(self, cnpj: str) -> str:
        """Extrai os dígitos 9-12 (ordem do estabelecimento)"""
        cnpj_limpo = self.normalizar(cnpj)
        return cnpj_limpo[8:12]

    def eh_matriz(self, cnpj: str) -> bool:
        """Verifica se o CNPJ é de matriz (filial = 0001)"""
        return self.extrair_filial(cnpj) == "0001"

    def mesma_empresa(self, cnpj1: str, cnpj2: str) -> bool:
        """Verifica se dois CNPJs pertencem à mesma empresa (mesma raiz)"""
        return self.extrair_raiz(cnpj1) == self.extrair_raiz(cnpj2)
