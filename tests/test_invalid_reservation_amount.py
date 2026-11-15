"""Regressão para valores não finitos no CSV de reservas."""

import csv
import os
import subprocess
import sys

import pytest
from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity"])
def test_cli_rejects_non_finite_reservation_amount(tmp_path, amount):
    reservations = tmp_path / "reservas.csv"
    with reservations.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerow({**BASE, "amount": amount})
    output = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "onfly_report",
            "--input",
            str(reservations),
            "--rates",
            str(PROJECT_ROOT / "data" / "taxas_cambio.csv"),
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
    assert "linha 2" in result.stderr
    assert "amount deve ser um número finito" in result.stderr
    assert not output.exists()
