"""
notificacoes.py
---------------
Notificacao no computador usando a biblioteca plyer.

Isso so funciona quando o app roda LOCALMENTE (no seu Windows), porque
usa a central de notificacoes do sistema operacional. Em um servidor na
internet nao existe tela para mostrar notificacao - por isso tudo aqui
esta dentro de try/except e nunca derruba o site.

O import do plyer fica dentro da funcao de proposito: assim, se o plyer
nao estiver instalado, o app nem percebe.
"""

# Quanto tempo a notificacao fica na tela, em segundos.
DURACAO_SEGUNDOS = 10

# Titulo que aparece na notificacao do Windows.
TITULO_PADRAO = "T.E.R.R.A."


def notificar(titulo, mensagem):
    """
    Mostra uma notificacao no computador.
    Devolve True se conseguiu e False se nao deu (sem nunca dar erro).
    """
    try:
        # O import fica aqui dentro: se o plyer nao existir, cai no except.
        from plyer import notification

        notification.notify(
            title=titulo,
            message=mensagem,
            app_name=TITULO_PADRAO,
            timeout=DURACAO_SEGUNDOS,
        )
        return True

    except Exception:
        # plyer nao instalado, rodando em servidor, sistema sem suporte...
        # Em todos os casos o app continua funcionando normalmente.
        return False


def notificar_missao_do_dia(missao):
    """
    Avisa a pessoa sobre a missao do dia pela notificacao do Windows.
    Chamada apenas pela rota /notificar do app.py (uso local).
    """
    if not missao:
        return False

    mensagem = missao["titulo"] + "\n" + missao["descricao"]
    return notificar("Missao do dia - T.E.R.R.A.", mensagem)


def notificar_lembrete(lembrete):
    """Avisa a pessoa com o lembrete do horario atual."""
    if not lembrete:
        return False

    return notificar(lembrete["titulo"], lembrete["texto"])
