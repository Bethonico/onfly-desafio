"""Regressão para reserva com moeda ausente na tabela de câmbio."""

import os
import subprocess
import sys

from helpers import PROJECT_ROOT, SRC_DIR


def test_cli_reports_missing_exchange_rate_as_invalid_input(tmp_path):
    rates = tmp_path / "rates.csv"
    rates.write_text("currency,rate_to_brl\nBRL,1.00\n", encoding="utf-8")
    output = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "onfly_report",
            "--input",
            str(PROJECT_ROOT / "data" / "exemplo-validacao.csv"),
            "--rates",
            str(rates),
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
    assert "taxa de câmbio ausente para USD" in result.stderr
    assert not output.exists()
