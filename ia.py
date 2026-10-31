"""
ia.py
-----
Integracao OPCIONAL com a API do Claude (Anthropic).

O que a IA faz aqui: recebe a rotina da pessoa e a lista de missoes que as
REGRAS do missoes.py ja aprovaram, e devolve a mesma lista reordenada, com
uma frase explicando por que cada missao faz sentido para aquela pessoa.

O que a IA NAO faz: inventar missao nova. Toda missao que aparece na tela
saiu do missoes.json. Isso deixa o app previsivel e seguro.

Se o arquivo .env nao existir, se nao tiver chave, ou se a API falhar,
todas as funcoes devolvem None e o app usa so as regras.
"""

import json
import os

import requests

PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ENV = os.path.join(PASTA_ATUAL, ".env")

# Endereco e configuracao da API do Claude.
URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2023-06-01"
MODELO = "claude-sonnet-5"
MAXIMO_DE_TOKENS = 1000
TEMPO_LIMITE = 20  # segundos


def ler_env():
    """
    Le o arquivo .env e devolve um dicionario com as variaveis.

    O formato do .env e simples: uma linha "CHAVE=valor" por vez.
    Linhas vazias e linhas que comecam com # sao ignoradas.
    (Fazemos na mao para nao precisar instalar nenhuma biblioteca extra.)
    """
    variaveis = {}

    if not os.path.exists(CAMINHO_ENV):
        return variaveis

    try:
        with open(CAMINHO_ENV, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, valor = linha.split("=", 1)
                # Tira espacos e aspas que a pessoa pode ter deixado.
                variaveis[chave.strip()] = valor.strip().strip('"').strip("'")
    except OSError:
        return {}

    return variaveis


def obter_chave():
    """
    Devolve a chave da API do Claude, ou None se nao existir.
    Procura primeiro no .env e depois nas variaveis de ambiente do sistema.
    """
    chave = ler_env().get("ANTHROPIC_API_KEY")
    if not chave:
        chave = os.environ.get("ANTHROPIC_API_KEY")

    # Uma chave vazia ou ainda com o texto de exemplo nao serve.
    if not chave or chave.startswith("cole-sua-chave"):
        return None
    return chave


def ia_disponivel():
    """Diz se a IA esta configurada (serve para mostrar um aviso na tela)."""
    return obter_chave() is not None


def _montar_pergunta(rotina, missoes):
    """Monta o texto que sera enviado para o Claude."""
    # Resumo da rotina em portugues simples.
    resumo_rotina = (
        "Nome: " + rotina["nome"] + "\n"
        "Cidade: " + rotina["cidade"] + "\n"
        "Banho: " + str(rotina["minutos_banho"]) + " minutos, "
        + str(rotina["banhos_dia"]) + " vez(es) por dia\n"
        "Descargas por dia: " + str(rotina["descargas_dia"]) + "\n"
        "Escova os dentes com a torneira aberta: "
        + ("sim" if rotina["torneira_escovar"] else "nao") + "\n"
        "Lava louca com a torneira aberta: "
        + ("sim" if rotina["torneira_louca"] else "nao") + "\n"
        "Separa o lixo: " + ("sim" if rotina["separa_lixo"] else "nao") + "\n"
        "Descarte de pilhas/oleo/eletronicos: " + rotina["descarte_especial"] + "\n"
        "Acorda as " + rotina["hora_acorda"] + " e dorme as " + rotina["hora_dorme"]
    )

    # Lista enxuta das missoes (so o que a IA precisa saber).
    lista = []
    for missao in missoes:
        lista.append({
            "id": missao["id"],
            "titulo": missao["titulo"],
            "categoria": missao["categoria"],
            "economia_litros_dia": missao.get("economia_dia", 0),
        })

    return (
        "Voce ajuda um aplicativo de sustentabilidade chamado T.E.R.R.A.\n\n"
        "ROTINA DA PESSOA:\n" + resumo_rotina + "\n\n"
        "MISSOES DISPONIVEIS (escolha apenas entre estas):\n"
        + json.dumps(lista, ensure_ascii=False, indent=2) + "\n\n"
        "TAREFA: escolha as 6 missoes mais uteis para esta pessoa, da mais "
        "importante para a menos importante. Para cada uma, escreva um motivo "
        "curto (no maximo 20 palavras), em portugues do Brasil, falando "
        "diretamente com a pessoa e citando um numero da rotina dela.\n\n"
        "Responda SOMENTE com um array JSON, sem texto antes ou depois, "
        'no formato: [{"id": "...", "motivo": "..."}]'
    )


def _extrair_json(texto):
    """
    Pega o array JSON de dentro da resposta da IA.
    Se a IA escrever algo antes ou depois, cortamos do primeiro [ ao ultimo ].
    """
    inicio = texto.find("[")
    fim = texto.rfind("]")
    if inicio == -1 or fim == -1:
        return None
    return json.loads(texto[inicio:fim + 1])


def priorizar_missoes(rotina, missoes):
    """
    Pede para a IA reordenar e explicar as missoes.

    Devolve a lista de missoes reordenada (cada uma com um campo "motivo"),
    ou None se a IA nao estiver disponivel ou der qualquer erro.
    """
    chave = obter_chave()
    if not chave or not missoes:
        return None

    try:
        resposta = requests.post(
            URL_API,
            headers={
                "x-api-key": chave,
                "anthropic-version": VERSAO_API,
                "content-type": "application/json",
            },
            json={
                "model": MODELO,
                "max_tokens": MAXIMO_DE_TOKENS,
                "messages": [
                    {"role": "user", "content": _montar_pergunta(rotina, missoes)}
                ],
            },
            timeout=TEMPO_LIMITE,
        )
        resposta.raise_for_status()

        # A resposta vem assim: {"content": [{"type": "text", "text": "..."}]}
        texto = resposta.json()["content"][0]["text"]
        escolhidas = _extrair_json(texto)
        if not escolhidas:
            return None

        # Monta um indice para achar cada missao pelo id rapidamente.
        por_id = {missao["id"]: missao for missao in missoes}

        resultado = []
        for item in escolhidas:
            missao = por_id.get(item.get("id"))
            # Ignora qualquer id que a IA tenha inventado.
            if missao is None:
                continue
            copia = dict(missao)
            copia["motivo"] = item.get("motivo", "")
            resultado.append(copia)

        # Se a IA nao acertou nenhum id, melhor usar as regras.
        if not resultado:
            return None

        return resultado

    except Exception:
        # Sem internet, chave errada, JSON estranho... tudo cai aqui.
        # Devolver None faz o missoes.py usar as regras automaticamente.
        return None
