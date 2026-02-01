# Guia de Build e Distribuição

Este documento explica como criar pacotes de distribuição do SDK para usuários finais.

## Visão Geral

O SDK precisa ser **plug-and-play** para usuários finais. Isso significa que o Node.js deve estar incluído no pacote ZIP de distribuição (ou detectado no sistema).

## Estrutura de Binários

### Arquivos Necessários para Distribuição

Para que o SDK funcione completamente, os seguintes binários devem estar presentes:

#### Windows
- `runtime/windows/node.exe` - Node.js executável
- `runtime/windows/npm.cmd` - npm wrapper (opcional)

#### Linux
- `runtime/linux/node-linux64` - Node.js executável

#### macOS
- `runtime/macos/node-osx` - Node.js executável

## Processo de Build

### 1. Preparar o Ambiente

Certifique-se de que todos os binários estão instalados:

```bash
# 1. Baixar Node.js
python scripts/download_dependencies.py

# 2. (Opcional) scripts/setup_sdk.py para estrutura de pastas
python scripts/setup_sdk.py
```

### 2. Verificar Arquivos

Antes de criar o pacote, verifique se todos os arquivos necessários estão presentes:

```bash
python scripts/build_package.py --check-only
```

Isso mostrará quais arquivos estão presentes e quais estão faltando.

### 3. Criar Pacote de Distribuição

Execute o script de build:

```bash
python scripts/build_package.py
```

Isso criará um arquivo ZIP em `../upbge-nodejs-sdk-X.X.X-YYYYMMDD.zip` com:
- Todos os arquivos Python do add-on
- Binários Node.js (runtime/)
- Arquivos de tipos (.d.ts) para editores
- Documentação essencial

### 4. Especificar Diretório de Saída (Opcional)

```bash
python scripts/build_package.py --output ./dist
```

## O que é Incluído no Pacote

### Incluído
- ✅ Todos os arquivos Python do add-on
- ✅ Binários do Node.js (runtime/)
- ✅ Definições de tipos (types/*.d.ts)
- ✅ README.md e CHANGELOG.md

### Excluído
- ❌ Scripts de desenvolvimento (scripts/)
- ❌ Arquivos temporários
- ❌ Cache Python (__pycache__)
- ❌ Arquivos de IDE (.vscode, .idea)
- ❌ INSTALL_DEPENDENCIES.md (não necessário no pacote final)
- ❌ SETUP.md (não necessário no pacote final)

## Estrutura do Pacote ZIP

O ZIP gerado terá a seguinte estrutura (importante: `__init__.py` deve estar dentro de um diretório):

```
upbge-nodejs-sdk-1.0.0-20240101.zip
└── upbge_nodejs_sdk/          ← Diretório do add-on (mesmo nome do bl_idname)
    ├── __init__.py            ← Deve estar dentro do diretório, não na raiz!
    ├── README.md
    ├── CHANGELOG.md
    ├── python/
    │   ├── __init__.py
    │   ├── start.py
    │   ├── preferences.py
    │   ├── operators.py
    │   ├── console/
    │   ├── game_engine/
    │   └── runtime/
    ├── types/
    │   ├── index.d.ts
    │   └── bge.d.ts
    └── runtime/
        ├── windows/
        │   └── node.exe
        ├── linux/
        │   └── node-linux64
        └── macos/
            └── node-osx
```

**IMPORTANTE**: O Blender requer que o `__init__.py` esteja dentro de um diretório no ZIP, não na raiz. O script `build_package.py` cria automaticamente essa estrutura correta.

## Instalação pelo Usuário Final

O usuário final simplesmente:

1. Baixa o arquivo ZIP
2. No Blender/UPBGE: **Edit → Preferences → Add-ons → Install...**
3. Seleciona o arquivo ZIP
4. Ativa o add-on
5. **Pronto!** O SDK funciona imediatamente (plug-and-play)

Não é necessário:
- ❌ Instalar Node.js separadamente (se incluído no ZIP)
- ❌ Configurar caminhos manualmente

## Notas Importantes

### Tamanho do Pacote

O pacote será relativamente grande (~30-50 MB) devido ao Node.js incluído:
- Node.js: ~30-50 MB
- Código Python e tipos: ~1-2 MB

Isso é aceitável para um SDK plug-and-play.

### Versionamento

O nome do arquivo ZIP inclui:
- Versão do SDK (do `bl_info` em `__init__.py`)
- Data de build (YYYYMMDD)

Exemplo: `upbge-nodejs-sdk-1.0.0-20240115.zip`

### Multiplataforma

O pacote inclui binários para todas as plataformas (Windows, Linux, macOS). O add-on detecta automaticamente a plataforma e usa os binários corretos.

## Troubleshooting

### Erro: "Arquivos faltando"

Se o script reportar arquivos faltando:

1. Execute `python scripts/download_dependencies.py` para baixar Node.js
2. Execute `python scripts/build_package.py --check-only` novamente

### Erro: "ZIP muito grande"

Se o ZIP estiver muito grande, verifique:
- Não incluir `node_modules/` desnecessários
- Não incluir arquivos de cache
- Verificar se `.gitignore` está correto

### Erro: "Add-on não funciona após instalação"

Verifique:
- Todos os binários estão no ZIP
- Permissões de execução (Linux/macOS)
- Estrutura de diretórios está correta
