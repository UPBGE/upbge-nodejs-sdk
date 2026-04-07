"""
Testes para _extract_commands - parser de comandos JSON da saída Node.js.

Esse teste é crítico porque:
1. Valida que o parser extrai comandos corretamente de diferentes formatos
2. Garante robustez contra malformações de JSON
3. Testa suporte ao formato de worker (com ID prefixado)
"""

import pytest
import sys
import os

# Adicionar diretório python ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from game_engine.script_handler import _extract_commands


class TestExtractCommands:
    """Suite de testes para _extract_commands."""

    @pytest.mark.unit
    def test_extract_single_command(self, json_output_samples):
        """Deve extrair um único comando da saída."""
        output = json_output_samples["valid_commands"]
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "applyMovement"
        assert commands[0]["object"] == "Player"
        assert commands[0]["vec"] == [0.1, 0, 0]

    @pytest.mark.unit
    def test_extract_multiple_commands(self, json_output_samples):
        """Deve extrair múltiplos comandos de uma única linha."""
        output = json_output_samples["multiple_commands"]
        commands = _extract_commands(output)

        assert len(commands) == 2
        assert commands[0]["op"] == "setPosition"
        assert commands[1]["op"] == "setScale"

    @pytest.mark.unit
    def test_extract_empty_command_list(self, json_output_samples):
        """Deve retornar lista vazia quando não há comandos."""
        output = json_output_samples["no_commands"]
        commands = _extract_commands(output)

        assert isinstance(commands, list)
        assert len(commands) == 0

    @pytest.mark.unit
    def test_extract_with_debug_logs(self, json_output_samples):
        """Deve ignorar logs e extrair comandos mesmo com debug output."""
        output = json_output_samples["with_debug_logs"]
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "applyMovement"

    @pytest.mark.unit
    def test_extract_worker_format(self, json_output_samples):
        """Deve suportar formato de worker com ID prefixado."""
        output = json_output_samples["worker_format"]
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "applyMovement"

    @pytest.mark.unit
    def test_extract_no_marker(self, json_output_samples):
        """Deve retornar lista vazia quando não há marcador de comandos."""
        output = json_output_samples["no_marker"]
        commands = _extract_commands(output)

        assert len(commands) == 0

    @pytest.mark.unit
    def test_extract_invalid_json(self, json_output_samples):
        """Deve retornar lista vazia em caso de JSON inválido."""
        output = json_output_samples["invalid_json"]
        commands = _extract_commands(output)

        assert len(commands) == 0

    @pytest.mark.unit
    def test_extract_empty_output(self):
        """Deve retornar lista vazia para saída vazia."""
        commands = _extract_commands("")
        assert len(commands) == 0

    @pytest.mark.unit
    def test_extract_none_output(self):
        """Deve retornar lista vazia para None."""
        commands = _extract_commands(None)
        assert len(commands) == 0

    @pytest.mark.unit
    def test_extract_multiline_output(self):
        """Deve extrair comandos de saída com múltiplas linhas."""
        output = """
        Starting Node.js process...
        Loading modules...
        console.log("Ready");
        ___BGE_CMDS___[{"op": "applyMovement", "object": "Player", "vec": [1, 0, 0]}]
        Process ended
        """
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "applyMovement"

    @pytest.mark.unit
    def test_extract_complex_command_structure(self):
        """Deve extrair comandos com estrutura complexa."""
        output = '___BGE_CMDS___[{"op": "vehicleAddWheel", "object": "Car", "wheel": "Wheel1", "attachPos": [0.5, 0, 0], "downDir": [0, 0, -1], "axleDir": [0, 1, 0], "suspensionRestLength": 0.5, "wheelRadius": 0.4, "hasSteering": true}]'
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "vehicleAddWheel"
        assert commands[0]["wheel"] == "Wheel1"
        assert commands[0]["hasSteering"] is True

    @pytest.mark.unit
    def test_extract_command_with_null_values(self):
        """Deve extrair comandos com valores null."""
        output = '___BGE_CMDS___[{"op": "setProperty", "object": "Player", "property": "data", "value": null}]'
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["value"] is None

    @pytest.mark.unit
    def test_extract_preserves_data_types(self):
        """Deve preservar tipos de dados (int, float, bool, str, list)."""
        output = '___BGE_CMDS___[{"op": "test", "int": 42, "float": 3.14, "bool": true, "str": "hello", "list": [1, 2, 3], "null": null}]'
        commands = _extract_commands(output)

        assert commands[0]["int"] == 42
        assert commands[0]["float"] == 3.14
        assert commands[0]["bool"] is True
        assert commands[0]["str"] == "hello"
        assert commands[0]["list"] == [1, 2, 3]
        assert commands[0]["null"] is None

    @pytest.mark.unit
    def test_extract_first_occurrence_only(self):
        """Deve extrair apenas a primeira ocorrência do marcador."""
        output = """
        ___BGE_CMDS___[{"op": "first"}]
        ___BGE_CMDS___[{"op": "second"}]
        """
        commands = _extract_commands(output)

        assert len(commands) == 1
        assert commands[0]["op"] == "first"
