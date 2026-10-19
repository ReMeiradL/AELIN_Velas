# Instruções do projeto — Aelin Velas Aromáticas

Loja virtual didática com painel de estoque: Python, Flask, Jinja e PostgreSQL.

## Regras obrigatórias

- Use apenas Python, Flask, Jinja, HTML, CSS e `psycopg2` direto.
- Não use ORM, JavaScript, API separada, framework CSS novo ou bibliotecas extras.
- Todo SQL com dados do usuário usa placeholders `%s` (nunca formatação de string).
- Siga a estrutura atual do projeto: `app.py`, `banco.py`, `criar_banco.py`, `templates/` e `static/`.
- Implemente somente a operação pedida; não "aproveite" para refatorar o resto.
- Preserve os nomes e o estilo que já existem no projeto.
- Segredos (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_SENHA`) vêm de variáveis de ambiente; nunca escreva senhas no código.
- Depois de editar, informe quais arquivos foram alterados e liste os testes manuais que o usuário deve executar.
- Nunca diga que terminou sem antes conferir a sintaxe e explicar o diff em linguagem simples.
- Não execute testes funcionais que alterem o banco `aelin` (rodar o servidor, chamar rotas com curl, ou inserir/apagar produtos via terminal). Confira apenas a sintaxe (ex.: `py_compile`) e deixe os testes manuais no navegador para o usuário.
