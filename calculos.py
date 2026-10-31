"""
calculos.py
-----------
Todas as contas do T.E.R.R.A. ficam aqui: consumo de agua, economia
das missoes e o sistema de niveis.

Este arquivo NAO sabe o que e Flask, nem HTML, nem banco de dados.
Ele so recebe numeros e devolve numeros - por isso e facil de testar.
"""

# =====================================================================
# CONSTANTES DE REFERENCIA
# Todos os valores usados nas contas estao aqui, com a fonte no comentario.
# Se um dado mudar, basta trocar neste bloco.
# =====================================================================

# Chuveiro eletrico comum gasta cerca de 9 litros por minuto.
# Fonte: SABESP / ANA (Agencia Nacional de Aguas) - guia de uso consciente.
VAZAO_CHUVEIRO_L_MIN = 9.0

# Descarga de caixa acoplada antiga: ~10 litros por acionamento.
# (As novas, com duplo acionamento, usam de 3 a 6 litros.)
# Fonte: ANA - Manual de Conservacao de Agua em Edificacoes.
LITROS_POR_DESCARGA = 10.0

# Torneira de pia aberta: cerca de 6 litros por minuto.
# Fonte: SABESP - tabela de consumo domestico.
VAZAO_TORNEIRA_L_MIN = 6.0

# Escovar os dentes: 3 vezes ao dia, 2 minutos cada vez.
# Fonte: recomendacao de escovacao da Sociedade Brasileira de Odontologia.
ESCOVACOES_POR_DIA = 3
MINUTOS_POR_ESCOVACAO = 2.0

# Lavar louca com a torneira aberta do inicio ao fim: ~15 minutos por dia.
# Fonte: estimativa da SABESP para uma familia pequena.
MINUTOS_LAVANDO_LOUCA = 15.0

# Consumo de agua recomendado pela ONU: 110 litros por pessoa por dia
# para suprir todas as necessidades (beber, higiene, cozinhar, limpar).
# Fonte: ONU / Programa das Nacoes Unidas para o Meio Ambiente.
CONSUMO_RECOMENDADO_ONU = 110.0

# Medias usadas para transformar o consumo diario em mensal e anual.
DIAS_NO_MES = 30
DIAS_NO_ANO = 365

# Niveis do jogo: (xp_necessario, nome_do_nivel).
# A lista precisa ficar em ordem crescente de XP.
NIVEIS = [
    (0, "Semente"),
    (50, "Broto"),
    (120, "Muda"),
    (250, "Arvore"),
    (500, "Floresta"),
]


# =====================================================================
# CONSUMO DE AGUA
# =====================================================================

def litros_banho(minutos_banho, banhos_dia):
    """Litros gastos por dia tomando banho."""
    return minutos_banho * banhos_dia * VAZAO_CHUVEIRO_L_MIN


def litros_descargas(descargas_dia):
    """Litros gastos por dia com a descarga do vaso sanitario."""
    return descargas_dia * LITROS_POR_DESCARGA


def litros_escovacao(torneira_aberta):
    """
    Litros gastos por dia escovando os dentes.
    Com a torneira fechada, consideramos apenas um copo de agua (0,5 L).
    """
    if torneira_aberta:
        return ESCOVACOES_POR_DIA * MINUTOS_POR_ESCOVACAO * VAZAO_TORNEIRA_L_MIN
    return ESCOVACOES_POR_DIA * 0.5


def litros_louca(torneira_aberta):
    """
    Litros gastos por dia lavando louca.
    Fechando a torneira na hora de ensaboar, o gasto cai pela metade.
    """
    total_aberta = MINUTOS_LAVANDO_LOUCA * VAZAO_TORNEIRA_L_MIN
    if torneira_aberta:
        return total_aberta
    return total_aberta / 2


def calcular_consumo(rotina):
    """
    Recebe a rotina (dicionario vindo do banco) e devolve um dicionario
    com o consumo separado por atividade e os totais por dia, mes e ano.
    """
    # 1) Calcula cada atividade separadamente.
    atividades = {
        "Banho": litros_banho(rotina["minutos_banho"], rotina["banhos_dia"]),
        "Descarga": litros_descargas(rotina["descargas_dia"]),
        "Escovar os dentes": litros_escovacao(rotina["torneira_escovar"]),
        "Lavar louca": litros_louca(rotina["torneira_louca"]),
    }

    # 2) Soma tudo para achar o consumo do dia.
    total_dia = sum(atividades.values())

    # 3) Monta uma lista com a porcentagem de cada atividade (para a tela).
    detalhes = []
    for nome, litros in atividades.items():
        if total_dia > 0:
            porcentagem = round(litros / total_dia * 100)
        else:
            porcentagem = 0
        detalhes.append({
            "nome": nome,
            "dia": round(litros, 1),
            "mes": round(litros * DIAS_NO_MES, 1),
            "ano": round(litros * DIAS_NO_ANO, 1),
            "porcentagem": porcentagem,
        })

    # Ordena da atividade que gasta mais para a que gasta menos.
    detalhes.sort(key=lambda item: item["dia"], reverse=True)

    return {
        "detalhes": detalhes,
        "total_dia": round(total_dia, 1),
        "total_mes": round(total_dia * DIAS_NO_MES, 1),
        "total_ano": round(total_dia * DIAS_NO_ANO, 1),
    }


def comparar_com_onu(total_dia):
    """
    Compara o consumo da pessoa com os 110 L/dia recomendados pela ONU.
    Devolve um dicionario pronto para a tela de resultado.
    """
    diferenca = total_dia - CONSUMO_RECOMENDADO_ONU
    # Quantos por cento do recomendado a pessoa usa.
    porcentagem = round(total_dia / CONSUMO_RECOMENDADO_ONU * 100)

    if diferenca > 0:
        situacao = "acima"
        mensagem = (
            "Voce gasta " + str(round(diferenca, 1)) + " litros por dia ACIMA "
            "do recomendado pela ONU (" + str(int(CONSUMO_RECOMENDADO_ONU))
            + " L/dia)."
        )
    else:
        situacao = "dentro"
        mensagem = (
            "Parabens! Voce esta " + str(round(abs(diferenca), 1)) + " litros "
            "por dia ABAIXO do limite recomendado pela ONU ("
            + str(int(CONSUMO_RECOMENDADO_ONU)) + " L/dia)."
        )

    return {
        "referencia_onu": CONSUMO_RECOMENDADO_ONU,
        "diferenca": round(diferenca, 1),
        "porcentagem": porcentagem,
        "barra": min(porcentagem, 200),  # a barra da tela para em 200%
        "situacao": situacao,
        "mensagem": mensagem,
    }


# =====================================================================
# ECONOMIA DAS MISSOES
# =====================================================================

def estimar_economia(missao, rotina):
    """
    Calcula quantos litros por dia a pessoa economizaria com UMA missao.

    Cada missao do missoes.json tem um campo "economia" com um tipo e um
    valor. O if/elif abaixo decide a conta certa para cada tipo.
    Missoes de descarte economizam 0 litros - o ganho delas e outro
    (menos lixo e menos poluicao do solo e da agua).
    """
    economia = missao.get("economia", {})
    tipo = economia.get("tipo", "zero")
    valor = economia.get("valor", 0)

    if tipo == "banho_reduzir":
        # Cortar "valor" minutos de cada banho.
        # Nunca economiza mais minutos do que a pessoa realmente gasta.
        minutos_cortados = min(valor, rotina["minutos_banho"])
        litros = minutos_cortados * rotina["banhos_dia"] * VAZAO_CHUVEIRO_L_MIN

    elif tipo == "banho_remover":
        # Tomar "valor" banhos menos por dia (sempre sobra pelo menos 1).
        banhos_cortados = min(valor, max(rotina["banhos_dia"] - 1, 0))
        litros = banhos_cortados * rotina["minutos_banho"] * VAZAO_CHUVEIRO_L_MIN

    elif tipo == "descarga_reduzir":
        # Economizar "valor" litros em cada descarga.
        litros = valor * rotina["descargas_dia"]

    elif tipo == "descarga_remover":
        # Dar "valor" descargas menos por dia (sempre sobra pelo menos 1).
        descargas_cortadas = min(valor, max(rotina["descargas_dia"] - 1, 0))
        litros = descargas_cortadas * LITROS_POR_DESCARGA

    elif tipo == "torneira_escovar":
        # Diferenca entre escovar com a torneira aberta e usando um copo.
        if rotina["torneira_escovar"]:
            litros = litros_escovacao(True) - litros_escovacao(False)
        else:
            litros = 0  # a pessoa ja faz certo, nao tem o que economizar

    elif tipo == "torneira_louca":
        # Diferenca entre lavar louca com a torneira aberta e fechada.
        if rotina["torneira_louca"]:
            litros = litros_louca(True) - litros_louca(False)
        else:
            litros = 0

    elif tipo == "fixo":
        # Economia estimada fixa, que nao depende da rotina da pessoa.
        litros = valor

    else:
        # tipo == "zero": missoes de descarte de residuos.
        litros = 0

    return round(litros, 1)


def resumir_economia(missoes, rotina):
    """
    Recebe uma lista de missoes e devolve a mesma lista com os campos de
    economia (dia, mes e ano) preenchidos dentro de cada missao.
    """
    resultado = []
    for missao in missoes:
        litros_dia = estimar_economia(missao, rotina)
        copia = dict(missao)  # copia para nao alterar o catalogo original
        copia["economia_dia"] = litros_dia
        copia["economia_mes"] = round(litros_dia * DIAS_NO_MES, 1)
        copia["economia_ano"] = round(litros_dia * DIAS_NO_ANO, 1)
        resultado.append(copia)
    return resultado


def economia_combinada(missoes):
    """
    Calcula a economia total de um conjunto de missoes SEM contar duas vezes.

    Por que isso e necessario: varias missoes mexem na mesma coisa.
    "Corte 5 minutos do banho", "Banho de 5 minutos" e "Um banho por dia"
    economizam todas no chuveiro. Somar as tres daria um numero maior do
    que a pessoa gasta de verdade - o que seria impossivel.

    A solucao: cada missao tem um "grupo" no missoes.json. Dentro de um
    grupo so vale a missao que economiza mais.
    """
    melhor_de_cada_grupo = {}

    for missao in missoes:
        grupo = missao.get("grupo", missao["id"])
        litros = missao.get("economia_dia", 0)
        # Guarda so o maior valor de cada grupo.
        if litros > melhor_de_cada_grupo.get(grupo, 0):
            melhor_de_cada_grupo[grupo] = litros

    return round(sum(melhor_de_cada_grupo.values()), 1)


# =====================================================================
# SISTEMA DE NIVEIS
# =====================================================================

def calcular_nivel(xp):
    """
    Transforma o XP total em nivel, nome do nivel e barra de progresso.

    Exemplo: 70 de XP -> nivel 2 (Broto), faltando 50 XP para virar Muda.
    """
    numero = 1
    nome = NIVEIS[0][1]
    xp_inicio = 0

    # Percorre a lista de niveis e guarda o ultimo que a pessoa alcancou.
    for indice, (xp_necessario, nome_nivel) in enumerate(NIVEIS):
        if xp >= xp_necessario:
            numero = indice + 1
            nome = nome_nivel
            xp_inicio = xp_necessario

    # Descobre qual e o proximo nivel (se ainda existir um).
    if numero < len(NIVEIS):
        xp_proximo = NIVEIS[numero][0]
        nome_proximo = NIVEIS[numero][1]
        faixa = xp_proximo - xp_inicio
        progresso = round((xp - xp_inicio) / faixa * 100)
        falta = xp_proximo - xp
    else:
        # A pessoa chegou no nivel maximo (Floresta).
        xp_proximo = None
        nome_proximo = None
        progresso = 100
        falta = 0

    return {
        "xp": xp,
        "numero": numero,
        "nome": nome,
        "nome_proximo": nome_proximo,
        "xp_proximo": xp_proximo,
        "progresso": progresso,
        "falta": falta,
        "total_niveis": len(NIVEIS),
    }
