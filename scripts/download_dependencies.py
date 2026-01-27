#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Script para baixar e instalar dependências do SDK (Node.js).

Uso:
    python scripts/download_dependencies.py [--platform windows|linux|macos] [--version 24.13.0]
"""

import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
import argparse
from pathlib import Path

# URLs base para downloads
NODEJS_BASE_URL = "https://nodejs.org/dist"
NODEJS_VERSION = "v24.13.0"

# Estrutura de URLs por plataforma
PLATFORM_CONFIGS = {
    "windows": {
        "url": f"{NODEJS_BASE_URL}/{NODEJS_VERSION}/node-{NODEJS_VERSION}-win-x64.zip",
        "node_binary": "node.exe",
        "target_dir": "runtime/windows",
        "target_name": "node.exe",
    },
    "linux": {
        "url": f"{NODEJS_BASE_URL}/{NODEJS_VERSION}/node-{NODEJS_VERSION}-linux-x64.tar.xz",
        "node_binary": "bin/node",
        "target_dir": "runtime/linux",
        "target_name": "node-linux64",
    },
    "macos": {
        "url": f"{NODEJS_BASE_URL}/{NODEJS_VERSION}/node-{NODEJS_VERSION}-darwin-x64.tar.gz",
        "node_binary": "bin/node",
        "target_dir": "runtime/macos",
        "target_name": "node-osx",
    },
}


def get_platform():
    """Detecta a plataforma atual."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "macos"
    else:
        raise ValueError(f"Plataforma não suportada: {system}")


def download_file(url, dest_path):
    """Baixa um arquivo de uma URL."""
    print(f"Baixando {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Download concluído: {dest_path}")
        return True
    except Exception as e:
        print(f"Erro ao baixar: {e}")
        return False


def extract_zip(zip_path, extract_to, node_binary, target_path):
    """Extrai Node.js de um arquivo ZIP (Windows), incluindo npm."""
    print(f"Extraindo {zip_path}...")
    try:
        target_dir = target_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extrair tudo para um diretório temporário
            temp_extract = extract_to / "nodejs_temp"
            zip_ref.extractall(temp_extract)
            
            # Encontrar node.exe e npm
            node_found = False
            npm_found = False
            
            for root, dirs, files in os.walk(temp_extract):
                # Procurar node.exe
                if node_binary in files:
                    node_source = Path(root) / node_binary
                    shutil.copy2(node_source, target_path)
                    node_found = True
                    print(f"Extraído: {target_path}")
                
                # Procurar npm.cmd e npm (Windows)
                if "npm.cmd" in files:
                    npm_source = Path(root) / "npm.cmd"
                    npm_target = target_dir / "npm.cmd"
                    shutil.copy2(npm_source, npm_target)
                    npm_found = True
                    print(f"Extraído: {npm_target}")
                
                # Procurar node_modules/npm (necessário para npm funcionar)
                if "node_modules" in dirs:
                    npm_modules_source = Path(root) / "node_modules" / "npm"
                    if npm_modules_source.exists():
                        npm_modules_target = target_dir / "node_modules" / "npm"
                        if npm_modules_target.exists():
                            shutil.rmtree(npm_modules_target)
                        shutil.copytree(npm_modules_source, npm_modules_target)
                        npm_found = True
                        print(f"Extraído: {npm_modules_target}")
            
            # Limpar
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            
            if node_found:
                if not npm_found:
                    print("  Aviso: npm não encontrado no arquivo ZIP. O npm pode não funcionar corretamente.")
                return True
            return False
    except Exception as e:
        print(f"Erro ao extrair ZIP: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_tar(tar_path, extract_to, node_binary, target_path):
    """Extrai Node.js de um arquivo TAR (Linux/macOS)."""
    print(f"Extraindo {tar_path}...")
    try:
        # Determinar compressão
        mode = 'r'
        if tar_path.endswith('.xz'):
            mode = 'r:xz'
        elif tar_path.endswith('.gz'):
            mode = 'r:gz'
        
        with tarfile.open(tar_path, mode) as tar_ref:
            # Encontrar o membro do node
            for member in tar_ref.getmembers():
                if member.name.endswith(node_binary):
                    member.name = os.path.basename(member.name)
                    tar_ref.extract(member, extract_to)
                    # Mover para o destino final
                    extracted_path = os.path.join(extract_to, member.name)
                    if os.path.exists(extracted_path):
                        shutil.move(extracted_path, target_path)
                        # Tornar executável
                        os.chmod(target_path, 0o755)
                        print(f"Extraído: {target_path}")
                        return True
        return False
    except Exception as e:
        print(f"Erro ao extrair TAR: {e}")
        return False


def install_nodejs(platform_name, version=NODEJS_VERSION):
    """Instala Node.js para a plataforma especificada."""
    if platform_name not in PLATFORM_CONFIGS:
        print(f"Plataforma não suportada: {platform_name}")
        return False
    
    config = PLATFORM_CONFIGS[platform_name]
    config["url"] = config["url"].replace(NODEJS_VERSION, version)
    
    # Caminhos
    script_dir = Path(__file__).parent.parent
    target_dir = script_dir / config["target_dir"]
    target_path = target_dir / config["target_name"]
    
    # Criar diretório se não existir
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Verificar se já existe
    if target_path.exists():
        response = input(f"{target_path} já existe. Sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("Instalação cancelada.")
            return False
    
    # Baixar
    temp_file = script_dir / f"temp_nodejs_{platform_name}.{config['url'].split('.')[-1]}"
    if not download_file(config["url"], temp_file):
        return False
    
    # Extrair
    extract_to = script_dir / "temp_extract"
    extract_to.mkdir(exist_ok=True)
    
    success = False
    if platform_name == "windows":
        success = extract_zip(temp_file, extract_to, config["node_binary"], target_path)
    else:
        success = extract_tar(temp_file, extract_to, config["node_binary"], target_path)
    
    # Limpar arquivos temporários
    if temp_file.exists():
        temp_file.unlink()
    if extract_to.exists():
        shutil.rmtree(extract_to)
    
    if success:
        print(f"Node.js instalado com sucesso em {target_path}")
        return True
    else:
        print("Falha ao instalar Node.js")
        return False

def main():
    parser = argparse.ArgumentParser(description="Baixar e instalar dependências do SDK")
    parser.add_argument("--platform", choices=["windows", "linux", "macos"], 
                       help="Plataforma (padrão: detectar automaticamente)")
    parser.add_argument("--version", default=NODEJS_VERSION,
                       help=f"Versão do Node.js (padrão: {NODEJS_VERSION})")
    
    args = parser.parse_args()
    
    # Detectar plataforma se não especificada
    platform_name = args.platform or get_platform()
    
    print(f"Instalando dependências para plataforma: {platform_name}")
    print(f"Versão do Node.js: {args.version}")
    
    # Instalar Node.js
    if install_nodejs(platform_name, args.version):
        print("\nNode.js instalado com sucesso!")
        
    else:
        print("\nFalha ao instalar Node.js")
        sys.exit(1)


if __name__ == "__main__":
    main()
