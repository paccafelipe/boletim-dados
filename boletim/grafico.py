"""Gráficos do boletim."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _mes(d: date) -> str:
    return f"{MESES[d.month - 1]}/{d.year % 100:02d}"


def _num(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",").replace("-", "−")


def _buscar_serie(con: duckdb.DuckDBPyConnection, serie: str) -> tuple[list[date], list[float]]:
    """Um valor por mês: o último registrado no mês (para séries diárias, a meta vigente
    no fechamento do mês; para séries já mensais, como o IPCA, o único valor existente)."""
    linhas = con.execute(
        """
        WITH mensal AS (
            SELECT date_trunc('month', data)::DATE AS mes, arg_max(valor, data) AS valor
            FROM series
            WHERE serie = ?
            GROUP BY mes
        )
        SELECT mes, valor
        FROM mensal
        WHERE mes > (SELECT max(mes) FROM mensal) - INTERVAL 36 MONTH
        ORDER BY mes
        """,
        [serie],
    ).fetchall()
    return [d for d, _ in linhas], [v for _, v in linhas]


def _grafico_barras(
    datas: list[date],
    valores: list[float],
    pasta: Path,
    arquivo: str,
    titulo: str,
    subtitulo: str,
    fonte: str,
) -> Path:
    ultimo = len(valores) - 1

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    cores = ["#9ec5f4"] * ultimo + ["#2a78d6"]
    ax.bar(range(len(valores)), valores, width=0.72, color=cores, zorder=2)
    ax.axhline(0, color="#c3c2b7", linewidth=1, zorder=3)

    deslocamento = 6 if valores[ultimo] >= 0 else -6
    ax.annotate(
        f"{_num(valores[ultimo])}%",
        (ultimo, valores[ultimo]),
        xytext=(0, deslocamento),
        textcoords="offset points",
        ha="center",
        va="bottom" if deslocamento > 0 else "top",
        fontsize=9,
        fontweight="bold",
        color="#0b0b0b",
    )

    marcas = [i for i in range(len(datas)) if (ultimo - i) % 6 == 0]
    ax.set_xticks(marcas, [_mes(datas[i]) for i in marcas])
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{_num(y, 1)}%"))
    ax.tick_params(colors="#898781", labelsize=8, length=0)
    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8, zorder=0)
    for lado in ax.spines.values():
        lado.set_visible(False)

    fig.text(0.06, 0.93, titulo, fontsize=14, fontweight="bold", color="#0b0b0b")
    fig.text(0.06, 0.875, subtitulo, fontsize=9.5, color="#52514e")
    fig.text(0.06, 0.03, fonte, fontsize=7.5, color="#898781")
    fig.subplots_adjust(left=0.07, right=0.97, top=0.82, bottom=0.14)

    caminho = pasta / arquivo
    fig.savefig(caminho, facecolor=fig.get_facecolor(), metadata={"Software": None})
    plt.close(fig)
    return caminho


def grafico_ipca(con: duckdb.DuckDBPyConnection, pasta: Path) -> Path:
    datas, valores = _buscar_serie(con, "ipca")
    ultimo = len(valores) - 1

    acumulado_12m = 1.0
    for v in valores[-12:]:
        acumulado_12m *= 1 + v / 100
    acumulado_12m = (acumulado_12m - 1) * 100

    subtitulo = (
        f"Últimos 36 meses. Em {_mes(datas[ultimo])}: {_num(valores[ultimo])}%. "
        f"Acumulado em 12 meses: {_num(acumulado_12m)}%."
    )
    fonte = "Fonte: Banco Central do Brasil (SGS, série 433). Elaboração: boletim-dados."

    return _grafico_barras(
        datas, valores, pasta, "ipca.png", "IPCA: variação mensal", subtitulo, fonte
    )


def grafico_selic(con: duckdb.DuckDBPyConnection, pasta: Path) -> Path:
    datas, valores = _buscar_serie(con, "selic")
    ultimo = len(valores) - 1

    subtitulo = f"Últimos 36 meses. Em {_mes(datas[ultimo])}: {_num(valores[ultimo])}%."
    fonte = "Fonte: Banco Central do Brasil (SGS, série 432). Elaboração: boletim-dados."

    return _grafico_barras(
        datas,
        valores,
        pasta,
        "selic.png",
        "Selic: meta definida pelo Copom",
        subtitulo,
        fonte,
    )
