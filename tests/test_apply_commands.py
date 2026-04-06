"""
Testes para _apply_commands - aplicação de comandos ao BGE.

Esse teste é crítico porque:
1. Valida cada handler de comando individualmente
2. Garante que objetos e cenas sejam resolvidos corretamente
3. Testa tratamento de erros sem crash
4. Fornece base para refatoração com dispatch pattern
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Adicionar diretório python ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from game_engine import script_handler
from game_engine.script_handler import _apply_commands


@pytest.fixture(autouse=True)
def _patch_script_handler(mock_bge):
    """Injetar mock_bge dentro do script_handler para todos os testes."""
    original_bge = script_handler.bge
    script_handler.bge = mock_bge['bge']
    yield
    script_handler.bge = original_bge


class TestApplyCommandsBasics:
    """Testes básicos de aplicação de comandos."""

    @pytest.mark.unit
    def test_apply_no_bge(self, basic_context):
        """Deve retornar gracefully se BGE não estiver disponível."""
        # Quando bge é None, _apply_commands retorna sem erro
        original_bge = script_handler.bge
        try:
            script_handler.bge = None
            # Não deve lançar exceção
            _apply_commands([{"op": "applyMovement"}], basic_context)
        finally:
            script_handler.bge = original_bge

    @pytest.mark.unit
    def test_apply_no_scene(self, mock_bge, basic_context):
        """Deve retornar gracefully se cena não existir."""
        # Remover todas as cenas
        mock_bge['logic'].scenes = {}
        mock_bge['logic'].current_scene = None

        # Não deve lançar exceção
        _apply_commands([{"op": "applyMovement", "object": "Player", "vec": [0.1, 0, 0]}], basic_context)

    @pytest.mark.unit
    def test_apply_no_object(self, mock_bge, mock_scene, basic_context):
        """Deve ignorar comandos para objetos que não existem."""
        commands = [
            {"op": "applyMovement", "object": "NonExistentObject", "vec": [0.1, 0, 0]}
        ]

        # Não deve lançar exceção
        _apply_commands(commands, basic_context)
        # Objeto enemy não deve ser afetado
        assert mock_scene['enemy'].worldPosition == [0.0, 0.0, 0.0]

    @pytest.mark.unit
    def test_apply_empty_command_list(self, basic_context):
        """Deve lidar com lista vazia de comandos."""
        # Não deve lançar exceção
        _apply_commands([], basic_context)
        _apply_commands(None, basic_context)


class TestApplyCommandsMovement:
    """Testes para comandos de movimento."""

    @pytest.mark.unit
    def test_apply_movement(self, mock_bge, mock_scene, basic_context):
        """Deve aplicar movimento relativo ao objeto."""
        commands = [
            {"op": "applyMovement", "object": "Player", "vec": [0.1, 0.2, 0.3]}
        ]

        player = mock_scene['player']
        initial_pos = player.localPosition.copy()

        _apply_commands(commands, basic_context)

        assert player.localPosition[0] == initial_pos[0] + 0.1
        assert player.localPosition[1] == initial_pos[1] + 0.2
        assert player.localPosition[2] == initial_pos[2] + 0.3

    @pytest.mark.unit
    def test_apply_movement_no_vec(self, mock_bge, mock_scene, basic_context):
        """Deve usar vetor [0,0,0] se 'vec' não for fornecido."""
        commands = [{"op": "applyMovement", "object": "Player"}]

        player = mock_scene['player']
        initial_pos = player.localPosition.copy()

        _apply_commands(commands, basic_context)

        # Deve ser igual, pois aplicou [0,0,0]
        assert player.localPosition == initial_pos

    @pytest.mark.unit
    def test_apply_movement_uses_value_fallback(self, mock_bge, mock_scene, basic_context):
        """Deve usar 'value' como fallback para 'vec'."""
        commands = [
            {"op": "applyMovement", "object": "Player", "value": [0.1, 0.2, 0.3]}
        ]

        player = mock_scene['player']
        initial_pos = player.localPosition.copy()

        _apply_commands(commands, basic_context)

        assert player.localPosition[0] == initial_pos[0] + 0.1

    @pytest.mark.unit
    def test_set_position(self, mock_bge, mock_scene, basic_context):
        """Deve definir posição absoluta do objeto."""
        commands = [
            {"op": "setPosition", "object": "Player", "value": [1.0, 2.0, 3.0]}
        ]

        player = mock_scene['player']
        _apply_commands(commands, basic_context)

        assert player.worldPosition == [1.0, 2.0, 3.0]

    @pytest.mark.unit
    def test_set_local_position(self, mock_bge, mock_scene, basic_context):
        """Deve definir posição local do objeto."""
        commands = [
            {"op": "setLocalPosition", "object": "Player", "value": [1.0, 2.0, 3.0]}
        ]

        player = mock_scene['player']
        _apply_commands(commands, basic_context)

        assert player.localPosition == [1.0, 2.0, 3.0]

    @pytest.mark.unit
    def test_set_scale(self, mock_bge, mock_scene, basic_context):
        """Deve definir escala do objeto."""
        commands = [
            {"op": "setScale", "object": "Enemy", "value": [2.0, 2.0, 2.0]}
        ]

        enemy = mock_scene['enemy']
        _apply_commands(commands, basic_context)

        assert enemy.worldScale == [2.0, 2.0, 2.0]


class TestApplyCommandsRotation:
    """Testes para comandos de rotação."""

    @pytest.mark.unit
    def test_set_rotation(self, mock_bge, mock_scene, basic_context):
        """Deve definir rotação global do objeto."""
        commands = [
            {"op": "setRotation", "object": "Camera", "value": [0.0, 0.0, 0.0]}
        ]

        camera = mock_scene['camera']
        # Não deve lançar exceção
        _apply_commands(commands, basic_context)

    @pytest.mark.unit
    def test_set_local_rotation(self, mock_bge, mock_scene, basic_context):
        """Deve definir rotação local do objeto."""
        commands = [
            {"op": "setLocalRotation", "object": "Camera", "value": [0.0, 0.0, 0.0]}
        ]

        camera = mock_scene['camera']
        # Não deve lançar exceção
        _apply_commands(commands, basic_context)


class TestApplyCommandsProperties:
    """Testes para comandos de propriedades."""

    @pytest.mark.unit
    def test_set_property(self, mock_bge, mock_scene, basic_context):
        """Deve definir propriedade dinâmica do objeto."""
        commands = [
            {"op": "setProperty", "object": "Player", "property": "health", "value": 100}
        ]

        player = mock_scene['player']
        _apply_commands(commands, basic_context)

        assert player["health"] == 100

    @pytest.mark.unit
    def test_set_property_various_types(self, mock_bge, mock_scene, basic_context):
        """Deve definir propriedades de vários tipos."""
        commands = [
            {"op": "setProperty", "object": "Player", "property": "int_val", "value": 42},
            {"op": "setProperty", "object": "Player", "property": "float_val", "value": 3.14},
            {"op": "setProperty", "object": "Player", "property": "str_val", "value": "hello"},
            {"op": "setProperty", "object": "Player", "property": "bool_val", "value": True},
            {"op": "setProperty", "object": "Player", "property": "list_val", "value": [1, 2, 3]},
        ]

        player = mock_scene['player']
        _apply_commands(commands, basic_context)

        assert player["int_val"] == 42
        assert player["float_val"] == 3.14
        assert player["str_val"] == "hello"
        assert player["bool_val"] is True
        assert player["list_val"] == [1, 2, 3]


class TestApplyCommandsActuators:
    """Testes para comandos de atuadores (activate/deactivate)."""

    @pytest.mark.unit
    def test_activate_actuator(self, mock_bge, mock_scene, basic_context):
        """Deve ativar um atuador."""
        commands = [
            {"op": "activate", "object": "Player", "actuator": "MainActuator"}
        ]

        controller = mock_scene['controller']
        assert controller.activated is False

        _apply_commands(commands, basic_context)

        assert controller.activated is True

    @pytest.mark.unit
    def test_deactivate_actuator(self, mock_bge, mock_scene, basic_context):
        """Deve desativar um atuador."""
        controller = mock_scene['controller']
        controller.activated = True

        commands = [
            {"op": "deactivate", "object": "Player", "actuator": "MainActuator"}
        ]

        _apply_commands(commands, basic_context)

        assert controller.activated is False

    @pytest.mark.unit
    def test_activate_nonexistent_actuator(self, mock_bge, mock_scene, basic_context):
        """Deve ignorar se atuador não existir."""
        commands = [
            {"op": "activate", "object": "Player", "actuator": "NonExistent"}
        ]

        # Não deve lançar exceção
        _apply_commands(commands, basic_context)


class TestApplyCommandsParenting:
    """Testes para comandos de parenting."""

    @pytest.mark.unit
    def test_set_parent(self, mock_bge, mock_scene, basic_context):
        """Deve definir pai de um objeto."""
        commands = [
            {"op": "setParent", "object": "Enemy", "parent": "Player"}
        ]

        enemy = mock_scene['enemy']
        player = mock_scene['player']
        assert enemy.parent is None

        _apply_commands(commands, basic_context)

        assert enemy.parent == player

    @pytest.mark.unit
    def test_unset_parent(self, mock_bge, mock_scene, basic_context):
        """Deve remover pai de um objeto."""
        enemy = mock_scene['enemy']
        player = mock_scene['player']
        enemy.parent = player

        commands = [
            {"op": "setParent", "object": "Enemy", "parent": None}
        ]

        _apply_commands(commands, basic_context)

        assert enemy.parent is None


class TestApplyCommandsGlobal:
    """Testes para comandos globais (sem objeto específico)."""

    @pytest.mark.unit
    def test_end_game(self, mock_bge, mock_scene, basic_context):
        """Deve chamar endGame no logic."""
        commands = [{"op": "endGame"}]

        logic = mock_bge['logic']
        assert logic.end_game_called is False

        _apply_commands(commands, basic_context)

        assert logic.end_game_called is True

    @pytest.mark.unit
    def test_restart_game(self, mock_bge, mock_scene, basic_context):
        """Deve chamar restartGame no logic."""
        commands = [{"op": "restartGame"}]

        logic = mock_bge['logic']
        assert logic.restart_game_called is False

        _apply_commands(commands, basic_context)

        assert logic.restart_game_called is True

    @pytest.mark.unit
    def test_set_gravity(self, mock_bge, mock_scene, basic_context):
        """Deve definir gravidade global."""
        commands = [
            {"op": "setGravity", "vec": [0, 0, -20.0]}
        ]

        constraints = mock_bge['constraints']
        _apply_commands(commands, basic_context)

        assert constraints.gravity_value == [0, 0, -20.0]

    @pytest.mark.unit
    def test_set_gravity_with_value_fallback(self, mock_bge, mock_scene, basic_context):
        """Deve usar 'value' como fallback para 'vec' em setGravity."""
        commands = [
            {"op": "setGravity", "value": [0, 0, -15.0]}
        ]

        constraints = mock_bge['constraints']
        _apply_commands(commands, basic_context)

        assert constraints.gravity_value == [0, 0, -15.0]


class TestApplyCommandsRobustness:
    """Testes de robustez e tratamento de erros."""

    @pytest.mark.unit
    def test_apply_commands_with_invalid_float_conversion(self, mock_bge, mock_scene, basic_context):
        """Deve lidar com valores que não podem ser convertidos para float."""
        commands = [
            {"op": "applyMovement", "object": "Player", "vec": ["invalid", "also_invalid", "nope"]}
        ]

        # Não deve lançar exceção, deve lidar gracefully
        try:
            _apply_commands(commands, basic_context)
        except ValueError:
            pytest.fail("_apply_commands deveria lidar com float inválido")

    @pytest.mark.unit
    def test_apply_multiple_commands_in_sequence(self, mock_bge, mock_scene, basic_context):
        """Deve aplicar múltiplos comandos em sequência."""
        commands = [
            {"op": "applyMovement", "object": "Player", "vec": [1.0, 0, 0]},
            {"op": "setProperty", "object": "Player", "property": "moved", "value": True},
            {"op": "applyMovement", "object": "Player", "vec": [0, 1.0, 0]},
        ]

        player = mock_scene['player']
        initial_pos = player.localPosition.copy()

        _apply_commands(commands, basic_context)

        assert player.localPosition[0] == initial_pos[0] + 1.0
        assert player.localPosition[1] == initial_pos[1] + 1.0
        assert player["moved"] is True

    @pytest.mark.unit
    def test_apply_command_with_invalid_op(self, mock_bge, mock_scene, basic_context):
        """Deve ignorar comandos com operação desconhecida."""
        commands = [
            {"op": "unknownOperation", "object": "Player", "value": [1, 2, 3]}
        ]

        # Não deve lançar exceção
        _apply_commands(commands, basic_context)

    @pytest.mark.unit
    def test_apply_command_partial_data(self, mock_bge, mock_scene, basic_context):
        """Deve lidar com comandos com dados parciais."""
        commands = [
            {"op": "setPosition", "object": "Player"},  # Sem 'value'
            {"op": "setPosition", "value": [1, 2, 3]},  # Sem 'object' - usa context
            {"op": "setScale"},  # Sem tudo
        ]

        # Não deve lançar exceção
        _apply_commands(commands, basic_context)
