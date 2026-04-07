# Referência Completa de Handlers

## Índice de Handlers por Categoria

---

## 1. Operações Globais (3 handlers)

### endGame
- **Localização**: Linha 99
- **Descrição**: Termina o jogo
- **Parâmetros**: Nenhum adicional
- **Exemplo de comando**:
```json
{"op": "endGame"}
```

### restartGame
- **Localização**: Linha 107
- **Descrição**: Reinicia o jogo
- **Parâmetros**: Nenhum adicional
- **Exemplo de comando**:
```json
{"op": "restartGame"}
```

### setGravity
- **Localização**: Linha 115
- **Descrição**: Define gravidade global
- **Parâmetros**: `vec` (array [x, y, z]) ou `value` (fallback)
- **Exemplo de comando**:
```json
{"op": "setGravity", "vec": [0, 0, -9.81]}
```

---

## 2. Raycast e Detecção (2 handlers)

### rayCast
- **Localização**: Linha 211
- **Descrição**: Raycast com múltiplos parâmetros
- **Parâmetros**:
  - `to` (array): Ponto final [x, y, z]
  - `from` (array): Ponto inicial [x, y, z] (opcional)
  - `dist` (float): Distância
  - `prop` (string): Propriedade
  - `face` (bool): Inclui face
  - `xray` (bool): Modo X-ray
  - `mask` (int): Máscara de colisão
- **Exemplo de comando**:
```json
{"op": "rayCast", "object": "Camera", "to": [0, 0, -10], "dist": 100}
```

### rayCastTo
- **Localização**: Linha 240
- **Descrição**: Raycast para um alvo específico
- **Parâmetros**:
  - `target` (array ou string): Ponto [x, y, z] ou nome do objeto
  - `dist` (float): Distância
  - `prop` (string): Propriedade
- **Exemplo de comando**:
```json
{"op": "rayCastTo", "object": "Camera", "target": "Enemy", "dist": 100}
```

---

## 3. Constraints de Veículo (5 handlers)

### createVehicle
- **Localização**: Linha 266
- **Descrição**: Cria constraint de veículo no objeto
- **Parâmetros**: Nenhum adicional (usa physics_id do objeto)
- **Exemplo de comando**:
```json
{"op": "createVehicle", "object": "CarChassis"}
```

### vehicleApplyEngineForce
- **Localização**: Linha 283
- **Descrição**: Aplica força ao motor do veículo
- **Parâmetros**:
  - `wheelIndex` (int): Índice da roda
  - `force` (float): Força a aplicar
- **Exemplo de comando**:
```json
{"op": "vehicleApplyEngineForce", "object": "CarChassis", "wheelIndex": 0, "force": 100}
```

### vehicleSetSteeringValue
- **Localização**: Linha 299
- **Descrição**: Define direção de uma roda
- **Parâmetros**:
  - `wheelIndex` (int): Índice da roda
  - `value` (float): Valor de direção
- **Exemplo de comando**:
```json
{"op": "vehicleSetSteeringValue", "object": "CarChassis", "wheelIndex": 0, "value": 0.5}
```

### vehicleAddWheel
- **Localização**: Linha 315
- **Descrição**: Adiciona roda ao veículo
- **Parâmetros**:
  - `wheel` (string): Nome do objeto da roda
  - `attachPos` (array): Posição de conexão [x, y, z]
  - `downDir` (array): Direção para baixo [x, y, z]
  - `axleDir` (array): Direção do eixo [x, y, z]
  - `suspensionRestLength` (float): Comprimento de repouso da suspensão
  - `wheelRadius` (float): Raio da roda
  - `hasSteering` (bool): Tem direção
- **Exemplo de comando**:
```json
{
  "op": "vehicleAddWheel",
  "object": "CarChassis",
  "wheel": "Wheel_FL",
  "attachPos": [1, 1, 0],
  "wheelRadius": 0.4,
  "hasSteering": true
}
```

### vehicleApplyBraking
- **Localização**: Linha 345
- **Descrição**: Aplica freio a uma roda
- **Parâmetros**:
  - `wheelIndex` (int): Índice da roda
  - `force` (float): Força de frenagem
- **Exemplo de comando**:
```json
{"op": "vehicleApplyBraking", "object": "CarChassis", "wheelIndex": 0, "force": 50}
```

---

## 4. Atuadores (2 handlers)

### activate
- **Localização**: Linha 127
- **Descrição**: Ativa um atuador
- **Parâmetros**: `actuator` (string): Nome do atuador
- **Contextual**: Usa `controller_name` do contexto
- **Exemplo de comando**:
```json
{"op": "activate", "object": "Player", "actuator": "Movement"}
```

### deactivate
- **Localização**: Linha 169
- **Descrição**: Desativa um atuador
- **Parâmetros**: `actuator` (string): Nome do atuador
- **Contextual**: Usa `controller_name` do contexto
- **Exemplo de comando**:
```json
{"op": "deactivate", "object": "Player", "actuator": "Movement"}
```

---

## 5. Character Controller (3 handlers)

### characterJump
- **Localização**: Linha 361
- **Descrição**: Faz personagem pular
- **Parâmetros**: Nenhum adicional
- **Exemplo de comando**:
```json
{"op": "characterJump", "object": "Player"}
```

### characterWalkDirection
- **Localização**: Linha 376
- **Descrição**: Define direção de caminhada
- **Parâmetros**: `vec` (array): Direção [x, y, z] ou `value` (fallback)
- **Exemplo de comando**:
```json
{"op": "characterWalkDirection", "object": "Player", "vec": [1, 0, 0]}
```

### characterSetVelocity
- **Localização**: Linha 392
- **Descrição**: Define velocidade do personagem
- **Parâmetros**:
  - `vec` (array): Velocidade [x, y, z] ou `value` (fallback)
  - `time` (float): Tempo de aplicação (default: 0.2)
  - `local` (bool): Velocidade local ou global (default: false)
- **Exemplo de comando**:
```json
{"op": "characterSetVelocity", "object": "Player", "vec": [0, 0, 5], "time": 0.2}
```

---

## 6. Transformação - Movimento (1 handler)

### applyMovement
- **Localização**: Linha 410
- **Descrição**: Aplica movimento relativo ao objeto
- **Parâmetros**: `vec` (array): Movimento [x, y, z] ou `value` (fallback)
- **Exemplo de comando**:
```json
{"op": "applyMovement", "object": "Player", "vec": [0.1, 0, 0]}
```

---

## 7. Transformação - Posição (2 handlers)

### setPosition
- **Localização**: Linha 430
- **Descrição**: Define posição absoluta global
- **Parâmetros**: `value` (array): Posição [x, y, z]
- **Exemplo de comando**:
```json
{"op": "setPosition", "object": "Player", "value": [0, 0, 5]}
```

### setLocalPosition
- **Localização**: Linha 526
- **Descrição**: Define posição local
- **Parâmetros**: `value` (array): Posição local [x, y, z]
- **Exemplo de comando**:
```json
{"op": "setLocalPosition", "object": "Player", "value": [1, 0, 0]}
```

---

## 8. Transformação - Rotação (3 handlers)

### setRotation
- **Localização**: Linha 443
- **Descrição**: Define rotação global em Euler (radianos)
- **Parâmetros**: `value` (array): Rotação [x, y, z] em radianos
- **Exemplo de comando**:
```json
{"op": "setRotation", "object": "Camera", "value": [0, 0, 0]}
```

### setLocalRotation
- **Localização**: Linha 539
- **Descrição**: Define rotação local em Euler (radianos)
- **Parâmetros**: `value` (array): Rotação [x, y, z] em radianos
- **Exemplo de comando**:
```json
{"op": "setLocalRotation", "object": "Camera", "value": [1.57, 0, 0]}
```

### lookAt
- **Localização**: Linha 460
- **Descrição**: Faz objeto apontar para um alvo
- **Parâmetros**: `target` (string): Nome do objeto alvo
- **Exemplo de comando**:
```json
{"op": "lookAt", "object": "Camera", "target": "Player"}
```

---

## 9. Transformação - Escala (1 handler)

### setScale
- **Localização**: Linha 497
- **Descrição**: Define escala do objeto
- **Parâmetros**: `value` (array): Escala [x, y, z]
- **Exemplo de comando**:
```json
{"op": "setScale", "object": "Enemy", "value": [2, 2, 2]}
```

---

## 10. Propriedades (1 handler)

### setProperty
- **Localização**: Linha 513
- **Descrição**: Define propriedade dinâmica do objeto
- **Parâmetros**:
  - `property` (string): Nome da propriedade
  - `value` (any): Valor (int, float, string, bool, list, etc.)
- **Exemplo de comando**:
```json
{"op": "setProperty", "object": "Player", "property": "health", "value": 100}
```

---

## 11. Parenting (1 handler)

### setParent
- **Localização**: Linha 556
- **Descrição**: Define ou remove pai do objeto
- **Parâmetros**: `parent` (string ou null): Nome do objeto pai ou null para remover
- **Exemplo de comando**:
```json
{"op": "setParent", "object": "Child", "parent": "Parent"}
```

---

## 12. Cena (2 handlers)

### sceneAddObject
- **Localização**: Linha 573
- **Descrição**: Adiciona objeto à cena
- **Parâmetros**: `object` (string): Nome do objeto a adicionar
- **Contextual**: Usa `object_name` do contexto como owner
- **Exemplo de comando**:
```json
{"op": "sceneAddObject", "object": "NewObject"}
```

### sceneRemoveObject
- **Localização**: Linha 598
- **Descrição**: Remove objeto da cena
- **Parâmetros**: `object` (string): Nome do objeto a remover
- **Exemplo de comando**:
```json
{"op": "sceneRemoveObject", "object": "OldObject"}
```

---

## 13. Câmera e Viewport (2 handlers)

### setViewport
- **Localização**: Linha 618
- **Descrição**: Define viewport da câmera
- **Parâmetros**:
  - `left` (int): Coordenada esquerda
  - `bottom` (int): Coordenada inferior
  - `right` (int): Coordenada direita
  - `top` (int): Coordenada superior
- **Exemplo de comando**:
```json
{"op": "setViewport", "object": "Camera", "left": 0, "bottom": 0, "right": 800, "top": 600}
```

### setActiveCamera
- **Localização**: Linha 637
- **Descrição**: Define câmera ativa da cena
- **Parâmetros**: `scene` (string, opcional): Cena alvo (usa cena atual se não fornecido)
- **Exemplo de comando**:
```json
{"op": "setActiveCamera", "object": "Camera", "scene": "MainScene"}
```

---

## Sumário Rápido

| Categoria | Handlers | Operações |
|-----------|----------|-----------|
| Globais | 3 | endGame, restartGame, setGravity |
| Raycast | 2 | rayCast, rayCastTo |
| Veículo | 5 | createVehicle, engineForce, steering, addWheel, braking |
| Atuadores | 2 | activate, deactivate |
| Character | 3 | jump, walkDirection, setVelocity |
| Movimento | 1 | applyMovement |
| Posição | 2 | setPosition, setLocalPosition |
| Rotação | 3 | setRotation, setLocalRotation, lookAt |
| Escala | 1 | setScale |
| Propriedades | 1 | setProperty |
| Parenting | 1 | setParent |
| Cena | 2 | sceneAddObject, sceneRemoveObject |
| Câmera | 2 | setViewport, setActiveCamera |
| **TOTAL** | **28** | **28 operações** |

---

## Fluxo de Dispatch

```
Comando entra em _apply_commands(cmd)
        |
        v
op = cmd.get("op")
        |
        v
    [Resolver cena]
        |
        v
    [Operação global?] --- SIM ---> Chamar handler(cmd, context, scene, None, logic)
        |
       NÃO
        |
        v
    [Resolver objeto]
        |
        v
    [Objeto existe?] --- NÃO --> Log e continue
        |
       SIM
        |
        v
    [op em _COMMAND_HANDLERS?] --- SIM --> Chamar handler(cmd, context, scene, obj, logic)
        |
       NÃO --> Ignora operação desconhecida
        |
        v
    [Continua para próximo comando]
```

---

## Notas Importantes

1. **Todos os handlers** seguem o padrão de robustez: erros são capturados e ignorados silenciosamente
2. **Validações** são feitas antes de chamar a lógica (objeto não None, parâmetros válidos)
3. **Fallbacks** existem onde apropriado (ex: `value` como fallback para `vec`)
4. **Context** contém informações globais: `scene_name`, `object_name`, `controller_name`
5. **Logic** é a instância `bge.logic` usada para operações globais
