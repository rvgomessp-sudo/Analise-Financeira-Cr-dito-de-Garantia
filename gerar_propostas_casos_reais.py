#!/usr/bin/env python3
"""
Geração de Propostas - Casos Reais
"""

from datetime import datetime, date, timedelta
from decimal import Decimal

from src.comercial.operacao import (
    Operacao, TipoOperacao, TipoGarantia, OrigemOperacao,
    criar_fases_padrao
)
from src.comercial.tomador import (
    Tomador, PorteTomador, SetorTomador, NivelContato,
    ClassificacaoRisco, criar_tomador_novo
)
from src.comercial.qualificador import QualificadorOperacao
from src.comercial.proposta import GeradorProposta


def gerar_caso_distribuidora():
    """Caso 1: Distribuidora de Alimentos - ICMS Anglo Americana"""

    print("=" * 80)
    print("CASO 1: DISTRIBUIDORA DE ALIMENTOS - GARANTIA ICMS")
    print("=" * 80)

    # Criar tomador
    tomador = criar_tomador_novo(
        id="DIST001",
        razao_social="Distribuidora de Alimentos S.A.",
        cnpj="XX.XXX.XXX/0001-XX",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.COMERCIO,
        contato_nome="[Chefe do Jurídico]",
        contato_cargo="Chefe do Jurídico",
        contato_email="juridico@distribuidora.com.br",
        nome_fantasia="Distribuidora Alimentos",
        contato_nivel=NivelContato.DIRETORIA,
        faturamento_anual=Decimal('10000000000')  # 10 Bi
    )

    # RED FLAG CRÍTICO: Geo é o corretor atual
    tomador.corretores_conhecidos = ["Geo Seguros"]
    tomador.adicionar_red_flag(
        categoria="Concorrência",
        descricao="Corretor atual é Geo - família dona da Pottencial (seguradora líder)",
        severidade=5,
        fonte="Informação do caso"
    )
    tomador.adicionar_red_flag(
        categoria="Relacionamento",
        descricao="Contato via Jurídico, não decisor final",
        severidade=2,
        fonte="Análise de relacionamento"
    )

    # Histórico positivo
    from src.comercial.tomador import HistoricoOperacao
    tomador.historico.adicionar_operacao(HistoricoOperacao(
        data=datetime(2024, 1, 1),
        tipo="Emissão anterior",
        valor_operacao=Decimal('50000000'),  # Valor estimado
        valor_honorarios=Decimal('100000'),
        valor_pago=Decimal('100000'),
        valor_pendente=Decimal('0'),
        status="Concluída",
        observacoes="Emissão de grande valor - histórico positivo"
    ))

    tomador.calcular_score_risco()

    # Criar operação
    operacao = Operacao(
        id="OP_DIST_001",
        nome="Garantia de Pagamento ICMS - Anglo Americana",
        tomador_id=tomador.id,
        tomador_nome=tomador.razao_social,
        tomador_cnpj=tomador.cnpj,
        tipo_operacao=TipoOperacao.FINANCEIRA,
        tipo_garantia=TipoGarantia.FINANCEIRA,
        valor_garantia=Decimal('10000000'),  # 10 Mi
        valor_contrato=Decimal('10000000'),
        descricao="Garantia de pagamento para compra de ICMS da Anglo Americana. "
                  "Operação recusada pelo mercado convencional.",
        origem=OrigemOperacao.RETORNO_CLIENTE,
        contato_nome=tomador.contato_nome,
        contato_cargo=tomador.contato_cargo,
        contato_email=tomador.contato_email,
        contato_telefone="",
        ja_tentou_outros_corretores=True,
        corretores_anteriores=["Geo Seguros"]
    )
    operacao.adicionar_red_flag("Corretor Geo no histórico - risco de desvio para Pottencial")

    # Qualificar
    qualificador = QualificadorOperacao()
    analise = qualificador.qualificar(operacao, tomador)

    print("\n" + qualificador.gerar_resumo_executivo(analise))

    # Gerar proposta
    gerador = GeradorProposta()
    proposta = gerador.gerar_proposta(operacao, tomador, analise, "PC-DIST-2024-001")

    print("\n" + "=" * 80)
    print("PROPOSTA COMERCIAL")
    print("=" * 80)
    print(proposta.gerar_texto())

    # Scripts de abordagem (é retomada de cliente)
    print("\n" + "=" * 80)
    print("SCRIPT DE RETOMADA - CASO DISTRIBUIDORA")
    print("=" * 80)

    script_retomada = f"""
══════════════════════════════════════════════════════════════════════════════
SCRIPT: RETOMADA DE CONTATO - DISTRIBUIDORA ALIMENTOS
Contexto: Cliente existente, operação recusada no mercado, Geo é corretor atual
══════════════════════════════════════════════════════════════════════════════

MENSAGEM PARA A CHEFE DO JURÍDICO:

Prezada [Nome],

Espero que esteja bem.

Estou retomando o contato sobre a operação de garantia de pagamento
para a compra de ICMS da Anglo Americana.

Sei que essa operação foi recusada no mercado. Isso acontece porque
garantias financeiras (garantia de pagamento) são a modalidade mais
restritiva do seguro garantia. A maioria das seguradoras simplesmente
não trabalha com esse tipo de risco.

Nossa especialidade é justamente estruturar operações que o mercado
recusa. Já resolvemos casos similares onde a abordagem convencional
não funcionou.

Para avançar, preciso fazer um diagnóstico técnico do caso:
• Entender por que exatamente foi recusado
• Analisar a estrutura da operação com a Anglo
• Identificar qual caminho de aprovação é viável
• Mapear as seguradoras com apetite para este risco

Esse diagnóstico tem um investimento de R$ {analise.valor_recomendado_diagnostico:,.2f}.

Por que cobramos pelo diagnóstico?

Porque o trabalho técnico acontece ANTES da aprovação. Vamos analisar
em profundidade, buscar na legislação, estruturar a operação. Isso tem
valor independente do resultado.

Se o diagnóstico indicar viabilidade, apresentamos proposta para a
fase de execução. A decisão de continuar é de vocês.

Posso enviar a proposta formal?

Atenciosamente,
[Seu nome]

══════════════════════════════════════════════════════════════════════════════
PONTOS DE ATENÇÃO ESPECÍFICOS DESTE CASO:
══════════════════════════════════════════════════════════════════════════════

🚨 ALERTA CRÍTICO: GEO É O CORRETOR ATUAL

A família Geo é dona da Pottencial. Isso significa:
1. Se você estruturar a operação, Geo pode emitir pela Pottencial
2. Você faz o trabalho, ele leva a comissão
3. Você pode nem receber os honorários

PROTEÇÕES NECESSÁRIAS:

1. DIAGNÓSTICO 100% ANTECIPADO - NÃO NEGOCIÁVEL
   Não envie NENHUMA análise sem pagamento confirmado

2. CONTRATO COM CLÁUSULA DE EXCLUSIVIDADE REFORÇADA
   "Durante a vigência deste contrato e por 12 meses após,
    a CONTRATANTE se compromete a não utilizar os estudos,
    análises e estruturações desenvolvidas para emissão
    com qualquer outro corretor."

3. CLÁUSULA DE PENALIDADE SEVERA
   "Em caso de emissão por outro corretor utilizando a
    estruturação desenvolvida: multa de 10x o valor dos
    honorários + perdas e danos."

4. DOCUMENTAR TUDO
   Cada e-mail, cada ligação, cada documento enviado.
   Se for para litígio, você precisa de evidências.

5. CONSIDERAR NÃO ENTRAR
   Score de viabilidade: {analise.score_viabilidade:.1f}/100
   O risco de desvio para o Geo é MUITO ALTO.
   Avalie se vale a pena.

══════════════════════════════════════════════════════════════════════════════
"""
    print(script_retomada)

    return proposta, analise


def gerar_caso_agronegocio():
    """Caso 2: Exportação de Grãos - Agronegócio"""

    print("\n" + "=" * 80)
    print("CASO 2: EXPORTAÇÃO DE GRÃOS - AGRONEGÓCIO")
    print("=" * 80)

    # Criar tomador
    tomador = criar_tomador_novo(
        id="AGRO001",
        razao_social="Trading Exportadora de Grãos Ltda",
        cnpj="YY.YYY.YYY/0001-YY",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.AGRONEGOCIO,
        contato_nome="[Contato Principal]",
        contato_cargo="Diretor Comercial",
        contato_email="comercial@trading.com.br",
        nome_fantasia="Trading Grãos",
        contato_nivel=NivelContato.DIRETORIA
    )

    tomador.calcular_score_risco()

    # Criar operação
    operacao = Operacao(
        id="OP_AGRO_001",
        nome="Estruturação Exportação de Grãos - Garantia Internacional",
        tomador_id=tomador.id,
        tomador_nome=tomador.razao_social,
        tomador_cnpj=tomador.cnpj,
        tipo_operacao=TipoOperacao.OUTRO,
        tipo_garantia=TipoGarantia.FINANCEIRA,
        valor_garantia=Decimal('50000000'),  # Estimativa - 50 Mi
        valor_contrato=Decimal('100000000'),  # Estimativa
        descricao="""
        Estruturação complexa de operação de exportação de grãos:

        PROBLEMA:
        - Antecipação de pagamento da exportação não aprovada
        - Necessidade de garantir recebimento no exterior
        - OU garantir retorno/destinação da mercadoria

        COMPLEXIDADE:
        - Operação internacional
        - Múltiplas jurisdições
        - Risco de performance + risco financeiro
        - Estruturação não convencional
        """,
        origem=OrigemOperacao.DEMANDA_PASSIVA,
        contato_nome=tomador.contato_nome,
        contato_cargo=tomador.contato_cargo,
        contato_email=tomador.contato_email,
        contato_telefone=""
    )

    # Qualificar com valor de diagnóstico maior devido à complexidade
    qualificador = QualificadorOperacao()
    analise = qualificador.qualificar(operacao, tomador)

    # Ajustar valor do diagnóstico para cima (complexidade internacional)
    analise.valor_recomendado_diagnostico = Decimal('50000')  # Mínimo R$ 50K
    analise.valor_minimo_diagnostico = Decimal('40000')

    print("\n" + qualificador.gerar_resumo_executivo(analise))

    # Gerar proposta
    gerador = GeradorProposta()

    print("\n" + "=" * 80)
    print("PROPOSTA COMERCIAL - EXPORTAÇÃO GRÃOS")
    print("=" * 80)

    proposta_texto = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PROPOSTA COMERCIAL                                   ║
║                         Estruturação Operação de Exportação                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Data: {datetime.now().strftime('%d/%m/%Y'):<72} ║
║ Validade: 15 dias                                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TOMADOR                                                                      ║
║ Razão Social: {tomador.razao_social:<62} ║
║ CNPJ: A definir                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ OPERAÇÃO                                                                     ║
║ Tipo: Estruturação de Exportação de Grãos - Garantia Internacional           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ DESCRIÇÃO DO PROBLEMA                                                        ║
║                                                                              ║
║ A operação envolve a exportação de grãos com necessidade de:                 ║
║ • Antecipação do pagamento (ACC/ACE ou similar)                              ║
║ • Garantia de recebimento no exterior                                        ║
║ • OU garantia de retorno/destinação alternativa da mercadoria                ║
║                                                                              ║
║ Complexidade adicional:                                                      ║
║ • Operação internacional (múltiplas jurisdições)                             ║
║ • Risco combinado: performance + financeiro                                  ║
║ • Estruturação fora do padrão de mercado                                     ║
║ • Necessidade de análise de legislação aduaneira e cambial                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ESTRUTURA DE TRABALHO E INVESTIMENTO                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║ FASE 1: DIAGNÓSTICO TÉCNICO APROFUNDADO                                      ║
║ ─────────────────────────────────────────────────────────────────────────    ║
║                                                                              ║
║ Escopo do diagnóstico:                                                       ║
║                                                                              ║
║ 1. ANÁLISE DA ESTRUTURA DA OPERAÇÃO                                          ║
║    • Fluxo completo da exportação (embarque → destino → pagamento)           ║
║    • Identificação dos pontos de risco em cada etapa                         ║
║    • Mapeamento de partes envolvidas (importador, banco, trader)             ║
║                                                                              ║
║ 2. ANÁLISE REGULATÓRIA                                                       ║
║    • Legislação aduaneira aplicável                                          ║
║    • Normativas do Banco Central (câmbio)                                    ║
║    • Exigências do país de destino                                           ║
║                                                                              ║
║ 3. ANÁLISE DE GARANTIAS POSSÍVEIS                                            ║
║    • Seguro garantia de performance                                          ║
║    • Garantia financeira (stand-by letter of credit)                         ║
║    • Estruturas híbridas                                                     ║
║    • Garantias alternativas (penhor de mercadoria, etc.)                     ║
║                                                                              ║
║ 4. PARECER DE VIABILIDADE                                                    ║
║    • Conclusão sobre viabilidade                                             ║
║    • Caminho recomendado                                                     ║
║    • Estimativa de custos e prazos                                           ║
║                                                                              ║
║ Entregáveis:                                                                 ║
║   • Relatório de Diagnóstico Técnico (30-50 páginas)                         ║
║   • Análise Regulatória Fundamentada                                         ║
║   • Mapeamento de Riscos e Mitigadores                                       ║
║   • Parecer de Viabilidade                                                   ║
║   • Plano de Trabalho para Execução (se viável)                              ║
║                                                                              ║
║ Investimento: R$ 50.000,00                                                   ║
║ Condição: 100% ANTECIPADO - Início após confirmação de pagamento             ║
║ Prazo: 15-20 dias úteis                                                      ║
║                                                                              ║
║ ─────────────────────────────────────────────────────────────────────────    ║
║                                                                              ║
║ FASE 2: EXECUÇÃO / ESTRUTURAÇÃO (se diagnóstico indicar viabilidade)         ║
║ ─────────────────────────────────────────────────────────────────────────    ║
║                                                                              ║
║ • Elaboração da estrutura completa                                           ║
║ • Negociação com seguradoras/bancos                                          ║
║ • Documentação técnica                                                       ║
║ • Aprovação de limites                                                       ║
║                                                                              ║
║ Investimento: A ser definido após diagnóstico (estimativa: R$ 100-200K)      ║
║ Condição: 50% início + 50% conclusão                                         ║
║                                                                              ║
║ ─────────────────────────────────────────────────────────────────────────    ║
║                                                                              ║
║ FASE 3: IMPLEMENTAÇÃO                                                        ║
║ ─────────────────────────────────────────────────────────────────────────    ║
║                                                                              ║
║ • Emissão de garantias                                                       ║
║ • Acompanhamento da operação                                                 ║
║                                                                              ║
║ Investimento: Comissões de corretagem (conforme mercado)                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ VALOR DO DIAGNÓSTICO: R$ 50.000,00                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ IMPORTANTE                                                                   ║
║                                                                              ║
║ • O diagnóstico tem valor INDEPENDENTE do resultado                          ║
║ • Você está contratando nossa análise técnica especializada                  ║
║ • O diagnóstico entrega clareza sobre o problema                             ║
║ • Não é garantia de aprovação, mas de análise profunda                       ║
║ • Todos os estudos são propriedade intelectual exclusiva                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ POR QUE R$ 50.000 NO DIAGNÓSTICO?                                            ║
║                                                                              ║
║ Operações de exportação com garantia internacional são extremamente          ║
║ complexas. Envolvem:                                                         ║
║                                                                              ║
║ • Legislação brasileira (aduaneira, cambial)                                 ║
║ • Legislação do país de destino                                              ║
║ • Práticas bancárias internacionais                                          ║
║ • Mercado de seguros especializado                                           ║
║ • Estruturas jurídicas complexas                                             ║
║                                                                              ║
║ O diagnóstico vai demandar:                                                  ║
║ • Pesquisa técnica aprofundada                                               ║
║ • Consultas especializadas                                                   ║
║ • Análise de precedentes                                                     ║
║ • Elaboração de parecer fundamentado                                         ║
║                                                                              ║
║ Este valor é uma FRAÇÃO do que você perderia se:                             ║
║ • Embarcar a mercadoria sem garantia adequada                                ║
║ • Perder a oportunidade de negócio                                           ║
║ • Ter problemas de recebimento no exterior                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CONDIÇÕES DE PAGAMENTO                                                       ║
║                                                                              ║
║ • Diagnóstico: 100% antecipado via transferência ou boleto                   ║
║ • Execução: 50% início + 50% conclusão                                       ║
║ • Implementação: Comissões de mercado                                        ║
║                                                                              ║
║ Dados bancários para pagamento serão enviados após aceite.                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ACEITE                                                                       ║
║                                                                              ║
║ Declaro que li e aceito os termos desta proposta.                            ║
║                                                                              ║
║ Data: ___/___/______                                                         ║
║                                                                              ║
║ ___________________________________                                          ║
║ Assinatura do Responsável                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(proposta_texto)

    return proposta_texto, analise


def main():
    """Gera as duas propostas"""
    print("\n" + "=" * 80)
    print("GERANDO PROPOSTAS PARA OS CASOS REAIS")
    print("=" * 80 + "\n")

    # Caso 1
    proposta1, analise1 = gerar_caso_distribuidora()

    # Caso 2
    proposta2, analise2 = gerar_caso_agronegocio()

    # Salvar em arquivos
    with open("proposta_distribuidora_icms.txt", "w", encoding="utf-8") as f:
        f.write("PROPOSTA - DISTRIBUIDORA DE ALIMENTOS - GARANTIA ICMS\n")
        f.write("=" * 80 + "\n\n")
        f.write(proposta1.gerar_texto())

    with open("proposta_agronegocio_exportacao.txt", "w", encoding="utf-8") as f:
        f.write(proposta2)

    print("\n" + "=" * 80)
    print("PROPOSTAS SALVAS:")
    print("  • proposta_distribuidora_icms.txt")
    print("  • proposta_agronegocio_exportacao.txt")
    print("=" * 80)


if __name__ == "__main__":
    main()
