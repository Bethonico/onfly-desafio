"""Regressão para CSVs inválidos recebidos pelo CLI."""

import os
import subprocess
import sys

import pytest
from helpers import PROJECT_ROOT, SRC_DIR


@pytest.mark.parametrize(
    ("argument", "content", "message"),
    [
        ("--input", b"\xff\n", "falha ao ler"),
        ("--rates", b"\xff\n", "falha ao ler"),
        ("--rates", b"currency,rate_to_brl\nBRL,NaN\n", "taxa deve ser finita para BRL"),
        ("--rates", b"currency,rate_to_brl\nBRL,Infinity\n", "taxa deve ser finita para BRL"),
    ],
    ids=["reservas-utf8", "taxas-utf8", "taxa-nan", "taxa-infinita"],
)
def test_cli_rejects_invalid_csv(tmp_path, argument, content, message):
    invalid_file = tmp_path / "invalid.csv"
    invalid_file.write_bytes(content)
    output = tmp_path / "report.json"
    inputs = {
        "--input": PROJECT_ROOT / "data" / "exemplo-validacao.csv",
        "--rates": PROJECT_ROOT / "data" / "taxas_cambio.csv",
    }
    inputs[argument] = invalid_file

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "onfly_report",
            "--input",
            str(inputs["--input"]),
            "--rates",
            str(inputs["--rates"]),
            "--output",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )

    assert result.returncode == 2, result.stderr
    assert message in result.stderr
    assert not output.exists()
