"""
clima.py
--------
Busca o clima da cidade da pessoa na API Open-Meteo (gratuita, sem chave).

Sao duas chamadas:
  1. Geocodificacao -> transforma "Campinas" em latitude e longitude
  2. Previsao       -> pega a temperatura, o codigo do tempo e a chuva

REGRA DE OURO: se qualquer coisa der errado (sem internet, cidade nao
encontrada, API fora do ar), a funcao devolve None e o app simplesmente
esconde a parte do clima. O T.E.R.R.A. nunca quebra por causa da API.
"""

import requests

# Enderecos das duas APIs do Open-Meteo.
URL_GEOCODIFICACAO = "https://geocoding-api.open-meteo.com/v1/search"
URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

# Tempo maximo de espera, em segundos. Sem isso o site poderia travar.
TEMPO_LIMITE = 8

# Quantos milimetros de chuva previstos ja contam como "vai chover".
MINIMO_PARA_CHUVA_MM = 0.5

# Traducao dos codigos de tempo (WMO) que a Open-Meteo devolve.
# Fonte: documentacao oficial da Open-Meteo (weather_code).
CODIGOS_DO_TEMPO = {
    0: "Ceu limpo",
    1: "Quase limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com geada",
    51: "Garoa fraca",
    53: "Garoa",
    55: "Garoa forte",
    61: "Chuva fraca",
    63: "Chuva",
    65: "Chuva forte",
    66: "Chuva congelante",
    67: "Chuva congelante forte",
    71: "Neve fraca",
    73: "Neve",
    75: "Neve forte",
    80: "Pancadas de chuva",
    81: "Pancadas de chuva fortes",
    82: "Pancadas de chuva muito fortes",
    95: "Tempestade",
    96: "Tempestade com granizo",
    99: "Tempestade forte com granizo",
}

# Codigos que significam que esta chovendo agora.
CODIGOS_DE_CHUVA = [51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]


def buscar_coordenadas(cidade):
    """
    Descobre a latitude e a longitude de uma cidade.
    Devolve (latitude, longitude, nome_encontrado) ou None se nao achar.
    """
    parametros = {
        "name": cidade,
        "count": 1,            # queremos so o primeiro resultado
        "language": "pt",
        "format": "json",
    }

    resposta = requests.get(
        URL_GEOCODIFICACAO, params=parametros, timeout=TEMPO_LIMITE
    )
    resposta.raise_for_status()  # se vier erro 404/500, levanta excecao
    dados = resposta.json()

    # Se a cidade nao existe, a API devolve um JSON sem a chave "results".
    resultados = dados.get("results")
    if not resultados:
        return None

    primeiro = resultados[0]
    nome_completo = primeiro.get("name", cidade)
    estado = primeiro.get("admin1")
    if estado:
        nome_completo = nome_completo + " - " + estado

    return primeiro["latitude"], primeiro["longitude"], nome_completo


def buscar_clima(cidade):
    """
    Devolve um dicionario com o clima da cidade, ou None se algo der errado.

    Exemplo do que volta:
      {
        "cidade": "Campinas - Sao Paulo",
        "temperatura": 24.3,
        "descricao": "Chuva fraca",
        "chuva_mm": 3.2,
        "esta_chovendo": True
      }
    """
    try:
        # 1) Transforma o nome da cidade em coordenadas.
        coordenadas = buscar_coordenadas(cidade)
        if coordenadas is None:
            return None
        latitude, longitude, nome_encontrado = coordenadas

        # 2) Pede a previsao para essas coordenadas.
        parametros = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,precipitation",
            "daily": "precipitation_sum",
            "timezone": "auto",
            "forecast_days": 1,
        }
        resposta = requests.get(
            URL_PREVISAO, params=parametros, timeout=TEMPO_LIMITE
        )
        resposta.raise_for_status()
        dados = resposta.json()

        agora = dados.get("current", {})
        hoje = dados.get("daily", {})

        codigo = agora.get("weather_code", 0)
        temperatura = agora.get("temperature_2m")
        chuva_agora = agora.get("precipitation", 0) or 0

        # precipitation_sum vem como lista (um valor por dia).
        lista_chuva = hoje.get("precipitation_sum") or [0]
        chuva_do_dia = lista_chuva[0] or 0

        # 3) Decide se "esta chovendo ou vai chover":
        #    ou o codigo atual e de chuva, ou a previsao do dia tem chuva.
        esta_chovendo = (
            codigo in CODIGOS_DE_CHUVA
            or chuva_agora > 0
            or chuva_do_dia >= MINIMO_PARA_CHUVA_MM
        )

        return {
            "cidade": nome_encontrado,
            "temperatura": temperatura,
            "descricao": CODIGOS_DO_TEMPO.get(codigo, "Tempo indefinido"),
            "chuva_mm": round(chuva_do_dia, 1),
            "esta_chovendo": esta_chovendo,
        }

    except Exception:
        # Qualquer problema (internet, timeout, JSON estranho) cai aqui.
        # Devolvemos None e a tela esconde o bloco do clima.
        return None
