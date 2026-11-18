# -*- coding: utf-8 -*-
"""
Base Legal - Lei 14.133/2021 (Nova Lei de Licitações e Contratos)
================================================================

Este módulo contém a base de conhecimento da Lei 14.133/2021 com foco em:
- Garantias contratuais
- Habilitação de licitantes
- Documentação obrigatória
- Qualificação econômico-financeira
- Seguro-garantia

Autor: Sistema de Análise Jurídica
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


class TipoDispositivo(Enum):
    """Tipos de dispositivos legais."""
    ARTIGO = "artigo"
    PARAGRAFO = "parágrafo"
    INCISO = "inciso"
    ALINEA = "alínea"
    CAPUT = "caput"


class CategoriaLegal(Enum):
    """Categorias temáticas dos dispositivos."""
    GARANTIA = "garantia"
    HABILITACAO = "habilitação"
    QUALIFICACAO_ECONOMICA = "qualificação_econômico_financeira"
    DOCUMENTACAO = "documentação"
    SEGURO = "seguro"
    SANCAO = "sanção"
    PRINCIPIO = "princípio"
    CONTRATACAO = "contratação"
    EXECUCAO = "execução"
    FISCALIZACAO = "fiscalização"


@dataclass
class DispositivoLegal:
    """Representa um dispositivo legal específico."""
    numero: str
    texto: str
    tipo: TipoDispositivo
    categoria: CategoriaLegal
    palavras_chave: List[str] = field(default_factory=list)
    relacionados: List[str] = field(default_factory=list)
    observacoes: str = ""


@dataclass
class ArtigoLei:
    """Representa um artigo completo da lei com seus dispositivos."""
    numero: int
    caput: str
    categoria: CategoriaLegal
    paragrafos: Dict[str, str] = field(default_factory=dict)
    incisos: Dict[str, str] = field(default_factory=dict)
    alineas: Dict[str, Dict[str, str]] = field(default_factory=dict)
    palavras_chave: List[str] = field(default_factory=list)
    relevancia_garantia: int = 0  # 0-10 para relevância em análise de garantias
    aplicavel_cc17_2025: bool = False


class BaseLegal14133:
    """
    Base de conhecimento da Lei 14.133/2021.

    Contém os artigos mais relevantes para análise de licitações
    com foco em garantias, habilitação e qualificação econômico-financeira.
    """

    def __init__(self):
        self.lei = "Lei nº 14.133/2021"
        self.nome = "Lei de Licitações e Contratos Administrativos"
        self.data_publicacao = datetime(2021, 4, 1)
        self.artigos: Dict[int, ArtigoLei] = {}
        self._carregar_base_legal()

    def _carregar_base_legal(self):
        """Carrega todos os artigos relevantes da lei."""

        # =====================================================================
        # TÍTULO I - DISPOSIÇÕES PRELIMINARES
        # =====================================================================

        # Art. 5º - Princípios
        self.artigos[5] = ArtigoLei(
            numero=5,
            caput="""Na aplicação desta Lei, serão observados os princípios da
            legalidade, da impessoalidade, da moralidade, da publicidade,
            da eficiência, do interesse público, da probidade administrativa,
            da igualdade, do planejamento, da transparência, da eficácia,
            da segregação de funções, da motivação, da vinculação ao edital,
            do julgamento objetivo, da segurança jurídica, da razoabilidade,
            da competitividade, da proporcionalidade, da celeridade,
            da economicidade e do desenvolvimento nacional sustentável.""",
            categoria=CategoriaLegal.PRINCIPIO,
            palavras_chave=[
                "princípios", "legalidade", "impessoalidade", "moralidade",
                "eficiência", "interesse público", "vinculação ao edital",
                "julgamento objetivo", "economicidade", "competitividade"
            ],
            relevancia_garantia=8,
            aplicavel_cc17_2025=True
        )

        # =====================================================================
        # TÍTULO II - DAS LICITAÇÕES - CAPÍTULO VI - DA HABILITAÇÃO
        # =====================================================================

        # Art. 62 - Habilitação
        self.artigos[62] = ArtigoLei(
            numero=62,
            caput="""A habilitação é a fase da licitação em que se verifica o
            conjunto de informações e documentos necessários e suficientes para
            demonstrar a capacidade do licitante de realizar o objeto da licitação.""",
            categoria=CategoriaLegal.HABILITACAO,
            palavras_chave=[
                "habilitação", "documentos", "capacidade", "licitante"
            ],
            relevancia_garantia=7,
            aplicavel_cc17_2025=True
        )

        # Art. 63 - Requisitos para habilitação
        self.artigos[63] = ArtigoLei(
            numero=63,
            caput="""Na fase de habilitação das licitações serão observadas as
            seguintes disposições:""",
            categoria=CategoriaLegal.HABILITACAO,
            incisos={
                "I": """serão exigidas dos licitantes a habilitação jurídica e a
                    regularidade fiscal, social e trabalhista;""",
                "II": """poderão ser exigidas dos licitantes a qualificação
                    técnica e a qualificação econômico-financeira;""",
                "III": """será exigida declaração de que o licitante tomou
                    conhecimento de todas as informações e condições locais
                    para cumprimento das obrigações objeto da licitação;""",
                "IV": """será exigida declaração formal de que o licitante é
                    microempresa ou empresa de pequeno porte, se for o caso,
                    para fins do disposto nos arts. 42 a 49 da Lei Complementar
                    nº 123, de 14 de dezembro de 2006;""",
            },
            palavras_chave=[
                "habilitação jurídica", "regularidade fiscal", "qualificação técnica",
                "qualificação econômico-financeira", "declaração"
            ],
            relevancia_garantia=9,
            aplicavel_cc17_2025=True
        )

        # Art. 67 - Qualificação econômico-financeira
        self.artigos[67] = ArtigoLei(
            numero=67,
            caput="""A documentação relativa à qualificação econômico-financeira
            será restrita a:""",
            categoria=CategoriaLegal.QUALIFICACAO_ECONOMICA,
            incisos={
                "I": """balanço patrimonial, demonstração de resultado de exercício
                    e demais demonstrações contábeis dos 2 (dois) últimos exercícios
                    sociais;""",
                "II": """certidão negativa de feitos sobre falência expedida pelo
                    distribuidor da sede do licitante;""",
            },
            paragrafos={
                "§1º": """A critério da Administração, poderá ser exigido, ainda,
                    como requisito de qualificação econômico-financeira, capital
                    mínimo, ou patrimônio líquido mínimo, ou garantias de até 1%
                    (um por cento) do valor estimado da contratação.""",
                "§2º": """As exigências a que se refere o § 1º deste artigo,
                    além das referidas nos incisos I e II do caput deste artigo,
                    deverão ter parâmetros aferidos em valores absolutos,
                    e a documentação exigida será restrita àquela indispensável
                    à demonstração da condição exigida no edital.""",
            },
            palavras_chave=[
                "qualificação econômico-financeira", "balanço patrimonial",
                "capital mínimo", "patrimônio líquido", "garantias",
                "demonstrações contábeis"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 70 - Documentação obrigatória de habilitação
        self.artigos[70] = ArtigoLei(
            numero=70,
            caput="""A documentação referida neste Capítulo poderá ser:""",
            categoria=CategoriaLegal.DOCUMENTACAO,
            incisos={
                "I": """apresentada em original, por cópia ou por qualquer outro
                    meio expressamente admitido pela Administração;""",
                "II": """substituída por registro cadastral emitido por órgão
                    ou entidade pública, desde que previsto no edital e que
                    o registro tenha sido feito em obediência ao disposto
                    nesta Lei;""",
                "III": """dispensada, total ou parcialmente, nas contratações
                    para entrega imediata, nas contratações em valores inferiores
                    a 1/4 (um quarto) do limite para dispensa de licitação
                    para compras em geral e nas contratações de produto para
                    pesquisa e desenvolvimento até o valor de R$ 300.000,00
                    (trezentos mil reais).""",
            },
            palavras_chave=[
                "documentação", "original", "cópia", "registro cadastral"
            ],
            relevancia_garantia=6,
            aplicavel_cc17_2025=True
        )

        # =====================================================================
        # TÍTULO III - DOS CONTRATOS - CAPÍTULO II - DAS GARANTIAS
        # =====================================================================

        # Art. 96 - Garantia de execução contratual
        self.artigos[96] = ArtigoLei(
            numero=96,
            caput="""A critério da autoridade competente, em cada caso, poderá
            ser exigida, mediante previsão no edital, prestação de garantia
            nas contratações de obras, serviços e fornecimentos.""",
            categoria=CategoriaLegal.GARANTIA,
            paragrafos={
                "§1º": """Caberá ao contratado optar por uma das seguintes
                    modalidades de garantia:
                    I - caução em dinheiro ou em títulos da dívida pública
                    emitidos sob a forma escritural, mediante registro em
                    sistema centralizado de liquidação e de custódia autorizado
                    pelo Banco Central do Brasil, e avaliados por seus valores
                    econômicos, conforme definido pelo Ministério da Economia;
                    II - seguro-garantia;
                    III - fiança bancária emitida por banco ou instituição
                    financeira devidamente autorizada a operar no País pelo
                    Banco Central do Brasil.""",
                "§2º": """Na hipótese de suspensão do contrato por ordem ou
                    inadimplemento da Administração, o contratado ficará
                    desobrigado de renovar a garantia ou de endossar a apólice
                    de seguro até a ordem de reinício da execução ou o
                    adimplemento pela Administração.""",
                "§3º": """O edital fixará prazo mínimo de 1 (um) mês, contado
                    da data de homologação da licitação e anterior à assinatura
                    do contrato, para a prestação da garantia pelo contratado
                    quando optar pela modalidade prevista no inciso II do § 1º
                    deste artigo.""",
                "§4º": """Na contratação de obras e serviços de engenharia,
                    o edital poderá exigir a prestação da garantia na
                    modalidade seguro-garantia e prever a obrigação de a
                    seguradora, em caso de inadimplemento pelo contratado,
                    assumir a execução e concluir o objeto do contrato.""",
            },
            palavras_chave=[
                "garantia", "caução", "seguro-garantia", "fiança bancária",
                "apólice", "execução contratual"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 97 - Percentuais de garantia
        self.artigos[97] = ArtigoLei(
            numero=97,
            caput="""O valor da garantia não excederá 5% (cinco por cento) do
            valor inicial do contrato, exceto nas seguintes hipóteses, em que
            poderá ser elevado para até 10% (dez por cento):""",
            categoria=CategoriaLegal.GARANTIA,
            incisos={
                "I": """contratação de serviços e fornecimentos de grande vulto;""",
                "II": """contratação de obras, serviços e fornecimentos em que
                    haja previsão de entrega de bens pela Administração, dos
                    quais o contratado ficará depositário."""
            },
            paragrafos={
                "§1º": """Nas contratações de obras, serviços e fornecimentos
                    de grande vulto, poderá ser exigida prestação de garantia,
                    sob a modalidade de seguro-garantia, em percentual
                    equivalente a até 30% (trinta por cento) do valor inicial
                    do contrato.""",
                "§2º": """Para os fins desta Lei, considera-se grande vulto
                    a licitação de valor estimado superior a R$ 200.000.000,00
                    (duzentos milhões de reais).""",
            },
            palavras_chave=[
                "percentual garantia", "5%", "10%", "30%", "grande vulto",
                "seguro-garantia"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 98 - Condições da garantia
        self.artigos[98] = ArtigoLei(
            numero=98,
            caput="""Nas contratações de obras, serviços e fornecimentos,
            a garantia poderá ser de até 5% (cinco por cento) do valor inicial
            do contrato, devendo ser atualizada nas mesmas condições daquele.""",
            categoria=CategoriaLegal.GARANTIA,
            incisos={
                "I": """preveja prazo de vigência de, no mínimo, 3 (três) meses
                    a mais do que a vigência estabelecida no contrato, devendo
                    esse prazo ser renovado nos termos do regulamento;""",
                "II": """estabeleça cobertura para:
                    a) prejuízos advindos do não cumprimento do objeto do contrato
                    e do não adimplemento das demais obrigações nele previstas;
                    b) multas moratórias e punitivas aplicadas pela Administração
                    ao contratado;
                    c) obrigações trabalhistas e previdenciárias de qualquer
                    natureza, não adimplidas pelo contratado, quando couber.""",
            },
            palavras_chave=[
                "vigência", "cobertura", "prejuízos", "multas", "obrigações trabalhistas"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 99 - Seguro-garantia
        self.artigos[99] = ArtigoLei(
            numero=99,
            caput="""Nas contratações de obras e serviços de engenharia de
            grande vulto, poderá ser exigida a prestação de garantia, na
            modalidade seguro-garantia, com cláusula de retomada prevista
            no art. 102 desta Lei, em percentual equivalente a até 30%
            (trinta por cento) do valor inicial do contrato.""",
            categoria=CategoriaLegal.GARANTIA,
            paragrafos={
                "§1º": """A seguradora deverá firmar o contrato de
                    seguro-garantia, prestando as informações exigidas
                    pelo órgão ou entidade contratante.""",
                "§2º": """Em caso de inadimplemento do contratado,
                    a seguradora deverá, na forma prevista no contrato,
                    assumir a execução e concluir o objeto do contrato,
                    observado o disposto no art. 102 desta Lei.""",
            },
            palavras_chave=[
                "seguro-garantia", "retomada", "seguradora", "inadimplemento",
                "30%", "grande vulto"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 100 - Utilização da garantia
        self.artigos[100] = ArtigoLei(
            numero=100,
            caput="""A garantia prestada pelo contratado será liberada ou
            restituída após a fiel execução do contrato ou após a sua
            extinção por culpa exclusiva da Administração e, quando em
            dinheiro, atualizada monetariamente.""",
            categoria=CategoriaLegal.GARANTIA,
            palavras_chave=[
                "liberação garantia", "restituição", "extinção contrato"
            ],
            relevancia_garantia=8,
            aplicavel_cc17_2025=True
        )

        # Art. 102 - Cláusula de retomada
        self.artigos[102] = ArtigoLei(
            numero=102,
            caput="""Na contratação de obras e serviços de engenharia, o edital
            poderá exigir a prestação de garantia na modalidade seguro-garantia
            e prever a obrigação de a seguradora, em caso de inadimplemento
            pelo contratado, assumir a execução e concluir o objeto do
            contrato, hipótese em que:""",
            categoria=CategoriaLegal.GARANTIA,
            incisos={
                "I": """a seguradora deverá apresentar, no prazo máximo de 1
                    (um) mês, contado da data de inadimplemento, proposta para
                    conclusão do contrato pelo preço da apólice deduzidos os
                    valores pagos pela Administração ao contratado, ou,
                    alternativamente, comprovar o início das tratativas para
                    a celebração do contrato de empreitada com empresa distinta
                    da contratada;""",
                "II": """no caso de a seguradora optar pela celebração de
                    contrato de empreitada, deverá apresentar à Administração
                    empresa idônea para a conclusão do contrato pelo preço
                    da apólice deduzidos os valores já pagos pelo contratante
                    ao contratado inadimplente;""",
                "III": """a Administração concederá à seguradora o prazo de 3
                    (três) meses, contado da data de inadimplemento,
                    para conclusão dos trâmites para assunção da obra ou
                    serviço de engenharia;""",
            },
            palavras_chave=[
                "retomada", "seguradora", "inadimplemento", "empreitada",
                "apólice", "conclusão contrato"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # =====================================================================
        # TÍTULO IV - DAS IRREGULARIDADES - CAPÍTULO I - DAS INFRAÇÕES
        # =====================================================================

        # Art. 155 - Sanções administrativas
        self.artigos[155] = ArtigoLei(
            numero=155,
            caput="""O licitante ou o contratado será responsabilizado
            administrativamente pelas seguintes infrações:""",
            categoria=CategoriaLegal.SANCAO,
            incisos={
                "I": """dar causa à inexecução parcial do contrato;""",
                "II": """dar causa à inexecução parcial do contrato que cause
                    grave dano à Administração, ao funcionamento dos serviços
                    públicos ou ao interesse coletivo;""",
                "III": """dar causa à inexecução total do contrato;""",
                "IV": """deixar de entregar a documentação exigida para o
                    certame;""",
                "V": """não manter a proposta, salvo em decorrência de fato
                    superveniente devidamente justificado;""",
                "VI": """não celebrar o contrato ou não entregar a documentação
                    exigida para a contratação, quando convocado dentro do
                    prazo de validade de sua proposta;""",
                "VII": """ensejar o retardamento da execução ou da entrega do
                    objeto da licitação sem motivo justificado;""",
                "VIII": """apresentar declaração ou documentação falsa exigida
                    para o certame ou prestar declaração falsa durante a
                    licitação ou a execução do contrato;""",
                "IX": """fraudar a licitação ou praticar ato fraudulento na
                    execução do contrato;""",
                "X": """comportar-se de modo inidôneo ou cometer fraude de
                    qualquer natureza;""",
                "XI": """praticar atos ilícitos com vistas a frustrar os
                    objetivos da licitação;""",
                "XII": """praticar ato lesivo previsto no art. 5º da Lei nº
                    12.846, de 1º de agosto de 2013.""",
            },
            palavras_chave=[
                "sanções", "infrações", "inexecução", "documentação falsa",
                "fraude", "inidôneo"
            ],
            relevancia_garantia=9,
            aplicavel_cc17_2025=True
        )

        # Art. 156 - Penalidades
        self.artigos[156] = ArtigoLei(
            numero=156,
            caput="""Serão aplicadas ao responsável pelas infrações
            administrativas previstas nesta Lei as seguintes sanções:""",
            categoria=CategoriaLegal.SANCAO,
            incisos={
                "I": """advertência;""",
                "II": """multa;""",
                "III": """impedimento de licitar e contratar;""",
                "IV": """declaração de inidoneidade para licitar ou contratar.""",
            },
            paragrafos={
                "§1º": """Na aplicação das sanções serão considerados:
                    I - a natureza e a gravidade da infração cometida;
                    II - as peculiaridades do caso concreto;
                    III - as circunstâncias agravantes ou atenuantes;
                    IV - os danos que dela provierem para a Administração Pública;
                    V - a implantação ou o aperfeiçoamento de programa de
                    integridade, conforme normas e orientações dos órgãos
                    de controle.""",
            },
            palavras_chave=[
                "advertência", "multa", "impedimento", "inidoneidade", "penalidades"
            ],
            relevancia_garantia=7,
            aplicavel_cc17_2025=True
        )

        # =====================================================================
        # ARTIGOS ADICIONAIS RELEVANTES
        # =====================================================================

        # Art. 11 - Objetivos do processo licitatório
        self.artigos[11] = ArtigoLei(
            numero=11,
            caput="""O processo licitatório tem por objetivos:""",
            categoria=CategoriaLegal.PRINCIPIO,
            incisos={
                "I": """assegurar a seleção da proposta apta a gerar o
                    resultado de contratação mais vantajoso para a
                    Administração Pública, inclusive no que se refere ao
                    ciclo de vida do objeto;""",
                "II": """assegurar tratamento isonômico entre os licitantes,
                    bem como a justa competição;""",
                "III": """evitar contratações com sobrepreço ou com preços
                    manifestamente inexequíveis e superfaturamento na
                    execução dos contratos;""",
                "IV": """incentivar a inovação e o desenvolvimento nacional
                    sustentável.""",
            },
            paragrafos={
                "parágrafo único": """A alta administração do órgão ou entidade
                    é responsável pela governança das contratações e deve
                    implementar processos e estruturas, inclusive de gestão
                    de riscos e controles internos, para avaliar, direcionar
                    e monitorar os processos licitatórios e os respectivos
                    contratos, com o intuito de alcançar os objetivos
                    estabelecidos no caput deste artigo, promover um ambiente
                    íntegro e confiável, assegurar o alinhamento das
                    contratações ao planejamento estratégico e às leis
                    orçamentárias e promover eficiência, efetividade e
                    eficácia em suas contratações.""",
            },
            palavras_chave=[
                "objetivos", "vantajosidade", "isonomia", "sobrepreço",
                "governança", "gestão de riscos"
            ],
            relevancia_garantia=10,
            aplicavel_cc17_2025=True
        )

        # Art. 18 - Fase preparatória
        self.artigos[18] = ArtigoLei(
            numero=18,
            caput="""A fase preparatória do processo licitatório é caracterizada
            pelo planejamento e deve compatibilizar-se com o plano de
            contratações anual de que trata o inciso VII do caput do art. 12
            desta Lei, sempre que elaborado, e com as leis orçamentárias,
            bem como abordar todas as considerações técnicas, mercadológicas
            e de gestão que podem interferir na contratação.""",
            categoria=CategoriaLegal.CONTRATACAO,
            paragrafos={
                "§1º": """O estudo técnico preliminar a que se refere o
                    inciso I do caput deste artigo deverá evidenciar o
                    problema a ser resolvido e a sua melhor solução, de modo
                    a permitir a avaliação da viabilidade técnica e econômica
                    da contratação, e conterá os seguintes elementos:
                    I - descrição da necessidade da contratação, considerado
                    o problema a ser resolvido sob a perspectiva do interesse
                    público;
                    II - demonstração da previsão da contratação no plano de
                    contratações anual, sempre que elaborado, de modo a
                    indicar o seu alinhamento com o planejamento da
                    Administração;
                    III - requisitos da contratação;
                    IV - estimativas das quantidades para a contratação,
                    acompanhadas das memórias de cálculo e dos documentos
                    que lhes dão suporte, que considerem interdependências
                    com outras contratações, de modo a possibilitar economia
                    de escala;
                    V - levantamento de mercado, que consiste na análise das
                    alternativas possíveis, e justificativa técnica e
                    econômica da escolha do tipo de solução a contratar;
                    VI - estimativa do valor da contratação, acompanhada dos
                    preços unitários referenciais, das memórias de cálculo e
                    dos documentos que lhe dão suporte, que poderão constar
                    de anexo classificado, se a Administração optar por
                    preservar o seu sigilo até a conclusão da licitação;
                    VII - descrição da solução como um todo, inclusive das
                    exigências relacionadas à manutenção e à assistência
                    técnica, quando for o caso;
                    VIII - justificativas para o parcelamento ou não da
                    contratação;
                    IX - demonstrativo dos resultados pretendidos em termos
                    de economicidade e de melhor aproveitamento dos recursos
                    humanos, materiais e financeiros disponíveis;
                    X - providências a serem adotadas pela Administração
                    previamente à celebração do contrato, inclusive quanto
                    à capacitação de servidores ou de empregados para
                    fiscalização e gestão contratual;
                    XI - contratações correlatas e/ou interdependentes;
                    XII - descrição de possíveis impactos ambientais e
                    respectivas medidas mitigadoras, incluídos requisitos
                    de baixo consumo de energia e de outros recursos, bem
                    como logística reversa para desfazimento e reciclagem
                    de bens e refugos, quando aplicável;
                    XIII - posicionamento conclusivo sobre a adequação da
                    contratação para o atendimento da necessidade a que se
                    destina.""",
            },
            palavras_chave=[
                "fase preparatória", "estudo técnico preliminar", "planejamento",
                "viabilidade", "levantamento de mercado"
            ],
            relevancia_garantia=8,
            aplicavel_cc17_2025=True
        )

        # Art. 25 - Critérios de julgamento
        self.artigos[25] = ArtigoLei(
            numero=25,
            caput="""O critério de julgamento das propostas será o de menor
            preço ou maior desconto, técnica e preço, melhor técnica ou
            conteúdo artístico, maior lance, no caso de leilão, ou maior
            retorno econômico.""",
            categoria=CategoriaLegal.CONTRATACAO,
            incisos={
                "I": """menor preço;""",
                "II": """maior desconto;""",
                "III": """melhor técnica ou conteúdo artístico;""",
                "IV": """técnica e preço;""",
                "V": """maior lance, no caso de leilão;""",
                "VI": """maior retorno econômico.""",
            },
            paragrafos={
                "§1º": """O critério de julgamento de menor preço ou maior
                    desconto considerará o menor dispêndio para a Administração,
                    atendidos os parâmetros mínimos de qualidade definidos
                    no edital.""",
            },
            palavras_chave=[
                "critério julgamento", "menor preço", "maior desconto",
                "técnica e preço", "vantajosidade"
            ],
            relevancia_garantia=9,
            aplicavel_cc17_2025=True
        )

        # Art. 72 - Fase de habilitação
        self.artigos[72] = ArtigoLei(
            numero=72,
            caput="""Encerrada a fase de julgamento, após a verificação de
            conformidade da proposta classificada em primeiro lugar com os
            requisitos estabelecidos no edital, inclusive quanto à sua
            adequação ao preço estimado para a contratação, será aberta a
            fase de habilitação.""",
            categoria=CategoriaLegal.HABILITACAO,
            paragrafos={
                "§1º": """A Administração poderá, em relação ao licitante
                    provisoriamente vencedor, realizar análise e diligências
                    necessárias para aferir a exequibilidade da proposta ou
                    exigir a demonstração de sua exequibilidade.""",
            },
            palavras_chave=[
                "fase habilitação", "conformidade", "diligências", "exequibilidade"
            ],
            relevancia_garantia=8,
            aplicavel_cc17_2025=True
        )

    def buscar_por_categoria(self, categoria: CategoriaLegal) -> List[ArtigoLei]:
        """Busca artigos por categoria temática."""
        return [
            artigo for artigo in self.artigos.values()
            if artigo.categoria == categoria
        ]

    def buscar_por_palavra_chave(self, palavra: str) -> List[ArtigoLei]:
        """Busca artigos que contenham determinada palavra-chave."""
        palavra_lower = palavra.lower()
        resultados = []
        for artigo in self.artigos.values():
            if any(palavra_lower in kw.lower() for kw in artigo.palavras_chave):
                resultados.append(artigo)
            elif palavra_lower in artigo.caput.lower():
                resultados.append(artigo)
        return resultados

    def buscar_artigos_garantia(self) -> List[ArtigoLei]:
        """Retorna todos os artigos relacionados a garantias."""
        return sorted(
            [a for a in self.artigos.values() if a.relevancia_garantia >= 7],
            key=lambda x: x.relevancia_garantia,
            reverse=True
        )

    def buscar_artigos_aplicaveis_cc17(self) -> List[ArtigoLei]:
        """Retorna artigos aplicáveis ao certame CC17/2025."""
        return [a for a in self.artigos.values() if a.aplicavel_cc17_2025]

    def get_artigo(self, numero: int) -> Optional[ArtigoLei]:
        """Retorna um artigo específico pelo número."""
        return self.artigos.get(numero)

    def get_texto_completo_artigo(self, numero: int) -> str:
        """Retorna o texto completo formatado de um artigo."""
        artigo = self.get_artigo(numero)
        if not artigo:
            return f"Artigo {numero} não encontrado."

        texto = f"Art. {artigo.numero}. {artigo.caput}\n"

        if artigo.incisos:
            for num, inciso in artigo.incisos.items():
                texto += f"  {num} - {inciso}\n"

        if artigo.paragrafos:
            for num, paragrafo in artigo.paragrafos.items():
                texto += f"  {num} {paragrafo}\n"

        return texto

    def gerar_fundamentacao_legal(self, categorias: List[CategoriaLegal]) -> str:
        """
        Gera fundamentação legal baseada nas categorias selecionadas.

        Args:
            categorias: Lista de categorias para fundamentação

        Returns:
            Texto formatado com a fundamentação legal
        """
        fundamentacao = "FUNDAMENTAÇÃO LEGAL\n"
        fundamentacao += "=" * 50 + "\n\n"
        fundamentacao += f"Base Legal: {self.lei} - {self.nome}\n\n"

        artigos_selecionados = []
        for categoria in categorias:
            artigos_selecionados.extend(self.buscar_por_categoria(categoria))

        # Remove duplicatas mantendo ordem
        artigos_unicos = list({a.numero: a for a in artigos_selecionados}.values())
        artigos_unicos.sort(key=lambda x: x.numero)

        for artigo in artigos_unicos:
            fundamentacao += f"Art. {artigo.numero}\n"
            fundamentacao += "-" * 30 + "\n"
            fundamentacao += f"Categoria: {artigo.categoria.value}\n"
            fundamentacao += f"Dispositivo: {artigo.caput[:200]}...\n\n"

        return fundamentacao


# Instância global para uso no sistema
BASE_LEGAL = BaseLegal14133()
