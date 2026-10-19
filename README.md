# Aelin Velas Aromáticas

Loja virtual com painel de estoque. Python, Flask, Jinja e PostgreSQL (`psycopg2` direto, sem ORM).

## Estrutura

```
AELIN/
├── app.py             rotas da loja, login e painel de estoque
├── banco.py           funções de acesso ao PostgreSQL
├── criar_banco.py     cria as tabelas e carrega o catálogo do PDF
├── requirements.txt
├── templates/         base, index, sobre, aromas, login, estoque, produto_form, excluir, _macros
└── static/style.css   visual da marca (verde, dourado e pergaminho)
```

## Primeira execução (PyCharm)

1. **Instalar as bibliotecas:** clique em "Install requirements" na faixa do `requirements.txt`
   (ou, no terminal do PyCharm: `pip install -r requirements.txt`).
2. **Criar o banco vazio** no pgAdmin: botão direito em *Databases → Create → Database*, nome `aelin`.
3. **Variáveis de ambiente.** Em *Run → Edit Configurations*, para `app.py` **e** para `criar_banco.py`,
   preencha o campo *Environment variables*:

   ```
   DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/aelin;SECRET_KEY=uma-frase-longa-e-aleatoria;ADMIN_SENHA=escolha-a-senha-do-painel
   ```

4. **Criar as tabelas:** execute `criar_banco.py` uma vez (botão direito → Run). Ele é seguro para rodar de novo.
5. **Rodar o site:** execute `app.py` e abra http://127.0.0.1:5000
6. **Entrar no painel:** http://127.0.0.1:5000/login com usuário `admin` e a senha de `ADMIN_SENHA`.

## O que cada página faz

| Rota | Quem acessa | O que mostra |
|---|---|---|
| `/` | todos | capa e atalhos para as demais páginas |
| `/sobre` | todos | sobre a marca |
| `/velas` | todos | velas de 20g a 100g |
| `/produtos` | todos | flores aromáticas, aromatizadores, escalda-pés, wax melt e sachê |
| `/kits` | todos | kits Aelin |
| `/aromas` | todos | aromas por família (`?familia=Floral`) |
| `/descontos` | todos | descontos progressivos |
| `/pedido` | todos | como fazer o pedido, WhatsApp e Instagram |
| `/login`, `/logout` | todos | entrada e saída do painel |
| `/estoque`, `/estoque/kits`, `/estoque/aromas` | logado | painel com +/−, busca e disponibilidade dos aromas |
| `/estoque/novo`, `/estoque/<id>/editar`, `/estoque/<id>/excluir` | logado | cadastro de produtos |

## Para ajustar depois

- **Quantidades:** o banco começa com 10 unidades de cada item (`ESTOQUE_INICIAL` em `criar_banco.py`). Corrija no painel.
- **Preços em "consulte":** Tulipa, Margarida e Wax melt estão sem preço no catálogo. Edite pelo painel.
- **Fotos:** os quadros tracejados são espaços reservados. Coloque as imagens em `static/img/` e troque
  o quadro por `<img src="/static/img/arquivo.jpg" alt="...">`.
- **Antes de publicar:** troque `app.run(debug=True)` por um servidor de produção (por exemplo Gunicorn),
  use uma `SECRET_KEY` nova e uma senha forte para o admin.
