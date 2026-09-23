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


def grafico_ipca(con: duckdb.DuckDBPyConnection, pasta: Path) -> Path:
    linhas = con.execute(
        """
        SELECT data, valor
        FROM series
        WHERE serie = 'ipca'
          AND data > (SELECT max(data) FROM series WHERE serie = 'ipca') - INTERVAL 36 MONTH
        ORDER BY data
        """
    ).fetchall()
    datas = [d for d, _ in linhas]
    valores = [v for _, v in linhas]
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

    fig.text(0.06, 0.93, "IPCA: variação mensal", fontsize=14, fontweight="bold", color="#0b0b0b")
    fig.text(
        0.06,
        0.875,
        f"Últimos 36 meses. Em {_mes(datas[ultimo])}: {_num(valores[ultimo])}%.",
        fontsize=9.5,
        color="#52514e",
    )
    fig.text(
        0.06,
        0.03,
        "Fonte: Banco Central do Brasil (SGS, série 433). Elaboração: boletim-dados.",
        fontsize=7.5,
        color="#898781",
    )
    fig.subplots_adjust(left=0.07, right=0.97, top=0.82, bottom=0.14)

    caminho = pasta / "ipca.png"
    fig.savefig(caminho, facecolor=fig.get_facecolor(), metadata={"Software": None})
    plt.close(fig)
    return caminho
