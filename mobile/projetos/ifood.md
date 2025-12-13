# Projeto Específico — **iFood Lite (Clone de Delivery)**

> **Visão:** Marketplace de comida com três apps/superfícies: **Cliente** (Web + Mobile RN), **Restaurante** (Web/Portal) e **Entregador** (Mobile RN). Fluxos principais: descoberta de restaurantes por geolocalização, cardápio, carrinho, checkout com frete e pagamento **simulado**, roteamento do pedido (restaurante ↔ entregador ↔ cliente), rastreio em tempo real e avaliações pós‑entrega.

## 1) Escopo (MVP Essencial)

**Papéis:** *Cliente*, *Restaurante*, *Entregador*, *Admin*.

**MUST (obrigatório)**

- **Geo & Descoberta:** listagem de restaurantes próximos (raio por CEP/lat,lng) com filtros (cozinha, taxa de entrega, tempo estimado, aberto/agora).
- **Cardápio:** categorias, itens, opcionais/adicionais (modifiers), variações (ex.: tamanho), combos.
- **Carrinho & Checkout:** endereço, cálculo de frete (simulado por distância), tempo estimado, cupom (simples), pagamento simulado (pix/cartão).
- **Pedido:** pipeline `created → accepted → preparing → ready_for_pickup → picked_up → delivering → delivered` (ou `cancelled`).
- **Rastreamento:** atualizações em tempo quase real (WS/polling), mapa com posição do entregador (simulada).
- **Restaurante (Portal):** aceitar/recusar pedidos, definir tempo de preparo, atualizar status, gerenciar cardápio e horários.
- **Entregador (App):** ficar online/offline, aceitar corrida, ver rota, marcar retirado/entregue.
- **Avaliações:** do restaurante e do entregador após `delivered`.

**SHOULD (desejável)**

- Múltiplos endereços do cliente; favoritos; histórico de pedidos e repetição de pedido.
- Notificações in‑app (e push simulada no mobile).
- Admin: CRUD de categorias de cozinha, auditoria de pedidos/cancelamentos.



## 2) Regras de Negócio

- **Aberto/Fechado:** `is_open = within(restaurant_hours)`; pedidos só podem ser criados quando aberto (exceto agendados).
- **Frete (simulado):** `delivery_fee = base_delivery_fee + (fee_per_km * distancia_km) * surge_multiplier`.
- **ETA (estimativa):** `eta_min = avg_prep_minutes + (distancia_km / velocidade_media_km_h * 60)` (velocidade média configurável, ex.: 20 km/h).
- **Pagamento:** motor simulado (`pending → paid/refused`) com probabilidade de aprovação ajustável; estorno lógico em caso de cancelamento.
- **Roteamento:** ao `accepted`, cria‑se oferta para entregadores online num raio; primeiro a aceitar assume `delivery_assignments`.
- **Cancelamento:**
  - Cliente pode cancelar até status `preparing` (sem custo).
  - Restaurante pode cancelar por indisponibilidade; cliente é notificado.
  - Sistema cancela automático se sem aceitação por entregador em X minutos.
- **Avaliações:** liberadas após `delivered`; média atualizada incrementalmente.
- **Comissão/Repasse (simulado):** `platform_fee = total * 0.10` (exemplo); sem necessidade de integração bancária no MVP.

## 3) Telas & Fluxos (Cliente Web/Mobile)

- **Home:** endereço atual (CEP/GPS), restaurantes abertos, filtros por cozinha, taxa, tempo; busca textual.
- **Restaurante:** cardápio com grupos e opcionais, resumo de carrinho fixo, calculadora de frete/ETA.
- **Checkout:** endereço (CRUD), cupom, método de pagamento (simulado), resumo e confirmação.
- **Pedido:** timeline de status, mapa com posição do entregador (mock), chat simples opcional.
- **Histórico/Favoritos:** reordenar pedido; listar restaurantes favoritos.

## 4) Telas & Fluxos (Portal do Restaurante)

- **Pedidos em tempo real:** fila por status; aceitar/definir tempo; mover para `preparing` e `ready_for_pickup`.
- **Cardápio:** CRUD de itens, grupos de opcionais e horários de funcionamento.
- **Métricas básicas:** pedidos/dia, ticket médio, avaliação média.

## 5) Telas & Fluxos (App do Entregador RN)

- **Dashboard:** ficar online; ver ofertas próximas com distância estimada, valor do frete e restaurante.
- **Fluxo de entrega:** aceitar → navegar até o restaurante → marcar `picked_up` → navegar até cliente → `delivered`.
- **Perfil:** histórico de entregas e avaliação média.

## 6) Critérios de Aceitação (Gherkin)

**Geo‑busca**
*Given* que estou com endereço em Recife (lat/lng)
*When* abro a tela inicial
*Then* vejo restaurantes abertos em um raio de 5 km
*And* consigo filtrar por “Pizza” e ordenar por `eta`.

**Carrinho com opcionais**
*Given* um item “Hambúrguer” com grupo “Adicionais” (min=0, max=2)
*When* escolho queijo e bacon
*Then* o preço do item reflete os `price_delta` e o subtotal do carrinho é atualizado sem recarregar.

**Checkout & Pagamento**
*Given* um pedido válido
*When* finalizo com método `pix`
*Then* o motor marca `payment_status=paid` (80% de aprovação simulada)
*And* o status do pedido muda para `accepted` no portal do restaurante em ≤ 3s.

**Roteamento para entregador**
*Given* entregadores online num raio de 3 km
*When* o pedido entra em `ready_for_pickup`
*Then* a oferta aparece no app do entregador
*And* ao aceitar, cria‑se `delivery_assignments` e o cliente vê o mapa atualizado.

**Rastreamento & Entrega**
*Given* um pedido `delivering`
*When* o entregador marca `delivered`
*Then* o cliente recebe notificação e pode avaliar restaurante e entregador.

**Cancelamento por SLA**
*Given* um pedido `created`
*When* não for aceito pelo restaurante em 5 minutos
*Then* o sistema cancela e notifica o cliente com estorno lógico do pagamento.

## 7) Checklist de Aceite Final

- Fluxo completo **cliente (descoberta → cardápio → checkout) → restaurante (aceita/prepara) → entregador (retira/entrega) → avaliação** demonstrável em vídeo ≤ 5 min.
- README com `docker compose up`, `.env.example`, contas de teste, `seed`, prints/gifs.
- Todos os **MUST** entregues nas três frentes (Cliente, Restaurante, Entregador).