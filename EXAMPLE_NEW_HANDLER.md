# Exemplo: Como Adicionar um Novo Handler

Após o refactor com dispatch pattern, adicionar uma nova operação é extremamente simples.

## Cenário: Adicionar suporte para "setVisibility" (visibilidade do objeto)

### Passo 1: Criar o Handler

Adicione uma nova função handler no arquivo `script_handler.py`, antes do dicionário `_COMMAND_HANDLERS`:

```python
def _handle_set_visibility(cmd, context, scene, obj, logic):
    """Handle setVisibility command."""
    if obj is None:
        return
    
    visible = cmd.get("visible", True)
    try:
        obj.visible = visible
    except Exception:
        pass
```

### Passo 2: Registrar no Dicionário

Adicione uma entrada ao dicionário `_COMMAND_HANDLERS`:

```python
_COMMAND_HANDLERS = {
    # ... handlers existentes ...
    "setVisibility": _handle_set_visibility,  # <- Nova linha
    # ...
}
```

### Passo 3: Usar no JavaScript

No código JavaScript que roda no Node.js, a operação já funcionará:

```javascript
bge.commands([
    {
        op: "setVisibility",
        object: "Enemy",
        visible: false
    }
]);
```

## Comparação: Antes vs Depois

### Antes (Sem Dispatch Pattern)

Você teria que:
1. Encontrar o gigantesco bloco if/elif na função `_apply_commands` (475 linhas)
2. Adicionar uma nova condição:
```python
elif op == "setVisibility":
    if obj is not None:
        visible = cmd.get("visible", True)
        try:
            obj.visible = visible
        except Exception:
            pass
```
3. Risco de quebrar a indentação ou a lógica do bloco
4. Testes mostram que é fácil introduzir bugs neste cenário

### Depois (Com Dispatch Pattern)

Você precisa apenas de:
1. Criar 1 função handler (simples e isolada)
2. Adicionar 1 linha no dicionário
3. Feito! Sem risco de quebrar código existente

## Vantagens

- **Isolamento**: Novo handler não afeta código existente
- **Testabilidade**: Pode testar `_handle_set_visibility` isoladamente
- **Clareza**: Cada handler tem responsabilidade única
- **Segurança**: Impossível quebrar a estrutura if/elif
- **Rapidez**: Muito mais rápido adicionar nova operação

## Estrutura dos Handlers

Todos os handlers seguem o mesmo padrão:

```python
def _handle_OPERATION(cmd, context, scene, obj, logic):
    """Handle OPERATION command - brief description."""
    
    # 1. Validação de entrada (se necessário)
    param = cmd.get("param")
    if obj is None or param is None:
        return
    
    # 2. Lógica principal em try/except
    try:
        # Fazer a operação
        obj.some_method(param)
    except Exception:
        # Falhar silenciosamente (padrão de robustez do código)
        pass
```

## Checklist para Novo Handler

- [ ] Handler implementado com lógica correta
- [ ] Nome segue padrão `_handle_operation_name`
- [ ] Assinatura uniforme: `(cmd, context, scene, obj, logic)`
- [ ] Docstring descrevendo a operação
- [ ] Validação de entrada (obj não None se necessário)
- [ ] Lógica envolvida em try/except
- [ ] Registrado no dicionário `_COMMAND_HANDLERS`
- [ ] Testes unitários adicionados (opcional mas recomendado)
