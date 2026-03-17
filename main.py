#!/usr/bin/env python3
"""
Agente Documentador Inteligente usando Claude API
Analisa projetos, pastas ou arquivos específicos e gera documentação contextual automaticamente
"""

import asyncio
import os
import sys

# Adiciona o diretório do agente ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from utils import Logger
from utils import Logger, print_banner
from config import Settings
from scanner import FileScanner
from src import DocGenerator, ClaudeClient
from ui import PathPicker, FolderPicker


def _resolve_output(folder: str, filename: str) -> str:
    """Combina pasta e nome do arquivo .md."""
    if not filename:
        filename = 'README.md'
    if not filename.endswith('.md'):
        filename += '.md'
    return os.path.abspath(os.path.join(folder, filename))


def _ensure_output_dir(output_path: str, log: Logger) -> bool:
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            log.success(f"Diretório criado: {directory}")
        except Exception as e:
            log.error(f"Não foi possível criar o diretório: {e}")
            return False
    return True


def _validate_paths(paths: list[str], log: Logger) -> list[str]:
    print()
    log.info("Validando caminhos...")
    valid = []
    for p in paths:
        if os.path.exists(p):
            kind = "DIR" if os.path.isdir(p) else "FILE"
            log.success(f"[{kind}] {p}")
            valid.append(p)
        else:
            log.warning(f"Não encontrado: {p}")
    return valid


def _print_summary(paths: list[str], project_name: str, output_path: str, log: Logger) -> None:
    log.section("RESUMO")
    print(f"Caminhos: {len(paths)}")
    for p in paths:
        kind = "DIR" if os.path.isdir(p) else "FILE"
        print(f"   - [{kind}] {p}")
    print(f"📋 Projeto : {project_name}")
    print(f"💾 Saida   : {output_path}")
    print("=" * 60)


async def run(paths: list[str], output_path: str, project_name: str, api_key: str, log: Logger) -> None:
    cfg = Settings()
    scanner = FileScanner(cfg, log)
    client = ClaudeClient(api_key, cfg)
    generator = DocGenerator(scanner, client, cfg, log)

    for path in paths:
        if os.path.isfile(path):
            log.info(f"Adicionando arquivo: {path}")
            scanner.add_specific_file(path)
        elif os.path.isdir(path):
            scanner.scan_directory(path)
        else:
            log.warning(f"Path não encontrado: {path}")

    if scanner.total_files == 0:
        log.warning("Nenhum arquivo relevante encontrado.")
        return

    documentation = await generator.generate(project_name)

    log.info(f"Salvando em: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(documentation)

    log.section("DOCUMENTACAO GERADA COM SUCESSO")
    print(f"↳ Arquivo : {output_path}")
    print(f"↳ Tamanho : {len(documentation)} caracteres")
    print(f"↳ Linhas  : {len(documentation.splitlines())}")
    print(f"↳ Modo    : {scanner.detect_documentation_type()}\n")


def main() -> None:
    log = Logger()
    print_banner()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        log.error("ANTHROPIC_API_KEY não encontrada!")
        print("\nConfigure sua API key:")
        print("  Linux/Mac : export ANTHROPIC_API_KEY='sua-chave'")
        print("  Windows   : set ANTHROPIC_API_KEY=sua-chave")
        print("Obtenha sua chave em: https://console.anthropic.com/\n")
        sys.exit(1)

    log.success("API Key configurada")
    log.info("Checando diretório atual...")
    print(f"\n➥  Diretório atual: {os.getcwd()}\n")

    # Seleção de paths com @ picker
    paths = PathPicker(base_dir='.').run()
    if not paths:
        log.error("Nenhum caminho informado.")
        sys.exit(1)

    valid_paths = _validate_paths(paths, log)
    if not valid_paths:
        log.error("Nenhum caminho válido.")
        sys.exit(1)

    # Nome do projeto
    print("\nNome do projeto (Enter para 'Projeto'):")
    project_name = input("> ").strip() or "Projeto"

    # Seleção de pasta de saída com / picker
    output_folder = FolderPicker(base_dir='.').run()

    # Nome do arquivo .md
    R   = '\033[0m'
    DIM = '\033[2m'
    print(f"\nNome do arquivo {DIM}(Enter para README.md){R}:")
    filename = input('> ').strip()
    output_path = _resolve_output(output_folder, filename)

    if not _ensure_output_dir(output_path, log):
        sys.exit(1)

    _print_summary(valid_paths, project_name, output_path, log)

    confirm = input("\nContinuar? (s/n): ").strip().lower()
    if confirm not in ('s', 'sim', 'y', 'yes'):
        log.info("Operação cancelada.")
        sys.exit(0)

    print()
    try:
        asyncio.run(run(valid_paths, output_path, project_name, api_key, log))
    except KeyboardInterrupt:
        log.info("Operação interrompida pelo usuário.")
    except Exception as e:
        log.error(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()