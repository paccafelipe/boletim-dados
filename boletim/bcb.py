"""Séries temporais do Banco Central (API do SGS), com cache local.

A API cai e tem limite de requisições, então toda leitura passa pelo cache em
dados/cache/: se o arquivo da série existe, é ele que vale. A API só é chamada
quando o arquivo não existe ou quando se pede atualização.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
PASTA_CACHE = Path(__file__).resolve().parent.parent / "dados" / "cache"


def buscar_serie(codigo: int, atualizar: bool = False) -> list[dict]:
    """Devolve a série como a API entrega: [{"data": "dd/mm/aaaa", "valor": "0.16"}, ...]."""
    arquivo = PASTA_CACHE / f"sgs_{codigo}.json"
    if arquivo.exists() and not atualizar:
        return json.loads(arquivo.read_text(encoding="utf-8"))

    resposta = requests.get(URL.format(codigo=codigo), timeout=30)
    if resposta.status_code != 200:
        raise RuntimeError(
            f"API do BC respondeu {resposta.status_code} para a série {codigo}: {resposta.text[:400]}"
        )
    dados = resposta.json()

    PASTA_CACHE.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return dados
