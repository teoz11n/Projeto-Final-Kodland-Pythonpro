"""
app.py
------
O arquivo principal do T.E.R.R.A. Aqui ficam SO as rotas do Flask.

A ideia e que este arquivo seja um "garcom": ele recebe o pedido do
navegador, chama as funcoes dos outros arquivos (calculos, missoes,
clima, database) e entrega o resultado para o template HTML.
Nenhuma conta de litros ou regra de missao fica aqui.

Para rodar:  py -3.11 app.py
Depois abra: http://127.0.0.1:5000
"""

from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)

import calculos
import clima
import database
import ia
import missoes
import notificacoes

app = Flask(__name__)

# A chave secreta e o que permite o Flask usar session e flash.
# Em um projeto de verdade ela viria do .env; para a escola pode ficar aqui.
app.secret_key = "terra-projeto-escolar-kodland"

# Opcoes aceitas no campo de descarte (usadas na validacao e no template).
OPCOES_DESCARTE = {
    "lixo_comum": "Jogo no lixo comum",
    "guardo": "Guardo em casa, mas não levo a lugar nenhum",
    "ponto_coleta": "Levo a um ponto de coleta ou ecoponto",
}


# =====================================================================
# FUNCOES DE APOIO
# =====================================================================

def usuario_atual():
    """
    Devolve a rotina da pessoa que esta usando o app, ou None.

    Primeiro tenta pela sessao do navegador. Se nao achar (por exemplo,
    o navegador foi fechado), pega o ultimo perfil salvo no banco - assim
    a apresentacao nao quebra se o Flask reiniciar.
    """
    usuario_id = session.get("usuario_id")

    if usuario_id:
        usuario = database.buscar_usuario(usuario_id)
        if usuario:
            return usuario

    # Reserva: ultimo perfil cadastrado.
    usuario = database.buscar_ultimo_usuario()
    if usuario:
        session["usuario_id"] = usuario["id"]
    return usuario


# Os campos numericos do formulario, com o limite de cada um.
# Cada item e: (nome_do_campo, texto_amigavel, minimo, maximo)
CAMPOS_NUMERICOS = [
    ("minutos_banho", "minutos de banho", 1, 120),
    ("banhos_dia", "banhos por dia", 1, 10),
    ("descargas_dia", "descargas por dia", 1, 40),
]

# Os campos de sim/nao, que viram 1 ou 0 para o SQLite.
CAMPOS_SIM_NAO = ("torneira_escovar", "torneira_louca", "separa_lixo")

# Os horarios, com o valor de reserva caso a pessoa mande algo invalido.
CAMPOS_HORARIO = [
    ("hora_acorda", "acorda", "07:00"),
    ("hora_dorme", "dorme", "22:00"),
]

TAMANHO_MAXIMO_DO_NOME = 60


# --- Cada funcao abaixo valida UM tipo de campo ---------------------
# Todas seguem o mesmo contrato: recebem o formulario, escrevem no
# dicionario "dados" e devolvem a lista de erros que encontraram.
# Fica facil de ler, de testar e de acrescentar um campo novo.

def _validar_textos(formulario, dados):
    """Nome e cidade: nao podem ficar vazios."""
    erros = []

    nome = formulario.get("nome", "").strip()
    if not nome:
        erros.append("Preencha o seu nome.")
    elif len(nome) > TAMANHO_MAXIMO_DO_NOME:
        erros.append("O nome está muito longo (máximo "
                     + str(TAMANHO_MAXIMO_DO_NOME) + " letras).")
    dados["nome"] = nome

    cidade = formulario.get("cidade", "").strip()
    if not cidade:
        erros.append("Preencha a sua cidade.")
    dados["cidade"] = cidade

    return erros


def _validar_numeros(formulario, dados):
    """Banho, banhos por dia e descargas: numero inteiro dentro do limite."""
    erros = []

    for campo, rotulo, minimo, maximo in CAMPOS_NUMERICOS:
        texto = formulario.get(campo, "").strip()
        dados[campo] = minimo   # valor de reserva, trocado se der certo

        if not texto:
            erros.append("Preencha o campo de " + rotulo + ".")
            continue

        try:
            numero = int(texto)
        except ValueError:
            erros.append("O campo de " + rotulo + " precisa ser um número.")
            continue

        if numero < minimo:
            erros.append("O campo de " + rotulo + " não pode ser menor que "
                         + str(minimo) + ".")
        elif numero > maximo:
            erros.append("O campo de " + rotulo + " não pode passar de "
                         + str(maximo) + ".")
        dados[campo] = numero

    return erros


def _validar_sim_nao(formulario, dados):
    """Converte os sim/nao em 1 ou 0. Nunca da erro: o que nao for 'sim' e 0."""
    for campo in CAMPOS_SIM_NAO:
        dados[campo] = 1 if formulario.get(campo) == "sim" else 0
    return []


def _validar_descarte(formulario, dados):
    """O descarte precisa ser uma das opcoes que o app conhece."""
    erros = []

    descarte = formulario.get("descarte_especial", "")
    if descarte not in OPCOES_DESCARTE:
        erros.append("Escolha como você descarta pilhas, óleo e eletrônicos.")
        descarte = "lixo_comum"
    dados["descarte_especial"] = descarte

    return erros


def _validar_horarios(formulario, dados):
    """Os horarios precisam estar no formato HH:MM."""
    erros = []

    for campo, rotulo, reserva in CAMPOS_HORARIO:
        texto = formulario.get(campo, "").strip()
        try:
            # strptime da erro se o texto nao for um horario valido.
            datetime.strptime(texto, "%H:%M")
            dados[campo] = texto
        except ValueError:
            erros.append("Informe o horário em que você " + rotulo + ".")
            dados[campo] = reserva

    return erros


def validar_rotina(formulario):
    """
    Confere os dados do formulario, chamando um validador por tipo de campo.

    Devolve uma tupla (dados, erros):
      dados -> dicionario pronto para salvar no banco
      erros -> lista de mensagens; se estiver vazia, esta tudo certo.
    """
    dados = {}
    erros = []

    for validar in (_validar_textos, _validar_numeros, _validar_sim_nao,
                    _validar_descarte, _validar_horarios):
        erros.extend(validar(formulario, dados))

    return dados, erros


def buscar_clima_seguro(cidade):
    """
    Busca o clima sem risco de derrubar a pagina.
    Devolve o dicionario do clima ou None.
    """
    try:
        return clima.buscar_clima(cidade)
    except Exception:
        return None


# =====================================================================
# ROTAS
# =====================================================================

@app.route("/")
def inicio():
    """Pagina inicial: apresenta o projeto e tem o botao Comecar."""
    tem_perfil = database.buscar_ultimo_usuario() is not None
    return render_template(
        "index.html",
        tem_perfil=tem_perfil,
        dica=missoes.sortear_dica(),
    )


@app.route("/rotina", methods=["GET", "POST"])
def rotina():
    """Formulario da rotina. Serve para cadastrar e para editar."""
    usuario = usuario_atual()

    if request.method == "POST":
        dados, erros = validar_rotina(request.form)

        # Se achou erro, volta para o formulario mostrando as mensagens
        # e mantendo o que a pessoa ja tinha digitado.
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template(
                "rotina.html",
                usuario=dados,
                opcoes_descarte=OPCOES_DESCARTE,
                editando=usuario is not None,
            )

        # Esta tudo certo: salva ou atualiza.
        if usuario and request.form.get("editar") == "sim":
            database.atualizar_rotina(usuario["id"], dados)
            session["usuario_id"] = usuario["id"]
            flash("Rotina atualizada!", "ok")
        else:
            novo_id = database.salvar_rotina(dados)
            session["usuario_id"] = novo_id
            flash("Rotina salva! Veja o seu resultado.", "ok")

        return redirect(url_for("resultado"))

    # GET: mostra o formulario (preenchido, se a pessoa ja tiver perfil).
    return render_template(
        "rotina.html",
        usuario=usuario,
        opcoes_descarte=OPCOES_DESCARTE,
        editando=usuario is not None,
    )


@app.route("/resultado")
def resultado():
    """Mostra o consumo calculado, a comparacao com a ONU e as missoes."""
    usuario = usuario_atual()
    if not usuario:
        flash("Preencha a sua rotina primeiro.", "erro")
        return redirect(url_for("rotina"))

    # 1) Contas de consumo.
    consumo = calculos.calcular_consumo(usuario)
    comparacao = calculos.comparar_com_onu(consumo["total_dia"])

    # 2) Clima (para liberar a missao da chuva, se for o caso).
    tempo = buscar_clima_seguro(usuario["cidade"])
    esta_chovendo = tempo["esta_chovendo"] if tempo else False

    # 3) Missoes personalizadas.
    lista, origem = missoes.escolher_missoes(usuario, esta_chovendo)

    # 4) Economia total sem contar duas vezes a mesma coisa
    #    (tres missoes de banho nao economizam tres vezes o mesmo banho).
    economia_total = calculos.economia_combinada(lista)

    return render_template(
        "resultado.html",
        usuario=usuario,
        consumo=consumo,
        comparacao=comparacao,
        missoes_sugeridas=lista,
        origem=origem,
        economia_total=economia_total,
        economia_total_mes=round(economia_total * calculos.DIAS_NO_MES, 1),
    )


@app.route("/painel")
def painel():
    """Painel do dia: missao sorteada, lembrete do horario, clima e missoes."""
    usuario = usuario_atual()
    if not usuario:
        flash("Preencha a sua rotina primeiro.", "erro")
        return redirect(url_for("rotina"))

    # Clima primeiro, porque ele pode liberar a missao da chuva.
    tempo = buscar_clima_seguro(usuario["cidade"])
    esta_chovendo = tempo["esta_chovendo"] if tempo else False

    lista, origem = missoes.escolher_missoes(usuario, esta_chovendo)

    # Marca quais missoes a pessoa ja concluiu hoje.
    for missao in lista:
        missao["feita_hoje"] = database.concluida_hoje(
            usuario["id"], missao["id"]
        )

    # Missao do dia (random com semente da data) e lembrete (datetime).
    missao_do_dia = missoes.sortear_missao_do_dia(lista)
    lembrete = missoes.lembrete_do_momento(usuario)

    # Dados do nivel, para a barrinha no topo do painel.
    xp = database.total_xp(usuario["id"])
    nivel = calculos.calcular_nivel(xp)

    return render_template(
        "painel.html",
        usuario=usuario,
        tempo=tempo,
        missoes_ativas=lista,
        missao_do_dia=missao_do_dia,
        lembrete=lembrete,
        nivel=nivel,
        origem=origem,
        dica=missoes.sortear_dica(),
        ia_ligada=ia.ia_disponivel(),
    )


@app.route("/concluir/<missao_id>", methods=["POST"])
def concluir(missao_id):
    """Marca uma missao como concluida e da o XP para a pessoa."""
    usuario = usuario_atual()
    if not usuario:
        return redirect(url_for("rotina"))

    # Procura a missao no catalogo pelo id.
    escolhida = None
    for missao in missoes.listar_missoes():
        if missao["id"] == missao_id:
            escolhida = missao
            break

    if escolhida is None:
        flash("Missão não encontrada.", "erro")
        return redirect(url_for("painel"))

    # Nao deixa ganhar XP duas vezes com a mesma missao no mesmo dia.
    if database.concluida_hoje(usuario["id"], missao_id):
        flash("Você já concluiu essa missão hoje. Volte amanhã!", "erro")
        return redirect(url_for("painel"))

    # Guarda o nivel antes para saber se a pessoa subiu de nivel agora.
    nivel_antes = calculos.calcular_nivel(database.total_xp(usuario["id"]))

    litros = calculos.estimar_economia(escolhida, usuario)
    database.concluir_missao(usuario["id"], escolhida, litros)

    nivel_depois = calculos.calcular_nivel(database.total_xp(usuario["id"]))

    flash(
        "Missão concluída! +" + str(escolhida["xp"]) + " XP", "ok"
    )
    if nivel_depois["numero"] > nivel_antes["numero"]:
        flash("Você subiu de nível: agora você é " + nivel_depois["nome"] + "!", "ok")

    return redirect(url_for("painel"))


@app.route("/perfil")
def perfil():
    """Nivel, XP, barra de progresso, historico e total economizado."""
    usuario = usuario_atual()
    if not usuario:
        flash("Preencha a sua rotina primeiro.", "erro")
        return redirect(url_for("rotina"))

    xp = database.total_xp(usuario["id"])
    nivel = calculos.calcular_nivel(xp)
    litros_dia = database.total_litros_economizados(usuario["id"])

    return render_template(
        "perfil.html",
        usuario=usuario,
        nivel=nivel,
        niveis=calculos.NIVEIS,
        historico=database.listar_historico(usuario["id"]),
        total_missoes=database.contar_missoes(usuario["id"]),
        litros_dia=litros_dia,
        litros_mes=round(litros_dia * calculos.DIAS_NO_MES, 1),
        litros_ano=round(litros_dia * calculos.DIAS_NO_ANO, 1),
    )


@app.route("/sobre")
def sobre():
    """Explica o problema, as fontes dos dados e quem fez o projeto."""
    return render_template(
        "sobre.html",
        total_missoes=len(missoes.listar_missoes()),
        dicas=missoes.listar_dicas(),
        # Passamos as constantes para a tela mostrar as fontes de verdade.
        vazao_chuveiro=calculos.VAZAO_CHUVEIRO_L_MIN,
        litros_descarga=calculos.LITROS_POR_DESCARGA,
        vazao_torneira=calculos.VAZAO_TORNEIRA_L_MIN,
        referencia_onu=calculos.CONSUMO_RECOMENDADO_ONU,
    )


@app.route("/notificar", methods=["POST"])
def notificar():
    """
    Dispara a notificacao do Windows (plyer).
    So funciona rodando no proprio computador - por isso fica numa rota
    separada, chamada por um botao no painel.
    """
    usuario = usuario_atual()
    if not usuario:
        return redirect(url_for("rotina"))

    lista, _ = missoes.escolher_missoes(usuario, usar_ia=False)
    missao_do_dia = missoes.sortear_missao_do_dia(lista)

    if notificacoes.notificar_missao_do_dia(missao_do_dia):
        flash("Notificação enviada para a sua área de trabalho!", "ok")
    else:
        flash(
            "Não foi possível notificar. Isso só funciona rodando o app "
            "no seu próprio computador com o plyer instalado.", "erro"
        )

    return redirect(url_for("painel"))


@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    """Pagina de erro 404 personalizada."""
    return render_template("404.html"), 404


# =====================================================================
# INICIO DO PROGRAMA
# =====================================================================

# Cria o banco de dados automaticamente na primeira execucao.
# Fica fora do if abaixo para funcionar tambem com "flask run".
database.criar_tabelas()

if __name__ == "__main__":
    # debug=True mostra os erros na tela e reinicia sozinho ao salvar.
    app.run(debug=True)
