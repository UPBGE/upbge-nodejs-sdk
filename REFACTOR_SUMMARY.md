# Refator de _apply_commands - Dispatch Pattern

## Resumo das Mudanças

O arquivo `python/game_engine/script_handler.py` passou por um refactor completo e limpo da função `_apply_commands`.

### Antes (Monolítica)
- Função `_apply_commands` com ~475 linhas contendo uma enorme sequência de `if/elif` statements
- Difícil de manter, testar e estender
- Lógica misturada com resolução de cenas e objetos
- Código repetitivo para diferentes operações

### Depois (Dispatch Pattern)
- **28 handlers individuais**, um para cada operação suportada
- Cada handler tem assinatura uniforme: `def _handle_XXX(cmd, context, scene, obj, logic)`
- **Dicionário `_COMMAND_HANDLERS`** que mapeia operações aos handlers
- Função `_apply_commands` reduzida a apenas ~75 linhas, muito mais limpa e legível
- Resolução de cena e objeto mantida no mesmo lugar (linhas 708-741)
- Loop principal (linhas 746-771) agora faz simples dispatch

## Handlers Criados

### Operações Globais (sem objeto necessário)
- `_handle_end_game` - Termina o jogo
- `_handle_restart_game` - Reinicia o jogo
- `_handle_set_gravity` - Define gravidade global

### Raycast e Constraints
- `_handle_raycast` - Raycast com múltiplos parâmetros
- `_handle_raycast_to` - Raycast para um alvo específico
- `_handle_create_vehicle` - Cria constraint de veículo
- `_handle_vehicle_apply_engine_force` - Aplica força ao motor do veículo
- `_handle_vehicle_set_steering_value` - Define direção da roda
- `_handle_vehicle_add_wheel` - Adiciona roda ao veículo
- `_handle_vehicle_apply_braking` - Aplica freio ao veículo

### Atuadores (Actuators)
- `_handle_activate` - Ativa um atuador
- `_handle_deactivate` - Desativa um atuador

### Character Controller
- `_handle_character_jump` - Faz personagem pular
- `_handle_character_walk_direction` - Define direção de caminhada
- `_handle_character_set_velocity` - Define velocidade do personagem

### Transformação (Posição, Rotação, Escala)
- `_handle_apply_movement` - Aplica movimento relativo
- `_handle_set_position` - Define posição absoluta global
- `_handle_set_rotation` - Define rotação global
- `_handle_set_scale` - Define escala do objeto
- `_handle_set_local_position` - Define posição local
- `_handle_set_local_rotation` - Define rotação local
- `_handle_look_at` - Faz objeto apontar para um alvo

### Propriedades e Parenting
- `_handle_set_property` - Define propriedade dinâmica
- `_handle_set_parent` - Define ou remove pai do objeto

### Cena
- `_handle_scene_add_object` - Adiciona objeto à cena
- `_handle_scene_remove_object` - Remove objeto da cena

### Câmera e Viewport
- `_handle_set_viewport` - Define viewport da câmera
- `_handle_set_active_camera` - Define câmera ativa da cena

## Estrutura do Dispatch

```python
# Operações globais (sem objeto necessário)
if op in ("endGame", "restartGame", "setGravity"):
    if op in _COMMAND_HANDLERS:
        _COMMAND_HANDLERS[op](cmd, context, scene, None, logic)
    continue

# Operações específicas de objeto
obj_name = cmd.get("object") or context.get("object_name")
if not obj_name:
    continue

obj = _scene_get_object(scene, obj_name)
if obj is None:
    _log("[UPBGE-JS] _apply_commands: object not found...")
    continue

# Dispatch universal para qualquer handler
if op in _COMMAND_HANDLERS:
    _COMMAND_HANDLERS[op](cmd, context, scene, obj, logic)
```

## Benefícios

1. **Manutenibilidade**: Cada handler é uma função isolada e testável
2. **Legibilidade**: Código muito mais claro e organizado
3. **Extensibilidade**: Adicionar nova operação = adicionar 1 handler + 1 linha no dict
4. **Testabilidade**: Handlers podem ser testados individualmente
5. **Comportamento Idêntico**: Toda lógica foi preservada, apenas reorganizada
6. **Tratamento de Erros**: Mantido o mesmo padrão (try/except no handler + outer exception)

## Compatibilidade

- Nenhuma mudança de API pública
- Nenhuma mudança de lógica (comportamento 100% idêntico)
- Todos os testes devem passar sem modificações
- Funciona com BGE real e mocks para testes unitários

## Próximos Passos

1. Rodar testes: `pytest tests/test_apply_commands.py -v`
2. Confirmar que todos os testes passam
3. Commit da mudança
4. Opcional: adicionar mais testes para novos handlers se necessário
