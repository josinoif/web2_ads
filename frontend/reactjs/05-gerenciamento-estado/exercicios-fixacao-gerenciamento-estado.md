# Exercícios de fixação — Gerenciamento de estado

Decidir **onde** o estado mora costuma valer mais que escolher **qual** biblioteca usar. Estes exercícios consolidam o que você viu em `estado-local-global.md`, `context-e-padroes.md` e `tutorial-estado.md`: local vs global, Context API no React 19, providers e bons hábitos.

> **Como usar:** faça na ordem quando possível. Desenhe a árvore de componentes no papel antes de codar nos exercícios maiores — poupa retrabalho.

**Formato de cada exercício:** leia **O que fazer** e confira com **Definição de pronto**. Se todos os itens da definição de pronto forem verdadeiros na sua tela/comportamento (ou na sua resposta escrita, quando for reflexão), o exercício está feito.

---

## Nível 1 — Onde o estado deve morar?

**Objetivo:** treinar o critério “só globalizo quando preciso”.

### 1. Classificação local vs global

**O que fazer**

Para cada item abaixo, responda **apenas** com uma palavra: **local** ou **global**. Em uma linha opcional, cite **quem** usa o dado (um componente, uma página, várias telas).

1. Ordem das linhas em uma tabela que só aparece em uma página de relatório.
2. Nome do usuário logado exibido no cabeçalho de todas as páginas.
3. Aberto/fechado de um modal de confirmação que só existe dentro do componente `ExcluirItem`.
4. Idioma da interface (PT/EN) escolhido pelo usuário e persistente na sessão.
5. Lista de produtos retornada por uma API e mostrada em várias rotas, sempre precisando da mesma versão em cache.

**Definição de pronto**

- [ ] Cada um dos 5 itens tem **uma** etiqueta (`local` ou `global`) sem ambiguidade.
- [ ] Nos itens em que você marcou **global**, a justificativa implícita é “vários ramos da árvore / várias telas precisam do mesmo dado” ou equivalente.

**Fixação:** estado local resolve a maioria dos casos; global entra quando compartilhamento ou prop drilling pesado aparecem.

---

### 2. Um estado, dois componentes irmãos

**O que fazer**

1. Monte um pai `App` com **dois filhos irmãos**: `Entrada` e `Resumo`.
2. `Entrada`: um único campo numérico controlado (quantidade, por exemplo).
3. `Resumo`: mostra o texto **“Quantidade escolhida: N”**, onde `N` é exatamente o valor digitado em `Entrada`.
4. **Não** use Context. O estado deve morar no pai e descer por **props**.

**Definição de pronto**

- [ ] Alterar o número em `Entrada` atualiza `Resumo` na hora, sem recarregar a página.
- [ ] Nem `Entrada` nem `Resumo` declaram `useState` para esse número — só o pai.

**Fixação:** elevação de estado para o ancestral comum mais próximo.

---

### 3. Quando **não** promover para global

**O que fazer**

Escreva **duas frases** respondendo: por que guardar no Context o valor de um campo de busca que só filtra uma lista na mesma página pode ser uma má ideia?

**Definição de pronto**

- [ ] A resposta menciona pelo menos um entre: re-renders desnecessários, acoplamento, ou simplicidade do estado local.

---

## Nível 2 — Prop drilling e limites

**Objetivo:** sentir quando passar props “em escada” deixa de compensar.

### 4. Prop drilling em três níveis

**O que fazer**

1. Estado string `mensagem` no componente `App` (valor inicial `"Olá"`).
2. Árvore fixa: `App` → `Camada1` → `Camada2` → `Camada3`.
3. `Camada3` renderiza um `<input>` controlado cuja fonte da verdade é **sempre** `mensagem` do `App` (ou seja, duas props: valor e `onChange`).
4. `App` também mostra o mesmo texto em um `<p>` no topo.

**Definição de pronto**

- [ ] `Camada1` e `Camada2` **não** usam o valor da mensagem para nada além de repassar props para baixo.
- [ ] Digitar em `Camada3` atualiza o parágrafo em `App`.

**Fixação:** prop drilling leve é normal; documente quem só repassa.

---

### 5. Do drilling ao Context (refatoração guiada)

**O que fazer**

1. Pegue a árvore do exercício 4 e **refatore**: remova as props `mensagem` / `setMensagem` das camadas intermediárias.
2. Crie um contexto `MensagemContext` com valor `{ mensagem, setMensagem }` e Provider na raiz (use a sintaxe React 19: `<MensagemContext value={...}>`).
3. `Camada3` consome com `useContext` (ou hook customizado que encapsula isso).
4. `App` continua exibindo o `<p>` no topo — pode consumir o mesmo contexto ou manter estado apenas no Provider (escolha **uma** abordagem coerente e sem duplicar fonte da verdade).

**Definição de pronto**

- [ ] `Camada1` e `Camada2` não recebem mais props só para “furar” a mensagem.
- [ ] O input em `Camada3` e o `<p>` em `App` continuam sempre sincronizados.

---

## Nível 3 — Context API e hooks customizados

**Objetivo:** igual ao tutorial — mas você monta sozinho com regras explícitas.

### 6. Provider + `use` ou `useContext` com validação

**O que fazer**

1. `createContext(null)` para um contexto de **preferências**: `{ notificacoesAtivas: boolean, alternarNotificacoes: () => void }`.
2. Provider com `useState` para o boolean (inicial `true`).
3. Exporte um hook `usePreferencias()` que:
   - lê o contexto com `useContext`;
   - se o valor for `null`, lança `Error` com mensagem clara (ex.: “usePreferencias deve ser usado dentro do Provider”).
4. Um componente filho qualquer com um botão que alterna o texto entre “Notificações ligadas” e “Notificações desligadas” conforme o estado.

**Definição de pronto**

- [ ] Provider usa `<MeuContext value={...}>` (sintaxe React 19), não `.Provider`.
- [ ] Renderizar o consumidor **sem** Provider em volta quebra com o erro do hook (comportamento esperado ao testar).

---

### 7. Dois contextos independentes

**O que fazer**

1. Reaproveite ou recrie um **ThemeContext** (`'claro' | 'escuro'`) como no tutorial.
2. Crie um segundo contexto **ContadorGlobalContext**: número inteiro, botões ou funções `incrementar` e `zerar`.
3. Em `App`, envolva com **dois** Providers (ordem livre, desde que ambos envolvam os consumidores).
4. Componente `Painel` que usa **os dois** hooks e mostra tema atual + valor do contador + botões que alteram cada coisa.

**Definição de pronto**

- [ ] Alterar o tema não exige mexer no código do reducer/contador (são fontes independentes).
- [ ] Alterar o contador não exige alterar o estado do tema.

---

### 8. Estado do servidor vs estado do cliente (reflexão aplicada)

**O que fazer**

1. Em **até cinco frases**, explique por que dados vindos de uma API compartilhados entre telas costumam ser melhor tratados com **TanStack Query** (ou conceito equivalente de cache de servidor) do que com um único Context gigante que guarda “tudo da API”.
2. Dê **um** exemplo de dado que continua sendo estado de **cliente** mesmo em um app que usa TanStack Query.

**Definição de pronto**

- [ ] A parte (1) menciona explicitamente ideias como cache, revalidação, loading/error ou separação servidor/UI.
- [ ] O exemplo em (2) é claramente de UI (modal aberto, tema, rascunho de formulário, etc.).

---

## Nível 4 — Performance mental e padrões avançados

**Objetivo:** reduzir re-renders desnecessários **por design**.

### 9. Dividir contexto: tema vs usuário

**O que fazer**

1. Implemente **dois** contextos separados: autenticação (`usuario`, `login`, `logout`) e tema (`tema`, `alternarTema`), no estilo do `tutorial-estado.md`.
2. Crie um componente `SomenteTema` que **só** chama o hook de tema e mostra o nome do tema.
3. Crie um componente `SomenteAuth` que **só** chama o hook de auth e mostra se está logado.
4. Coloque ambos na mesma página. Ao simular `login`/`logout`, o trecho de tema **não** deve precisar ser reescrito — e vice-versa (critério lógico: mudanças isoladas por responsabilidade).

**Definição de pronto**

- [ ] Não existe um único objeto gigante no Context misturando tema + usuário sem separação.
- [ ] Os dois componentes podem ser lidos por outra pessoa e fica óbvio qual contexto cada um usa.

---

### 10. Estado e dispatch separados

**O que fazer**

1. Implemente um `useReducer` para um estado `{ itens: string[] }` com ações `ADICIONAR` e `LIMPAR`.
2. Exponha **dois** contextos: um só com **state**, outro só com **dispatch** (padrão do arquivo `context-e-padroes.md`).
3. Componente `ListaVisual` que consome **apenas** o contexto de estado e renderiza a lista (sem receber `dispatch` por props).
4. Componente `ListaControles` que consome **apenas** `dispatch` e tem botões “adicionar texto fixo” e “limpar”.
5. Opcional: use `memo` em `ListaVisual` — ao disparar uma ação só pelo `dispatch`, componentes que só leem `dispatch` não devem depender do state.

**Definição de pronto**

- [ ] `ListaVisual` não importa/consome o contexto de dispatch se você seguiu o enunciado à risca.
- [ ] `ListaControles` não precisa do array `itens` para disparar as ações.
- [ ] Adicionar e limpar funcionam e a lista reflete o estado do reducer.

---

### 11. Valor estável no Provider

**O que fazer**

1. Num Provider com `useState`, você passa `value={{ usuario, login, logout }}` **sem** `useMemo`.
2. Explique em **duas ou três frases** o problema da **nova referência de objeto** a cada render do Provider.
3. Refatore **um** dos métodos: ou memoize o objeto `value` com `useMemo` dependendo de `usuario`, ou estabilize `login`/`logout` com `useCallback`. Descreva na última linha qual opção escolheu.

**Definição de pronto**

- [ ] A explicação (2) menciona re-render de consumidores ou comparação por referência.
- [ ] O código (3) evita recriar **desnecessariamente** funções ou objeto `value` quando `usuario` não mudou.

---

## Nível 5 — Integração e cenários realistas

**Objetivo:** encaixar decisões como num app pequeno de verdade.

### 12. Mini app “preferências + formulário”

**O que fazer**

Monte uma página com **três** blocos visuais com título:

1. **Busca local:** input que filtra uma lista de strings **mantida em estado no componente da página** (não coloque essa string de busca no Context).
2. **Preferência global:** tema claro/escuro via Context (toda a página reage).
3. **Formulário:** estado local do formulário (nome + e-mail); ao “salvar”, apenas `console.log` ou alert — não precisa Context.

No topo da página, um parágrafo explicando em **uma frase** por que a busca ficou local.

**Definição de pronto**

- [ ] Três blocos aparecem e funcionam ao mesmo tempo.
- [ ] Parágrafo justifica a busca local com argumento de escopo ou frequência de mudança.

---

### 13. Árvore de decisão na prática

**O que fazer**

Descreva **por escrito** (bullet points ou tabela) como você armazenaria cada dado abaixo nestes projetos:

| Dado | App A (só uma tela) | App B (várias rotas) |
|------|---------------------|----------------------|
| Carrinho de compras | ? | ? |
| Toggle “somente favoritos” na lista da página atual | ? | ? |
| Token JWT após login | ? | ? |

Para cada célula `?`, indique **uma** solução dentre: estado local no componente, estado no pai, Context, biblioteca externa (nomeie TanStack Query só onde for estado de servidor), ou “persistência + Context”.

**Definição de pronto**

- [ ] Nenhuma célula fica vazia.
- [ ] Token em App B não fica só em estado volátil de um neto sem explicação — você menciona persistência ou Provider raiz.

---

### 14. Checklist de revisão de PR

**O que fazer**

Escreva uma lista de **cinco** perguntas que **você mesmo** faria ao revisar um pull request que introduz um novo Context (podem ser sim/não). A primeira pergunta já está dada abaixo — complete com mais quatro.

1. Esse estado é realmente usado por ramos distantes da árvore ou poderia ser local?
2. *(suas quatro perguntas)*

**Definição de pronto**

- [ ] Existem exatamente **cinco** perguntas no total.
- [ ] Pelo menos duas perguntas tocam em performance (re-render, frequência, tamanho) ou separação de contextos.

---

## Autoavaliação honesta (sem nota, só direção)

Marque mentalmente:

- [ ] Consigo justificar **local vs global** sem abrir a documentação.
- [ ] Sei explicar prop drilling e quando o Context ajuda.
- [ ] Consigo criar Provider com sintaxe React 19 **`<Context value={...}>`**.
- [ ] Entendo por que vários contextos pequenos podem ser melhores que um monólito.
- [ ] Sei nomear a diferença entre estado de **servidor** e estado de **cliente**.

Se algo pesar, volte a `estado-local-global.md` e `context-e-padroes.md` e refaça só o nível correspondente.

---

## Mensagem final

Bom gerenciamento de estado é **disciplina de organização**: menos “tecnologia mágica”, mais decisões claras. Cada exercício que você fecha é um padrão que seu cérebro reconhece mais rápido no próximo projeto. Boa prática.
