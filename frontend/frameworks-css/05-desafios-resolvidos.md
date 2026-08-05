# 5. Desafios resolvidos — soluções comentadas

Este arquivo traz **uma** forma de resolver cada desafio, com comentários sobre decisões e alternativas. As soluções são exemplos; você pode ter escolhido outro framework ou outra estrutura e ainda estar correto. O importante é o **raciocínio** e a **consistência** com o contexto.

---

## Desafio 1 — Dashboard em tempo limitado

**Solução de referência:** Bootstrap 5 (componentes prontos aceleram muito).

### Ideia da estrutura

- **Sidebar + conteúdo:** Um `container-fluid` com `row`; na primeira coluna (`col-md-3` ou similar) a sidebar; na segunda (`col-md-9`) o conteúdo. Em mobile, a sidebar pode virar um `offcanvas` ou ficar em cima com `order`.
- **Cards de métrica:** Três `col-md-4` (ou `col-12 col-md-4`) com `card` dentro; cada card com um número grande e um rótulo.
- **Tabela:** `table table-striped` (ou `table-hover`) dentro da área de conteúdo.

### Trecho de referência (Bootstrap)

```html
<div class="container-fluid">
  <div class="row">
    <aside class="col-md-3 bg-light py-3">
      <h6 class="text-muted">Menu</h6>
      <ul class="nav flex-column">
        <li class="nav-item"><a class="nav-link" href="#">Dashboard</a></li>
        <li class="nav-item"><a class="nav-link" href="#">Relatórios</a></li>
      </ul>
    </aside>
    <main class="col-md-9 py-4">
      <h1 class="h4 mb-4">Dashboard</h1>
      <div class="row g-3 mb-4">
        <div class="col-12 col-md-4">
          <div class="card">
            <div class="card-body">
              <p class="text-muted small mb-0">Usuários ativos</p>
              <p class="fs-3 mb-0">1.234</p>
            </div>
          </div>
        </div>
        <!-- mais 2 cards -->
      </div>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead><tr><th>Nome</th><th>Data</th><th>Status</th></tr></thead>
          <tbody><!-- 5 linhas --></tbody>
        </table>
      </div>
    </main>
  </div>
</div>
```

### Por que essa escolha

- Bootstrap entrega sidebar (nav + col), cards e tabela sem CSS próprio. Para “limpo e funcional” em pouco tempo, é uma boa opção.
- **Alternativa com Tailwind:** Você montaria tudo com `flex`, `grid`, `bg-gray-100`, `p-4`, `rounded`, etc. Mais liberdade, um pouco mais de tempo na primeira vez; resultado pode ser mais “único”.
- **Alternativa com Bulma:** `columns`, `column`, `box`, `table`; estrutura parecida, visual mais limpo, sem JS.

---

## Desafio 2 — Landing page responsiva

**Solução de referência:** Tailwind CSS (controle fino do layout e do visual).

### Ideia da estrutura

- **Hero:** Uma `section` com `flex flex-col items-center justify-center min-h-[50vh]` (ou similar), título com `text-4xl md:text-5xl`, subtítulo e `btn` (classes de botão do Tailwind ou componente).
- **Como funciona:** `grid grid-cols-1 md:grid-cols-3 gap-8` com três blocos; cada bloco com ícone/número, título e texto.
- **Rodapé:** `flex` com links e texto de copyright; em mobile pode ser `flex-col text-center`.

### Trecho de referência (Tailwind)

```html
<section class="py-16 px-4 text-center">
  <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Nosso Produto</h1>
  <p class="text-lg text-gray-600 max-w-2xl mx-auto mb-8">Descrição curta e chamada.</p>
  <a href="#" class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Começar agora</a>
</section>

<section class="py-16 px-4 bg-gray-50">
  <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
    <div class="text-center p-4">
      <span class="text-3xl font-bold text-blue-600">1</span>
      <h3 class="text-xl font-semibold mt-2">Passo um</h3>
      <p class="text-gray-600 mt-1">Texto explicativo.</p>
    </div>
    <!-- mais 2 blocos -->
  </div>
</section>

<footer class="py-6 px-4 border-t flex flex-col md:flex-row justify-between items-center gap-4">
  <nav class="flex gap-4"><a href="#">Link 1</a><a href="#">Link 2</a></nav>
  <p class="text-sm text-gray-500">© 2025 Empresa.</p>
</footer>
```

### Por que essa escolha

- Tailwind permite ajustar espaçamento, cores e breakpoints sem sair do HTML; ótimo para landing com identidade definida.
- **Alternativa com Bootstrap:** `container`, `row`, `col-12 col-md-4`, `display-4`, `btn btn-primary`; mais rápido se você já conhece, visual mais “Bootstrap” se não customizar.

---

## Desafio 3 — Formulário acessível e consistente

**Solução de referência:** Qualquer framework, desde que você use **labels associados** e estrutura semântica.

### Boas práticas (independente do framework)

- Cada `input` deve ter um `<label>` com `for` apontando ao `id` do input (ou o input dentro do label).
- Agrupe campos com `<fieldset>` e `<legend>` quando fizer sentido (ex.: “Termos”).
- Mensagens de erro: associadas ao campo (aria-describedby) e visíveis no foco.
- Botão de envio: `type="submit"`; evite divs estilizadas como botão sem acessibilidade.

### Exemplo com Bootstrap (estrutura)

```html
<form class="row g-3">
  <div class="col-12 col-md-6">
    <label for="nome" class="form-label">Nome</label>
    <input type="text" class="form-control" id="nome" required>
  </div>
  <div class="col-12 col-md-6">
    <label for="email" class="form-label">E-mail</label>
    <input type="email" class="form-control" id="email" required>
  </div>
  <div class="col-12">
    <label for="senha" class="form-label">Senha</label>
    <input type="password" class="form-control" id="senha" required>
  </div>
  <div class="col-12">
    <label for="confirmar" class="form-label">Confirmar senha</label>
    <input type="password" class="form-control" id="confirmar" required>
  </div>
  <div class="col-12">
    <div class="form-check">
      <input class="form-check-input" type="checkbox" id="termos" required>
      <label class="form-check-label" for="termos">Li e aceito os termos.</label>
    </div>
  </div>
  <div class="col-12 flex gap-2">
    <button type="submit" class="btn btn-primary">Cadastrar</button>
    <button type="button" class="btn btn-outline-secondary">Cancelar</button>
  </div>
</form>
```

### Por que essa escolha

- `form-label` e `form-control` mantêm consistência visual; a acessibilidade vem da marcação HTML (label + id), não do framework. Qualquer framework que não quebre isso serve.

---

## Desafio 4 — “Migração” de layout (card)

**Solução de referência:** Reimplementar o card com as peças do framework.

### Exemplo: card em CSS puro (antes)

```html
<div class="card-manual">
  <img src="..." alt="..." class="card-manual__img">
  <div class="card-manual__body">
    <h3 class="card-manual__title">Título</h3>
    <p class="card-manual__text">Texto.</p>
    <a href="#" class="card-manual__btn">Ver mais</a>
  </div>
</div>
```

```css
.card-manual { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; max-width: 320px; }
.card-manual__img { width: 100%; height: 180px; object-fit: cover; }
.card-manual__body { padding: 1rem; }
.card-manual__title { margin: 0 0 0.5rem; font-size: 1.25rem; }
.card-manual__btn { display: inline-block; padding: 0.5rem 1rem; background: #0066cc; color: #fff; border-radius: 4px; }
```

### Depois com Bootstrap

```html
<div class="card" style="max-width: 320px;">
  <img src="..." class="card-img-top" alt="...">
  <div class="card-body">
    <h5 class="card-title">Título</h5>
    <p class="card-text">Texto.</p>
    <a href="#" class="btn btn-primary">Ver mais</a>
  </div>
</div>
```

### O que ganhamos e perdemos

- **Ganho:** Menos CSS para manter; padrão alinhado ao resto do sistema; responsividade e temas do Bootstrap.
- **Perda possível:** Bordas, raios e espaçamentos exatamente iguais ao original podem exigir sobrescrita (variáveis ou classes utilitárias). Em muitos casos a diferença é aceitável em troca da padronização.

---

## Desafio 5 — Escolha de ferramenta (respostas sugeridas)

### Projeto A (React, gestão de tarefas, 2 meses, design em definição)

**Recomendação sugerida:** Tailwind CSS.

**Justificativa:** O time já conhece Tailwind; em React, componentes podem encapsular as classes e o design ainda em definição se beneficia da flexibilidade (mudar cores, espaços e breakpoints sem refatorar componentes prontos). Prazo de 2 meses combina com produtividade após a curva inicial.

**Se o time insistisse em Bootstrap:** Argumentar que Bootstrap também atende (react-bootstrap), mas que o custo de “escapar” do visual padrão e a duplicação com um possível design system futuro podem aumentar a dívida. Propor um piloto de 1 semana com os dois e decidir com base em velocidade e satisfação do time.

---

### Projeto B (Site institucional, HTML/CSS/JS, acessibilidade e peso)

**Recomendação sugerida:** CSS próprio bem estruturado ou Bulma (se quiser um grid e componentes leves).

**Justificativa:** Site institucional costuma ter poucas páginas e necessidade forte de acessibilidade e performance. Um framework pesado (Bootstrap completo) pode ser excesso. CSS customizado com variáveis, grid/flexbox e foco em a11y atende bem; Bulma, se a equipe quiser um grid e alguns componentes sem JS, mantém o bundle menor e o controle alto.

---

## Referências rápidas

- **Bootstrap:** [getbootstrap.com](https://getbootstrap.com/) — Components, Grid, Utilities.
- **Tailwind:** [tailwindcss.com](https://tailwindcss.com/) — Utility-first, configuração, responsividade.
- **Bulma:** [bulma.io](https://bulma.io/) — Flexbox-based, modular, sem JS.
- **Acessibilidade:** [WCAG](https://www.w3.org/WAI/WCAG21/quickref/) — Critérios e boas práticas para formulários e navegação.

---

*Com esses desafios e respostas você exercita tanto a mão no código quanto o raciocínio por trás da escolha do framework — exatamente o que o mercado e as entrevistas valorizam.*

**Voltar ao índice:** [README.md](README.md)
