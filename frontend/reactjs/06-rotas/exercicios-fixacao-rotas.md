# Exercícios de fixação — Rotas no frontend (React Router v7)

Em SPA, a URL é contrato com o usuário: favoritos, “voltar” do navegador e compartilhamento de link só funcionam bem quando as rotas estão corretas. Estes exercícios fixam o que você viu em `rotas-frontend.md` e `tutorial-rotas.md`: `BrowserRouter`, rotas aninhadas, `Link`/`NavLink`, `Outlet`, `useParams`, `useNavigate`, 404 e rotas protegidas.

> **Como usar:** use um único projeto Vite + React 19 com `react-router-dom` v7, como no tutorial. Teste sempre digitando a URL na barra de endereço, não só clicando em links.

**Formato de cada exercício:** leia **O que fazer** e confira com **Definição de pronto**. Se todos os itens da definição de pronto forem verdadeiros, o exercício está feito.

---

## Nível 1 — SPA e primeiras rotas

**Objetivo:** perceber que navegar sem recarregar a página é regra, não exceção.

### 1. O que muda numa SPA?

**O que fazer**

Em **uma ou duas frases**, explique por que, numa SPA com React Router, clicar em um `<Link to="...">` costuma **não** recarregar a página inteira como um `<a href="...">` tradicional faria.

**Definição de pronto**

- [ ] A resposta menciona que a navegação fica a cargo do JavaScript/Router (History API) em vez de um novo pedido HTML completo da página.

**Fixação:** Router + `Link` preservam estado na memória e tornam a troca de “tela” instantânea.

---

### 2. Três páginas irmãs sem layout

**O que fazer**

1. Envolva o app com `BrowserRouter`.
2. Dentro de `Routes`, defina **três** rotas no **mesmo nível** (sem aninhar ainda):
   - `/` → componente `Home` com título “Home”;
   - `/sobre` → `Sobre` com título “Sobre”;
   - `/contato` → `Contato` com título “Contato”.
3. Em cada página, coloque um `<Link>` para as **outras duas** rotas (texto livre, mas o `to` deve estar correto).

**Definição de pronto**

- [ ] A URL no navegador muda para `/`, `/sobre` e `/contato` ao navegar.
- [ ] Não há erro no console ao alternar entre as três páginas.

---

### 3. Rota curinga acidental

**O que fazer**

1. Sem adicionar `path="*"` ainda, acesse manualmente uma URL que **não** existe (ex.: `/xyz`).
2. Anote o que o React Router mostra (tela em branco, mensagem padrão, etc.).
3. Em **uma frase**, diga por que centralizar rotas e ter uma rota 404 explícita ajuda o usuário.

**Definição de pronto**

- [ ] Você observou o comportamento real do app antes de responder (não só “chute teórico”).
- [ ] A frase final faz sentido para quem nunca viu SPA.

---

## Nível 2 — Layout, Outlet e NavLink

**Objetivo:** um shell comum (menu) e conteúdo que muda.

### 4. Layout com `Outlet`

**O que fazer**

1. Crie um componente `Layout` com um `<header>` ou `<nav>` fixo contendo o texto **“Meu App”** e, abaixo, um `<Outlet />`.
2. Reorganize as rotas do exercício 2 para ficarem **filhas** de `<Route path="/" element={<Layout />}>`:
   - rota **index** → `Home`;
   - `sobre` → `Sobre`;
   - `contato` → `Contato`.
3. Remova navegação duplicada das páginas se ficar redundante **ou** mantenha links mínimos — mas o menu principal deve estar no `Layout`.

**Definição de pronto**

- [ ] “Meu App” permanece visível ao mudar entre Home, Sobre e Contato.
- [ ] Os paths na URL são `/`, `/sobre` e `/contato` (paths relativos ao pai, como no tutorial).

---

### 5. `NavLink` com estado ativo

**O que fazer**

1. No `Layout`, troque os `<Link>` do menu por `<NavLink>` para Home, Sobre e Contato.
2. Use a prop `className` como função `({ isActive }) => ...` **ou** `style` equivalente para que o link da rota atual tenha aparência **visivelmente** diferente (cor ou negrito).
3. Na rota Home, use `end` no `NavLink` para `/` (como no tutorial), para que `/sobre` não deixe Home como “ativa” por engano.

**Definição de pronto**

- [ ] Ao estar em `/sobre`, apenas o link “Sobre” aparece como ativo.
- [ ] Em `/`, apenas Home aparece ativa (não todas de uma vez).

**Fixação:** `end` evita que o prefixo `/` coincid com todas as URLs.

---

### 6. Link relativo vs absoluto

**O que fazer**

1. Dentro da página `Contato`, adicione um `<Link to="sobre">` **sem** barra inicial e um `<Link to="/sobre">` **com** barra inicial.
2. Teste os dois cliques partindo de `/contato` e anote para onde cada um leva (URL final na barra). Se um deles abrir 404 ou um path inesperado, **não corrija antes de registrar** — isso faz parte do aprendizado.
3. Escreva **duas frases** explicando a diferença entre `to="sobre"` e `to="/sobre"` neste app, com base no que você observou.

**Definição de pronto**

- [ ] Você descreveu corretamente o destino de cada link após o teste.
- [ ] A explicação menciona path relativo ao segmento atual vs path absoluto a partir da raiz.

---

## Nível 3 — Parâmetros e navegação programática

**Objetivo:** URLs dinâmicas e `navigate` quando o link sozinho não basta.

### 7. Parâmetro na URL (`useParams`)

**O que fazer**

1. Crie a rota `usuario/:id` aninhada sob o mesmo `Layout` do exercício 4.
2. Página `Usuario` que usa `useParams()` para ler `id` e exibe: **“Perfil do usuário: {id}”**.
3. No menu do `Layout`, adicione um link para `/usuario/1` e outro para `/usuario/42`.
4. Digite diretamente na barra `/usuario/999` e confira se o número aparece.

**Definição de pronto**

- [ ] `1`, `42` e `999` aparecem corretamente na frase da página.
- [ ] Nenhum uso de `window.location` manual para “mudar” a rota — só Router + links ou navegação do tutorial.

---

### 8. Navegação após ação (`useNavigate`)

**O que fazer**

1. Na página `Usuario`, adicione um botão **“Ir para Home”** que chama `navigate('/')` (hook `useNavigate`).
2. Adicione outro botão **“Voltar”** que chama `navigate(-1)` (histórico do navegador).
3. Teste: entre em `/sobre` → vá para `/usuario/5` → clique “Voltar” e confira se retorna a `/sobre`.

**Definição de pronto**

- [ ] “Ir para Home” sempre leva a `/`, independentemente de onde você estava antes.
- [ ] “Voltar” usa o histórico real (`-1`), não um path fixo inventado.

**Fixação:** `useNavigate` é ideal após login, submit ou wizard.

---

### 9. Lista → detalhe com mesma base de path

**O que fazer**

1. Crie rotas `posts` (lista) e `posts/:postId` (detalhe), ambas sob o `Layout`.
2. `ListaPosts` mostra pelo menos três links `<Link to={...}>` para `/posts/1`, `/posts/2`, `/posts/3` (pode ser lista fixa).
3. `PostDetalhe` lê `postId` com `useParams` e mostra “Post #{postId}”.
4. Garanta que `/posts` não quebre e que `/posts/2` mostre o id certo.

**Definição de pronto**

- [ ] A partir da lista, dá para ir ao detalhe e a URL reflete o id.
- [ ] Recarregar a página no detalhe mantém o mesmo `postId` na tela.

---

## Nível 4 — 404, redirecionamento e rotas protegidas

**Objetivo:** URLs inválidas e áreas restritas com contrato claro.

### 10. Página 404

**O que fazer**

1. Crie a página `NaoEncontrada` com título claro (ex.: “404”) e um `<Link to="/">` para a Home.
2. Dentro do `Route` do `Layout`, adicione **por último** entre os filhos uma rota `path="*"` apontando para `NaoEncontrada`.
3. Acesse `/pagina-que-nao-existe` e confirme a 404.

**Definição de pronto**

- [ ] Qualquer path não mapeado sob o layout mostra `NaoEncontrada`.
- [ ] Rotas válidas (`/`, `/sobre`, etc.) **não** caem na 404.

**Fixação:** a ordem importa: `*` por último entre os irmãos.

---

### 11. Redirecionamento com `<Navigate />`

**O que fazer**

1. Crie a rota `/painel` que **deveria** ser privada (você protegerá no próximo exercício).
2. Por enquanto, crie uma rota `/legacy` que **sempre** redireciona para `/contato` usando `<Navigate to="/contato" replace />`.
3. Acesse `/legacy` e verifique URL final e histórico (substituição com `replace`).

**Definição de pronto**

- [ ] Abrir `/legacy` termina em `/contato` sem precisar clicar em nada.
- [ ] O uso de `replace` está presente se você quis evitar um passo “fantasma” no botão voltar (confira no navegador).

---

### 12. Rota protegida simples

**O que fazer**

1. Simule autenticação com estado **no topo do app** ou com o `AuthContext` do módulo 05 (qualquer uma, desde que funcione): `usuario` null ou `{ nome }`.
2. Crie componente `RotaProtegida` que recebe `children`: se **não** houver usuário, renderize `<Navigate to="/login" replace />`; senão renderize `children`.
3. Páginas mínimas: `/login` com botão “Entrar” que define um usuário fake; `/painel` protegida mostrando “Bem-vindo ao painel”.
4. Logout deve limpar o usuário e, se estiver no painel, voltar ao login (via `Navigate` ou `navigate`).

**Definição de pronto**

- [ ] Usuário não logado não vê o conteúdo do painel — só redireciona para `/login`.
- [ ] Usuário logado acessa `/painel` direto pela URL sem ser expulso.
- [ ] A proteção usa renderização condicional + `<Navigate>`, não só esconder botões no menu.

**Fixação:** esconder link não protege rota; proteção é na **árvore de rotas** ou no guard.

---

## Nível 5 — Organização, extras e visão de produto

**Objetivo:** hábitos de projeto real e pontapé no Data Router.

### 13. Centralizar definição de rotas

**O que fazer**

1. Mova a árvore de `<Routes>` para um arquivo `src/router.jsx` (ou `RoutesApp.jsx`) exportando um componente `AppRoutes`.
2. `App.jsx` deve ficar enxuto: só `<BrowserRouter><AppRoutes /></BrowserRouter>` (ou equivalente).
3. Comente **uma linha** no código ou no README do exercício explicando **por que** centralizar ajuda manutenção.

**Definição de pronto**

- [ ] O app continua funcionando igual após a extração.
- [ ] Existe o comentário pedido.

---

### 14. Lazy loading de uma página

**O que fazer**

1. Escolha **uma** página pesada ou simulada (pode ser um componente grande ou só uma página nomeada `Relatorio`).
2. Importe com `React.lazy(() => import('./pages/Relatorio'))`.
3. Envolva o `element` dessa rota com `<Suspense fallback={...}>` mostrando “Carregando…” (texto simples basta).
4. Navegue até essa rota e confirme que o fallback aparece pelo menos brevemente (em dev pode ser rápido).

**Definição de pronto**

- [ ] A rota usa `lazy` + `Suspense` sem erro de import dinâmico.
- [ ] O fallback aparece ou você documenta por que em dev foi instantâneo demais para ver.

**Fixação:** code splitting por rota melhora o primeiro carregamento.

---

### 15. Consulta na URL (`useSearchParams`)

**O que fazer**

1. Na página `ListaPosts` (ou equivalente), adicione um campo de busca controlado que sincroniza com a query string `?q=` usando `useSearchParams` do React Router.
2. Ao digitar e confirmar (botão “Buscar” ou submit), a URL deve ficar tipo `/posts?q=react`.
3. Ao carregar `/posts?q=react` direto, o campo deve mostrar `react`.

**Definição de pronto**

- [ ] O parâmetro `q` aparece na URL após buscar.
- [ ] Recarregar a página mantém o valor exibido coerente com `q`.

---

### 16. Modo Data Router (leitura)

**O que fazer**

Leia a seção **Modo Data Router** em `rotas-frontend.md` e responda:

1. Em **uma frase**, o que é um `loader` neste contexto?
2. Em **uma frase**, por que o tutorial do curso começa pelo modo declarativo com `<Routes>`?

**Definição de pronto**

- [ ] A frase sobre `loader` menciona dados antes do render ou equivalente correto.
- [ ] A segunda frase menciona didática/simplicidade ou curva de aprendizado.

---

## Autoavaliação honesta (sem nota, só direção)

Marque mentalmente:

- [ ] Consigo desenhar minha árvore de rotas no papel e ela bate com o `Routes`.
- [ ] Sei quando usar `NavLink` em vez de `Link`.
- [ ] Sei ler `:id` da URL e navegar com `useNavigate` sem hacks.
- [ ] Sei proteger uma rota e por que “esconder o botão” não basta.
- [ ] Sei o papel do `Outlet` num layout aninhado.

Se algo falhar, volte ao `tutorial-rotas.md` e refaça só o nível correspondente.

---

## Mensagem final

URL boa é documentação que o usuário pode compartilhar. Cada exercício aqui te aproxima de um app navegável de verdade — sem reload, sem surpresa. Boa prática.
