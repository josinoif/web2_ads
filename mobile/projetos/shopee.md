# Shopee Lite — Especificação do Projeto (Clone de Marketplace)

**Disciplina:** Projeto & Prática (ADS)
**Plataformas:** Web (React/Next.js), Mobile (React Native/Expo) e Backend (NestJS + TypeORM + PostgreSQL)
**Visão:** Marketplace **C2C/B2C** com foco em preço baixo e promoções: catálogo com busca/filtragem, lojas de vendedores, carrinho, checkout com **frete simulado**, **vouchers** (da loja e da plataforma), **coins** (gamificação leve) e acompanhamento de pedidos ponta‑a‑ponta.

> **MVP:** Pagamento e logística **simulados**; sem live commerce e sem split real de pagamentos.

## 1) Escopo do MVP

**Papéis:** *Comprador*, *Vendedor (Loja)*, *Admin*.

### MUST (obrigatório)

- **Autenticação** (registro, login, JWT + refresh) e **perfil** com endereços.
- **Catálogo & Busca:** categorias, subcategorias, filtros (preço min/max, frete grátis elegível, avaliação, loja oficial), ordenação (relevância/mais vendidos/preço asc/desc/novidades).
- **Produto com variações** (SKU): cor/tamanho/etc., estoque por variação, galeria de imagens, descrição rica.
- **Loja do vendedor:** vitrine, avaliação média, políticas (envio/troca), listagem de produtos.
- **Carrinho** com múltiplas lojas; **cálculo de frete** por loja (simulado por CEP/distância/peso).
- **Checkout** com aplicação de **vouchers** (plataforma/loja), regras de acumulação e **coins** (resgate parcial).
- **Pedido** multi‑loja (split lógico): `created → paid → packing → shipped → delivered → completed/cancelled`.
- **Avaliações** (produto e loja) após `delivered` com nota (1–5) + comentário.
- **Q&A** por produto (perguntas públicas, resposta do vendedor).
- **Vendedor (Seller Center):** CRUD de produtos/variações, estoque, preço promocional, processamento de pedidos (packing/shipped).
- **Notificações** in‑app (status do pedido, resposta de Q&A, voucher aplicado).

### SHOULD (desejável)

- **Vouchers**: por loja (ex.: R$ 10 acima de R$ 100) e da plataforma (ex.: 10% off até R$ 20); **frete grátis** com teto e mínimo de compra.
- **Coins:** ganhar por compra concluída (ex.: 1% do subtotal) e **resgatar** no checkout (ex.: 100 coins = R$ 1).
- **Favoritos:** produto e loja; **seguir loja** (feed simples da loja).
- **Flash Deals** (janela de promoções com estoque limitado).

## 2) Regras de Negócio

- **Variações & Estoque:** estoque é controlado por **variant**; decrementa ao `paid`; se `refused/cancelled`, repõe.
- **Frete (simulado por loja):** `shipping_cost = base 9.90 + (peso_total_kg * 2.00) + (UF != "PE" ? 5.00 : 0)` por **order_partition**.
- **Free Shipping Voucher:** aplica `shipping_cost = 0` até `max_discount` e **apenas se** `subtotal >= min_order_value`.
- **Vouchers (stacking):** `platform` e `store` **podem** acumular se `stacking=with_coins`; **nunca** dois `platform` simultâneos.
- **Coins:** ganho = `round(subtotal * 0.01)`; resgate no checkout (ex.: 100 coins = R$ 1), limitados a **até 10%** do subtotal.
- **Flash Deal:** usa `deal_price` enquanto houver estoque da promo e janela ativa.
- **Split Lógico do Pedido:** um `order` agrega múltiplas lojas via `order_partitions` com status independentes.
- **Cancelamento:** comprador pode cancelar até `packing`; vendedor pode cancelar antes de `shipped`.
- **Avaliações:** liberadas após `delivered` por `order_partition` (produto e loja).
- **Q&A:** só em produto `active`; vendedor apenas responde `pending`.

## 3) Telas & Fluxos

### Comprador — Web/Mobile

- **Home:** busca, categorias, carrossel de campanhas, seção “Frete Grátis”, **Flash Deals**.
- **Produto:** fotos, variações (seleção gera preço/estoque), cálculo de frete, Q&A, reviews, **Adicionar ao Carrinho** e **Comprar Agora**.
- **Carrinho:** agrupado por loja, resumo de vouchers por loja e da plataforma, estimativas de frete por loja.
- **Checkout:** endereço, escolher frete por loja, aplicar vouchers/coins, resumo e confirmação.
- **Pedidos:** lista/detalhe com timeline por **partition** e tracking; ação “confirmar entrega”.
- **Perfil:** coins, vouchers salvos, favoritos, lojas seguidas.

### Vendedor — Seller Center (Web)

- **Pedidos em tempo real:** filas `created/paid` → ação `packing/shipped`; tracking.
- **Produtos:** CRUD, variações, preço promocional/flash deal, estoque.
- **Loja:** banner, políticas, resposta a Q&A, métricas (vendas, avaliação).

### Admin (básico)

- **Categorias**, **vouchers de plataforma**, inspeção de métricas e moderação leve.

## 4) Critérios de Aceitação (Gherkin)

**Variação & Preço**
*Given* um produto com variantes (Cor: Preto/Branco; Tamanho: M/G)
*When* seleciono Preto + G
*Then* vejo preço e estoque correspondentes e posso adicionar ao carrinho.

**Voucher & Coins no Checkout**
*Given* subtotal de R$ 200 e voucher `LOJA10` (R$ 10 off mín. R$ 100)
*When* aplico o voucher e resgato 200 coins (R$ 2)
*Then* o desconto total é R$ 12 e o total final é atualizado
*And* os coins resgatados não ultrapassam 10% do subtotal.

**Frete por Loja**
*Given* itens de 2 lojas diferentes no carrinho
*When* avanço ao checkout
*Then* recebo opções de frete separadas por loja e o total considera a soma dos fretes.

**Pedido & Split Lógico**
*Given* finalizei um pedido com 2 lojas
*When* uma loja marca `shipped` e a outra ainda está `packing`
*Then* vejo timelines independentes
*And* posso avaliar cada loja/produto após suas respectivas entregas.

**Q&A**
*Given* uma pergunta `pending` em um produto
*When* o vendedor responde
*Then* o status vira `answered` e a resposta aparece para todos os compradores.

**Flash Deal**
*Given* um variant em flash deal (estoque 10, janela ativa)
*When* tento comprar 12 unidades
*Then* o sistema limita a 10 na condição de promoção
*And* excedente usa preço normal (ou bloqueia, conforme política de campanha).

## 5) Checklist de Aceite Final

- Fluxo completo **comprador (busca → variações → carrinho multi‑loja → vouchers/coins → pedido) → vendedor (packing/shipped) → avaliações** demonstrável em vídeo ≤ 5 min.
- README com `docker compose up`, `.env.example`, `seed` e contas de teste.
- Todos os **MUST** entregues em Web, Mobile e Backend.