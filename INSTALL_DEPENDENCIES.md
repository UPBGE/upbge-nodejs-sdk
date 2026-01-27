# Instruções para Instalar Dependências do SDK

Este documento explica como instalar Node.js, TypeScript Compiler e TypeScript Language Server no SDK.

## Pré-requisitos

- Acesso à internet para baixar os binários
- Ferramentas para extrair arquivos (7-Zip, tar, etc.)

## Opção 1: Instalação Manual (Recomendado para Desenvolvimento)

### 1. Instalar Node.js

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

### 2. Instalar TypeScript Compiler

1. Use o Node.js instalado no SDK:
   - Windows: `runtime\windows\node.exe npm install -g typescript`
   - Linux: `runtime/linux/node-linux64 npm install -g typescript`
   - macOS: `runtime/macos/node-osx npm install -g typescript`

2. Copie o binário `tsc`:
   - Windows: Copie de `%APPDATA%\npm\node_modules\typescript\bin\tsc` para `lib/typescript/tsc.exe`
   - Linux/macOS: Copie de `/usr/local/lib/node_modules/typescript/bin/tsc` para `lib/typescript/tsc`
   - Torne executável (Linux/macOS): `chmod +x lib/typescript/tsc`

### 3. Instalar TypeScript Language Server

1. Use o Node.js instalado no SDK:
   - Windows: `runtime\windows\node.exe npm install -g typescript-language-server`
   - Linux: `runtime/linux/node-linux64 npm install -g typescript-language-server`
   - macOS: `runtime/macos/node-osx npm install -g typescript-language-server`

2. Copie o binário:
   - Windows: Copie de `%APPDATA%\npm\node_modules\typescript-language-server\lib\cli.js` para `lib/lsp/typescript-language-server`
   - Linux/macOS: Copie de `/usr/local/lib/node_modules/typescript-language-server/lib/cli.js` para `lib/lsp/typescript-language-server`
   - Torne executável (Linux/macOS): `chmod +x lib/lsp/typescript-language-server`

## Opção 2: Script de Instalação Automática (Futuro)

Um script Python será criado para automatizar o download e instalação de todas as dependências.

## Verificação

Após instalar, verifique se os arquivos existem:

- `runtime/windows/node.exe` (Windows)
- `runtime/linux/node-linux64` (Linux)
- `runtime/macos/node-osx` (macOS)
- `lib/typescript/tsc` ou `lib/typescript/tsc.exe`
- `lib/lsp/typescript-language-server`

## Notas

- Use sempre versões LTS do Node.js para estabilidade
- Mantenha as versões consistentes entre plataformas
- Os binários devem ser executáveis (Linux/macOS)
