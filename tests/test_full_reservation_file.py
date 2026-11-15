"""Regressão para a leitura de todas as reservas do CSV."""

from helpers import run_cli


def test_cli_processes_more_than_200_reservations(tmp_path):
    rows = [{"reservation_id": f"R-{number}"} for number in range(1, 202)]

    summary = run_cli(tmp_path, rows)["summary"]

    assert summary["total_reservations"] == 201
    assert summary["confirmed_reservations"] == 201
    assert summary["total_room_nights"] == 201
    assert summary["total_amount_brl"] == "20100.00"
