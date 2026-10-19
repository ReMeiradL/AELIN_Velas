import hmac
import os
import secrets
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

import banco

app = Flask(__name__)

# O padrão serve só para rodar em casa; em produção defina SECRET_KEY no ambiente.
app.secret_key = os.environ.get("SECRET_KEY", "aelin-chave-so-para-desenvolvimento")

# O navegador não envia o cookie de login em requisições vindas de outros sites.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

WHATSAPP = "5583991358966"
INSTAGRAM = "aelinvelas"
FAMILIAS = ["Floral", "Frutado", "Gourmand", "Oriental", "Cítrico", "Herbal", "Amadeirado", "Especiarias"]
SENHA_MINIMA = 8
NOME_MINIMO = 3
NOME_MAXIMO = 40


@app.context_processor
def dados_da_loja():
    return {"whatsapp": WHATSAPP, "instagram": INSTAGRAM, "senha_minima": SENHA_MINIMA}


# ---------- proteção contra envios forjados (CSRF) ----------

def token_csrf():
    """Token da sessão; todo formulário POST leva esse valor em um campo escondido."""
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = token_csrf


@app.before_request
def conferir_csrf():
    if request.method == "POST":
        enviado = request.form.get("csrf", "")
        esperado = session.get("csrf", "")
        if not esperado or not hmac.compare_digest(enviado, esperado):
            return "Requisição inválida ou sessão expirada. Volte à página anterior, recarregue e tente de novo.", 400


@app.template_filter("brl")
def brl(valor):
    if valor is None:
        return "consulte"
    return "R$ " + f"{valor:.2f}".replace(".", ",")


def login_required(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorada


# ---------- loja (pública) ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/velas")
def velas():
    produtos = banco.listar_produtos()
    return render_template(
        "velas.html",
        velas=[p for p in produtos if p["categoria"] == "Velas"],
    )


@app.route("/produtos")
def produtos():
    lista = banco.listar_produtos()

    def da_categoria(*nomes):
        return [p for p in lista if p["categoria"] in nomes]

    return render_template(
        "produtos.html",
        flores=da_categoria("Flores aromáticas"),
        aromatizadores=da_categoria("Aromatizadores"),
        outros=da_categoria("Escalda-pés", "Wax melt", "Sachê aromático"),
    )


@app.route("/kits")
def kits():
    return render_template("kits.html", kits=banco.listar_kits())


@app.route("/descontos")
def descontos():
    return render_template("descontos.html", faixas=banco.listar_faixas())


@app.route("/pedido")
def pedido():
    return render_template("pedido.html")


@app.route("/aromas")
def aromas():
    familia = request.args.get("familia", "").strip()
    return render_template(
        "aromas.html",
        aromas=banco.listar_aromas(familia),
        familias=FAMILIAS,
        familia=familia,
    )


# ---------- login ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        usuario = banco.buscar_usuario(nome)
        if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
            return render_template("login.html", erro="Usuário ou senha inválidos.")

        session["usuario"] = usuario["nome"]
        session.pop("csrf", None)  # novo token a cada login
        flash("Login realizado com sucesso!")
        return redirect("/estoque")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    session.pop("csrf", None)
    return redirect("/")


# ---------- minha conta ----------

@app.route("/conta")
@login_required
def conta():
    return render_template("conta.html")


@app.route("/conta/senha", methods=["GET", "POST"])
@login_required
def conta_senha():
    if request.method == "POST":
        atual = request.form["atual"]
        nova = request.form["nova"]
        confirmacao = request.form["confirmacao"]

        usuario = banco.buscar_usuario(session["usuario"])
        if usuario is None:
            session.pop("usuario", None)
            return redirect("/login")

        erro = None
        if not check_password_hash(usuario["senha_hash"], atual):
            erro = "A senha atual está incorreta."
        elif len(nova) < SENHA_MINIMA:
            erro = f"A nova senha deve ter pelo menos {SENHA_MINIMA} caracteres."
        elif nova != confirmacao:
            erro = "A confirmação não é igual à nova senha."
        elif nova == atual:
            erro = "A nova senha deve ser diferente da atual."

        if erro:
            return render_template("conta_senha.html", erro=erro)

        banco.atualizar_senha(usuario["id"], generate_password_hash(nova))
        flash("Senha alterada com sucesso!")
        return redirect("/conta")

    return render_template("conta_senha.html")


@app.route("/conta/usuario", methods=["GET", "POST"])
@login_required
def conta_usuario():
    if request.method == "POST":
        atual = request.form["atual"]
        novo_nome = request.form["nome"].strip()

        usuario = banco.buscar_usuario(session["usuario"])
        if usuario is None:
            session.pop("usuario", None)
            return redirect("/login")

        outro = banco.buscar_usuario(novo_nome)

        erro = None
        if not check_password_hash(usuario["senha_hash"], atual):
            erro = "A senha atual está incorreta."
        elif not NOME_MINIMO <= len(novo_nome) <= NOME_MAXIMO:
            erro = f"O nome de acesso deve ter de {NOME_MINIMO} a {NOME_MAXIMO} caracteres."
        elif novo_nome == usuario["nome"]:
            erro = "Esse já é o seu nome de acesso."
        elif outro is not None:
            erro = "Esse nome de acesso já está em uso."

        if erro:
            return render_template("conta_usuario.html", erro=erro, nome=novo_nome)

        banco.atualizar_nome(usuario["id"], novo_nome)
        session["usuario"] = novo_nome
        flash("Nome de acesso alterado com sucesso!")
        return redirect("/conta")

    return render_template("conta_usuario.html", nome="")


# ---------- painel de estoque ----------

def pagina_estoque(aba, **dados):
    return render_template(
        "estoque.html",
        aba=aba,
        resumo=banco.resumo_estoque(),
        limite=banco.LIMITE_BAIXO,
        **dados,
    )


@app.route("/estoque")
@login_required
def estoque():
    busca = request.args.get("busca", "").strip()
    categoria_id = request.args.get("categoria", type=int)
    return pagina_estoque(
        "produtos",
        produtos=banco.listar_produtos(busca, categoria_id),
        categorias=banco.listar_categorias(),
        busca=busca,
        categoria_id=categoria_id,
    )


@app.route("/estoque/kits")
@login_required
def estoque_kits():
    return pagina_estoque("kits", kits=banco.listar_kits())


@app.route("/estoque/aromas")
@login_required
def estoque_aromas():
    return pagina_estoque("aromas", aromas=banco.listar_aromas())


def delta_do_form():
    return 1 if request.form.get("delta") == "1" else -1


@app.route("/estoque/produtos/<int:id>/ajustar", methods=["POST"])
@login_required
def produto_ajustar(id):
    banco.ajustar_estoque_produto(id, delta_do_form())
    return redirect("/estoque")


@app.route("/estoque/kits/<int:id>/ajustar", methods=["POST"])
@login_required
def kit_ajustar(id):
    banco.ajustar_estoque_kit(id, delta_do_form())
    return redirect("/estoque/kits")


@app.route("/estoque/aromas/<int:id>/alternar", methods=["POST"])
@login_required
def aroma_alternar(id):
    banco.alternar_aroma(id)
    return redirect("/estoque/aromas")


# ---------- cadastro de produtos ----------

def ler_formulario_produto():
    """Devolve (valores para reexibir, dados convertidos, mensagem de erro)."""
    valores = {
        "nome": request.form["nome"].strip(),
        "categoria_id": request.form["categoria_id"],
        "preco": request.form["preco"].strip(),
        "estoque": request.form["estoque"].strip(),
    }

    if not valores["nome"]:
        return valores, None, "O nome não pode ficar vazio."

    try:
        categoria_id = int(valores["categoria_id"])
    except ValueError:
        return valores, None, "Escolha uma categoria."

    preco = None
    if valores["preco"]:
        try:
            preco = Decimal(valores["preco"].replace(",", "."))
        except InvalidOperation:
            return valores, None, "Preço inválido. Exemplo: 24,90"
        if preco <= 0:
            return valores, None, "O preço deve ser maior que zero (ou deixe vazio para “consulte”)."

    try:
        estoque = int(valores["estoque"])
    except ValueError:
        return valores, None, "Estoque inválido."
    if estoque < 0:
        return valores, None, "O estoque não pode ser negativo."

    return valores, (valores["nome"], categoria_id, preco, estoque), None


@app.route("/estoque/novo", methods=["GET", "POST"])
@login_required
def produto_novo():
    categorias = banco.listar_categorias()
    valores = {"nome": "", "categoria_id": "", "preco": "", "estoque": "0"}

    if request.method == "POST":
        valores, dados, erro = ler_formulario_produto()
        if erro:
            return render_template("produto_form.html", titulo="Novo item", acao="/estoque/novo",
                                   categorias=categorias, valores=valores, erro=erro)
        banco.cadastrar_produto(*dados)
        flash("Produto cadastrado com sucesso!")
        return redirect("/estoque")

    return render_template("produto_form.html", titulo="Novo item", acao="/estoque/novo",
                           categorias=categorias, valores=valores)


@app.route("/estoque/<int:id>/editar", methods=["GET", "POST"])
@login_required
def produto_editar(id):
    produto = banco.buscar_produto(id)
    if produto is None:
        return "Produto não encontrado!", 404

    categorias = banco.listar_categorias()
    acao = f"/estoque/{id}/editar"

    if request.method == "POST":
        valores, dados, erro = ler_formulario_produto()
        if erro:
            return render_template("produto_form.html", titulo="Editar item", acao=acao,
                                   categorias=categorias, valores=valores, erro=erro)
        banco.atualizar_produto(id, *dados)
        flash("Produto atualizado com sucesso!")
        return redirect("/estoque")

    valores = {
        "nome": produto["nome"],
        "categoria_id": str(produto["categoria_id"]),
        "preco": "" if produto["preco"] is None else str(produto["preco"]).replace(".", ","),
        "estoque": str(produto["estoque"]),
    }
    return render_template("produto_form.html", titulo="Editar item", acao=acao,
                           categorias=categorias, valores=valores)


@app.route("/estoque/<int:id>/excluir", methods=["GET", "POST"])
@login_required
def produto_excluir(id):
    produto = banco.buscar_produto(id)
    if produto is None:
        return "Produto não encontrado!", 404

    if request.method == "POST":
        banco.excluir_produto(id)
        flash("Produto excluído com sucesso!")
        return redirect("/estoque")

    return render_template("excluir.html", produto=produto)


if __name__ == "__main__":
    app.run(debug=True)
