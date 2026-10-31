"""
database.py
-----------
Tudo que envolve o banco de dados SQLite do T.E.R.R.A.

Sao duas tabelas:
  usuarios           -> a rotina que a pessoa respondeu no formulario
  missoes_concluidas -> o historico de missoes (de onde sai o XP)

O XP NAO fica guardado numa coluna solta: ele e a SOMA da coluna xp_ganho
da tabela missoes_concluidas. Assim o XP nunca fica diferente do historico.
"""

import sqlite3
from datetime import datetime

# Nome do arquivo do banco. Ele e criado sozinho na primeira execucao.
CAMINHO_BANCO = "terra.db"


def conectar():
    """Abre a conexao com o SQLite e faz as linhas virarem tipo dicionario."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    # sqlite3.Row permite acessar os dados por nome: linha["nome"]
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    """Cria as tabelas se elas ainda nao existirem (roda a cada inicio do app)."""
    conexao = conectar()
    cursor = conexao.cursor()

    # Tabela com a rotina de cada pessoa.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            nome               TEXT    NOT NULL,
            cidade             TEXT    NOT NULL,
            minutos_banho      INTEGER NOT NULL,
            banhos_dia         INTEGER NOT NULL,
            descargas_dia      INTEGER NOT NULL,
            torneira_escovar   INTEGER NOT NULL,
            torneira_louca     INTEGER NOT NULL,
            separa_lixo        INTEGER NOT NULL,
            descarte_especial  TEXT    NOT NULL,
            hora_acorda        TEXT    NOT NULL,
            hora_dorme         TEXT    NOT NULL,
            criado_em          TEXT    NOT NULL
        )
    """)

    # Tabela com as missoes que a pessoa ja concluiu.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missoes_concluidas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id    INTEGER NOT NULL,
            missao_id     TEXT    NOT NULL,
            titulo        TEXT    NOT NULL,
            categoria     TEXT    NOT NULL,
            xp_ganho      INTEGER NOT NULL,
            litros_dia    REAL    NOT NULL,
            concluida_em  TEXT    NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conexao.commit()
    conexao.close()


def salvar_rotina(dados):
    """Grava uma rotina nova e devolve o id do usuario criado."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO usuarios (
            nome, cidade, minutos_banho, banhos_dia, descargas_dia,
            torneira_escovar, torneira_louca, separa_lixo, descarte_especial,
            hora_acorda, hora_dorme, criado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["nome"], dados["cidade"], dados["minutos_banho"],
        dados["banhos_dia"], dados["descargas_dia"],
        dados["torneira_escovar"], dados["torneira_louca"],
        dados["separa_lixo"], dados["descarte_especial"],
        dados["hora_acorda"], dados["hora_dorme"],
        datetime.now().isoformat(timespec="seconds"),
    ))
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return novo_id


def atualizar_rotina(usuario_id, dados):
    """Atualiza a rotina de um usuario que ja existe (botao de editar)."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE usuarios SET
            nome = ?, cidade = ?, minutos_banho = ?, banhos_dia = ?,
            descargas_dia = ?, torneira_escovar = ?, torneira_louca = ?,
            separa_lixo = ?, descarte_especial = ?, hora_acorda = ?,
            hora_dorme = ?
        WHERE id = ?
    """, (
        dados["nome"], dados["cidade"], dados["minutos_banho"],
        dados["banhos_dia"], dados["descargas_dia"],
        dados["torneira_escovar"], dados["torneira_louca"],
        dados["separa_lixo"], dados["descarte_especial"],
        dados["hora_acorda"], dados["hora_dorme"],
        usuario_id,
    ))
    conexao.commit()
    conexao.close()


def buscar_usuario(usuario_id):
    """Devolve a rotina de um usuario como dicionario, ou None se nao achar."""
    conexao = conectar()
    linha = conexao.execute(
        "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    conexao.close()
    return dict(linha) if linha else None


def buscar_ultimo_usuario():
    """
    Devolve o ultimo perfil cadastrado.
    Serve de reserva: se o navegador perder a sessao, o app ainda acha a rotina.
    """
    conexao = conectar()
    linha = conexao.execute(
        "SELECT * FROM usuarios ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conexao.close()
    return dict(linha) if linha else None


def concluir_missao(usuario_id, missao, litros_dia):
    """Registra uma missao concluida (e e isso que da XP para a pessoa)."""
    conexao = conectar()
    conexao.execute("""
        INSERT INTO missoes_concluidas (
            usuario_id, missao_id, titulo, categoria,
            xp_ganho, litros_dia, concluida_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        usuario_id, missao["id"], missao["titulo"], missao["categoria"],
        missao["xp"], litros_dia,
        datetime.now().isoformat(timespec="seconds"),
    ))
    conexao.commit()
    conexao.close()


def concluida_hoje(usuario_id, missao_id):
    """
    Diz se a pessoa ja concluiu essa missao HOJE.
    Evita que alguem clique mil vezes no mesmo botao e ganhe XP infinito.
    """
    hoje = datetime.now().strftime("%Y-%m-%d")
    conexao = conectar()
    linha = conexao.execute("""
        SELECT id FROM missoes_concluidas
        WHERE usuario_id = ? AND missao_id = ? AND concluida_em LIKE ?
    """, (usuario_id, missao_id, hoje + "%")).fetchone()
    conexao.close()
    return linha is not None


def listar_historico(usuario_id, limite=50):
    """Lista as missoes concluidas, da mais nova para a mais antiga."""
    conexao = conectar()
    linhas = conexao.execute("""
        SELECT * FROM missoes_concluidas
        WHERE usuario_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (usuario_id, limite)).fetchall()
    conexao.close()
    return [dict(linha) for linha in linhas]


def total_xp(usuario_id):
    """Soma todo o XP que a pessoa ja ganhou."""
    conexao = conectar()
    resultado = conexao.execute(
        "SELECT SUM(xp_ganho) FROM missoes_concluidas WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()[0]
    conexao.close()
    # Se a pessoa nunca concluiu nada, o SQLite devolve None -> viramos 0.
    return resultado or 0


def total_litros_economizados(usuario_id):
    """
    Soma a economia de agua (litros por dia) de todas as missoes concluidas.
    E uma estimativa: mostra o impacto se a pessoa mantiver os habitos.
    """
    conexao = conectar()
    resultado = conexao.execute(
        "SELECT SUM(litros_dia) FROM missoes_concluidas WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()[0]
    conexao.close()
    return round(resultado or 0, 1)


def contar_missoes(usuario_id):
    """Conta quantas missoes a pessoa ja concluiu no total."""
    conexao = conectar()
    resultado = conexao.execute(
        "SELECT COUNT(*) FROM missoes_concluidas WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()[0]
    conexao.close()
    return resultado
