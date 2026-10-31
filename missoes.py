"""
missoes.py
----------
Escolhe quais missoes combinam com a rotina da pessoa.

A escolha funciona em duas camadas:
  1. REGRAS com if/else (sempre funcionam, nao dependem de internet)
  2. IA opcional (ia.py), que apenas REORDENA e EXPLICA as missoes
     que as regras ja aprovaram.

Se a IA nao estiver configurada ou der qualquer erro, o app continua
funcionando normalmente com as regras. A IA nunca inventa missao nova.
"""

import json
import os
import random
from datetime import datetime

import calculos
import ia

# Caminho do catalogo. Usamos a pasta deste arquivo para funcionar
# mesmo se o app for iniciado de outro lugar no computador.
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CATALOGO = os.path.join(PASTA_ATUAL, "missoes.json")

# Horarios usados nos lembretes (datetime).
HORA_FIM_DA_MANHA = 12
HORA_FIM_DA_TARDE = 18


def carregar_catalogo():
    """Le o missoes.json e devolve o dicionario completo (missoes + dicas)."""
    with open(CAMINHO_CATALOGO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def listar_missoes():
    """Devolve a lista com todas as missoes do catalogo."""
    return carregar_catalogo()["missoes"]


def listar_dicas():
    """Devolve a lista de dicas de educacao ambiental."""
    return carregar_catalogo()["dicas"]


def _hora_para_numero(texto_hora):
    """
    Transforma o texto "07:30" no numero 7 (so a hora).
    Se o texto vier estranho, devolve None em vez de quebrar o app.
    """
    try:
        return int(texto_hora.split(":")[0])
    except (ValueError, AttributeError, IndexError):
        return None


def condicao_atendida(condicao, rotina, esta_chovendo=False):
    """
    O CORACAO DAS REGRAS.
    Recebe o nome de uma condicao e devolve True se ela combina com a rotina.
    Cada if abaixo e uma regra do T.E.R.R.A.
    """
    hora_acorda = _hora_para_numero(rotina["hora_acorda"])
    hora_dorme = _hora_para_numero(rotina["hora_dorme"])

    # --- Missoes que aparecem para todo mundo ---
    if condicao == "sempre":
        return True

    # --- Regras sobre o banho ---
    if condicao == "banho_muito_longo":
        return rotina["minutos_banho"] >= 15
    if condicao == "banho_longo":
        return rotina["minutos_banho"] > 8
    if condicao == "muitos_banhos":
        return rotina["banhos_dia"] > 1

    # --- Regras sobre torneira e descarga ---
    if condicao == "torneira_escovar":
        return rotina["torneira_escovar"] == 1
    if condicao == "torneira_louca":
        return rotina["torneira_louca"] == 1
    if condicao == "muitas_descargas":
        return rotina["descargas_dia"] > 5

    # --- Regras sobre o lixo ---
    if condicao == "nao_separa_lixo":
        return rotina["separa_lixo"] == 0
    if condicao == "separa_lixo":
        return rotina["separa_lixo"] == 1
    if condicao == "descarte_errado":
        return rotina["descarte_especial"] == "lixo_comum"

    # --- Regras sobre horario (datetime) ---
    if condicao == "acorda_cedo":
        return hora_acorda is not None and hora_acorda <= 7
    if condicao == "dorme_tarde":
        return hora_dorme is not None and (hora_dorme >= 23 or hora_dorme <= 3)

    # --- Regra que depende do clima (clima.py) ---
    if condicao == "chuva":
        return esta_chovendo

    # Condicao desconhecida: por seguranca, nao mostra a missao.
    return False


def escolher_missoes(rotina, esta_chovendo=False, usar_ia=True):
    """
    Escolhe as missoes personalizadas para a rotina da pessoa.

    Devolve uma tupla: (lista_de_missoes, origem)
      origem = "ia"     -> a IA ajudou a ordenar e explicar
      origem = "regras" -> apenas as regras if/else foram usadas
    """
    # 1) As regras filtram o catalogo inteiro.
    aprovadas = []
    for missao in listar_missoes():
        if condicao_atendida(missao["condicao"], rotina, esta_chovendo):
            aprovadas.append(missao)

    # 2) Calcula quanto cada missao economiza para esta pessoa.
    aprovadas = calculos.resumir_economia(aprovadas, rotina)

    # 3) Ordena: quem economiza mais agua aparece primeiro.
    #    Em caso de empate (missoes de descarte), vale o maior XP.
    aprovadas.sort(key=lambda m: (m["economia_dia"], m["xp"]), reverse=True)

    # 4) Tenta melhorar a lista com a IA (totalmente opcional).
    origem = "regras"
    if usar_ia:
        sugestao = ia.priorizar_missoes(rotina, aprovadas)
        if sugestao:
            aprovadas = sugestao
            origem = "ia"

    return aprovadas, origem


def sortear_missao_do_dia(missoes):
    """
    Sorteia uma missao do dia usando random.
    Usamos a data de hoje como "semente" do sorteio: assim a missao do dia
    e sempre a mesma se a pessoa recarregar a pagina, mas muda amanha.
    """
    if not missoes:
        return None

    sorteador = random.Random(datetime.now().strftime("%Y-%m-%d"))
    return sorteador.choice(missoes)


def sortear_dica():
    """Sorteia uma dica de educacao ambiental para mostrar na tela."""
    dicas = listar_dicas()
    if not dicas:
        return None
    return random.choice(dicas)


def lembrete_do_momento(rotina, agora=None):
    """
    Monta o lembrete de acordo com o horario atual (datetime) e com a
    rotina da pessoa. De manha o foco e o banho, de noite e o lixo.
    """
    if agora is None:
        agora = datetime.now()

    hora = agora.hour
    nome = rotina["nome"].split()[0]  # usa so o primeiro nome

    if hora < HORA_FIM_DA_MANHA:
        periodo = "Bom dia"
        if rotina["minutos_banho"] > 8:
            texto = (
                "Antes do banho: tente cortar alguns minutos hoje. "
                "Cada minuto a menos economiza cerca de 9 litros."
            )
        else:
            texto = (
                "Seu banho já é rápido. Hoje tente fechar o chuveiro "
                "enquanto se ensaboa."
            )
    elif hora < HORA_FIM_DA_TARDE:
        periodo = "Boa tarde"
        if rotina["torneira_louca"] == 1:
            texto = (
                "Hora do almoço: ensaboe a louça com a torneira fechada "
                "e enxágue tudo de uma vez."
            )
        else:
            texto = (
                "Aproveite a tarde para conferir se tem alguma torneira "
                "pingando em casa."
            )
    else:
        periodo = "Boa noite"
        if rotina["separa_lixo"] == 0:
            texto = (
                "Antes de dormir: separe os recicláveis do lixo orgânico. "
                "Duas sacolas resolvem."
            )
        else:
            texto = (
                "Antes de dormir: confira se o lixo reciclável está separado "
                "para a coleta."
            )

    return {
        "titulo": periodo + ", " + nome + "!",
        "texto": texto,
    }
