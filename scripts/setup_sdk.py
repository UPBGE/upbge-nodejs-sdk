#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Script de setup completo para o SDK.
Cria estrutura de diretórios e verifica dependências.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Cria a estrutura de diretórios necessária."""
    base_dir = Path(__file__).parent.parent
    
    directories = [
        "runtime/windows",
        "runtime/linux",
        "runtime/macos",
        "scripts",
    ]
    
    print("Criando estrutura de diretórios...")
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    print("\nEstrutura de diretórios criada com sucesso!")


def get_node_path(base_dir):
    """Retorna o caminho do Node.js para a plataforma atual."""
    platform = sys.platform
    if platform == "win32":
        return base_dir / "runtime" / "windows" / "node.exe"
    elif platform == "darwin":
        return base_dir / "runtime" / "macos" / "node-osx"
    else:  # linux
        return base_dir / "runtime" / "linux" / "node-linux64"


def find_npm_executable(node_path):
    """Encontra o executável npm associado ao node.exe."""
    node_dir = node_path.parent
    platform = sys.platform
    
    # Tentar encontrar npm na mesma pasta do node.exe
    if platform == "win32":
        npm_candidates = [
            node_dir / "npm.cmd",
            node_dir / "npm",
        ]
        # Procurar npm-cli.js em várias localizações
        npm_cli_candidates = [
            node_dir / "node_modules" / "npm" / "bin" / "npm-cli.js",
            node_dir.parent / "node_modules" / "npm" / "bin" / "npm-cli.js",
            node_dir.parent.parent / "node_modules" / "npm" / "bin" / "npm-cli.js",
        ]
    else:
        npm_candidates = [
            node_dir / "npm",
        ]
        npm_cli_candidates = [
            node_dir / "node_modules" / "npm" / "bin" / "npm-cli.js",
            node_dir.parent / "node_modules" / "npm" / "bin" / "npm-cli.js",
            node_dir.parent.parent / "node_modules" / "npm" / "bin" / "npm-cli.js",
        ]
    
    # Primeiro, tentar executáveis npm diretos
    for npm_candidate in npm_candidates:
        if npm_candidate.exists():
            return npm_candidate
    
    # Se não encontrar, tentar usar npm-cli.js com node.exe
    for npm_cli in npm_cli_candidates:
        if npm_cli.exists():
            # Retornar como uma lista para usar com node.exe
            return [str(node_path), str(npm_cli)]
    
    # Se não encontrar, tentar usar npm do sistema
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("    Usando npm do sistema (PATH)")
            return "npm"  # Usar npm do PATH
    except:
        pass
    
    return None


def get_npm_global_prefix(node_path, npm_executable):
    """Obtém o prefixo global do npm usando o Node.js do SDK."""
    try:
        # Construir comando npm
        if isinstance(npm_executable, list):
            cmd = npm_executable + ["config", "get", "prefix"]
        else:
            cmd = [str(npm_executable), "config", "get", "prefix"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            prefix = result.stdout.strip()
            if prefix and os.path.exists(prefix):
                return Path(prefix)
    except Exception as e:
        print(f"    Aviso: Não foi possível obter prefixo npm: {e}")
    
    # Fallback: tentar localizações padrão
    platform = sys.platform
    if platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "npm"
    else:
        # Linux/macOS: /usr/local/lib/node_modules ou ~/.npm-global
        possible_paths = [
            Path("/usr/local/lib/node_modules"),
            Path.home() / ".npm-global",
        ]
        for path in possible_paths:
            if path.exists():
                return path.parent
    
    return None
    

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup completo do UPBGE JavaScript SDK")
    
    args = parser.parse_args()
    
    print("=== UPBGE JavaScript SDK Setup ===\n")
    
    # Criar estrutura de diretórios
    create_directory_structure()
    
    # Verificar Node.js
    base_dir = Path(__file__).parent.parent
    node_path = get_node_path(base_dir)
    
    if not node_path or not node_path.exists():
        print("\n=== Setup Incompleto ===")
        print("\nPróximos passos:")
        print("1. Instale Node.js: python scripts/download_dependencies.py")
        print("2. Configure o SDK path nas preferências do add-on no Blender")
        return
    
    print(f"\nNode.js encontrado: {node_path}")
        
    # Verificação final
    print("\n=== Verificação Final ===")
    all_ok = True
    
    if all_ok:
        print("\n=== Setup Concluído com Sucesso ===")
        print("\nPróximo passo:")
        print("Configure o SDK path nas preferências do add-on no Blender")
    else:
        print("\n=== Setup Parcialmente Concluído ===")
        print("\nAlgumas dependências não foram instaladas.")
        print("Execute novamente para tentar instalar novamente.")


if __name__ == "__main__":
    main()
