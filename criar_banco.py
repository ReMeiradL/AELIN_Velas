import os

from werkzeug.security import generate_password_hash

import banco

# Quantidade inicial de cada item. Ajuste depois no painel de estoque.
ESTOQUE_INICIAL = 10

# Fotos já enviadas ao projeto (static/img/produtos). Só entram em produtos que ainda estão sem foto.
FOTOS = {
    "Rosa": "produtos/rosa.jpg",
    "Jasmim": "produtos/jasmim.jpg",
    "Margarida": "produtos/margarida.jpg",
    "Home spray": "produtos/home-spray.jpg",
    "Difusor de varetas": "produtos/difusor.jpg",
    "Escalda-pés": "produtos/escalda-pes.jpg",
    "Sachê aromático": "produtos/sache.jpg",
    "Tulipa": "produtos/tulipa.jpg",
    "Aromatizador de carro": "produtos/aromatizador_de_carro.jpg",
    "Wax melt": "produtos/wax_melt.jpg",
}

# Fotos dos kits, com a mesma regra: só entram em kits que ainda estão sem foto.
FOTOS_KITS = {
    "Descubra Aelin": "produtos/descubra_aelin.jpg",
    "Ritual Aelin": "produtos/ritual_aelin.jpg",
    "Casa Perfumada": "produtos/casa_perfumada.jpg",
    "Jardim Aelin": "produtos/jardim_aelin.jpg",
    "Presente Aelin": "produtos/presente_aelin.jpg",
}

CATEGORIAS = [
    "Velas",
    "Flores aromáticas",
    "Aromatizadores",
    "Escalda-pés",
    "Wax melt",
    "Sachê aromático",
]

# (categoria, nome, preço, descrição). Preço None = "consulte".
PRODUTOS = [
    ("Velas", "Vela 20g", "14.90", None),
    ("Velas", "Vela 40g", "22.90", None),
    ("Velas", "Vela 60g", "29.90", None),
    ("Velas", "Vela 70g", "34.90", None),
    ("Velas", "Vela 100g", "44.90", None),
    ("Flores aromáticas", "Jasmim", "24.90", None),
    ("Flores aromáticas", "Rosa", "32.90", None),
    ("Flores aromáticas", "Tulipa", None, None),
    ("Flores aromáticas", "Margarida", None, None),
    ("Aromatizadores", "Home spray", "35.90", None),
    ("Aromatizadores", "Difusor de varetas", "48.90", None),
    ("Aromatizadores", "Aromatizador de carro", "19.90", None),
    ("Escalda-pés", "Escalda-pés", "21.90",
     "Um momento de relaxamento e cuidado para os seus pés. Alivia o cansaço, hidrata e perfuma, proporciona bem-estar."),
    ("Wax melt", "Wax melt", None,
     "Praticidade e aroma intenso para o seu ambiente. Ideal para rechaud, aroma por mais tempo, prático e seguro."),
    ("Sachê aromático", "Sachê aromático", "34.90",
     "Perfume discreto e duradouro para pequenos espaços. Ideal para gavetas e armários."),
]

# (nome, itens, descrição, preço)
KITS = [
    ("Descubra Aelin", "3 velas de 20g",
     "Para quem quer conhecer diferentes aromas antes de escolher sua próxima Aelin.", "37.90"),
    ("Ritual Aelin", "Vela 40g + Escalda-pés + Sachê",
     "Um pequeno ritual para desacelerar e cuidar de si.", "62.90"),
    ("Casa Perfumada", "Difusor + Home spray + Aromatizador de carro",
     "Uma experiência completa para deixar diferentes espaços perfumados.", "88.90"),
    ("Jardim Aelin", "Rosa + Wax melt + Sachê",
     "Um kit delicado, bonito e diferente. Ótimo para presentear.", "60.90"),
    ("Presente Aelin", "Vela 100g + Sachê + Aromatizador de carro",
     "Uma opção mais completa para presentear.", "73.90"),
]

# (faixa de quantidade, desconto)
FAIXAS = [
    ("1–4 unidades", "Preço cheio"),
    ("5–9 unidades", "5% OFF"),
    ("10–19 unidades", "8% OFF"),
    ("20–29 unidades", "12% OFF"),
    ("30–49 unidades", "15% OFF"),
    ("50+ unidades", "Orçamento"),
]

# (nome, família olfativa, notas aromáticas)
AROMAS = [
    ("Algas Marinhas", "Marítimo fresco", "Vento, Jasmim, Lírio Verde, Pêssego, Baunilha, Pachouly, Chá Branco e Sândalo"),
    ("Ameixa Negra", "Floral frutado gourmand", "Frutas Vermelhas, Violeta, Jasmim, Vanilla e Cedro"),
    ("Amêndoas", "Gourmand", "Castanha do Pará, Jasmim, Bergamota, Sândalo e Baunilha"),
    ("Avelã com Vanilla", "Oriental gourmand", "Amêndoas, Baunilha, Rosas, Chocolate, Vanilla, Violeta e Cedro"),
    ("Baunilha", "Oriental gourmand", "Amêndoas, Melaço, Orquídea, Rosas Brancas, Caramelo, Bergamota e Violeta"),
    ("Canela", "Especiarias", "Especiarias, Vanilla, Anis, Madeiras Nobres e Ylang Ylang"),
    ("Cascas e Folhas", "Amadeirado com especiarias", "Manjericão, Pimenta Rosa, Canela, Pachouly, Bergamota, Cedro, Sândalo, Limão Siciliano e Lavanda"),
    ("Cereja com Avelã", "Floral gourmand", "Chocolate, Cereja, Baunilha, Jasmim e Lírio Branco"),
    ("Chá Branco", "Herbal floral verde", "Lima e Flor de Laranjeira, Bergamota, Limão Siciliano, Jasmim, Violeta, Rosas Brancas, Manjericão, Sândalo e Cedro"),
    ("Dama da Noite", "Floral oriental leve", "Côco, Cravo, Lavanda, Rosas Brancas, Jasmim, Gerânio, Ylang Ylang, Cedro e Baunilha"),
    ("Ervas Frescas", "Herbal intenso", "Alecrim, Manjericão, Lírio Verde, Salvia, Laranja, Jasmim, Framboesa, Caramelo, Calêndula e Cedro"),
    ("Figo", "Frutado verde", "Maçã Verde, Laranja, Manga Verde, Jasmim, Cedro, Sândalo, Baunilha, Amêndoas e Caramelo"),
    ("Flor de Cerejeira", "Floral frutado", "Maçã vermelha, Bambu, canela, laranja, bergamota, Jasmim, Abacaxi, Cedro e Baunilha"),
    ("Flor de Laranjeira", "Floral cítrico", "Bergamota, Limão Siciliano, jasmim, lírio branco e pachouly"),
    ("Flores Brancas", "Floral aromático", "Rosas Brancas, Lírio Branco, Lavanda, Violeta, Cedro, Bergamota, Jasmim e Sândalo"),
    ("Frutas Vermelhas", "Floral frutado", "Bergamota, Rosas Vermelhas, Lichia, Sândalo e baunilha"),
    ("Gengibre", "Amadeirado com especiarias", "Gerânio, Tomilho, Pachouly, Rosas, Limão, Artemísia e Cedro"),
    ("Jasmim", "Floral oriental", "Notas Verdes, Madeiras Nobres, Pimenta Rosa, Rosas, Cravo, Frutas e Pachouly"),
    ("Lavanda Francesa", "Floral doce mentolado leve", "Alecrim, Menta, Lavanda Provence, Canela, Talco, Baunilha e Flor de Laranjeira"),
    ("Lichia", "Frutado floral", "Maçã Madura, Laranja, Melancia, Lavanda, Pêssego, Rosas, Framboesa, Sândalo e Cedro"),
    ("Lima da Pérsia", "Frutado cítrico", "Limão Siciliano, Laranja, Tangerina, Capim Limão, Orquídea, Vanilla, Cedro, Pachouly e Sândalo"),
    ("Limão Siciliano", "Frutado cítrico forte", "Lima Limão, Verbena, Laranja, Rosas, Pachouly e Sândalo"),
    ("Lírio Branco", "Floral adocicado leve", "Lavanda, framboesa, rosa, jasmim, violeta, baunilha e alecrim"),
    ("Maçã com Canela", "Frutado com especiarias", "Maçã madura, Canela, Cravo, Lírio Branco, Cedro e Pachouly"),
    ("Manga e Lírio Branco", "Frutado floral", "Manga Rosa, Lírio Branco, Lichia, Pêssego, Pachouly, Vanilla e Cedro"),
    ("MBaby", "Floral leve talcado", "Lavanda, Bergamota, Flor de Laranjeira, Rosas brancas, Talco e Baunilha"),
    ("Melaço", "Especiarias com fundo oriental", "Orquídea, Frutas Vermelhas, Cereja, Rosas, Cana de Açúcar, Caramelo, Baunilha e Cedro"),
    ("Mirra", "Floral adocicado leve", "Jasmim, Lavanda, Hortelã, Rosa, Gerânio, Bergamota, Cedro, Patchouli e Sândalo"),
    ("Morango com Champanhe", "Frutado gourmand", "Morango, Baunilha, Pêssego, Uva, Jasmim, Mirra e Sândalo"),
    ("Orquídea", "Floral oriental", "Rosas, jasmim, Sândalo, côco, Frutas vermelhas e Baunilha"),
    ("Pinho Silvestre", "Herbal aromático", "Manjericão, Lavanda, Limão, Bergamota, Sálvia, Cravo, Gerânio e Cedro"),
    ("Romã", "Frutado floral", "Jasmim, Canela, Pêssego, Maçã, Maçã Verde e Baunilha"),
    ("Rosas Brancas", "Floral adocicado", "Pêra, Lavanda, Bergamota, Rosas, Jasmim, Gerânio, Lírio Verde e Cedro"),
    ("Sândalo", "Amadeirado oriental leve", "Pachouly, Cedro, Vanilla e Benjoin"),
    ("Vanilla", "Oriental aromático", "Baunilha, Bergamota, Pimenta Rosa e Pachouly"),
    ("Verbena", "Cítrico floral", "Bergamota, Jasmim, Rosas, Cedro e Sândalo"),
]

conexao = banco.conectar()
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    ordem INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    preco NUMERIC(8,2),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS kits (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    itens TEXT,
    descricao TEXT,
    preco NUMERIC(8,2) NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS aromas (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    familia TEXT,
    notas TEXT,
    disponivel BOOLEAN NOT NULL DEFAULT TRUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS faixas_desconto (
    id SERIAL PRIMARY KEY,
    faixa TEXT NOT NULL,
    desconto TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE,
    senha_hash TEXT
)
""")

# Marca se a senha inicial já foi trocada (usada para o aviso de primeiro acesso).
cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS senha_trocada BOOLEAN NOT NULL DEFAULT FALSE")

# Nome do arquivo da foto (ex.: "produtos/flor-rosa.jpg", dentro de static/img). Vazio = sem foto.
cursor.execute("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS imagem TEXT")
cursor.execute("ALTER TABLE kits ADD COLUMN IF NOT EXISTS imagem TEXT")

for ordem, nome in enumerate(CATEGORIAS, start=1):
    cursor.execute(
        "INSERT INTO categorias (nome, ordem) VALUES (%s, %s) ON CONFLICT (nome) DO NOTHING",
        (nome, ordem),
    )

cursor.execute("SELECT COUNT(*) AS n FROM produtos")
if cursor.fetchone()["n"] == 0:
    for categoria, nome, preco, descricao in PRODUTOS:
        cursor.execute(
            """
            INSERT INTO produtos (nome, descricao, categoria_id, preco, estoque)
            VALUES (%s, %s, (SELECT id FROM categorias WHERE nome = %s), %s, %s)
            """,
            (nome, descricao, categoria, preco, ESTOQUE_INICIAL),
        )

cursor.execute("SELECT COUNT(*) AS n FROM kits")
if cursor.fetchone()["n"] == 0:
    for nome, itens, descricao, preco in KITS:
        cursor.execute(
            "INSERT INTO kits (nome, itens, descricao, preco, estoque) VALUES (%s, %s, %s, %s, %s)",
            (nome, itens, descricao, preco, ESTOQUE_INICIAL),
        )

for nome, imagem in FOTOS.items():
    cursor.execute(
        "UPDATE produtos SET imagem = %s WHERE nome = %s AND imagem IS NULL",
        (imagem, nome),
    )

for nome, imagem in FOTOS_KITS.items():
    cursor.execute(
        "UPDATE kits SET imagem = %s WHERE nome = %s AND imagem IS NULL",
        (imagem, nome),
    )

for nome, familia, notas in AROMAS:
    cursor.execute(
        "INSERT INTO aromas (nome, familia, notas) VALUES (%s, %s, %s) ON CONFLICT (nome) DO NOTHING",
        (nome, familia, notas),
    )

cursor.execute("SELECT COUNT(*) AS n FROM faixas_desconto")
if cursor.fetchone()["n"] == 0:
    for faixa, desconto in FAIXAS:
        cursor.execute(
            "INSERT INTO faixas_desconto (faixa, desconto) VALUES (%s, %s)",
            (faixa, desconto),
        )

# O acesso inicial só é criado se ainda não existir nenhum usuário. Assim, se o nome
# "admin" for trocado na conta, um novo deploy não recria um admin com a senha inicial.
cursor.execute("SELECT COUNT(*) AS n FROM usuarios")
if cursor.fetchone()["n"] == 0:
    # O padrão serve só para rodar em casa; em produção defina ADMIN_SENHA no ambiente.
    senha = os.environ.get("ADMIN_SENHA", "admin-so-para-desenvolvimento")
    cursor.execute(
        "INSERT INTO usuarios (nome, senha_hash) VALUES (%s, %s)",
        ("admin", generate_password_hash(senha)),
    )

conexao.commit()
conexao.close()
print("Banco pronto.")
