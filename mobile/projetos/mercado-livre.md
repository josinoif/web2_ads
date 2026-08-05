# Projeto Específico — **ML Lite (Clone do Mercado Livre)**

> **Visão:** Aplicação full‑stack (Web + Mobile + API) que replica o núcleo do Mercado Livre: catálogo com busca/filtragem, página de produto, perguntas & respostas, compra (carrinho/“comprar agora”), pedidos com frete simulado, avaliações pós‑entrega e área do vendedor para cadastro e gestão de produtos.

## 1) Escopo (MVP Essencial)

**Papéis:** *Visitante*, *Comprador*, *Vendedor*, *Admin*.

**MUST (obrigatório)**

- Autenticação (cadastro, login, JWT+refresh).
- Catálogo de produtos com busca por texto e filtros (categoria, preço, ordem por relevância/preço/data).
- Página de produto com galeria de imagens, especificações, cálculo de frete simulado por CEP, perguntas e respostas públicas.
- Carrinho (adicionar/remover/alterar quantidade) **e** fluxo “Comprar Agora”.
- Checkout: endereço de entrega, cotação de frete (Econômico/Rápido), pagamento **simulado** (cartão/pix), criação de pedido.
- Pedidos com status (created → paid → shipping → delivered → completed/cancelled).
- Avaliação do produto/pedido (nota 1–5 + comentário) após *delivered*.
- Área do Vendedor: CRUD de produtos (status *active/inactive*), estoque, preço, fotos.
- Favoritos/Wishlist (salvar produto).
- Q&A: comprador pergunta, vendedor responde; moderação simples.

**SHOULD (desejável)**

- Notificações in‑app (badge/lista) para respostas, mudanças de status e confirmações.
- Histórico de buscas e produtos vistos recentemente (localStorage/AsyncStorage).
- Admin: CRUD de categorias; moderação de denúncias básicas.

## 2) Regras de Negócio

- **Estoque:** decrementa ao pagar; se pagamento for recusado/cancelado, repõe.
- **Frete simulado por CEP:** fórmula base sem integração externa:
  - *Econômico*: `base 12.90 + (peso_total_kg * 2.50) + (UF != 'PE' ? 5.00 : 0)`
  - *Rápido*: `base 22.90 + (peso_total_kg * 3.50) + (UF != 'PE' ? 8.00 : 0)`
  - Peso total padrão do produto = 0.5 kg (campo opcional `weight_kg` no produto).
- **Pagamento:** simulado via motor interno: `pending → paid` (80% de aprovação aleatória controlada) ou `refused`.
- **Pedidos:** somente o vendedor muda para *shipping*; *delivered* pode ser confirmado pelo comprador.
- **Q&A:** vendedor só responde perguntas `pending`; após resposta, status `answered`.

## 3) Telas & Fluxos (Web)

- **Home/Catálogo:** busca, categorias, filtros (preço min/max, ordem), paginação infinita.
- **Produto:** título, preço, imagens, cálculo de frete por CEP, perguntas/respostas, botão Favoritar, **Comprar Agora** e **Adicionar ao Carrinho**.
- **Carrinho:** itens, subtotal, estimativa de frete, atualizar quantidades, seguir para checkout.
- **Checkout:** seleção/CRUD de endereço, opção de frete, pagamento simulado, resumo, confirmação.
- **Pedidos (comprador):** lista + detalhes (itens, status, tracking, ação confirmar entrega, avaliar).
- **Vendedor:** lista de produtos, criar/editar (fotos), pausar/ativar, estoque, pedidos recebidos com ação de envio.
- **Admin:** categorias; moderação simples (opcional).

## 4) Telas & Fluxos (Mobile RN)

- **Catálogo & Produto:** iguais ao web (layout mobile‑first).
- **Q&A:** enviar pergunta e ver respostas; notificação local quando respondida (simulada).
- **Carrinho/Checkout:** simplificado; persistência leve em AsyncStorage; reuso dos contratos da API.
- **Pedidos:** acompanhar status e confirmar entrega; avaliar produtos.
- **Navegação:** tabs (Home, Favoritos, Pedidos, Perfil) + stacks para detalhes/checkout.

## 5) Critérios de Aceitação

**Busca e Filtro**
*Given* que existem produtos nas categorias “Celulares” e “Informática”
*When* eu busco por "iPhone" e filtro categoria “Celulares” ordenando por `price_desc`
*Then* recebo uma lista paginada apenas de “Celulares” contendo “iPhone” no título/descrição
*And* a primeira página retorna ≤ 1.5s em ambiente de dev.

**Cálculo de Frete**
*Given* estou na página de um produto com `weight_kg=1`
*When* informo CEP de UF diferente de “PE”
*Then* vejo opções `Econômico` e `Rápido` com valores calculados pela fórmula definida
*And* o valor total do pedido no checkout reflete a opção selecionada.

**Adicionar ao Carrinho**
*Given* estou autenticado
*When* adiciono 2 unidades do produto X
*Then* o carrinho exibe X com `qty=2` e subtotal atualizado sem recarregar a página.

**Comprar Agora**
*Given* estou na página do produto X
*When* clico em “Comprar Agora”
*Then* sou levado ao checkout com X pré‑carregado
*And* consigo concluir o pedido ao selecionar endereço, frete e pagamento simulado.

**Pagamento Simulado**
*Given* finalizei o checkout com método `card`
*When* o motor de pagamento processa
*Then* o pedido muda para `paid` em ≤ 3s com probabilidade de aprovação configurável
*And* em caso de `refused`, recebo mensagem e o estoque não é decrementado.

**Envio & Entrega**
*Given* um pedido `paid`
*When* o vendedor informa `tracking_code` e muda status para `shipping`
*Then* o comprador vê o novo status
*And* ao confirmar entrega, o status vira `delivered` e habilita avaliação.

**Avaliação**
*Given* um pedido `delivered`
*When* avalio com `rating=5` e comentário
*Then* a avaliação fica vinculada ao produto e visível publicamente.

**Q&A**
*Given* uma pergunta `pending` no produto do vendedor
*When* o vendedor responde
*Then* o status vira `answered` e a resposta aparece abaixo da pergunta.

**Área do Vendedor**
*Given* que sou vendedor
*When* crio um produto com título, preço, estoque e imagens
*Then* o produto fica `active` e aparece nas buscas após indexação (imediata no MVP).

**Favoritos**
*Given* estou vendo um produto
*When* clico em “❤ Favoritar”
*Then* o item aparece na minha lista de favoritos e o estado persiste entre sessões.

## 6) Checklist de Aceite Final

- Todos os **MUST** cumpridos nas três plataformas.

- Fluxo completo **guest → login → busca → produto → frete → compra → pedido → entrega → avaliação** demonstrável em vídeo ≤ 5 min.

  