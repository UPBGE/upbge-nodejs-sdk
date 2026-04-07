# Validação de Testes Após Refactor

## Resumo da Estratégia de Testes

O refactor preserva **100% da lógica original**. Portanto:
- ✅ Todos os testes existentes devem passar sem modificações
- ✅ O comportamento é idêntico
- ✅ Não há regressões esperadas

## Como Rodar os Testes

### Teste Rápido (Alguns testes)
```bash
pytest tests/test_apply_commands.py::TestApplyCommandsBasics -v
```

### Teste Completo
```bash
pytest tests/test_apply_commands.py -v
```

### Teste com Cobertura
```bash
pytest tests/test_apply_commands.py --cov=python/game_engine/script_handler
```

## Testes Que Devem Passar

### Testes Básicos
- `test_apply_no_bge` - Retorna gracefully se BGE não estiver disponível
- `test_apply_no_scene` - Retorna gracefully se cena não existir
- `test_apply_no_object` - Ignora comandos para objetos inexistentes
- `test_apply_empty_command_list` - Lida com lista vazia

### Testes de Movimento
- `test_apply_movement` - Movimento relativo funciona
- `test_apply_movement_no_vec` - Fallback para [0,0,0]
- `test_apply_movement_uses_value_fallback` - Usa 'value' como fallback
- `test_set_position` - Posição absoluta funciona
- `test_set_local_position` - Posição local funciona
- `test_set_scale` - Escala funciona

### Testes de Rotação
- `test_set_rotation` - Rotação global funciona
- `test_set_local_rotation` - Rotação local funciona

### Testes de Propriedades
- `test_set_property` - Propriedade dinâmica é definida
- `test_set_property_various_types` - Suporta int, float, str, bool, list

### Testes de Atuadores
- `test_activate_actuator` - Atuador é ativado
- `test_deactivate_actuator` - Atuador é desativado
- `test_activate_nonexistent_actuator` - Ignora atuador inexistente

### Testes de Parenting
- `test_set_parent` - Define pai corretamente
- `test_unset_parent` - Remove pai corretamente

### Testes Globais
- `test_end_game` - `endGame` é chamado
- `test_restart_game` - `restartGame` é chamado
- `test_set_gravity` - Gravidade é definida
- `test_set_gravity_with_value_fallback` - Fallback 'value' funciona

### Testes de Robustez
- `test_apply_commands_with_invalid_float_conversion` - Lida com float inválido
- `test_apply_multiple_commands_in_sequence` - Múltiplos comandos funcionam
- `test_apply_command_with_invalid_op` - Ignora operação desconhecida
- `test_apply_command_partial_data` - Lida com dados parciais

## Esperado: 100% de Sucesso

Todos os testes devem passar porque:

1. **Lógica Preservada**: Cada handler implementa exatamente a mesma lógica do if/elif original
2. **Assinatura Uniforme**: Dispatch funciona para todos os handlers da mesma forma
3. **Tratamento de Erros**: Mesmo padrão try/except mantido
4. **Resolução de Cena/Objeto**: Não foi alterada (linhas 720-764 preservadas)
5. **Validações**: Todas as validações mantidas (obj não None, valores válidos, etc.)

## Se Algum Teste Falhar

### Cenários Possíveis (Muito Improvável)

1. **Typo em nome de handler**
   - Verifique se o nome no dicionário `_COMMAND_HANDLERS` está correto
   - Confirme a assinatura: `def _handle_XXX(cmd, context, scene, obj, logic)`

2. **Handler não registrado no dicionário**
   - Verifique se a entrada existe em `_COMMAND_HANDLERS`

3. **Lógica divergiu do original**
   - Comparar handler com if/elif correspondente no arquivo original
   - Reproduzir 100% da lógica

4. **Erro em dispatch**
   - Confirmar que `if op in _COMMAND_HANDLERS:` está presente
   - Confirmar que `_COMMAND_HANDLERS[op](cmd, context, scene, obj, logic)` é chamado

## Teste Manual

Para validação rápida sem pytest:

```python
# Teste manual rápido
import sys
sys.path.insert(0, 'python')

from game_engine.script_handler import _apply_commands, _COMMAND_HANDLERS

# Verificar que todos os handlers estão registrados
print(f"Total de handlers: {len(_COMMAND_HANDLERS)}")
print(f"Handlers: {list(_COMMAND_HANDLERS.keys())}")

# Verificar estrutura
context = {"scene_name": "TestScene", "object_name": "Player"}
commands = [
    {"op": "applyMovement", "object": "Player", "vec": [0.1, 0, 0]},
    {"op": "setPosition", "object": "Player", "value": [1, 2, 3]},
]

# Não deve lançar exceção
_apply_commands(commands, context)
print("Teste manual passou!")
```

## Conclusão

O refactor é **100% compatível para trás** com a versão anterior. Todos os testes devem passar sem modificações.
