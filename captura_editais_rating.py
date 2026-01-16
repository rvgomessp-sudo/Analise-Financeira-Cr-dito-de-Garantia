#!/usr/bin/env python3
"""
Script Principal: Captura de Editais com Exigência de Rating

Este script captura editais de licitações públicas que exigem rating/classificação
de risco para seguradoras, com ênfase especial no estado do Amazonas.

Uso:
    python captura_editais_rating.py [opções]

Opções:
    --uf UF              Estado para buscar (padrão: AM)
    --dias N             Dias retroativos (padrão: 30)
    --apenas-rating      Retorna apenas editais com rating
    --formato FORMATO    Formato de saída: json, txt, csv, todos (padrão: todos)
    --alerta             Modo alerta: mostra apenas editais urgentes
    --interativo         Modo interativo com menu

Exemplos:
    python captura_editais_rating.py --uf AM --dias 30
    python captura_editais_rating.py --apenas-rating --formato csv
    python captura_editais_rating.py --alerta --dias 7
    python captura_editais_rating.py --interativo

Autor: Sistema de Análise Financeira de Crédito de Garantia
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from captura_editais import (
        GestorCapturas,
        ConfiguracaoCaptura,
        DetectorRating,
        FonteEdital
    )
    from captura_editais.capturador_base import verificar_dependencias, instalar_dependencias
    MODULO_DISPONIVEL = True
except ImportError as e:
    MODULO_DISPONIVEL = False
    ERRO_IMPORTACAO = str(e)


def verificar_ambiente() -> bool:
    """Verifica se o ambiente está configurado corretamente."""
    if not MODULO_DISPONIVEL:
        print(f"\n❌ Erro ao importar módulo: {ERRO_IMPORTACAO}")
        print("\nVerifique se você está no diretório correto do projeto.")
        return False

    deps = verificar_dependencias()
    deps_faltando = [dep for dep, instalada in deps.items() if not instalada]

    if deps_faltando:
        print("\n⚠️  Dependências faltando:")
        for dep in deps_faltando:
            print(f"   - {dep}")
        print(f"\n   Instale com: {instalar_dependencias()}")
        return False

    return True


def exibir_banner():
    """Exibe banner do sistema."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     CAPTURA DE EDITAIS COM EXIGÊNCIA DE RATING                      ║
║     Sistema de Análise Financeira - Crédito de Garantia             ║
║                                                                      ║
║     Foco: Amazonas | Seguro Garantia | Rating de Seguradoras        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def modo_captura(args) -> None:
    """Executa captura de editais."""
    print(f"\n🔍 Iniciando captura de editais...")
    print(f"   UF: {args.uf}")
    print(f"   Período: últimos {args.dias} dias")
    print(f"   Apenas com rating: {'Sim' if args.apenas_rating else 'Não'}")

    config = ConfiguracaoCaptura(
        uf_prioritaria=args.uf,
        dias_retroativos=args.dias,
        apenas_com_rating=args.apenas_rating
    )

    with GestorCapturas(config) as gestor:
        relatorio = gestor.capturar_tudo(
            uf=args.uf,
            dias=args.dias,
            apenas_rating=args.apenas_rating
        )

        # Exibe resumo
        print("\n" + "=" * 60)
        print("RESUMO DA CAPTURA")
        print("=" * 60)
        print(f"Fontes consultadas: {relatorio.total_fontes}")
        print(f"Tempo de execução: {relatorio.tempo_total:.2f}s")
        print(f"\nTotal de editais: {relatorio.total_editais}")
        print(f"Com exigência de rating: {relatorio.total_com_rating}")
        print(f"Taxa de rating: {relatorio.taxa_rating_geral:.1f}%")
        print(f"\nEditais do Amazonas: {relatorio.total_amazonas}")
        print(f"Amazonas com rating: {relatorio.editais_rating_amazonas}")
        print(f"Taxa rating AM: {relatorio.taxa_rating_amazonas:.1f}%")

        # Salva arquivos
        arquivos_salvos = []

        if args.formato in ['json', 'todos']:
            arquivo = gestor.salvar_relatorio(relatorio, formato='json')
            arquivos_salvos.append(arquivo)

        if args.formato in ['txt', 'todos']:
            arquivo = gestor.salvar_relatorio(relatorio, formato='txt')
            arquivos_salvos.append(arquivo)

        if args.formato in ['csv', 'todos']:
            arquivo = gestor.salvar_editais_csv(relatorio)
            arquivos_salvos.append(arquivo)

        if arquivos_salvos:
            print("\n📁 Arquivos salvos:")
            for arquivo in arquivos_salvos:
                print(f"   {arquivo}")

        # Mostra editais prioritários
        if relatorio.editais_prioritarios:
            print("\n" + "=" * 60)
            print("🎯 EDITAIS PRIORITÁRIOS (Top 5)")
            print("=" * 60)

            for i, edital in enumerate(relatorio.editais_prioritarios[:5], 1):
                print(f"\n{i}. {edital.numero_edital}")
                print(f"   Órgão: {edital.orgao}")
                print(f"   Local: {edital.uf}/{edital.municipio or 'N/A'}")
                if edital.valor_estimado:
                    print(f"   Valor: R$ {edital.valor_estimado:,.2f}")
                if edital.tem_exigencia_rating:
                    print(f"   ⭐ RATING: {edital.exigencia_rating.nivel_minimo.value}")
                if edital.data_abertura:
                    dias_restantes = (edital.data_abertura - datetime.now()).days
                    print(f"   Abertura: {edital.data_abertura.strftime('%d/%m/%Y')} ({dias_restantes} dias)")

        # Erros
        if relatorio.erros:
            print("\n⚠️  Avisos/Erros:")
            for erro in relatorio.erros[:5]:
                print(f"   - {erro}")


def modo_alerta(args) -> None:
    """Exibe alertas de editais urgentes."""
    print(f"\n🚨 Buscando editais com rating e prazo próximo...")
    print(f"   UF: {args.uf} | Dias: {args.dias}")

    config = ConfiguracaoCaptura(
        uf_prioritaria=args.uf,
        dias_retroativos=args.dias
    )

    with GestorCapturas(config) as gestor:
        relatorio = gestor.capturar_tudo(uf=args.uf, dias=args.dias)
        alertas = gestor.gerar_alertas(relatorio)

        print("\n" + "=" * 60)
        print("ALERTAS DE EDITAIS COM EXIGÊNCIA DE RATING")
        print("=" * 60)

        if alertas:
            for alerta in alertas:
                print(f"\n{alerta}")
                print("-" * 50)
        else:
            print("\n✅ Nenhum edital urgente com rating encontrado no período.")

        print(f"\n📊 Resumo: {relatorio.total_com_rating} editais com rating")
        print(f"         {relatorio.editais_rating_amazonas} no Amazonas")


def modo_interativo() -> None:
    """Modo interativo com menu."""
    while True:
        print("\n" + "=" * 50)
        print("MENU PRINCIPAL")
        print("=" * 50)
        print("1. Capturar editais do Amazonas (últimos 30 dias)")
        print("2. Capturar editais do Amazonas (personalizado)")
        print("3. Capturar editais de outro estado")
        print("4. Buscar apenas editais com rating")
        print("5. Alertas urgentes (próximos 7 dias)")
        print("6. Analisar texto de edital")
        print("7. Verificar dependências")
        print("0. Sair")
        print("-" * 50)

        try:
            opcao = input("Escolha uma opção: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSaindo...")
            break

        if opcao == '0':
            print("\n👋 Até logo!")
            break

        elif opcao == '1':
            args = argparse.Namespace(
                uf='AM', dias=30, apenas_rating=False, formato='todos'
            )
            modo_captura(args)

        elif opcao == '2':
            try:
                dias = int(input("Quantos dias retroativos? [30]: ").strip() or '30')
                apenas_rating = input("Apenas com rating? (s/n) [n]: ").strip().lower() == 's'
                args = argparse.Namespace(
                    uf='AM', dias=dias, apenas_rating=apenas_rating, formato='todos'
                )
                modo_captura(args)
            except ValueError:
                print("❌ Valor inválido")

        elif opcao == '3':
            uf = input("Digite a UF (ex: SP, RJ, MG): ").strip().upper()
            if len(uf) != 2:
                print("❌ UF inválida")
                continue
            args = argparse.Namespace(
                uf=uf, dias=30, apenas_rating=False, formato='todos'
            )
            modo_captura(args)

        elif opcao == '4':
            args = argparse.Namespace(
                uf='AM', dias=30, apenas_rating=True, formato='todos'
            )
            modo_captura(args)

        elif opcao == '5':
            args = argparse.Namespace(uf='AM', dias=7)
            modo_alerta(args)

        elif opcao == '6':
            analisar_texto_interativo()

        elif opcao == '7':
            verificar_deps_interativo()

        else:
            print("❌ Opção inválida")


def analisar_texto_interativo() -> None:
    """Analisa texto de edital para detectar exigência de rating."""
    print("\n" + "=" * 50)
    print("ANÁLISE DE TEXTO DE EDITAL")
    print("=" * 50)
    print("Cole o texto do edital abaixo.")
    print("Digite 'FIM' em uma linha separada para finalizar:")
    print("-" * 50)

    linhas = []
    try:
        while True:
            linha = input()
            if linha.strip().upper() == 'FIM':
                break
            linhas.append(linha)
    except (KeyboardInterrupt, EOFError):
        print("\nAnálise cancelada.")
        return

    texto = '\n'.join(linhas)

    if not texto.strip():
        print("❌ Texto vazio")
        return

    detector = DetectorRating()
    resultado = detector.analisar_completo(texto)

    print("\n" + "=" * 50)
    print("RESULTADO DA ANÁLISE")
    print("=" * 50)
    print(resultado['resumo'])

    if resultado['tem_exigencia']:
        exigencia = resultado['exigencia_rating']
        if exigencia.texto_original:
            print(f"\n📝 Trecho relevante:")
            print(f'   "{exigencia.texto_original[:300]}..."')


def verificar_deps_interativo() -> None:
    """Verifica e exibe status das dependências."""
    print("\n" + "=" * 50)
    print("VERIFICAÇÃO DE DEPENDÊNCIAS")
    print("=" * 50)

    deps = verificar_dependencias()

    todas_ok = True
    for dep, instalada in deps.items():
        status = "✅" if instalada else "❌"
        print(f"  {status} {dep}")
        if not instalada:
            todas_ok = False

    if todas_ok:
        print("\n✅ Todas as dependências estão instaladas!")
    else:
        print(f"\n⚠️  Para instalar dependências faltantes:")
        print(f"   {instalar_dependencias()}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Captura editais de licitações com exigência de rating',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python captura_editais_rating.py --uf AM --dias 30
  python captura_editais_rating.py --apenas-rating --formato csv
  python captura_editais_rating.py --alerta --dias 7
  python captura_editais_rating.py --interativo
        """
    )

    parser.add_argument(
        '--uf',
        type=str,
        default='AM',
        help='Estado para buscar (padrão: AM - Amazonas)'
    )

    parser.add_argument(
        '--dias',
        type=int,
        default=30,
        help='Dias retroativos para busca (padrão: 30)'
    )

    parser.add_argument(
        '--apenas-rating',
        action='store_true',
        help='Retorna apenas editais com exigência de rating'
    )

    parser.add_argument(
        '--formato',
        choices=['json', 'txt', 'csv', 'todos'],
        default='todos',
        help='Formato de saída (padrão: todos)'
    )

    parser.add_argument(
        '--alerta',
        action='store_true',
        help='Modo alerta: mostra apenas editais urgentes com rating'
    )

    parser.add_argument(
        '--interativo',
        action='store_true',
        help='Modo interativo com menu'
    )

    args = parser.parse_args()

    # Exibe banner
    exibir_banner()

    # Verifica ambiente
    if not verificar_ambiente():
        print("\n❌ Ambiente não configurado corretamente.")
        print("   Verifique as dependências e tente novamente.")
        sys.exit(1)

    # Executa modo apropriado
    if args.interativo:
        modo_interativo()
    elif args.alerta:
        modo_alerta(args)
    else:
        modo_captura(args)


if __name__ == '__main__':
    main()
