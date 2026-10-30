# Aelin Velas Aromáticas

Loja virtual com painel de estoque. Python, Flask, Jinja e PostgreSQL (`psycopg2` direto, sem ORM).

## Direitos e uso

© 2026 Aelin Velas Aromáticas. **Todos os direitos reservados.**

O nome e a marca Aelin, o logotipo, os textos, as fotografias, o vídeo e as demais imagens deste repositório
pertencem à Aelin Velas Aromáticas. Não podem ser copiados, reproduzidos, modificados ou usados em outros
sites, lojas ou materiais sem autorização prévia.

O código-fonte está público para consulta. Este repositório não concede licença de uso, cópia, modificação
ou distribuição do projeto, salvo autorização prévia.

Exceção: a pasta `.claude/skills/frontend-design` é material de terceiros, distribuído sob a Apache License 2.0
(o texto da licença está em `.claude/skills/frontend-design/LICENSE.txt`).

Para pedir autorização de uso: Instagram [@aelinvelas](https://instagram.com/aelinvelas).

## Endereço e hospedagem

- **Site:** https://aelinvelas.com.br (o `www` redireciona para o endereço sem `www`, e o `http` para `https`).
- **Hospedagem:** Render (Web Service com Docker + Gunicorn e banco PostgreSQL). Cada `push` na `main` publica sozinho.
- **Domínio:** `aelinvelas.com.br`, registrado no Superdomínio. O certificado HTTPS é emitido e renovado pelo Render.
- **DNS (zona no Superdomínio):**

  | Nome | Tipo | Valor |
  |---|---|---|
  | `@` | A | `216.24.57.1` (IP indicado pelo Render para domínio raiz) |
  | `www` | CNAME | `aelin-velas-aromaticas.onrender.com.` (com o ponto final) |

  Os registros `NS` do domínio não devem ser alterados. No painel do Superdomínio, o valor do CNAME precisa terminar com
  ponto; sem ele o painel acrescenta o domínio ao final e o `www` deixa de funcionar.

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
| `/conta` | logado | início da conta: resumo do estoque e atalhos |
| `/conta/estoque`, `/conta/estoque/kits`, `/conta/estoque/aromas` | logado | painel com +/−, busca e disponibilidade dos aromas |
| `/conta/estoque/novo`, `/conta/estoque/<id>/editar`, `/conta/estoque/<id>/excluir` | logado | cadastro de produtos |
| `/conta/senha`, `/conta/usuario` | logado | trocar a senha e o nome de acesso |
| `/estoque` | todos | endereço antigo, redireciona para `/conta/estoque` |

## Para ajustar depois

- **Quantidades:** o banco começa com 10 unidades de cada item (`ESTOQUE_INICIAL` em `criar_banco.py`). Corrija no painel.
- **Preços em "consulte":** Tulipa, Margarida e Wax melt estão sem preço no catálogo. Edite pelo painel.
- **Fotos de produtos e kits:** coloque os arquivos (`.jpg`, `.png` ou `.webp`) em `static/img/produtos/`.
  No painel (Minha conta > Estoque), escolha a foto de cada produto (Editar) e de cada kit (aba Kits).
  Itens sem foto continuam mostrando o quadro tracejado. Foto nova precisa de commit e push para ir ao ar.
- **Página Sobre:** usa `static/img/marca_vela.mp4` (vídeo sem som, em repetição) e
  `static/img/montagem_sobre_site.jpg`. Para trocar, substitua os arquivos mantendo os nomes.
- **Montagem de fotos na página Velas:** é o arquivo `static/img/velas-conjunto.webp`, fixo em
  `templates/velas.html`. Para trocar, substitua o arquivo mantendo o nome.
- **Produção (Render):** o `Dockerfile` já sobe o site com Gunicorn; o `app.run(debug=True)` só vale ao rodar
  localmente. No Render, defina `DATABASE_URL`, `SECRET_KEY` e `ADMIN_SENHA` com valores próprios e fortes.
  Os valores de reserva que existem no código servem só para testes locais e são públicos.
