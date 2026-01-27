#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Script para criar pacote de distribuição do SDK.
Gera um arquivo ZIP pronto para instalação no Blender/UPBGE.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_version():
    """Obtém a versão do add-on do __init__.py."""
    init_file = Path(__file__).parent.parent / "__init__.py"
    if not init_file.exists():
        return "1.0.0"
    
    with open(init_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('"version"'):
                # Extrair versão: "version": (1, 0, 0),
                parts = line.split('(')[1].split(')')[0].split(',')
                version = '.'.join(p.strip() for p in parts)
                return version
    
    return "1.0.0"


def check_required_files(base_dir):
    """Verifica se todos os arquivos necessários estão presentes."""
    platform = sys.platform
    required = []
    missing = []
    
    # Node.js
    if platform == "win32":
        node_path = base_dir / "runtime" / "windows" / "node.exe"
    elif platform == "linux":
        node_path = base_dir / "runtime" / "linux" / "node-linux64"
    elif platform == "darwin":
        node_path = base_dir / "runtime" / "macos" / "node-osx"
    else:
        node_path = None
    
    if node_path and node_path.exists():
        required.append(("Node.js", node_path))
    else:
        missing.append(f"Node.js ({node_path})")
        
    # Arquivos Python essenciais
    essential_files = [
        base_dir / "__init__.py",
        base_dir / "python" / "__init__.py",
        base_dir / "python" / "start.py",
        base_dir / "python" / "preferences.py",
        base_dir / "python" / "operators.py",
    ]
    
    for file_path in essential_files:
        if file_path.exists():
            required.append((file_path.name, file_path))
        else:
            missing.append(f"Arquivo Python ({file_path})")
    
    return required, missing


def should_include_file(file_path, base_dir):
    """Determina se um arquivo deve ser incluído no pacote."""
    rel_path = file_path.relative_to(base_dir)
    rel_str = str(rel_path).replace('\\', '/')
    
    # Sempre incluir arquivos essenciais
    if rel_str.startswith(('__init__.py', 'python/', 'README.md', 'CHANGELOG.md')):
        return True
    
    # SEMPRE incluir binários (mesmo que estejam no .gitignore)
    if rel_str.startswith(('runtime/')):
        # Excluir apenas arquivos temporários e cache
        if any(x in rel_str for x in ['__pycache__', '.pyc', '.pyo', 'node_modules/.cache', '.gitkeep']):
            return False
        # Incluir todos os binários necessários
        return True
    
    # Excluir arquivos de desenvolvimento
    exclude_patterns = [
        '.git',
        '.gitignore',
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '.DS_Store',
        'Thumbs.db',
        'scripts/',
        'temp_',
        '*.zip',
        '*.tar.gz',
        '*.tar.xz',
        '__pycache__',
        '.pyc',
        '.pyo',
        'INSTALL_DEPENDENCIES.md',  # Não necessário no pacote final
        'SETUP.md',  # Não necessário no pacote final
    ]
    
    for pattern in exclude_patterns:
        if pattern in rel_str or rel_str.endswith(pattern.replace('*', '')):
            return False
    
    return True


def create_package(base_dir, output_dir=None):
    """Cria o pacote ZIP para distribuição."""
    if output_dir is None:
        output_dir = base_dir.parent
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    version = get_version()
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"upbge-nodejs-sdk-{version}-{timestamp}.zip"
    zip_path = output_dir / zip_name
    
    print("=== UPBGE JavaScript SDK - Build Package ===\n")
    
    # Verificar arquivos necessários
    print("Verificando arquivos necessários...")
    required, missing = check_required_files(base_dir)
    
    if missing:
        print("\n⚠ AVISO: Alguns arquivos estão faltando:")
        for item in missing:
            print(f"  ✗ {item}")
        print("\nO pacote será criado, mas pode não funcionar completamente.")
        print("Execute 'python scripts/setup_sdk.py' para instalar dependências.\n")
    else:
        print("  ✓ Todos os arquivos necessários encontrados\n")
    
    print(f"Arquivos essenciais encontrados:")
    for name, path in required:
        size = path.stat().st_size / (1024 * 1024)  # MB
        print(f"  ✓ {name}: {size:.2f} MB")
    
    # Criar ZIP
    print(f"\nCriando pacote: {zip_path}")
    
    # Remover ZIP existente
    if zip_path.exists():
        zip_path.unlink()
    
    files_added = 0
    total_size = 0
    
    # Nome do diretório dentro do ZIP (deve ser o mesmo do bl_idname do add-on)
    # O Blender espera que __init__.py esteja dentro de um diretório, não na raiz
    addon_dir_name = "upbge_nodejs_sdk"  # Mesmo nome do bl_idname
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        # Adicionar todos os arquivos
        # IMPORTANTE: Incluir arquivos mesmo que estejam no .gitignore
        # IMPORTANTE: Todos os arquivos devem estar dentro de um diretório no ZIP
        for root, dirs, files in os.walk(base_dir):
            # Filtrar diretórios a serem ignorados
            dirs[:] = [d for d in dirs if not any(x in d for x in ['.git', '__pycache__', '.vscode', '.idea'])]
            
            for file in files:
                file_path = Path(root) / file
                
                # Pular arquivos de build anteriores
                if file.endswith(('.zip', '.tar.gz', '.tar.xz')):
                    continue
                
                rel_path = file_path.relative_to(base_dir)
                
                if should_include_file(file_path, base_dir):
                    try:
                        # IMPORTANTE: Colocar todos os arquivos dentro do diretório do add-on
                        # arcname = "upbge_nodejs_sdk/__init__.py" ao invés de "__init__.py"
                        # Converter caminhos Windows (\) para formato ZIP (/)
                        rel_path_str = str(rel_path).replace('\\', '/')
                        arcname = f"{addon_dir_name}/{rel_path_str}"
                        zipf.write(file_path, arcname)
                        files_added += 1
                        total_size += file_path.stat().st_size
                    except Exception as e:
                        print(f"  Aviso: Não foi possível adicionar {rel_path}: {e}")
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n✓ Pacote criado com sucesso!")
    print(f"  Arquivo: {zip_path}")
    print(f"  Tamanho: {zip_size:.2f} MB")
    print(f"  Arquivos incluídos: {files_added}")
    print(f"  Tamanho total (descompactado): {total_size_mb:.2f} MB")
    
    print(f"\n=== Instruções de Instalação ===")
    print(f"1. No Blender/UPBGE, vá em Edit → Preferences → Add-ons")
    print(f"2. Clique em 'Install...' e selecione: {zip_name}")
    print(f"3. Ative o add-on 'UPBGE Node.js SDK'")
    print(f"4. O SDK está pronto para uso (plug-and-play)!")
    print(f"\nNota: O ZIP foi criado com a estrutura correta:")
    print(f"      {zip_name}")
    print(f"      └── {addon_dir_name}/")
    print(f"          ├── __init__.py")
    print(f"          ├── python/")
    print(f"          ├── lib/")
    print(f"          └── ...")
    
    return zip_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Criar pacote de distribuição do SDK")
    parser.add_argument("--output", "-o", type=str, help="Diretório de saída (padrão: parent do SDK)")
    parser.add_argument("--check-only", action="store_true", help="Apenas verificar arquivos, não criar ZIP")
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    if args.check_only:
        print("=== Verificação de Arquivos ===\n")
        required, missing = check_required_files(base_dir)
        
        if required:
            print("Arquivos encontrados:")
            for name, path in required:
                size = path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {name}: {size:.2f} MB")
        
        if missing:
            print("\nArquivos faltando:")
            for item in missing:
                print(f"  ✗ {item}")
            print("\nExecute 'python scripts/setup_sdk.py' para instalar dependências.")
            return 1
        else:
            print("\n✓ Todos os arquivos necessários estão presentes!")
            return 0
    else:
        output_dir = Path(args.output) if args.output else None
        create_package(base_dir, output_dir)
        return 0


if __name__ == "__main__":
    sys.exit(main())
