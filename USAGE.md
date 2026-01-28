# Guia de Uso - UPBGE Node.js SDK

Este documento explica como usar o SDK sem modificar o core do UPBGE.

## Funcionalidades Implementadas (via Add-on)

### 1. Console JavaScript

**Como usar:**
1. Abra o **Console** no Blender (Window → Toggle System Console ou Shift+F4)
2. No menu **"Languages..."**, selecione:
   - **JavaScript**
3. Digite código e pressione Enter para executar

**Exemplo:**
```javascript
>>> console.log("Hello, UPBGE!")
Hello, UPBGE!
>>> let x = 10 + 20
30
```

### 2. Painel no Logic Editor

**Localização:** Logic Editor → Painel lateral → Aba "Logic" → "JavaScript"

**Funcionalidades:**
- **Botão "Add JavaScript Controller"**: Cria um controller Python que será configurado para executar JavaScript
- **Lista de Controllers Ativos**: Mostra todos os controllers que têm arquivos `.js` atribuídos
- **Botão "Setup"**: Configura automaticamente o controller para usar o runtime JavaScript

**Como usar:**
1. No Logic Editor, selecione um objeto
2. No painel lateral, vá para a aba "Logic"
3. Role até encontrar o painel "JavaScript"
4. Clique em "Add JavaScript Controller"
5. Atribua um arquivo `.js` ao controller
6. Clique em "Setup for JavaScript"
7. O controller agora executará via Node.js ao invés de Python

### 3. (Legado) Painel no Text Editor

O SDK não registra mais o painel de editor interno por padrão. O desenvolvimento de scripts deve ser feito em um editor externo (VS Code, Cursor, etc.) usando arquivos `.js` diretamente.

### 4. Sistema de Wrapper para Controllers

**Como funciona:**
- Quando você atribui um arquivo `.js` a um controller Python e clica em "Setup"
- O SDK cria um script Python wrapper automaticamente
- O wrapper detecta que o arquivo é JavaScript e redireciona a execução para o Node.js
- O script original permanece em `bpy.data.texts` e é acessado pelo wrapper

**Limitações:**
- O wrapper precisa ser configurado manualmente (botão "Setup")
- A execução ainda passa pelo Python primeiro, mas é redirecionada imediatamente
- Performance pode ser ligeiramente menor que execução nativa (mas ainda muito rápida)

## Workflow Recomendado

### Workflow para Criar um Controller JavaScript

1. **Criar o Script em Editor Externo:**
   - Crie um arquivo `.js` (ex: `movement.js`) em um diretório do seu projeto
   - Escreva seu código JavaScript normalmente

2. **Adicionar Controller:**
   - No Logic Editor, selecione o objeto
   - No painel "JavaScript", clique em "Add JavaScript Controller"
   - Isso cria um controller Python

3. **Atribuir Script (Load JS From File):**
   - No painel "JavaScript", use o botão **"Load JS File"** para escolher o arquivo `.js` no disco
   - O painel mostrará que o arquivo foi detectado

4. **Configurar Execução:**
   - Clique no botão "Setup for JavaScript"
   - Isso cria o wrapper Python que intercepta a execução

5. **Testar:**
   - Pressione 'P' para iniciar o game engine
   - O script `.js` será executado via Node.js ao invés de Python

## Troubleshooting

### Consoles não aparecem no menu "Languages"

**Solução:**
1. Recarregue o add-on (desative e ative novamente)
2. Verifique o console do Blender para mensagens de erro
3. Certifique-se de que o SDK path está configurado corretamente

### Controller não executa JavaScript

**Solução:**
1. Certifique-se de que clicou em "Setup" após atribuir o arquivo
2. Verifique se o arquivo tem extensão `.js` ou `.mjs`
3. Verifique o console do Blender para erros de execução
4. Certifique-se de que Node.js está instalado no SDK (execute `setup_sdk.py`)

### Erro "UPBGE JavaScript SDK not found"

**Solução:**
1. Certifique-se de que o add-on está instalado e ativado
2. Configure o SDK path nas preferências do add-on
3. Recarregue o add-on

### Syntax highlighting não funciona (sem cores da linguagem)

**Problema:** Os arquivos `.js` aparecem sem syntax highlighting (todas as cores iguais).

**Causa:** O syntax highlighting no editor de texto do Blender/UPBGE é implementado em C++ e não pode ser adicionado via add-on Python. Requer modificação em `source/blender/editors/space_text/text_format.cc`.

**Solução:** Esta é uma limitação conhecida que só pode ser resolvida modificando o código C++ do UPBGE. O add-on fornece a execução via Node.js e integração com controllers, mas não pode adicionar syntax highlighting.

## Próximos Passos

Para funcionalidade completa (syntax highlighting nativo, controllers nativos), seria necessário:
- Implementar suporte a `.js` no `format_identifier` (C++)
- Criar `SCA_JavaScriptController` nativo
- Modificar execução de scripts no game engine (C++)

Mas com as soluções atuais via add-on, você já pode:
- ✅ Usar console JavaScript
- ✅ Criar controllers JavaScript
- ✅ Executar scripts `.js` no game engine
