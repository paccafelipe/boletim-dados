"""Banco local do boletim (DuckDB): uma tabela só, com todas as séries."""

from __future__ import annotations

from pathlib import Path

import duckdb

ARQUIVO = Path(__file__).resolve().parent.parent / "boletim.duckdb"


def conectar() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(ARQUIVO))
    con.execute("CREATE TABLE IF NOT EXISTS series (serie VARCHAR, data DATE, valor DOUBLE)")
    return con


def gravar_serie(con: duckdb.DuckDBPyConnection, serie: str, registros: list[dict]) -> int:
    """Troca os dados da série pelos registros que vieram da API."""
    con.execute("DELETE FROM series WHERE serie = ?", [serie])
    con.executemany(
        "INSERT INTO series VALUES (?, strptime(?, '%d/%m/%Y')::DATE, CAST(? AS DOUBLE))",
        [(serie, r["data"], r["valor"]) for r in registros],
    )
    return len(registros)
