# OLX Lite — Especificação do Projeto (Clone de Classificados)

**Disciplina:** Projeto & Prática (ADS)
**Plataformas:** Web (React/Next.js), Mobile (React Native/Expo) e Backend (NestJS + TypeORM + PostgreSQL)
**Visão:** Plataforma de **classificados C2C** para compra e venda locais. Fluxos essenciais: criação de anúncio com fotos e atributos por categoria, busca com filtros e **raio por CEP/lat,lng**, chat privado comprador↔vendedor, favoritos, denúncias e moderação básica. No **MVP não há pagamento/entrega integrados** (negociação via chat).

## 1) Escopo do MVP

**Papéis:** *Usuário* (comprador/vendedor), *Admin*.

### MUST (obrigatório)

- Cadastro/Login (JWT + refresh) e **perfil** com cidade/UF/CEP (opcional lat/lng).
- **Categorias** hierárquicas (ex.: Imóveis, Autos, Eletrônicos, Móveis).
- **Criar anúncio**: título, descrição, preço, estado (novo/usado), localização (CEP/lat,lng), categoria, até **10 fotos**, atributos específicos por categoria.
- **Gerenciar anúncios**: listar, pausar, editar, **marcar vendido**, renovar (repost).
- **Busca & Descoberta**: por texto, filtros (categoria/sub, preço min/max, estado, somente com foto), **raio por CEP/lat,lng**, ordenação (relevância/mais recentes/preço).
- **Chat** comprador↔vendedor (tempo quase real).
- **Favoritos** de anúncios.
- **Denúncia/Report** de anúncio/usuário (motivos pré-definidos).
- **Expiração** automática de anúncios (ex.: 30 dias).

### SHOULD (desejável)

- **Buscas salvas** + alerta in‑app quando surgirem novos anúncios que casem o filtro.
- **Atributos dinâmicos** por categoria (schema administrável).
- Métricas do anúncio: **visualizações** e **contatos iniciados**.
- **Revelar telefone** sob clique (contabiliza).

## 4) Regras de Negócio

- **Publicação:** título (≥ 10 chars), preço ≥ 0, categoria e **≥ 1 foto** obrigatórios.
- **Atributos por categoria:** respeitar `required` e validação (min/max, opções).
- **Expiração:** `expires_at = created_at + 30 dias`; job diário marca `expired`.
- **Renovar/Repost:** cria novo `created_at` (pode mudar id ou manter histórico em `ad_history`).
- **Chat:** inicia apenas se anúncio `active`; vendedor pode **bloquear** chat/usuário.
- **Ordenação (feed):** `spotlight` > `bump` recente > `created_at desc` (dentro dos filtros).
- **Denúncia:** após N denúncias (ex.: 3), anúncio vira `pending_review` até moderação.
- **Revelar telefone:** sob clique; incrementa `contact_clicks`.
- **Limites anti‑spam:** throttle em criação/edição de anúncios e início de chats.

## 6) Telas & Fluxos

### Web 

- **Home/Busca:** campo de busca, categorias, filtros rápidos, selecionar localização (CEP ou detectar), paginação/infinite scroll.
- **Detalhe do Anúncio:** carrossel de fotos, preço, atributos, descrição, localização no mapa, botões **Chat** e **Mostrar Telefone**.
- **Criar/Editar Anúncio:** passo‑a‑passo (categoria → básicos → atributos → fotos → localização → revisão).
- **Meus Anúncios:** status, métricas (views, contatos, favoritos), pausar/editar/renovar/marcar vendido.
- **Chat:** lista e mensagens em tempo quase real.
- **Favoritos & Buscas Salvas:** gerenciar e aplicar rapidamente.

### Mobile 

- **Feed por proximidade** (raio configurável), filtros, favoritos.
- **Detalhe:** carrossel, ação de chat/telefone.
- **Novo Anúncio:** captura de câmera, compressão, salvamento de rascunho offline (AsyncStorage).
- **Chat:** push local simulada, confirmação de leitura.
- **Perfil:** meus anúncios e configurações.

## 7) Critérios de Aceitação (Gherkin)

**Criar Anúncio**
*Given* selecionei “Eletrônicos > Celulares”
*When* preencho título, preço, CEP e adiciono 3 fotos
*Then* o anúncio é criado como `active`
*And* expira em 30 dias
*And* atributos obrigatórios da categoria são validados.

**Busca por Raio**
*Given* informei CEP do Recife
*When* defino raio de 10 km e filtro “somente com foto”
*Then* recebo anúncios `active` dentro do raio
*And* ordenados por mais recentes, com paginação.

**Chat**
*Given* estou no detalhe de um anúncio `active`
*When* clico em “Chat com vendedor” e envio mensagem
*Then* a conversa aparece para o vendedor em ≤ 3s
*And* novas mensagens chegam em tempo quase real.

**Pausar/Vendido**
*Given* um anúncio meu `active`
*When* marco como `sold`
*Then* ele some dos resultados e o chat não aceita novas mensagens.

**Denúncia**
*Given* um anúncio que infringe regras
*When* envio denúncia com “fraude”
*Then* o anúncio entra em `pending_review` após atingir 3 denúncias
*And* o Admin pode revisar e remover.

**Busca Salva**
*Given* salvei “Móveis > Mesa, preço ≤ 500, raio 5 km”
*When* surge novo anúncio que atende ao filtro
*Then* recebo notificação in‑app e vejo destaque na lista.

## 11) Checklist de Aceite Final

- Fluxo completo **usuário (login → criar anúncio → aparecer no feed) → outro usuário (buscar por raio → abrir chat) → vendedor (pausar/vendido) → admin (moderar)** demonstrável em vídeo ≤ 5 min.
- README com `docker compose up`, `.env.example`, `seed` e credenciais de teste.
- Todos os **MUST** entregues em Web, Mobile e Backend.