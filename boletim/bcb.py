"""Séries temporais do Banco Central (API do SGS), com cache local.

A API cai e tem limite de requisições, então toda leitura passa pelo cache em
dados/cache/: se o arquivo da série existe, é ele que vale. A API só é chamada
quando o arquivo não existe ou quando se pede atualização.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import requests

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
PASTA_CACHE = Path(__file__).resolve().parent.parent / "dados" / "cache"


def buscar_serie(codigo: int, atualizar: bool = False, dias: int | None = None) -> list[dict]:
    """Devolve a série como a API entrega: [{"data": "dd/mm/aaaa", "valor": "0.16"}, ...].

    `dias` limita a busca aos últimos N dias a partir de hoje — necessário para séries de
    periodicidade diária (como a Selic meta), que a API recusa consultar sem data inicial.
    """
    arquivo = PASTA_CACHE / f"sgs_{codigo}.json"
    if arquivo.exists() and not atualizar:
        return json.loads(arquivo.read_text(encoding="utf-8"))

    url = URL.format(codigo=codigo)
    if dias is not None:
        data_inicial = (date.today() - timedelta(days=dias)).strftime("%d/%m/%Y")
        url += f"&dataInicial={data_inicial}"

    resposta = requests.get(url, timeout=30)
    if resposta.status_code != 200:
        raise RuntimeError(
            f"API do BC respondeu {resposta.status_code} para a série {codigo}: {resposta.text[:400]}"
        )
    dados = resposta.json()

    PASTA_CACHE.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return dados
