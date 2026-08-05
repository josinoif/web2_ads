# Exercícios de fixação — Hooks no React

Hooks parecem “só funções” — até você dominar **quando** usar cada uma e **por que** o React se comporta assim. Estes exercícios são para **consolidar** o que você viu na pasta `04-hooks`: não são provas difíceis de propósito; são **passos claros** que somam confiança.

> **Como usar:** faça na ordem (ou pule só se já dominou o nível anterior). Vale rabiscar no caderno, abrir o DevTools e quebrar de propósito para ver o erro — depois conserte. Errar aqui é barato; errar em produção é caro.

**Formato de cada exercício:** leia **O que fazer** e confira com **Definição de pronto**. Se todos os itens da definição de pronto forem verdadeiros na sua tela/comportamento, o exercício está feito.

---

## Nível 1 — Fundamentos (você já consegue)

**Objetivo:** sentir que estado e renderização “conversam” de verdade.

### 1. Contador com histórico

**O que fazer**

1. Crie um estado numérico inteiro do contador, valor inicial `0`.
2. Na tela, mostre o **valor atual** do contador em texto visível (ex.: “Valor: 0”).
3. Coloque **três botões**: um aumenta o contador em `1`, outro diminui em `1`, outro **zera** o contador para `0`.
4. Mantenha um **histórico** em estado: uma lista dos valores do contador **depois de cada alteração** pelos botões (não precisa registrar o valor inicial `0` antes do primeiro clique, a menos que você clique em algo que mude o valor).
5. Mostre na interface os **últimos 5 valores** desse histórico, do mais recente ao mais antigo (ou o contrário, mas seja consistente e indique na UI qual é o mais recente).

**Definição de pronto**

- [ ] Cada clique em `+1`, `-1` ou `zerar` atualiza o número na tela na hora.
- [ ] A lista mostra **no máximo 5** entradas; quando há mais histórico, só aparecem as 5 últimas mudanças.
- [ ] O histórico **não** é mutado no lugar (use novo array a cada atualização).

**Fixação:** cada `setState` dispara nova renderização — observe o que aparece na tela.

---

### 2. Formulário controlado mínimo

**O que fazer**

1. Um `<input type="text">` **controlado**: o valor exibido no input vem sempre do estado React (prop `value`), e cada tecla atualiza o estado com `onChange`.
2. Abaixo ou ao lado, um `<p>` que mostra **exatamente** o mesmo texto que está no input, atualizando em tempo real.
3. Um botão **“Limpar”** que, ao clicar, define o texto para string vazia `''` **no estado** (o input e o parágrafo ficam vazios).

**Definição de pronto**

- [ ] Não é possível “desincronizar” input e parágrafo: ambos mostram sempre o mesmo texto.
- [ ] “Limpar” funciona com um clique e não exige apagar manualmente no teclado.

**Fixação:** estado como “fonte da verdade” do input.

---

### 3. Lista simples com adição

**O que fazer**

1. Estado: array de itens; cada item deve ser `{ id: string, texto: string }`. Comece com array vazio `[]`.
2. Um input de texto e um botão **“Adicionar”**.
3. Ao clicar em “Adicionar”: se o texto após `trim()` não for vazio, adicione um novo item com `id` único (use `crypto.randomUUID()` ou `Date.now().toString()` + índice) e `texto` igual ao que foi digitado; depois **esvazie** o input para facilitar a próxima entrada.
4. Renderize todos os itens em uma lista (`<ul>` / `<li>`). Cada `<li>` deve ter `key={item.id}`.

**Definição de pronto**

- [ ] Vários cliques em “Adicionar” criam várias linhas distintas com `key` estável.
- [ ] O array no estado nunca é alterado com `push` direto no mesmo array (use imutabilidade).

**Fixação:** **nunca** mutar o array no lugar — use spread ou `concat`.

---

### 4. Quiz rápido (sem código)

**O que fazer**

1. Escreva **uma única frase** respondendo: por que **não** podemos chamar hooks como `useState` ou `useEffect` dentro de `if`, `for` ou funções internas arbitrárias?
2. Inclua na frase a ideia da **ordem fixa** das chamadas de hooks entre renderizações.

**Definição de pronto**

- [ ] A resposta menciona ordem das chamadas / mesma ordem a cada render (não precisa citar termos da doc palavra por palavra, mas precisa estar correta).

---

## Nível 2 — Efeitos e fluxo de dados

**Objetivo:** separar “o que é estado local” de “o que é efeito colateral”.

### 5. Título da aba

**O que fazer**

1. Estado inteiro `visitas`, valor inicial `0`.
2. Um botão **“Registrar visita”** que faz `visitas + 1`.
3. Use `useEffect` para que, sempre que `visitas` mudar, `document.title` seja exatamente: `Visitas: X` (onde `X` é o número atual).
4. No mesmo efeito ou em outro coerente, garanta que você **não deixa timers ou listeners órfãos** se no futuro estender o código (neste exercício o foco é só o título; se usar apenas `document.title`, não há listener — está ok).

**Definição de pronto**

- [ ] Ao carregar a página, o título reflete `Visitas: 0` (ou o valor inicial que você escolheu, mas documente na UI qual é o inicial).
- [ ] A cada clique em “Registrar visita”, o número na aba do navegador acompanha o estado.

**Observação:** em Strict Mode (desenvolvimento), efeitos podem rodar duas vezes na montagem — observe e não assuma bug sem ler o console/React.

---

### 6. Timer que você controla

**O que fazer**

1. Estado inteiro `segundos`, inicial `0`.
2. Estado booleano `rodando`, inicial `false`.
3. Três botões: **“Iniciar”** (`rodando = true`), **“Pausar”** (`rodando = false`), **“Resetar”** (`segundos = 0` e pause se estiver rodando).
4. Enquanto `rodando === true`, incremente `segundos` em `1` a cada **um segundo real**, usando `setInterval` dentro de `useEffect`.
5. Quando `rodando` virar `false` ou o componente desmontar, **cancele** o intervalo no cleanup do `useEffect` (`clearInterval`).

**Definição de pronto**

- [ ] Com “Iniciar”, o número sobe 1, 2, 3… a cada segundo.
- [ ] Com “Pausar”, o número para de aumentar imediatamente.
- [ ] Com “Resetar”, volta a `0` e não continua subindo a menos que “Iniciar” seja pressionado de novo.
- [ ] Não há vários intervalos competindo (sem aceleração estranha após vários pausar/iniciar).

**Fixação:** o array de dependências do `useEffect` deve incluir o que controla se o intervalo existe (ex.: `rodando`).

---

### 7. Busca com debounce manual

**O que fazer**

1. Estado string `termo`, ligado a um input **controlado** (“Digite para buscar…”).
2. Estado string `resultadoDebounced` (ou nome equivalente), inicial `''`.
3. Sempre que `termo` mudar, **não** atualize `resultadoDebounced` na hora. Use `useEffect` que:
   - agenda um `setTimeout` de **300 ms**;
   - se `termo` mudar de novo antes dos 300 ms, **cancele** o timeout anterior (`clearTimeout` no cleanup);
   - quando o timeout disparar, atualize `resultadoDebounced` para ser **igual** ao `termo` atual daquele momento.
4. Na tela mostre **duas** linhas de texto: “Ao vivo: …” com `termo` e “Após debounce: …” com `resultadoDebounced`.
5. Além disso, quando `resultadoDebounced` mudar de fato, faça **um** `console.log('Buscar:', resultadoDebounced)` (simula chamada de API).

**Definição de pronto**

- [ ] Digitando rápido, “Ao vivo” acompanha na hora; “Após debounce” só muda ~300 ms depois da última tecla.
- [ ] O `console.log` **não** dispara a cada tecla; só quando o valor debounced estabiliza.

---

### 8. Derivar vs armazenar

**O que fazer**

1. Estado: array de números `precos` (pode começar com algo como `[10, 20, 30]`).
2. Na mesma tela, implemente **duas colunas ou duas seções claramente rotuladas**: **“Versão A — derivado no render”** e **“Versão B — guardado em estado”**.
3. **Versão A:** calcule `total` e `media` **diretamente** no corpo do componente a partir de `precos` (se `precos` vazio, `total = 0` e `media = 0` ou mostre “sem dados” — escolha uma regra e aplique nas duas versões igual).
4. **Versão B:** mantenha `total` e `media` em `useState` e use **um** `useEffect` que roda quando `precos` muda e atualiza esses dois estados.
5. Botões para alterar `precos`: por exemplo “Adicionar preço aleatório” e “Remover último”, para você ver as duas versões sempre iguais.

**Definição de pronto**

- [ ] Os números exibidos nas duas versões são **sempre iguais** para o mesmo `precos`.
- [ ] Você escreveu em **um parágrafo** (abaixo do código ou em comentário no projeto) qual versão prefere para esse caso e por quê.

---

## Nível 3 — Reducer e contexto

**Objetivo:** modelar estados mais ricos sem virar “sopa de setters”.

### 9. Carrinho fake com `useReducer`

**O que fazer**

1. Defina o estado do reducer como `{ itens: Array<{ id: string, nome: string, qtd: number, preco: number }> }`.
2. Implemente um `reducer` que trata **exatamente** estas ações (tipo discriminado ou `switch` por string):
   - `ADICIONAR`: payload `{ id, nome, preco }` — se já existir item com o mesmo `id`, aumente `qtd` em 1; senão, adicione com `qtd: 1`.
   - `REMOVER`: payload `{ id }` — remove o item com esse `id`.
   - `ALTERAR_QTD`: payload `{ id, qtd }` — define `qtd` para o número informado; se `qtd <= 0`, remova o item.
   - `LIMPAR`: sem payload — `itens` vira `[]`.
3. Na UI: lista cada item com nome, quantidade, sublinha (qtd × preco) e botões/ações para remover e mudar quantidade (+1 e −1 já bastam).
4. Mostre o **subtotal geral** (soma de `qtd * preco` de todos os itens).

**Definição de pronto**

- [ ] Todas as quatro ações existem e funcionam conforme as regras acima.
- [ ] O estado do carrinho só muda dentro do `reducer` (sem `setState` solto para mutar o carrinho).

---

### 10. Tema claro/escuro com `useContext`

**O que fazer**

1. Crie um contexto (ex.: `ThemeContext`) cujo valor é `{ tema: 'light' | 'dark', alternarTema: () => void }`.
2. No **provedor** (componente que envolve a árvore), mantenha `tema` em `useState` e implemente `alternarTema` para inverter entre `'light'` e `'dark'`.
3. Estruture a árvore assim: `App` renderiza o Provider → um componente intermediário **que não recebe props de tema** → um componente neto/bisneto **Profundo** que contém **somente** o botão “Alternar tema”.
4. O fundo ou cor do texto da página (ou de um `main` envolvido pelo Provider) deve refletir o tema: por exemplo fundo branco/texto preto no `light` e fundo escuro/texto claro no `dark`.
5. O botão dentro de `Profundo` deve chamar **apenas** `alternarTema` do contexto (sem props `onToggle` vindas do pai).

**Definição de pronto**

- [ ] O componente intermediário **não** declara props relacionadas a tema para passar ao filho.
- [ ] Um clique alterna visualmente entre os dois temas em toda a área envolvida pelo Provider.

---

## Nível 4 — Performance e form Actions (React 19)

**Objetivo:** saber **quando** memorizar e **como** forms modernos se integram aos hooks.

### 11. Lista pesada simulada

**O que fazer**

1. Gere um array fixo de **5000** strings no corpo do componente (ex.: `Array.from({ length: 5000 }, (_, i) => \`Item ${i}\`)` — pode usar `useMemo` só para não recriar a cada render se preferir).
2. Estado string `filtro` ligado a um input.
3. **Primeiro**, renderize a lista filtrada **sem** `useMemo`: derive `filtrados = linhas.filter(...)` no render e mapeie para `<li>`.
4. **Depois**, substitua por uma versão que usa `useMemo` para calcular `filtrados` apenas quando `filtro` ou a fonte das linhas mudar.
5. Opcional: use `console.time` / `console.timeEnd` ou React Profiler para comparar digitação rápida no filtro.

**Definição de pronto**

- [ ] Com filtro digitável, só aparecem linhas que contêm o texto do filtro (case sensitive ou insensitive — **defina na UI qual você escolheu**).
- [ ] Existe comentário no código indicando onde estava a versão sem `useMemo` e onde está com `useMemo`.

---

### 12. `useCallback` com filho memoizado

**O que fazer**

1. Componente pai com estado inteiro `contador`, inicial `0`, e botão “Incrementar pai” que faz `+1`.
2. Passe para um filho chamado `FilhoMemo` uma prop função `onSaudar` que **não recebe argumentos** e faz `alert('Olá')` ou `console.log`.
3. Envolva `FilhoMemo` em `React.memo`.
4. Dentro de `FilhoMemo`, renderize um botão “Saudar” que chama `onSaudar` e **também** mostre um texto “Renderizações do filho: N” usando `useRef` para contar quantas vezes o componente renderizou (incremente no corpo do render do filho).
5. **Fase A:** implemente `onSaudar` como função inline no pai (`() => ...`). Clique só em “Incrementar pai” várias vezes e observe o contador de renderizações do filho.
6. **Fase B:** refatore o pai para criar `onSaudar` com `useCallback` com array de dependências **correta**. Repita o teste: ao incrementar só o pai, o filho **não** deve aumentar o contador de renderizações (exceto na primeira montagem).

**Definição de pronto**

- [ ] Na Fase A, incrementar o pai aumenta as renderizações do filho.
- [ ] Na Fase B, incrementar o pai **não** aumenta as renderizações do filho; clicar “Saudar” ainda funciona.

---

### 13. Form com Action + estado (`useActionState`)

**O que fazer**

1. Monte um `<form>` que usa **Action** do React (função passada ao `action` do form ou padrão da sua stack conforme o tutorial da pasta).
2. Um campo **e-mail** (`input type="email"` ou `name="email"`).
3. Use `useActionState` para armazenar o **resultado** da action: por exemplo `{ ok: boolean, mensagem: string }` ou `null` no início.
4. A action (pode ser `async`) deve:
   - ler o `FormData` do formulário;
   - se o e-mail estiver **vazio** após `trim()`, retornar erro `{ ok: false, mensagem: 'E-mail obrigatório' }`;
   - caso contrário retornar sucesso `{ ok: true, mensagem: 'Enviado com sucesso (simulado)' }`.
5. Na UI, mostre sempre a **última mensagem** retornada e use estilo ou texto diferente para erro vs sucesso.

**Definição de pronto**

- [ ] Submit com campo vazio mostra a mensagem de erro sem travar a página.
- [ ] Submit com e-mail preenchido mostra sucesso (mesmo que não exista backend).

---

### 14. Botão de submit com `useFormStatus`

**O que fazer**

1. Use o mesmo formulário com Action do exercício anterior **ou** um form novo com action `async` que faz `await new Promise(r => setTimeout(r, 1500))` para simular rede.
2. Extraia um componente **`SubmitButton`** em arquivo ou bloco separado que chama `useFormStatus` de **`react-dom`**.
3. `SubmitButton` deve renderizar `<button type="submit">` que:
   - quando `pending === true`, fica `disabled` e o texto é **“Enviando…”**;
   - quando `pending === false`, o texto é **“Enviar”** (ou equivalente).

**Definição de pronto**

- [ ] Enquanto a action está em andamento, o botão não pode ser clicado de novo e mostra “Enviando…”.
- [ ] `SubmitButton` **não** recebe prop `pending` do pai — o pending vem só de `useFormStatus`.

---

### 15. Lista otimista com `useOptimistic`

**O que fazer**

1. Estado base: lista de strings `itens` (IDs únicos recomendados se for objeto; strings simples bastam).
2. Função **assíncrona** `confirmarNoServidor(item)` que usa `await new Promise(...)` com atraso de ~800 ms e **às vezes** reprova (ex.: `Math.random() < 0.3` lança erro ou retorna `{ ok: false }`).
3. Use `useOptimistic` para que, ao “adicionar”, o novo item apareça **na lista na hora**.
4. Se a confirmação **falhar**, o item some da lista (ou aparece mensagem de erro — **escolha um comportamento e descreva na UI**).
5. Se **passar**, o item permanece como parte definitiva da lista base.

**Definição de pronto**

- [ ] O usuário não precisa esperar o atraso para ver o item aparecer.
- [ ] Em caso de falha simulada, a interface volta ao estado coerente (sem item fantasma sem explicação).

---

## Nível 5 — Integração e pitacos de mestre

**Objetivo:** juntar vários hooks sem perder a cabeça — é assim que o trabalho real aparece.

### 16. Mini painel de estudo

**O que fazer**

Implemente **um painel** (pode ser um único `App` ou poucos arquivos) que contenha **todas** as partes abaixo, claramente separadas na tela (seções com título):

1. **Pomodoro:** estado `minutosRestantes` inteiro (ex.: começa em `25`), botões “Iniciar / Pausar”, contagem regressiva de **1 minuto real por minuto restante** ou simplifique para **segundos** se preferir — mas documente na UI a unidade. Quando chegar a zero, pare o timer.
2. **Título da página:** quando o pomodoro chegar a zero, use `useEffect` para definir `document.title` para uma string fixa tipo **“Hora da pausa!”** (enquanto não zerar, o título pode ser “Foco” ou similar).
3. **Lista de tarefas com filtro:** estado com várias tarefas `{ id, texto, feita }`; um input filtra por substring no `texto`; use `useMemo` para o array filtrado.
4. **Filho memoizado:** componente filho em `React.memo` que recebe uma função `marcarTodasFeitas` do pai; o pai deve criar essa função com `useCallback` com dependências corretas.
5. **Opcional (+):** pequeno form com Action registrando “O que estudei hoje” em uma lista abaixo.

**Definição de pronto**

- [ ] As quatro primeiras partes estão visíveis e funcionando ao mesmo tempo sem erros no console.
- [ ] Não há estado duplicado que precise ser atualizado em dois lugares para a mesma informação (ex.: não mantenha “tempo restante” em dois states independentes sem necessidade).

---

### 17. Hook customizado `useLocalStorage`

**O que fazer**

1. Crie uma função `useLocalStorage(chave, valorInicial)` que retorna `[valor, setValor]` com a mesma sensação de `useState`.
2. Na **primeira montagem**, leia `localStorage.getItem(chave)`; se existir JSON válido, use como valor inicial; senão use `valorInicial`.
3. Sempre que `valor` mudar, grave em `localStorage.setItem(chave, JSON.stringify(valor))`.
4. Exporte e use no `App`: por exemplo um campo que persiste o nome do usuário após recarregar a página.
5. Se você souber que o projeto pode rodar com SSR/hidratação, adicione **um comentário** explicando o risco de mismatch — não é obrigatório implementar SSR aqui.

**Definição de pronto**

- [ ] Recarregar a página (F5) mantém o valor persistido para a mesma `chave`.
- [ ] Erros de JSON inválido no storage não quebram a página (podem cair no `valorInicial`).

---

### 18. `use` em uma branch (React 19)

**O que fazer**

1. Leia na documentação oficial do React 19 quando o hook **`use`** pode aparecer dentro de condicionais (diferente dos outros hooks).
2. Escreva um componente **mínimo** (pode ser ~20–40 linhas) onde:
   - existe um `if` ou operador ternário que escolhe entre **dois caminhos**;
   - **somente em um dos caminhos** você chama `use` para ler uma **Promise** já criada (por exemplo uma promise que resolve uma string).
3. No mesmo arquivo, escreva **duas frases** (comentário ou markdown no projeto) comparando: por que `use` permite esse padrão e `useState` não.

**Definição de pronto**

- [ ] O exemplo compila e, ao alternar o fluxo que escolhe o caminho com `use`, o comportamento corresponde à doc (sem violar as regras dos outros hooks).
- [ ] As duas frases de explicação estão presentes e fazem sentido técnico.

---

## Autoavaliação honesta (sem nota, só direção)

Marque mentalmente:

- [ ] Consigo explicar **re-render** para um colega usando um exemplo com `useState`.  
- [ ] Sei quando um `useEffect` precisa de **cleanup**.  
- [ ] Entendo a diferença entre **derivar dados** e **duplicar estado**.  
- [ ] Sei por que `useMemo`/`useCallback` não são “otimização grátis”.  
- [ ] Consigo usar **form Actions** sem misturar validação com lógica de apresentação num único bloco ilegível.

Se algo ficou nebuloso, volte ao arquivo correspondente (`useState.md`, `useEffect.md`, etc.) e faça **só** o exercício ligado a esse tópico — progressão beats perfeccionismo.

---

## Mensagem final

Hooks não são decoração: são o jeito moderno de escrever componentes **claros**. Cada exercício que você termina é uma microvitória — some várias e você está **pronto** para componentes reais. Boa prática.
