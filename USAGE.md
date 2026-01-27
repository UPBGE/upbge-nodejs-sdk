# Guia de Uso - UPBGE Node.js SDK

Este documento explica como usar o SDK sem modificar o core do UPBGE.

## Funcionalidades Implementadas (via Add-on)

### 1. Consoles JavaScript/TypeScript

**Como usar:**
1. Abra o **Console** no Blender (Window → Toggle System Console ou Shift+F4)
2. No menu **"Languages..."**, você verá as opções:
   - **JavaScript**
   - **TypeScript**
3. Selecione a linguagem desejada
4. Digite código e pressione Enter para executar

**Exemplo:**
```javascript
>>> console.log("Hello, UPBGE!")
Hello, UPBGE!
>>> let x = 10 + 20
30
```

### 2. Painel no Logic Editor

**Localização:** Logic Editor → Painel lateral → Aba "Logic" → "JavaScript/TypeScript"

**Funcionalidades:**
- **Botões "Add JavaScript Controller" e "Add TypeScript Controller"**: Criam controllers Python que serão configurados para executar JavaScript/TypeScript
- **Lista de Controllers Ativos**: Mostra todos os controllers que têm arquivos `.js` ou `.ts` atribuídos
- **Botão "Setup"**: Configura automaticamente o controller para usar o runtime JavaScript/TypeScript

**Como usar:**
1. No Logic Editor, selecione um objeto
2. No painel lateral, vá para a aba "Logic"
3. Role até encontrar o painel "JavaScript/TypeScript"
4. Clique em "Add JavaScript Controller" ou "Add TypeScript Controller"
5. Atribua um arquivo `.js` ou `.ts` ao controller
6. Clique em "Setup for JavaScript" ou "Setup for TypeScript"
7. O controller agora executará via Node.js ao invés de Python

### 3. Painel no Text Editor

**Localização:** Text Editor → Painel lateral → Aba "Text" → "JavaScript/TypeScript"

**Funcionalidades:**
- **Detecção de Arquivos**: Detecta automaticamente arquivos `.ts` e `.js`
- **Informações do Arquivo**: Mostra tipo de arquivo, caminho, número de linhas
- **Compilação TypeScript**: Botão para compilar TypeScript para JavaScript
- **Execução via 'P'**: Ao pressionar **'P'** no text editor com um arquivo `.ts` ou `.js` aberto, o script será executado via Node.js (TypeScript será compilado automaticamente)

**Como usar:**
1. Abra ou crie um arquivo `.ts` ou `.js` no Text Editor
2. O painel "JavaScript/TypeScript" aparecerá automaticamente
3. Para arquivos TypeScript, use o botão "Compile TypeScript" para gerar JavaScript

### 4. Sistema de Wrapper para Controllers

**Como funciona:**
- Quando você atribui um arquivo `.ts` ou `.js` a um controller Python e clica em "Setup"
- O SDK cria um script Python wrapper automaticamente
- O wrapper detecta que o arquivo é JavaScript/TypeScript e redireciona a execução para o Node.js
- O script original permanece em `bpy.data.texts` e é acessado pelo wrapper

**Limitações:**
- O wrapper precisa ser configurado manualmente (botão "Setup")
- A execução ainda passa pelo Python primeiro, mas é redirecionada imediatamente
- Performance pode ser ligeiramente menor que execução nativa (mas ainda muito rápida)

## Workflow Recomendado

### Para Criar um Controller JavaScript/TypeScript:

1. **Criar o Script:**
   - No Text Editor, crie um novo arquivo (ex: `movement.js` ou `movement.ts`)
   - Escreva seu código JavaScript/TypeScript

2. **Adicionar Controller:**
   - No Logic Editor, selecione o objeto
   - No painel "JavaScript/TypeScript", clique em "Add JavaScript Controller" ou "Add TypeScript Controller"
   - Isso cria um controller Python

3. **Atribuir Script:**
   - No controller criado, atribua o arquivo `.js` ou `.ts` que você criou
   - O painel mostrará que o arquivo foi detectado

4. **Configurar Execução:**
   - Clique no botão "Setup for JavaScript" ou "Setup for TypeScript"
   - Isso cria o wrapper Python que intercepta a execução

5. **Testar:**
   - Pressione 'P' para iniciar o game engine
   - O script será executado via Node.js ao invés de Python

## Exemplo Completo

### 1. Criar Script TypeScript

No Text Editor, crie `movement.ts`:
```typescript
// Movimento básico com TypeScript
interface GameObject {
    position: [number, number, number];
}

let obj = bge.logic.getCurrentObject() as GameObject;
if (obj) {
    obj.position[2] += 0.1;
}
```

### 2. Adicionar Controller

1. Logic Editor → Painel "JavaScript/TypeScript" → "Add TypeScript Controller"
2. Atribua `movement.ts` ao controller
3. Clique em "Setup for TypeScript"

### 3. Executar

Pressione 'P' - o script será compilado e executado via Node.js!

## Troubleshooting

### Consoles não aparecem no menu "Languages"

**Solução:**
1. Recarregue o add-on (desative e ative novamente)
2. Verifique o console do Blender para mensagens de erro
3. Certifique-se de que o SDK path está configurado corretamente

### Controller não executa JavaScript/TypeScript

**Solução:**
1. Certifique-se de que clicou em "Setup" após atribuir o arquivo
2. Verifique se o arquivo tem extensão `.js`, `.mjs`, `.ts` ou `.tsx`
3. Verifique o console do Blender para erros de execução
4. Certifique-se de que Node.js está instalado no SDK (execute `setup_sdk.py`)

### Erro "UPBGE JavaScript SDK not found"

**Solução:**
1. Certifique-se de que o add-on está instalado e ativado
2. Configure o SDK path nas preferências do add-on
3. Recarregue o add-on

### Syntax highlighting não funciona (sem cores da linguagem)

**Problema:** Os arquivos `.ts` e `.js` aparecem sem syntax highlighting (todas as cores iguais).

**Causa:** O syntax highlighting no editor de texto do Blender/UPBGE é implementado em C++ e não pode ser adicionado via add-on Python. Requer modificação em `source/blender/editors/space_text/text_format.cc`.

**Solução:** Esta é uma limitação conhecida que só pode ser resolvida modificando o código C++ do UPBGE. O add-on fornece todas as outras funcionalidades (execução, compilação, consoles), mas não pode adicionar syntax highlighting.

## Próximos Passos

Para funcionalidade completa (syntax highlighting nativo, controllers nativos), seria necessário:
- Implementar suporte a `.ts/.js` no `format_identifier` (C++)
- Criar `SCA_JavaScriptController` e `SCA_TypeScriptController` (C++)
- Modificar execução de scripts no game engine (C++)

Mas com as soluções atuais via add-on, você já pode:
- ✅ Usar consoles JavaScript/TypeScript
- ✅ Criar controllers JavaScript/TypeScript
- ✅ Executar scripts `.ts/.js` no game engine
- ✅ Compilar TypeScript para JavaScript
