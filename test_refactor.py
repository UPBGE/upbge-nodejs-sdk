#!/usr/bin/env python3
"""
Script para validar o refactor da função _apply_commands.
Roda os testes principais e verifica se o comportamento é idêntico.
"""

import sys
import os
import subprocess

# Adicionar diretório ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def run_tests():
    """Rodar pytest no diretório de testes."""
    print("=" * 80)
    print("Rodando testes de _apply_commands com refactor...")
    print("=" * 80)

    test_file = os.path.join(os.path.dirname(__file__), "tests", "test_apply_commands.py")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
        cwd=os.path.dirname(__file__)
    )

    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()

    print("\n" + "=" * 80)
    if exit_code == 0:
        print("SUCCESS: Todos os testes passaram! O refactor está funcionando corretamente.")
        print("=" * 80)
    else:
        print("FAILURE: Alguns testes falharam. Verifique a saída acima.")
        print("=" * 80)

    sys.exit(exit_code)
