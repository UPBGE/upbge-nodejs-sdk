"""
Configurações e fixtures compartilhadas para testes.

Este arquivo define:
- Mocks do BGE para testes unitários (sem Blender/UPBGE real)
- Fixtures para objetos, cenas, controllers, etc.
- Utilitários para setup de testes
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
import json


# ============================================================================
# MOCKS DO BGE (quando BGE não está disponível)
# ============================================================================

class MockPhysicsObject:
    """Mock de um objeto com métodos BGE."""

    def __init__(self, name="TestObject"):
        self.name = name
        self.worldPosition = [0.0, 0.0, 0.0]
        self.localPosition = [0.0, 0.0, 0.0]
        self.worldOrientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Matriz 3x3
        self.localOrientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.worldScale = [1.0, 1.0, 1.0]
        self.localScale = [1.0, 1.0, 1.0]
        self.controllers = {}
        self.properties = {}
        self.parent = None
        self._physics_id = 1

    def __getitem__(self, key):
        """Acesso a propriedades dinâmicas como dict."""
        if key not in self.properties:
            raise KeyError(f"Property {key} not found")
        return self.properties[key]

    def __setitem__(self, key, value):
        """Definir propriedades dinâmicas."""
        self.properties[key] = value

    def applyMovement(self, vec, local=True):
        """Aplicar movimento local ou global."""
        if local:
            self.localPosition[0] += vec[0]
            self.localPosition[1] += vec[1]
            self.localPosition[2] += vec[2]
        else:
            self.worldPosition[0] += vec[0]
            self.worldPosition[1] += vec[1]
            self.worldPosition[2] += vec[2]

    def rayCast(self, to_point, from_point=None, dist=0, prop="", face=0, xray=0, poly=0, mask=0xFFFF):
        """Raycast simples - retorna None por padrão."""
        return None

    def rayCastTo(self, target, dist=0, prop=""):
        """RayCast para um alvo específico."""
        return None

    def setParent(self, parent):
        """Definir objeto pai."""
        self.parent = parent

    def getPhysicsId(self):
        """Retornar ID de física."""
        return self._physics_id

    def alignAxisToVect(self, direction, axis, factor):
        """Alinhar eixo a um vetor."""
        pass


class MockController:
    """Mock de um controller BGE."""

    def __init__(self, name="Controller"):
        self.name = name
        self.actuators = {}
        self.activated = False

    def activate(self, actuator):
        """Ativar um atuador."""
        self.activated = True
        if hasattr(actuator, '_activated'):
            actuator._activated = True

    def deactivate(self, actuator):
        """Desativar um atuador."""
        self.activated = False
        if hasattr(actuator, '_activated'):
            actuator._activated = False


class MockActuator:
    """Mock de um atuador BGE."""

    def __init__(self, name="Actuator"):
        self.name = name
        self._activated = False


class MockScene:
    """Mock de uma cena BGE."""

    def __init__(self, name="Scene"):
        self.name = name
        self.objects = {}
        self.active_camera = None

    def get(self, key):
        """Retornar objeto por nome."""
        return self.objects.get(key)

    def __getitem__(self, key):
        """Acesso tipo dict."""
        return self.objects[key]

    def addObject(self, obj, owner=None, time=0):
        """Adicionar objeto à cena."""
        if obj and hasattr(obj, 'name'):
            self.objects[obj.name] = obj

    def unlink(self, obj):
        """Remove um objeto da cena."""
        if obj and hasattr(obj, 'name'):
            self.objects.pop(obj.name, None)


class MockBGELogic:
    """Mock do módulo bge.logic."""

    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.end_game_called = False
        self.restart_game_called = False
        self.gravity = [0, 0, -9.81]
        self._call_history = []

    def getSceneList(self):
        """Retornar lista de cenas."""
        return list(self.scenes.values())

    def getCurrentScene(self):
        """Retornar cena atual."""
        return self.current_scene

    def endGame(self):
        """Terminar o jogo."""
        self.end_game_called = True
        self._call_history.append(('endGame',))

    def restartGame(self):
        """Reiniciar o jogo."""
        self.restart_game_called = True
        self._call_history.append(('restartGame',))


class MockBGEConstraints:
    """Mock do módulo bge.constraints."""

    def __init__(self):
        self.vehicles = {}
        self.gravity_value = [0, 0, -9.81]
        self._call_history = []

    def createVehicle(self, physics_id):
        """Criar constraint de veículo."""
        vehicle = Mock()
        vehicle.applyEngineForce = Mock()
        vehicle.setSteeringValue = Mock()
        vehicle.applyBraking = Mock()
        vehicle.addWheel = Mock()
        self.vehicles[physics_id] = vehicle
        return vehicle

    def setGravity(self, x, y, z):
        """Definir gravidade global."""
        self.gravity_value = [float(x), float(y), float(z)]
        self._call_history.append(('setGravity', x, y, z))

    def getCharacter(self, obj):
        """Retornar character controller para objeto."""
        return None


# ============================================================================
# FIXTURES PRINCIPAIS
# ============================================================================

@pytest.fixture
def mock_bge():
    """Fixture que fornece um mock completo do BGE."""
    logic = MockBGELogic()
    constraints = MockBGEConstraints()

    bge_mock = Mock()
    bge_mock.logic = logic
    bge_mock.constraints = constraints

    return {
        'bge': bge_mock,
        'logic': logic,
        'constraints': constraints,
    }


@pytest.fixture
def mock_scene(mock_bge):
    """Fixture que fornece uma cena mock com objetos."""
    scene = MockScene("TestScene")

    # Adicionar alguns objetos padrão
    player = MockPhysicsObject("Player")
    enemy = MockPhysicsObject("Enemy")
    camera = MockPhysicsObject("Camera")

    scene.objects["Player"] = player
    scene.objects["Enemy"] = enemy
    scene.objects["Camera"] = camera

    # Adicionar controller e actuator ao Player
    controller = MockController("MainController")
    actuator = MockActuator("MainActuator")
    controller.actuators["MainActuator"] = actuator
    player.controllers["MainController"] = controller

    # Registrar a cena no BGE mock
    mock_bge['logic'].scenes[scene.name] = scene
    mock_bge['logic'].current_scene = scene

    return {
        'scene': scene,
        'player': player,
        'enemy': enemy,
        'camera': camera,
        'controller': controller,
        'actuator': actuator,
    }


@pytest.fixture
def basic_context():
    """Fixture com contexto básico para testes."""
    return {
        "scene_name": "TestScene",
        "object_name": "Player",
        "controller_name": "MainController",
    }


@pytest.fixture
def commands_samples():
    """Fixture com exemplos de comandos para testes."""
    return {
        "apply_movement": {
            "op": "applyMovement",
            "object": "Player",
            "vec": [0.1, 0.0, 0.0],
        },
        "set_position": {
            "op": "setPosition",
            "object": "Player",
            "value": [1.0, 2.0, 3.0],
        },
        "set_rotation": {
            "op": "setRotation",
            "object": "Camera",
            "value": [0.0, 0.0, 0.0],
        },
        "set_scale": {
            "op": "setScale",
            "object": "Enemy",
            "value": [2.0, 2.0, 2.0],
        },
        "set_property": {
            "op": "setProperty",
            "object": "Player",
            "property": "health",
            "value": 100,
        },
        "activate": {
            "op": "activate",
            "object": "Player",
            "actuator": "MainActuator",
        },
        "deactivate": {
            "op": "deactivate",
            "object": "Player",
            "actuator": "MainActuator",
        },
        "end_game": {
            "op": "endGame",
        },
        "restart_game": {
            "op": "restartGame",
        },
        "set_gravity": {
            "op": "setGravity",
            "vec": [0, 0, -20.0],
        },
    }


@pytest.fixture
def json_output_samples():
    """Fixture com exemplos de saída Node.js."""
    return {
        "valid_commands": '___BGE_CMDS___[{"op": "applyMovement", "object": "Player", "vec": [0.1, 0, 0]}]',
        "multiple_commands": '___BGE_CMDS___[{"op": "setPosition", "object": "Player", "value": [1, 2, 3]}, {"op": "setScale", "object": "Enemy", "value": [2, 2, 2]}]',
        "no_commands": '___BGE_CMDS___[]',
        "with_debug_logs": 'console.log("Debug: starting");\n___BGE_CMDS___[{"op": "applyMovement", "object": "Player", "vec": [0, 0, 0.1]}]',
        "worker_format": '___BGE_CMDS___1\t[{"op": "applyMovement", "object": "Player", "vec": [0, 0, 0.1]}]',
        "no_marker": 'Some output without commands',
        "invalid_json": '___BGE_CMDS___this is not json',
    }


# ============================================================================
# SETUP DE MOCKS (executado antes de qualquer importação)
# ============================================================================

# Criar mocks de bpy e bge ANTES de importar qualquer código que dependa deles
def _create_bpy_mock():
    """Criar mock completo de bpy com todos os submodelos."""
    _bpy = MagicMock()
    _bpy.app = MagicMock()
    _bpy.app.handlers = MagicMock()
    _bpy.app.handlers.frame_change_pre = []
    _bpy.app.handlers.persistent = lambda x: x

    _bpy.props = MagicMock()
    _bpy.context = MagicMock()
    _bpy.context.preferences = MagicMock()
    _bpy.context.preferences.addons = MagicMock()
    _bpy.context.preferences.addons.get = MagicMock(return_value=None)

    return _bpy

def _create_bge_mock():
    """Criar mock completo de bge com todos os submodelos."""
    _bge = MagicMock()
    _bge.logic = MagicMock()
    _bge.constraints = MagicMock()
    return _bge

# Registrar mocks antes de qualquer importação
if 'bpy' not in sys.modules:
    _bpy_mock = _create_bpy_mock()
    _bpy_mock.types = MagicMock()
    _bpy_mock.types.Operator = MagicMock()
    _bpy_mock.types.AddonPreferences = MagicMock()

    sys.modules['bpy'] = _bpy_mock
    sys.modules['bpy.app'] = _bpy_mock.app
    sys.modules['bpy.app.handlers'] = _bpy_mock.app.handlers
    sys.modules['bpy.props'] = _bpy_mock.props
    sys.modules['bpy.types'] = _bpy_mock.types
    sys.modules['bpy.context'] = _bpy_mock.context

if 'bge' not in sys.modules:
    _bge_mock = _create_bge_mock()
    sys.modules['bge'] = _bge_mock
    sys.modules['bge.logic'] = _bge_mock.logic
    sys.modules['bge.constraints'] = _bge_mock.constraints

if 'mathutils' not in sys.modules:
    sys.modules['mathutils'] = MagicMock()

# ============================================================================
# AUTOUSE FIXTURES (aplicadas automaticamente)
# ============================================================================

@pytest.fixture(autouse=True)
def patch_bge():
    """Patch do módulo bge para não depender do Blender."""
    # Já foi feito no setup, apenas restaurar estado limpo entre testes
    yield


@pytest.fixture(autouse=True)
def patch_bpy():
    """Patch do módulo bpy para não depender do Blender."""
    # Já foi feito no setup, apenas garantir que está limpo
    yield
