# Instruções para Instalar Dependências do SDK

Este documento explica como instalar Node.js no SDK (quando não usar o pacote pré-empacotado).

## Pré-requisitos

- Acesso à internet para baixar os binários
- Ferramentas para extrair arquivos (7-Zip, tar, etc.)

## Opção 1: Instalação Manual

### Instalar Node.js

#### Windows:
1. Baixe Node.js LTS (v20.x ou v22.x) de https://nodejs.org/
2. Baixe a versão "Windows Binary (.zip)" para x64
3. Extraia o arquivo ZIP
4. Copie `node.exe` para `runtime/windows/node.exe`

#### Linux:
1. Baixe Node.js LTS de https://nodejs.org/
2. Baixe a versão "Linux Binary (x64)" (.tar.xz)
3. Extraia: `tar -xf node-v*.tar.xz`
4. Copie o binário `node` para `runtime/linux/node-linux64`
5. Torne executável: `chmod +x runtime/linux/node-linux64`

#### macOS:
1. Baixe Node.js LTS de https://nodejs.org/
2. Baixe a versão "macOS Binary (x64)" (.tar.gz)
3. Extraia: `tar -xzf node-v*.tar.gz`
4. Copie o binário `node` para `runtime/macos/node-osx`
5. Torne executável: `chmod +x runtime/macos/node-osx`

## Opção 2: Script de Download

Use o script do SDK para baixar Node.js:

```bash
python scripts/download_dependencies.py
```

## Verificação

Após instalar, verifique se o arquivo existe:

- `runtime/windows/node.exe` (Windows)
- `runtime/linux/node-linux64` (Linux)
- `runtime/macos/node-osx` (macOS)

## Notas

- Use sempre versões LTS do Node.js para estabilidade
- Os binários devem ser executáveis (Linux/macOS)
