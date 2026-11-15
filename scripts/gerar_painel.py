"""Gera um painel interativo a partir do relatório JSON do CLI da Onfly."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal, DecimalException
from html import escape
from pathlib import Path
from string import Template
from textwrap import wrap

try:
    import plotly.graph_objects as go
    from plotly.offline import get_plotlyjs
except ModuleNotFoundError as err:
    if err.name != "plotly":
        raise
    raise SystemExit("Instale o Plotly com: python -m pip install -r requirements-painel.txt") from None


MONTHS = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
TEAL = "#087d77"
NAVY = "#19374b"
GRID = "#e2eaf0"
FONT = "Inter, Segoe UI, system-ui, sans-serif"
PUNCTUATION = str.maketrans(",.", ".,")
CURRENCY_AXIS = {"tickprefix": "R$ ", "tickformat": ",.0f", "rangemode": "tozero"}


def format_brl(value: str) -> str:
    return f"R$ {Decimal(value):,.2f}".translate(PUNCTUATION)


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_month(value: str, *, short_year: bool = False) -> str:
    date = datetime.strptime(value, "%Y-%m")
    year = date.strftime("%y" if short_year else "%Y")
    return f"{MONTHS[date.month - 1]}/{year}"


def render_chart(
    figure: go.Figure,
    chart_id: str,
    height: int,
    *,
    left: int,
    bottom: int,
    post_script: str | None = None,
) -> str:
    figure.update_layout(
        autosize=True,
        height=height,
        margin={"l": left, "r": 18, "t": 26, "b": bottom},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"family": FONT, "size": 12, "color": NAVY},
        hoverlabel={"bgcolor": "#163748", "font": {"color": "#ffffff"}},
        separators=",.",
    )
    figure.update_xaxes(fixedrange=True, automargin=True, gridcolor=GRID, zeroline=False)
    figure.update_yaxes(fixedrange=True, automargin=True, gridcolor=GRID, zeroline=False)
    return figure.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displayModeBar": False},
        div_id=chart_id,
        default_width="100%",
        post_script=post_script,
    )


def monthly_chart(months: list[dict]) -> str:
    if not months:
        return '<p class="empty">Sem check-ins confirmados para exibir.</p>'

    hover_values = [
        [format_month(row["month"]), format_brl(row["total_brl"]),
         format_count(row["reservations"]), format_count(row["room_nights"])]
        for row in months
    ]
    month_ids = [row["month"] for row in months]
    figure = go.Figure(go.Scatter(
        x=month_ids,
        y=[Decimal(row["total_brl"]) for row in months],
        mode="lines+markers",
        line={"color": TEAL, "width": 3},
        marker={"color": TEAL, "size": 9, "line": {"color": "white", "width": 2}},
        fill="tozeroy",
        fillcolor="rgba(8, 125, 119, 0.10)",
        customdata=hover_values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
            "%{customdata[2]} reservas confirmadas<br>%{customdata[3]} noites de quarto"
            "<extra></extra>"
        ),
    ))
    figure.update_xaxes(
        type="category",
        showgrid=False,
        tickmode="array",
        tickvals=month_ids,
        ticktext=[format_month(month, short_year=True) for month in month_ids],
        ticklabelstandoff=7,
        range=[-0.27, len(month_ids) - 0.73],
    )
    figure.update_yaxes(**CURRENCY_AXIS)
    return render_chart(
        figure,
        "gasto-mensal",
        285,
        left=72,
        bottom=48,
        post_script='connectMonthFilter(document.getElementById("{plot_id}"));',
    )


def ranking_chart(hotels: list[dict]) -> str:
    if not hotels:
        return '<p class="empty">Sem hotéis com reservas confirmadas para exibir.</p>'

    hotel_ids = [escape(hotel["hotel_id"]) for hotel in hotels]
    labels = ["<br>".join(escape(line) for line in wrap(hotel["hotel_name"], width=18)) for hotel in hotels]
    figure = go.Figure(go.Bar(
        x=[Decimal(hotel["total_brl"]) for hotel in hotels],
        y=hotel_ids,
        orientation="h",
        marker_color=[TEAL] + ["#337692"] * (len(hotels) - 1),
        text=[format_brl(hotel["total_brl"]) for hotel in hotels],
        textposition="auto",
        customdata=[
            [escape(hotel["hotel_name"]), format_count(hotel["room_nights"])] for hotel in hotels
        ],
        hovertemplate="<b>%{customdata[0]}</b><br>%{text}<br>%{customdata[1]} noites de quarto<extra></extra>",
    ))
    figure.update_xaxes(**CURRENCY_AXIS)
    figure.update_yaxes(
        type="category",
        tickmode="array",
        tickvals=hotel_ids,
        ticktext=labels,
        autorange="reversed",
        showgrid=False,
    )
    figure.update_layout(bargap=0.42)
    return render_chart(figure, "ranking-hoteis", max(305, 51 * len(hotels) + 58), left=110, bottom=42)


def status_chart(summary: dict) -> str:
    counts = [summary["confirmed_reservations"], summary["cancelled_reservations"], summary["no_show_reservations"]]
    figure = go.Figure(go.Bar(
        x=["Confirmadas", "Canceladas", "Não<br>compareceram"],
        y=counts,
        marker_color=[TEAL, "#a75c2b", "#586b8a"],
        text=[format_count(value) for value in counts],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{text} reservas<extra></extra>",
    ))
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(range=[0, max(1, max(counts)) * 1.2], visible=False)
    figure.update_layout(bargap=0.44)
    return render_chart(figure, "reservas-status", 313, left=15, bottom=48)


def build_panel(report: dict) -> str:
    if report["report_version"] != "1.0":
        raise ValueError("o painel espera um relatório Onfly na versão 1.0")

    summary = report["summary"]
    months = report["by_month"]
    if months:
        first = format_month(months[0]["month"])
        last = format_month(months[-1]["month"])
        period = f"Check-ins confirmados · {first}" if first == last else f"Check-ins confirmados · {first} a {last}"
    else:
        period = "Sem check-ins confirmados"

    generated_at = datetime.fromisoformat(report["generated_at"]).strftime("%d/%m/%Y às %H:%M")
    month_options = "\n".join(
        f'<option value="{escape(row["month"])}">{format_month(row["month"])}</option>'
        for row in months
    )
    template = Template(Path(__file__).with_name("painel.html").read_text(encoding="utf-8"))
    return template.substitute(
        period=escape(period),
        month_filter_hidden="" if months else "hidden",
        month_options=month_options,
        generated_at=generated_at,
        total_reservations=format_count(summary["total_reservations"]),
        confirmed_reservations=format_count(summary["confirmed_reservations"]),
        total_room_nights=format_count(summary["total_room_nights"]),
        total_amount_brl=format_brl(summary["total_amount_brl"]),
        average_nightly_rate_brl=format_brl(summary["average_nightly_rate_brl"]),
        plotly_js=get_plotlyjs(),
        monthly_chart=monthly_chart(months),
        ranking_chart=ranking_chart(report["top_hotels"]),
        status_chart=status_chart(summary),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera um painel HTML interativo a partir do relatório Onfly.")
    parser.add_argument("--input", type=Path, default=Path("output/report.json"), help="relatório JSON do CLI")
    parser.add_argument("--output", type=Path, default=Path("output/painel.html"), help="destino do painel HTML")
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("escolha caminhos diferentes para o relatório e o painel")

    try:
        report = json.loads(args.input.read_text(encoding="utf-8"))
        panel = build_panel(report)
    except (OSError, ValueError, KeyError, TypeError, IndexError, DecimalException) as err:
        parser.error(f"não foi possível usar o relatório {args.input}: {err}")

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(panel, encoding="utf-8")
    except OSError as err:
        parser.error(f"não foi possível gravar {args.output}: {err}")

    print(f"Painel gerado em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
