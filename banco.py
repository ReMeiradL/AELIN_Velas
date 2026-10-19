import os

import psycopg2
from psycopg2.extras import RealDictCursor

# Até esta quantidade (e acima de 0), o item aparece como "Baixo" no painel.
LIMITE_BAIXO = 5


def conectar():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Defina a variável de ambiente DATABASE_URL (veja o README.md).")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


def consultar(sql, params=(), um=False):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(sql, params)
    resultado = cursor.fetchone() if um else cursor.fetchall()
    conexao.close()
    return resultado


def executar(sql, params=()):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(sql, params)
    conexao.commit()
    conexao.close()


# ---------- categorias ----------

def listar_categorias():
    return consultar("SELECT id, nome FROM categorias ORDER BY ordem")


# ---------- produtos ----------

def listar_produtos(busca="", categoria_id=None):
    sql = """
        SELECT p.id, p.nome, p.descricao, p.preco, p.estoque,
               c.id AS categoria_id, c.nome AS categoria
        FROM produtos p
        JOIN categorias c ON c.id = p.categoria_id
        WHERE p.nome ILIKE %s
    """
    params = ["%" + busca + "%"]
    if categoria_id:
        sql += " AND c.id = %s"
        params.append(categoria_id)
    sql += " ORDER BY c.ordem, p.id"
    return consultar(sql, params)


def buscar_produto(id):
    return consultar(
        "SELECT id, nome, descricao, categoria_id, preco, estoque FROM produtos WHERE id = %s",
        (id,),
        um=True,
    )


def cadastrar_produto(nome, categoria_id, preco, estoque):
    executar(
        "INSERT INTO produtos (nome, categoria_id, preco, estoque) VALUES (%s, %s, %s, %s)",
        (nome, categoria_id, preco, estoque),
    )


def atualizar_produto(id, nome, categoria_id, preco, estoque):
    executar(
        "UPDATE produtos SET nome = %s, categoria_id = %s, preco = %s, estoque = %s WHERE id = %s",
        (nome, categoria_id, preco, estoque, id),
    )


def excluir_produto(id):
    executar("DELETE FROM produtos WHERE id = %s", (id,))


def ajustar_estoque_produto(id, delta):
    executar(
        "UPDATE produtos SET estoque = GREATEST(estoque + %s, 0) WHERE id = %s",
        (delta, id),
    )


# ---------- kits ----------

def listar_kits():
    return consultar("SELECT id, nome, itens, descricao, preco, estoque FROM kits ORDER BY id")


def ajustar_estoque_kit(id, delta):
    executar(
        "UPDATE kits SET estoque = GREATEST(estoque + %s, 0) WHERE id = %s",
        (delta, id),
    )


# ---------- aromas ----------

def listar_aromas(familia=""):
    return consultar(
        "SELECT id, nome, familia, notas, disponivel FROM aromas WHERE familia ILIKE %s ORDER BY nome",
        ("%" + familia + "%",),
    )


def alternar_aroma(id):
    executar("UPDATE aromas SET disponivel = NOT disponivel WHERE id = %s", (id,))


# ---------- descontos ----------

def listar_faixas():
    return consultar("SELECT id, faixa, desconto FROM faixas_desconto ORDER BY id")


# ---------- resumo do painel ----------

def resumo_estoque():
    return consultar(
        """
        SELECT COUNT(*) AS itens,
               COALESCE(SUM(estoque), 0) AS unidades,
               COUNT(*) FILTER (WHERE estoque BETWEEN 1 AND %s) AS baixos,
               COUNT(*) FILTER (WHERE estoque = 0) AS esgotados
        FROM (SELECT estoque FROM produtos UNION ALL SELECT estoque FROM kits) t
        """,
        (LIMITE_BAIXO,),
        um=True,
    )


# ---------- usuários ----------

def buscar_usuario(nome):
    return consultar(
        "SELECT id, nome, senha_hash FROM usuarios WHERE nome = %s", (nome,), um=True
    )
