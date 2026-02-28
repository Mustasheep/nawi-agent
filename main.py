#!/usr/bin/env python3
"""
CLI para o agente Nawi
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Adiciona o diretório do agente ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import DocumentationAgent
from utils.logger import Logger
from utils.banner import print_banner


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Nawi - o agente documentador inteligente com Claude API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s ./src                           # Documenta diretório src
  %(prog)s file.py                         # Documenta arquivo único
  %(prog)s ./src ./tests -o docs/README.md # Múltiplos paths
  %(prog)s . -t api -o API.md              # Template específico
  %(prog)s ./src --no-tools                # Sem usar tools (legado)
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='+',
        help='Caminhos para analisar (diretórios ou arquivos)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='README.md',
        help='Caminho do arquivo de saída (default: README.md)'
    )
    
    parser.add_argument(
        '-n', '--name',
        default='Projeto',
        help='Nome do projeto (default: Projeto)'
    )
    
    parser.add_argument(
        '-t', '--template',
        choices=['auto', 'single_file', 'small_project', 'full_project', 'api'],
        default='auto',
        help='Template a usar (default: auto-detect)'
    )
    
    parser.add_argument(
        '--no-tools',
        action='store_true',
        help='Não usar tools (modo legado)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose (mais logs)'
    )
    
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Modo rápido (menos contexto/iterações, mais econômico)'
    )
    
    parser.add_argument(
        '--api-key',
        help='API Key da Anthropic (ou use ANTHROPIC_API_KEY env var)'
    )
    
    return parser.parse_args()


def validate_paths(paths):
    """Valida os caminhos fornecidos"""
    valid_paths = []
    logger = Logger()
    
    logger.info("Validando caminhos...")
    
    for path in paths:
        abs_path = os.path.abspath(path)
        
        if os.path.exists(abs_path):
            if os.path.isdir(abs_path):
                logger.success(f"✓ DIR : {abs_path}")
            else:
                logger.success(f"✓ FILE: {abs_path}")
            valid_paths.append(abs_path)
        else:
            logger.error(f"✗ Não encontrado: {abs_path}")
    
    return valid_paths


def setup_output_path(output):
    """Configura o caminho de saída"""
    # Se for diretório, adiciona README.md
    if output.endswith('/') or output.endswith('\\'):
        output = os.path.join(output, 'README.md')
    elif os.path.isdir(output):
        output = os.path.join(output, 'README.md')
    elif not output.endswith('.md'):
        output = f"{output}.md"
    
    output_path = os.path.abspath(output)
    output_dir = os.path.dirname(output_path)
    
    # Cria diretório se necessário
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    return output_path

def print_summary(args, valid_paths, output_path):
    """Imprime resumo da operação"""
    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO")
    print("=" * 60)
    print(f"📁 Caminhos: {len(valid_paths)}")
    for path in valid_paths:
        path_type = "DIR " if os.path.isdir(path) else "FILE"
        print(f"   - [{path_type}] {path}")
    print(f"\n↳ Projeto: {args.name}")
    print(f"↳ Template: {args.template}")
    print(f"↳ Tools: {'Desabilitadas' if args.no_tools else 'Habilitadas'}")
    print(f"\n💾 Saída: {output_path}")
    print("=" * 60)


async def main():
    """Função principal"""
    args = parse_arguments()
    
    print_banner()
    
    # Valida API Key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        logger = Logger()
        logger.error("ANTHROPIC_API_KEY não encontrada!")
        print("\n✘ Configure sua API key:")
        print("  - Linux/Mac: export ANTHROPIC_API_KEY='sua-chave'")
        print("  - Windows: set ANTHROPIC_API_KEY=sua-chave")
        print("  - Ou use: --api-key SUA_CHAVE")
        print("\nObtenha em: https://console.anthropic.com/")
        return 1
    
    # Valida paths
    valid_paths = validate_paths(args.paths)
    
    if not valid_paths:
        logger = Logger()
        logger.error("Nenhum caminho válido fornecido")
        return 1
    
    # Setup output
    output_path = setup_output_path(args.output)
    
    # Resumo
    print_summary(args, valid_paths, output_path)
    
    # Confirmação
    confirm = input("\n▶ Continuar? [S/n]: ").strip().lower()
    if confirm and confirm not in ['s', 'sim', 'y', 'yes']:
        print("\n✘ Operação cancelada.")
        return 0
    
    print()
    
    # Inicializa agente
    agent = DocumentationAgent(
        api_key=api_key,
        verbose=args.verbose,
        fast_mode=args.fast,
    )
    
    try:
        # Determina template
        template = None if args.template == 'auto' else args.template
        
        # Gera documentação
        documentation = await agent.generate_documentation(
            paths=valid_paths,
            project_name=args.name,
            template=template
        )
        
        # Salva
        success = await agent.save_documentation(documentation, output_path)
        
        if success:
            print("\n" + "=" * 60)
            print("✔ DOCUMENTAÇÃO GERADA COM SUCESSO!")
            print("=" * 60)
            print(f"\n📄 Arquivo: {output_path}")
            print(f"📊 Tamanho: {len(documentation):,} caracteres")
            print(f"📝 Linhas: {len(documentation.splitlines()):,}")
            return 0
        else:
            return 1
        
    except KeyboardInterrupt:
        logger = Logger()
        logger.warning("Operação interrompida pelo usuário")
        return 130
    
    except Exception as e:
        logger = Logger()
        logger.error(f"Erro: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
