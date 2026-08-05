# Exercícios de fixação — Arquivos no frontend (upload e download)

Arquivo não é “só mais um campo”: tipo, tamanho, `FormData` e segurança aparecem rápido. Estes exercícios fixam o que você viu em `conceitos-arquivos.md` e `tutorial-arquivos.md`: `input type="file"`, **File** / **Blob**, **FormData**, upload com **`useActionState`** + **`useFormStatus`**, preview e download.

> **Como usar:** use um projeto Vite + React 19. Para POST real de teste, pode seguir o tutorial com [httpbin.org](https://httpbin.org) ou endpoint equivalente que aceite `multipart/form-data`.

**Formato de cada exercício:** leia **O que fazer** e confira com **Definição de pronto**. Se todos os itens da definição de pronto forem verdadeiros, o exercício está feito.

---

## Nível 1 — Conceitos e File API

**Objetivo:** nomear os blocos antes de empilhar código.

### 1. Objetos do navegador

**O que fazer**

Responda **em uma frase cada**:

1. O que é um objeto **`File`** no contexto de `<input type="file">`?
2. Em uma palavra: **`File`** estende qual tipo base da Web API mencionado no material?
3. O que é **`FileList`** e onde ele aparece tipicamente no evento de mudança do input?

**Definição de pronto**

- [ ] A resposta (2) menciona **Blob** (ou equivalente correto).
- [ ] A resposta (3) indica `files` / `e.target.files` ou equivalente.

---

### 2. FormData no upload

**O que fazer**

1. Explique **em duas frases** por que `formData.append('arquivo', file)` é usado ao montar o corpo de um POST multipart.
2. No fluxo do tutorial com `<form action={formAction}>`, **quem** monta o primeiro `FormData` que chega na action?

**Definição de pronto**

- [ ] O item (1) menciona multipart / campos nomeados / servidor ler pelo nome do campo.
- [ ] O item (2) deixa claro que é o **navegador/React** a partir do `<form>` e dos `name` dos inputs (não você digitando campo a campo manualmente antes do submit).

**Fixação:** o nome do campo (`name="arquivo"`) deve combinar com o que o backend espera.

---

### 3. Validação em duas camadas

**O que fazer**

Escreva **duas frases**: por que validar tipo/tamanho **no frontend** e por que ainda assim validar **no backend**?

**Definição de pronto**

- [ ] Menciona UX ou feedback rápido para o usuário.
- [ ] Menciona que o cliente pode ser contornado / segurança / fonte da verdade no servidor.

---

## Nível 2 — Input file e validações básicas

**Objetivo:** dominar seleção, vazio e limites antes da rede.

### 4. Campo obrigatório e arquivo vazio

**O que fazer**

1. Formulário com `<input type="file" name="arquivo" />` dentro de `<form action={formAction}>`.
2. Na action async de `useActionState`, obtenha o arquivo com `formData.get('arquivo')`.
3. Se não for instância de `File`, ou se `size === 0`, retorne estado de erro com mensagem explícita (ex.: “Selecione um arquivo válido.”).

**Definição de pronto**

- [ ] Submit sem escolher arquivo mostra o erro (não mensagem de sucesso).
- [ ] A verificação usa `instanceof File` e `size` conforme o enunciado.

---

### 5. Limite de tamanho no cliente

**O que fazer**

1. Defina uma constante `MAX_MB` (ex.: `2`) e rejeite arquivos maiores que esse limite **antes** de chamar `axios.post` ou `fetch`.
2. A mensagem de erro deve incluir o valor do limite em MB para o usuário entender.

**Definição de pronto**

- [ ] Arquivo artificialmente “grande” (ou mock com `size` fake se você simular) é bloqueado sem enviar POST.
- [ ] Arquivo abaixo do limite ainda pode ser enviado normalmente.

---

### 6. Filtrar por tipo (`accept` + checagem)

**O que fazer**

1. No `<input type="file">`, use `accept="image/png,image/jpeg"` (ou `accept="image/*"` — **documente** qual usou).
2. Na action, se `file.type` não for permitido, retorne erro (lista explícita no código dos MIME types aceitos).
3. Explique **uma frase** por que `accept` sozinho não é segurança.

**Definição de pronto**

- [ ] Tentativa com tipo não permitido (ex.: `.pdf` se só imagens) resulta em erro na UI.
- [ ] A frase sobre `accept` menciona que o usuário/browser pode contornar ou que validação real é no servidor.

---

## Nível 3 — React 19: form Actions e UX

**Objetivo:** mesmo padrão do tutorial, com variações.

### 7. Estado da action (`useActionState`)

**O que fazer**

1. Estado inicial `{ status: 'idle', mensagem: '' }` com transições para `'success'`, `'error'` e opcionalmente `'idle'` após reset.
2. Em sucesso, mostre mensagem em estilo distinto do erro (classes CSS ou inline).
3. Após um sucesso, um novo envio com erro deve **substituir** a mensagem de sucesso pela de erro (sem acumular parágrafos antigos).

**Definição de pronto**

- [ ] Sempre há no máximo **uma** mensagem de resultado visível por vez vinda do `state`.
- [ ] `status` controla qual estilo aparece.

**Fixação:** `useActionState` centraliza o retorno da action — evite duplicar `useState` para o mesmo fim.

---

### 8. `BotaoEnviar` com `useFormStatus`

**O que fazer**

1. Componente isolado que usa `useFormStatus` de `react-dom`.
2. Botão `type="submit"`, `disabled` quando `pending`, texto **“Enviando…”** durante a action async.
3. O componente **não** recebe `pending` por props.

**Definição de pronto**

- [ ] Durante um POST lento (simule com `await new Promise(r => setTimeout(r, 1500))`), o botão não aceita double-click útil.
- [ ] O pai do botão não gerencia `pending` manualmente.

---

### 9. Vários campos no mesmo envio

**O que fazer**

1. No mesmo `<form>`, além do arquivo, inclua `<input name="descricao" />` (texto livre).
2. Na action, leia `formData.get('descricao')` e valide: se estiver vazio após `trim()`, erro antes do upload.
3. No `FormData` enviado à API (se você montar um segundo `fd` como no tutorial), faça `append` da **descrição** e do **arquivo** com nomes distintos (`descricao`, `arquivo`).

**Definição de pronto**

- [ ] Sem descrição, o arquivo não é enviado.
- [ ] Com descrição + arquivo válidos, o POST inclui os dois campos (confira no DevTools → Payload).

---

## Nível 4 — Preview e leitura local

**Objetivo:** FileReader e responsabilidades no cliente.

### 10. Preview de imagem com `FileReader`

**O que fazer**

1. Ao selecionar um arquivo **imagem** (`image/*`), use `FileReader` com **`readAsDataURL`** e guarde o resultado em estado React.
2. Mostre uma `<img>` com `src` igual ao data URL **somente** quando houver preview válido.
3. Se o arquivo não for imagem, não quebre a página: mostre mensagem “Preview indisponível” ou limpe o preview.

**Definição de pronto**

- [ ] Trocar a seleção para outra imagem atualiza o preview.
- [ ] Arquivo não imagem não deixa `src` inválido sem tratamento.

**Fixação:** preview é conveniência; o upload ainda usa o `File` original.

---

### 11. Limpar input e preview

**O que fazer**

1. Botão **“Limpar”** que:
   - redefine o estado do preview para `null`;
   - permite selecionar **de novo** o **mesmo** arquivo após limpar (dica: `inputRef.current.value = ''`).
2. Descreva em **uma frase** por que sem resetar o input o `onChange` pode não disparar ao escolher o mesmo arquivo.

**Definição de pronto**

- [ ] Após “Limpar”, não permanece imagem antiga na tela.
- [ ] Selecionar o mesmo arquivo outra vez funciona.

---

### 12. Múltiplos arquivos (`multiple`)

**O que fazer**

1. Adicione `multiple` ao input e `name` consistente (ex.: `arquivos`).
2. Na action, obtenha **todos** os arquivos via `formData.getAll('arquivos')` e filtre apenas instâncias de `File`.
3. Faça um loop `append` no `FormData` enviado à API **ou** envie o primeiro apenas — **documente na UI** qual estratégia você escolheu e por quê.

**Definição de pronto**

- [ ] Selecionar 3 arquivos e enviar resulta em comportamento coerente com o que você documentou (3 no POST ou só o primeiro).
- [ ] Nenhum erro ao iterar lista vazia.

---

## Nível 5 — Download, blobs e integração

**Objetivo:** fechar o ciclo como em produção.

### 13. Download simulado com blob + Object URL

**O que fazer**

1. Implemente uma função `baixarTextoFake(nomeArquivo, conteudo)` que:
   - cria um `Blob` com `type` adequado (ex.: `text/plain;charset=utf-8`);
   - usa `URL.createObjectURL(blob)`;
   - cria `<a>` temporário com `download={nomeArquivo}`, dispara `click()`;
   - chama **`URL.revokeObjectURL(href)`** após o click (ou após pequeno timeout) para liberar memória.
2. Um botão na UI chama essa função com nome e texto fixos para teste.

**Definição de pronto**

- [ ] O arquivo baixa no navegador com o nome esperado.
- [ ] O código chama `revokeObjectURL` em algum momento após o uso.

**Fixação:** sem `revoke`, URLs acumulam e consumem memória em fluxos longos.

---

### 14. `fetch` + blob de URL pública

**O que fazer**

1. Função async que faz `fetch` em uma URL que retorna arquivo (ex.: imagem pública de placeholder ou endpoint de documentação estável).
2. Converta `res.blob()`, gere object URL e dispare download com nome sugerido **ou** abra em nova aba — **escolha uma** e explique em um comentário limitações de CORS se aparecerem.

**Definição de pronto**

- [ ] Trata `!res.ok` com mensagem de erro na UI.
- [ ] Comente ou documente o que acontece se CORS bloquear.

---

### 15. Comparar estratégias de download

**O que fazer**

Preencha a tabela (uma frase curta por célula):

| Estratégia | Quando é mais simples | Principal risco ou limitação |
|------------|------------------------|------------------------------|
| Link `<a href={urlApi} download>` direto | | |
| `fetch` → blob → Object URL | | |

**Definição de pronto**

- [ ] As duas linhas estão preenchidas com raciocínio plausível (CORS, mesmo origin, headers, etc.).

---

### 16. Checklist antes de subir upload para produção

**O que fazer**

Liste **cinco** perguntas sim/não para revisar seu PR de upload (além de “testei com arquivo pequeno”). A primeira já está abaixo — complete com quatro.

1. O backend valida tipo e tamanho independentemente do frontend?
2. *(suas quatro perguntas)*

**Definição de pronto**

- [ ] Existem exatamente **cinco** perguntas no total.
- [ ] Pelo menos uma pergunta cobre HTTPS, autenticação do endpoint ou limite de taxa/abuse.

---

## Autoavaliação honesta (sem nota, só direção)

Marque mentalmente:

- [ ] Sei obter `File` a partir de `FormData` na action do formulário.
- [ ] Sei montar POST multipart com um ou mais `append`.
- [ ] Sei usar `useActionState` + `useFormStatus` sem estado duplicado para `pending`.
- [ ] Sei gerar download a partir de `Blob` sem vazar Object URLs.
- [ ] Sei explicar por que validação só no cliente não basta.

Travou em algum passo? Refaça o passo correspondente em `tutorial-arquivos.md`.

---

## Mensagem final

Upload bom é **contrato com o servidor**: nome do campo, tipo, limite e erro claro para o usuário. Download bom é **liberar memória** e respeitar CORS. Cada exercício aqui evita um tipo clássico de bug ou frustração em produção. Boa prática.
