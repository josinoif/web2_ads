# Exercícios de fixação — Autenticação em React

Autenticação boa combina **frontend** (formulário, estado, rotas) e **contrato com o backend** (token, headers, erros). Estes exercícios fixam o que você viu em `conceitos-autenticacao.md` e `tutorial-autenticacao.md`: Context, armazenamento do token, `useActionState`, `useFormStatus`, rotas protegidas e boas práticas.

> **Como usar:** em exercícios com código, parta do projeto do tutorial ou replique a estrutura (`AuthProvider`, React Router v7). Para fluxos com API real, use sempre HTTPS em produção — em dev, `localhost` já basta para treinar.

**Formato de cada exercício:** leia **O que fazer** e confira com **Definição de pronto**. Se todos os itens da definição de pronto forem verdadeiros, o exercício está feito.

---

## Nível 1 — Conceitos e fluxo

**Objetivo:** saber **o que** está sendo protegido antes de **como** codar.

### 1. Vocabulário rápido

**O que fazer**

Responda **em uma frase cada**:

1. O que é **autenticação** neste curso (quem é o usuário)?
2. O que é um **token** no fluxo típico email/senha → API?
3. Para que serve o header **`Authorization: Bearer …`** nas requisições após o login?

**Definição de pronto**

- [ ] As três respostas estão corretas e não confundem “token” com “senha”.
- [ ] A frase sobre `Bearer` deixa claro que o servidor reconhece a sessão sem reenviar a senha crua a cada GET/POST.

**Fixação:** autenticação ≠ autorização fina (papéis/permissões); aqui o foco é identificar o usuário com token.

---

### 2. O que **não** guardar

**O que fazer**

Liste **três** coisas que você **não** deve persistir em `localStorage`/`sessionStorage` no fluxo de login descrito no material.

**Definição de pronto**

- [ ] A lista inclui **senha em texto puro** (ou equivalente óbvio).
- [ ] Pelo menos um item menciona dado sensível além da senha (ex.: número completo de cartão), ou reforça que só o necessário deve ser armazenado.

---

### 3. Sequência do fluxo

**O que fazer**

Numere de **1 a 5** os passos abaixo na **ordem correta** do fluxo feliz (primeiro login até acesso autenticado):

- A. Frontend envia token no header das próximas requisições.  
- B. Usuário envia credenciais no formulário de login.  
- C. Backend valida e devolve token (e opcionalmente dados do usuário).  
- D. Frontend guarda o token e atualiza estado (Context).  
- E. Usuário vê uma área protegida da aplicação.

**Definição de pronto**

- [ ] A ordem está correta de ponta a ponta.
- [ ] Você não colocou “área protegida” antes de existir token no cliente (exceto se explicar redirect para login — neste exercício a ordinação assume fluxo feliz após login).

---

## Nível 2 — Armazenamento e sessão

**Objetivo:** hidratar estado e escolher onde o token vive.

### 4. Hidratar o Context ao carregar a página

**O que fazer**

1. No `AuthProvider`, use `useEffect` na montagem para ler `localStorage.getItem('token')` (ou a chave que você padronizar).
2. Se existir token, atualize `token` e um objeto `user` mínimo no estado (pode ser fake como no tutorial: `{ nome: 'Usuário' }`).
3. Se não existir, mantenha `user` e `token` como `null`.

**Definição de pronto**

- [ ] Após login e **recarga completa (F5)** da página, o app ainda considera o usuário autenticado (desde que o token continue no storage).
- [ ] Com storage vazio, após recarga o app **não** acha que há usuário logado.

**Fixação:** quem decide “está logado?” deve combinar storage + estado; evite duplicar fontes da verdade sem sincronizar.

---

### 5. `localStorage` vs `sessionStorage`

**O que fazer**

1. Copie a tabela abaixo para seu caderno ou arquivo e preencha cada célula com **uma** destas opções: `localStorage`, `sessionStorage` ou **“depende”**.

| Cenário | Onde guardar o token? | Por quê? (uma frase) |
|--------|------------------------|----------------------|
| Banco interno: usuário pode fechar o navegador e voltar logado no dia seguinte | | |
| Cybercafé / computador compartilhado: quer minimizar persistência após fechar a aba | | |
| Mesma origem, várias abas: cada aba com sessão isolada | | |

**Definição de pronto**

- [ ] As três linhas têm escolha coerente com o comportamento real desses storages no navegador.
- [ ] A coluna “Por quê?” não repete só o nome do storage — explica consequência (persistência, fim ao fechar aba, etc.).

---

### 6. Logout completo

**O que fazer**

1. Implemente `logout` que: remove o token do **mesmo** storage usado no login; define `user` e `token` no Context como `null`.
2. Na UI do painel logado, um botão “Sair” chama `logout`.
3. Após logout, navegue manualmente para `/dashboard` (ou rota protegida): deve redirecionar para login ou equivalente.

**Definição de pronto**

- [ ] Depois de “Sair”, `localStorage` (ou `sessionStorage`) **não** contém mais o token na chave usada pelo app.
- [ ] Rotas protegidas ficam inacessíveis até novo login.

---

## Nível 3 — Formulário de login (React 19)

**Objetivo:** alinhar UX com `useActionState` e `useFormStatus`.

### 7. Validação no servidor da action (`useActionState`)

**O que fazer**

1. Formulário de login com `useActionState`, action **async** que lê `FormData` dos campos `email` e `senha`.
2. Se **qualquer um** estiver vazio após `trim()` no email, retorne `{ ok: false, erro: '…' }` com mensagem clara.
3. Se ambos preenchidos, chame a função `login` do Context (fake ou real) e retorne `{ ok: true, erro: null }` em caso de sucesso.
4. Mostre `state.erro` abaixo do form quando existir.

**Definição de pronto**

- [ ] Submit com campos vazios **não** chama `login` com sucesso fingido — o erro aparece na tela.
- [ ] Submit válido autentica e limpa o erro anterior.

**Fixação:** validação no cliente melhora UX; o backend ainda deve validar de verdade.

---

### 8. Botão de envio com `useFormStatus`

**O que fazer**

1. Componente separado `BotaoEnviar` (ou nome equivalente) que usa **`useFormStatus`** de `react-dom`.
2. O botão deve ser `type="submit"`, ficar `disabled` quando `pending` e alternar o rótulo entre **“Entrar”** e **“Enviando…”**.
3. Use esse botão **dentro** do `<form action={formAction}>` do login — sem passar `pending` por props do pai.

**Definição de pronto**

- [ ] Durante a action async, o botão não aceita cliques duplicados (`disabled`).
- [ ] `BotaoEnviar` não recebe prop `pending` do formulário.

---

### 9. Redirecionar após login bem-sucedido

**O que fazer**

1. Após `login` resolver com sucesso, o usuário deve ir para **`/dashboard`** (ou rota que você documentar).
2. Implemente **uma** destas abordagens (escolha e mantenha consistente):
   - `useEffect` que observa `isAuthenticated` e chama `navigate('/dashboard')`; **ou**
   - retorno da action acoplado a navegação no componente (descreva no comentário por que é seguro contra loop).
3. Garanta que usuário **já logado** que abre `/login` seja enviado para `/dashboard` (rota de login “curta” para quem tem sessão).

**Definição de pronto**

- [ ] Login válido sempre termina na área autenticada sem precisar clicar em outro link.
- [ ] Acessar `/login` com sessão ativa não mantém o formulário eternamente na tela — há redirect.

---

## Nível 4 — Rotas protegidas e navegação

**Objetivo:** segurança de navegação no mesmo nível do tutorial.

### 10. Componente `RotaProtegida`

**O que fazer**

1. Crie `RotaProtegida` que renderiza `children` só se `isAuthenticated` for verdadeiro no Context.
2. Caso contrário, renderize `<Navigate to="/login" replace />` do React Router.
3. Envolva **pelo menos** a rota `/dashboard` com esse componente na árvore de rotas.

**Definição de pronto**

- [ ] Abrir `/dashboard` sem token/sessão redireciona para `/login`.
- [ ] Com sessão válida, `/dashboard` renderiza o conteúdo sem flash incorreto persistente (aceitável um frame em Strict Mode dev).

---

### 11. Evitar “buraco” na URL

**O que fazer**

1. Configure uma rota coringa `path="*"` que redireciona para `/` ou para `/login` — **documente qual escolheu** e por quê em uma frase no código ou README do exercício.
2. Acesse `/rota-inventada` e verifique o destino.

**Definição de pronto**

- [ ] URL inválida não deixa a aplicação em branco sem feedback.
- [ ] A frase de documentação existe.

---

### 12. Navegação programática **sem** vazar estado inconsistente

**O que fazer**

1. No `Dashboard`, botão “Sair” chama `logout` **e** redireciona com `navigate('/login')` **ou** confie só no `<Navigate>` das rotas protegidas — escolha uma estratégia.
2. Em **duas frases**, explique por que chamar só `logout` pode ser suficiente se `RotaProtegida` estiver correta.

**Definição de pronto**

- [ ] Após clicar “Sair”, você **vê** a tela de login (ou home pública) sem precisar atualizar manualmente de forma estranha.
- [ ] O texto explica o papel do guard na navegação.

---

## Nível 5 — Integração com API e boas práticas

**Objetivo:** aproximar do mundo real sem abandonar o escopo do curso.

### 13. Header `Authorization` em uma requisição

**O que fazer**

1. Crie uma função `fetchPerfilAutenticado()` (nome livre) que faz `fetch` para uma URL fake (`https://jsonplaceholder.typicode.com/users/1` basta) **incluindo** o header `Authorization: Bearer ${token}` lido do Context ou do storage.
2. Chame essa função ao montar o `Dashboard` (ou ao clicar em “Carregar perfil”) e mostre `loading` / erro / dados na UI de forma simples.

**Definição de pronto**

- [ ] No DevTools → Network, a requisição mostra o header `Authorization` com o prefixo `Bearer `.
- [ ] Sem token, você **não** dispara a chamada ou mostra mensagem explícita “não autenticado”.

**Fixação:** o servidor é quem valida o token; o header é só o mecanismo de transporte.

---

### 14. Tratar **401 Unauthorized** (simulado)

**O que fazer**

1. Simule uma função `apiGet()` que retorna `Response` com `status === 401` (pode ser `Promise.resolve` com objeto fake `{ ok: false, status: 401 }` se não usar `fetch` real).
2. No cliente, se detectar 401, execute **`logout()`** e redirecione para `/login` (ou mostre toast + logout — **descreva** o comportamento escolhido).
3. Escreva **uma frase**: por que tratar 401 no cliente é importante mesmo com rota protegida?

**Definição de pronto**

- [ ] Após o 401 simulado, o usuário não permanece com UI de “logado”.
- [ ] A frase menciona token expirado ou revogado / inconsistência entre cliente e servidor.

---

### 15. HTTPS e superfície de ataque (reflexão)

**O que fazer**

Responda:

1. Por que armazenar token em `localStorage` **e** trafegar sem HTTPS em produção é especialmente arriscado?
2. Em **uma frase**, o que cookies **httpOnly** ajudam a mitigar em relação ao acesso via JavaScript?

**Definição de pronto**

- [ ] O item (1) menciona interceptação/man-in-the-middle ou equivalente válido.
- [ ] O item (2) indica que JS da página não lê o cookie (reduz XSS roubando token desse cookie).

---

### 16. Checklist antes de entregar um fluxo de login

**O que fazer**

Escreva **cinco** perguntas sim/não que **você** faria ao revisar seu próprio PR de autenticação (além de “funciona no happy path”). A primeira já está abaixo — complete com mais quatro.

1. O logout remove o token do storage **e** limpa o Context?
2. *(suas quatro perguntas)*

**Definição de pronto**

- [ ] Existem exatamente **cinco** perguntas no total.
- [ ] Pelo menos duas tocam em erro de rede, 401/expiração, ou dupla submissão do formulário.

---

## Autoavaliação honesta (sem nota, só direção)

Marque mentalmente:

- [ ] Sei explicar o fluxo login → token → header → rota protegida.
- [ ] Consigo implementar login com `useActionState` + `useFormStatus` sem `pending` manual no pai.
- [ ] Sei proteger rotas com `<Navigate>` e Context.
- [ ] Entendo diferença prática entre `localStorage` e `sessionStorage`.
- [ ] Sei o que fazer quando a API responde 401.

Algo falhou? Volte ao `tutorial-autenticacao.md` e refaça o passo equivalente antes de subir de nível.

---

## Mensagem final

Autenticação é contrato: o React organiza a experiência, mas o **servidor** é a fonte da verdade sobre quem pode entrar. Cada exercício aqui reduz uma ambiguidade que em produção vira incidente ou suporte infinito. Boa prática.
