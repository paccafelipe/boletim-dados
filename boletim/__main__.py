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
SELIC = 432


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # no Windows, a saída redirecionada não sai em UTF-8
    parser = argparse.ArgumentParser(prog="boletim", description="Gera os gráficos do boletim.")
    parser.add_argument(
        "--atualizar",
        action="store_true",
        help="busca as séries na API do BC em vez de usar o cache",
    )
    args = parser.parse_args()

    con = banco.conectar()
    PASTA_SAIDA.mkdir(exist_ok=True)

    registros_ipca = bcb.buscar_serie(IPCA, atualizar=args.atualizar)
    banco.gravar_serie(con, "ipca", registros_ipca)
    caminho_ipca = grafico.grafico_ipca(con, PASTA_SAIDA)
    ultimo_ipca = registros_ipca[-1]
    print(f"IPCA: {len(registros_ipca)} meses, o último em {ultimo_ipca['data']} ({ultimo_ipca['valor']}%).")
    print(f"Gráfico: saida/{caminho_ipca.name}")

    registros_selic = bcb.buscar_serie(SELIC, atualizar=args.atualizar, dias=365 * 4)
    banco.gravar_serie(con, "selic", registros_selic)
    caminho_selic = grafico.grafico_selic(con, PASTA_SAIDA)
    ultimo_selic = registros_selic[-1]
    print(
        f"Selic: {len(registros_selic)} dias, a última em {ultimo_selic['data']} "
        f"({ultimo_selic['valor']}%)."
    )
    print(f"Gráfico: saida/{caminho_selic.name}")


if __name__ == "__main__":
    main()
