# UPBGE JavaScript/TypeScript SDK

SDK completo para suporte JavaScript/TypeScript no UPBGE Game Engine, totalmente independente do core do UPBGE.

## Visão Geral

Este SDK fornece suporte completo para desenvolvimento JavaScript/TypeScript no UPBGE, incluindo:

- **Console Interativo**: Console JavaScript e TypeScript para testar código rapidamente
- **Integração com Editor Externo**: Abertura rápida do SDK/projeto em VS Code, Cursor ou editor personalizado
- **Compilação TypeScript**: Compilação automática de TypeScript para JavaScript
- **Type Definitions**: Definições de tipos TypeScript para a API do BGE
- **Game Engine Integration**: Integração com controllers JavaScript/TypeScript no game engine

## Instalação

### Para Usuários Finais (Recomendado)

**Método Plug-and-Play**: Baixe o pacote oficial `upbge-javascript-sdk-X.X.X.zip` que inclui todos os binários necessários. Veja a seção "Opção 2" abaixo.

### Para Desenvolvedores

Se você está desenvolvendo ou contribuindo para o SDK, você precisará instalar as dependências manualmente:

1. **Estrutura de Diretórios**: Execute `python scripts/setup_sdk.py`
2. **Node.js**: Execute `python scripts/download_dependencies.py` ou instale manualmente (veja `INSTALL_DEPENDENCIES.md`)
3. **TypeScript e LSP**: Execute `python scripts/setup_sdk.py` (instala automaticamente) ou instale manualmente (veja `INSTALL_DEPENDENCIES.md`)

### Opção 1: Instalação Manual

1. Clone ou baixe este repositório
2. Execute `python scripts/setup_sdk.py` para criar estrutura de diretórios
3. Instale dependências (Node.js, TypeScript, LSP) - veja `INSTALL_DEPENDENCIES.md`
4. No Blender, vá em **Edit → Preferences → Add-ons**
5. Clique em **Install...** e selecione a pasta `upbge-javascript`
6. Ative o add-on "UPBGE JavaScript/TypeScript SDK"
7. Configure o caminho do SDK nas preferências do add-on

### Opção 2: Instalação via Add-on (ZIP) - Recomendado

1. **Baixe o pacote oficial** `upbge-javascript-sdk-X.X.X.zip` (inclui todos os binários)
2. No Blender/UPBGE, vá em **Edit → Preferences → Add-ons**
3. Clique em **Install...** e selecione o arquivo ZIP baixado
4. Ative o add-on "UPBGE JavaScript/TypeScript SDK"
5. **Pronto!** O SDK está funcionando (plug-and-play, sem necessidade de instalar dependências)

**Nota para Desenvolvedores**: Para criar um pacote de distribuição com todos os binários incluídos, execute:
```bash
python scripts/build_package.py
```

Isso criará um arquivo ZIP pronto para distribuição, incluindo Node.js, TypeScript e TypeScript Language Server.

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
│   ├── console/             # Consoles JavaScript/TypeScript
│   ├── editor/              # (Legado) módulos de integração com o Text Editor interno
│   ├── runtime/             # Runtime JavaScript (Node.js wrapper)
│   └── game_engine/         # Integração com game engine
├── runtime/                  # Node.js executáveis
│   ├── windows/
│   ├── linux/
│   └── macos/
├── lib/                      # Bibliotecas e ferramentas
│   ├── typescript/          # TypeScript compiler
│   └── lsp/                 # Language Server Protocol
└── types/                    # Type definitions TypeScript
    └── bge.d.ts
```

## Uso

### Console JavaScript/TypeScript

1. Abra o **Console** no Blender (Window → Toggle System Console ou Shift+F4)
2. No menu de linguagem do console, selecione **JavaScript** ou **TypeScript**
3. Digite código e pressione Enter para executar

**Exemplo JavaScript:**
```javascript
>>> console.log("Hello, UPBGE!")
Hello, UPBGE!
>>> let x = 10 + 20
30
```

**Exemplo TypeScript:**
```typescript
>>> interface Point { x: number; y: number; }
>>> let p: Point = { x: 10, y: 20 }
{ x: 10, y: 20 }
```

### Controllers JavaScript/TypeScript

1. No **Logic Editor**, adicione um **JavaScript Controller**
2. Selecione o controller e configure:
   - **Script Text**: Código JavaScript/TypeScript
   - **Use TypeScript**: Marque se o código é TypeScript
3. O código será compilado e executado no game engine

**Exemplo Controller:**
```javascript
// Move object forward
let obj = bge.logic.getCurrentObject();
if (obj) {
    obj.position[2] += 0.1;
}
```

### Type Definitions

Para usar as type definitions TypeScript em seu projeto:

1. Instale o TypeScript: `npm install -g typescript`
2. Configure `tsconfig.json`:
```json
{
  "compilerOptions": {
    "types": ["./upbge-javascript/types"]
  }
}
```

3. Importe os tipos:
```typescript
/// <reference path="./upbge-javascript/types/bge.d.ts" />

let scene = bge.logic.getCurrentScene();
let obj = scene.getObject("Cube");
```

## Requisitos

- **UPBGE**: Versão 5.0 ou superior
- **Node.js**: Incluído no SDK (não requer instalação externa)
- **TypeScript**: Incluído no SDK (não requer instalação externa)

## Desenvolvimento

### Estrutura do Código

- `python/console/`: Consoles JavaScript/TypeScript
- `python/runtime/`: Wrapper Node.js para execução
- `python/editor/`: (Legado) integração com o Text Editor interno – não registrado por padrão
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
- Node.js e TypeScript são incluídos no SDK
- O SDK pode ser atualizado independentemente do UPBGE
- Suporte a múltiplas versões do SDK por projeto
