# Notas de Implementação - Integração com UPBGE Core

Este documento descreve as funcionalidades que precisam ser implementadas no código C++ do UPBGE para suporte completo ao JavaScript/TypeScript.

## 1. Reconhecimento de Arquivos no Editor de Texto

**Status**: Parcialmente implementado (requer C++)

O editor de texto do Blender/UPBGE usa `format_identifier` em C++ para reconhecer tipos de arquivo. Para suporte completo a `.ts` e `.js`:

**Arquivo**: `source/blender/editors/space_text/text_format.cc` ou similar

**Necessário**:
- Adicionar `"typescript"` e `"javascript"` aos formatos reconhecidos
- Configurar `format_identifier` para retornar o formato correto baseado na extensão do arquivo
- Implementar syntax highlighting para TypeScript/JavaScript (ou usar uma biblioteca existente)

**Workaround atual**: O SDK registra handlers Python que detectam arquivos `.ts/.js`, mas o syntax highlighting completo requer C++.

## 2. Controllers JavaScript/TypeScript no Logic Bricks

**Status**: Não implementado (requer C++)

**Arquivo**: `source/blender/gameengine/` (provavelmente `SCA_PythonController.h/cpp` ou similar)

**Necessário**:
1. Criar `SCA_JavaScriptController` similar a `SCA_PythonController`
2. Registrar o tipo de controller no enum de tipos (provavelmente em `KX_GameObject.h` ou similar)
3. Adicionar opções "JavaScript" e "TypeScript" no menu de controllers
4. Implementar execução de scripts JavaScript/TypeScript usando o Node.js do SDK

**Workaround atual**: O SDK fornece `script_handler.py` que pode interceptar execução, mas a integração completa requer C++.

## 3. Execução de Scripts no Game Engine

**Status**: Não implementado (requer C++)

**Necessário**:
- Modificar o game engine para detectar quando um controller Python tem um arquivo `.ts` ou `.js`
- Redirecionar a execução para o runtime JavaScript/TypeScript ao invés do Python interpreter
- Ou criar controllers JavaScript/TypeScript nativos que usam o Node.js do SDK

**Arquivo**: Provavelmente em `source/blender/gameengine/` onde os controllers são executados.

## 4. Consoles JavaScript/TypeScript

**Status**: Implementado (Python)

Os consoles JavaScript/TypeScript estão implementados em Python e devem aparecer no menu "Languages" do console. Se não aparecerem:

1. Verificar se os módulos estão sendo registrados corretamente em `sys.modules`
2. Verificar se o menu de linguagens está procurando por `console_*` ou `_console_*`
3. Garantir que os módulos têm a função `execute` implementada

**Arquivos do SDK**:
- `python/console/javascript.py`
- `python/console/typescript.py`
- `python/console/__init__.py`

## Próximos Passos

### Para Desenvolvedores do UPBGE Core:

1. **Editor de Texto**: Adicionar suporte a `.ts` e `.js` em `format_identifier`
2. **Controllers**: Criar `SCA_JavaScriptController` e `SCA_TypeScriptController`
3. **Game Engine**: Modificar execução de scripts para detectar e usar runtime JavaScript

### Para Usuários do SDK:

1. **Workaround para Controllers**: Por enquanto, use controllers Python e atribua arquivos `.ts/.js` a eles. O SDK tentará interceptar, mas funcionalidade completa requer C++.
2. **Consoles**: Os consoles JavaScript/TypeScript devem aparecer no menu "Languages" após instalar o SDK.
3. **Editor de Texto**: Syntax highlighting pode não funcionar completamente até que seja implementado em C++.

## Referências

- Armory SDK: Exemplo de como um SDK externo pode integrar com Blender/UPBGE
- Blender Python API: Para entender como registrar novos tipos e handlers
- UPBGE Source Code: Para ver como controllers Python são implementados
