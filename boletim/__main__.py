"""Gera o boletim a partir das séries do Banco Central.

    python -m boletim              usa o cache em dados/cache/
    python -m boletim --atualizar  busca de novo na API do BC
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import banco, bcb, grafico

PASTA_SAIDA = Path(__file__).resolve().parent.parent / "saida"
IPCA = 433


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # no Windows, a saída redirecionada não sai em UTF-8
    parser = argparse.ArgumentParser(prog="boletim", description="Gera os gráficos do boletim.")
    parser.add_argument(
        "--atualizar",
        action="store_true",
        help="busca as séries na API do BC em vez de usar o cache",
    )
    args = parser.parse_args()

    registros = bcb.buscar_serie(IPCA, atualizar=args.atualizar)
    con = banco.conectar()
    banco.gravar_serie(con, "ipca", registros)

    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = grafico.grafico_ipca(con, PASTA_SAIDA)
    ultimo = registros[-1]
    print(f"IPCA: {len(registros)} meses, o último em {ultimo['data']} ({ultimo['valor']}%).")
    print(f"Gráfico: saida/{caminho.name}")


if __name__ == "__main__":
    main()
