# Troubleshooting - UPBGE Node.js SDK

## Problema: Add-on instalado mas nada funciona

### Verificações Necessárias

#### 1. SDK Path está vazio

**Sintoma:** SDK Path nas preferências está vazio

**Solução:**
- O SDK deve detectar automaticamente quando instalado via ZIP
- Se não detectar, configure manualmente:
  1. Vá em **Edit → Preferences → Add-ons**
  2. Selecione "UPBGE Node.js SDK"
  3. Clique no ícone de pasta ao lado de "SDK Path"
  4. Selecione o diretório do add-on: `C:\Users\bruno\AppData\Roaming\UPBGE\Blender\5.0\scripts\addons\upbge_nodejs_sdk\`
  5. O SDK será reiniciado automaticamente

#### 2. Verificar se o SDK está carregado

**Como verificar:**
1. Abra o **Console do Blender** (Window → Toggle System Console)
2. Procure por mensagens como:
   - `UPBGE Node.js SDK: Add-on registered`
   - `UPBGE JavaScript SDK: Console modules registered`
   - `UPBGE JavaScript SDK: Editor modules registered`
   - `UPBGE JavaScript SDK: Game engine modules registered`
   - `Running UPBGE JavaScript SDK from ...`

**Se não aparecer:**
- O SDK não está sendo carregado
- Verifique se há erros no console
- Verifique se o SDK Path está configurado

#### 3. Consoles não aparecem no menu "Languages"

**Verificações:**
1. Recarregue o add-on (desative e ative novamente)
2. Verifique o console do Blender para mensagens de erro
3. Verifique se aparecem mensagens como:
   - `UPBGE JavaScript SDK: Console modules in sys.modules: ['console_javascript']`

**Se ainda não aparecer:**
- Os módulos podem não estar sendo registrados corretamente
- Verifique se há erros de importação no console

#### 4. Logs do fluxo da ponte (bridge)

**O que são:** Mensagens com prefixo `[UPBGE-JS]` no console que mostram cada passo do fluxo (wrapper → Node.js → extração de comandos → aplicação no BGE).

**Ordem típica ao dar Play e pressionar uma tecla:**
- `[UPBGE-JS] Wrapper executing script: ...`
- `[UPBGE-JS] Context built object_name=... scene_name=...`
- `[UPBGE-JS] Node execute_with_context code_len=... node_path=...`
- `[UPBGE-JS] Node subprocess done returncode=... output_len=... has_marker=...`
- `[UPBGE-JS] Node run success=... output_len=...`
- `[UPBGE-JS] Extracted N commands`
- `[UPBGE-JS] _apply_commands scene=... object_name=... num_commands=...`
- `[UPBGE-JS] applyMovement obj=... vec=...` (quando há movimento)
- `[UPBGE-JS] JS execution success=...`

**Se o cubo não se mover:** confira se aparece `applyMovement obj=...` e se `object not found` não aparece. Se `has_marker=False` ou `Extracted 0 commands`, o Node não está enviando comandos.

**Desativar os logs:** em `python/game_engine/script_handler.py` defina `DEBUG_BRIDGE_LOGS = False`; em `python/runtime/nodejs.py` defina `DEBUG_NODE_LOGS = False`.

#### 5. Painel no Logic Editor não aparece

**Verificações:**
1. Certifique-se de que está no **Logic Editor**
2. No painel lateral, role até encontrar a aba **"Logic"**
3. Procure pelo painel **"JavaScript"**

**Se não aparecer:**
- Verifique se há erros no console do Blender
- Verifique se o módulo `ui` está sendo registrado

#### 6. Controller ainda executa como Python

**Sintoma:** Ao pressionar 'P', o erro mostra que Python está tentando executar o arquivo `.js`

**Solução:**
1. No Logic Editor, vá para o painel "JavaScript"
2. Encontre o controller que tem o arquivo `.js`
3. Clique no botão **"Setup for JavaScript"**
4. Isso criará o wrapper Python que intercepta a execução

**Importante:** O wrapper precisa ser configurado manualmente após atribuir o arquivo ao controller.

## Checklist de Verificação

Após instalar o add-on, verifique:

- [ ] SDK Path está configurado (ou foi auto-detectado)
- [ ] Mensagens de registro aparecem no console do Blender
- [ ] Console mostra "Running UPBGE JavaScript SDK from ..."
- [ ] Menu "Languages" no console mostra "JavaScript"
- [ ] Painel "JavaScript" aparece no Logic Editor
- [ ] Controllers foram configurados com "Setup" após atribuir arquivos `.js`

## Erros Comuns

### "Configure UPBGE JavaScript SDK path first"

**Causa:** SDK Path não está configurado

**Solução:** Configure o SDK Path nas preferências do add-on

### "UPBGE JavaScript SDK not found" no wrapper

**Causa:** O wrapper não consegue importar o módulo do SDK

**Solução:** 
1. Verifique se o add-on está ativado
2. Recarregue o add-on
3. Reconfigure o controller (clique em "Setup" novamente)

### "Node.js not found"

**Causa:** Node.js não está instalado no SDK

**Solução:**
1. Execute `python scripts/download_dependencies.py` para baixar Node.js
2. Execute `python scripts/setup_sdk.py` para configurar a estrutura do SDK
3. Recarregue o add-on

## Logs de Debug

Para ver logs detalhados:
1. Abra o Console do Blender
2. Procure por mensagens que começam com "UPBGE JavaScript SDK:" ou "UPBGE Node.js SDK:"
3. Essas mensagens indicam o que está funcionando e o que não está

## Próximos Passos

Se nada funcionar após seguir este guia:
1. Verifique o console do Blender para erros específicos
2. Certifique-se de que todos os binários essenciais estão instalados (Node.js)
3. Tente recarregar o add-on completamente (desative, feche Blender, reabra, ative)
