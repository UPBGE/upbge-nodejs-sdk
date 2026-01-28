# UPBGE JavaScript SDK

SDK completo para suporte JavaScript no UPBGE Game Engine, totalmente independente do core do UPBGE.

## Visão Geral

Este SDK fornece suporte para desenvolvimento JavaScript no UPBGE, incluindo:

- **Console Interativo**: Console JavaScript para testar código rapidamente
- **Integração com Editor Externo**: Abertura rápida do SDK/projeto em VS Code, Cursor ou editor personalizado
- **Type Definitions**: Definições de tipos em `types/` para uso opcional em editores que suportam TypeScript
- **Game Engine Integration**: Integração com controllers JavaScript no game engine

## Instalação

### Para Usuários Finais (Recomendado)

**Método Plug-and-Play**: Baixe o pacote oficial `upbge-javascript-sdk-X.X.X.zip` que inclui todos os binários necessários. Veja a seção "Opção 2" abaixo.

### Para Desenvolvedores

Se você está desenvolvendo ou contribuindo para o SDK, você precisará instalar as dependências manualmente:

1. **Estrutura de Diretórios**: Execute `python scripts/setup_sdk.py`
2. **Node.js**: Execute `python scripts/download_dependencies.py` ou instale manualmente (veja `INSTALL_DEPENDENCIES.md` se necessário)

### Opção 1: Instalação Manual

1. Clone ou baixe este repositório
2. Execute `python scripts/setup_sdk.py` para criar estrutura de diretórios
3. Instale dependências (Node.js) - veja `INSTALL_DEPENDENCIES.md` apenas se quiser instalar ferramentas extras
4. No Blender, vá em **Edit → Preferences → Add-ons**
5. Clique em **Install...** e selecione a pasta `upbge-javascript`
6. Ative o add-on "UPBGE JavaScript SDK"
7. Configure o caminho do SDK nas preferências do add-on

### Opção 2: Instalação via Add-on (ZIP) - Recomendado

1. **Baixe o pacote oficial** `upbge-javascript-sdk-X.X.X.zip` (inclui todos os binários)
2. No Blender/UPBGE, vá em **Edit → Preferences → Add-ons**
3. Clique em **Install...** e selecione o arquivo ZIP baixado
4. Ative o add-on "UPBGE JavaScript SDK"
5. **Pronto!** O SDK está funcionando (plug-and-play, sem necessidade de instalar dependências extras)

**Nota para Desenvolvedores**: Para criar um pacote de distribuição com todos os binários incluídos, execute:
```bash
python scripts/build_package.py
```

Isso criará um arquivo ZIP pronto para distribuição, incluindo o add-on e o runtime Node.js.

### Guia Rápido

Para um guia rápido de setup, consulte `SETUP.md`.

## Configuração

### Configurar SDK Path

1. Abra **Edit → Preferences → Add-ons**
2. Selecione "UPBGE JavaScript/TypeScript SDK"
3. Configure o **SDK Path** para o diretório do SDK
4. O SDK será carregado automaticamente

### Opções de SDK Path

O SDK pode ser configurado de três formas (em ordem de prioridade):

1. **Variável de Ambiente**: `BGE_JAVASCRIPT_SDK` (caminho absoluto)
2. **SDK Local**: `./bge_js_sdk/` relativo ao arquivo .blend
3. **Preferências**: Caminho configurado nas preferências do add-on

## Estrutura do SDK

```
upbge-javascript/
├── __init__.py              # Add-on principal
├── python/                   # Módulos Python
│   ├── console/             # Console JavaScript
│   ├── runtime/             # Runtime JavaScript (Node.js wrapper)
│   └── game_engine/         # Integração com game engine
├── runtime/                  # Node.js executáveis
│   ├── windows/
│   ├── linux/
│   └── macos/
├── lib/                      # (Opcional) bibliotecas e ferramentas adicionais
└── types/                    # Type definitions para uso em editores
    └── bge.d.ts
```

## Uso

### Console JavaScript

1. Abra o **Console** no Blender (Window → Toggle System Console ou Shift+F4)
2. No menu de linguagem do console, selecione **JavaScript**
3. Digite código e pressione Enter para executar

**Exemplo JavaScript:**
```javascript
>>> console.log("Hello, UPBGE!")
Hello, UPBGE!
>>> let x = 10 + 20
30
```

### Controllers JavaScript

1. No **Logic Editor**, adicione um **JavaScript Controller**
2. Selecione o controller e configure um script JavaScript usando o painel do add-on
3. O código será executado no game engine via Node.js

**Exemplo Controller:**
```javascript
// Move object forward
let obj = bge.logic.getCurrentObject();
if (obj) {
    obj.position[2] += 0.1;
}
```

### Type Definitions (opcional)

O diretório `types/` contém arquivos `.d.ts` opcionais para quem quiser melhor experiência em editores que suportam TypeScript. Eles não são usados pelo add-on em tempo de execução.

## Requisitos

- **UPBGE**: Versão 5.0 ou superior
- **Node.js**: Incluído no SDK (não requer instalação externa)

## Desenvolvimento

### Estrutura do Código

- `python/console/`: Console JavaScript
- `python/runtime/`: Wrapper Node.js para execução
- `python/game_engine/`: Integração com controllers

### Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

GPL-2.0-or-later (mesma licença do UPBGE)

## Links

- [Documentação](https://github.com/UPBGE/upbge-javascript-sdk/wiki)
- [Issues](https://github.com/UPBGE/upbge-javascript-sdk/issues)
- [UPBGE](https://upbge.org/)

## Notas

- O SDK é totalmente independente do UPBGE core
- Node.js é incluído no SDK
- O SDK pode ser atualizado independentemente do UPBGE
- Suporte a múltiplas versões do SDK por projeto
