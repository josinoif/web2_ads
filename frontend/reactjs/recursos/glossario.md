# Glossário — Termos do curso React (19)

| Termo | Definição |
|-------|-----------|
| **Componente** | Bloco de código (função ou classe) que retorna elementos React (JSX) e pode receber props e ter estado. Unidade básica de construção da interface. |
| **Props** | Propriedades passadas de um componente pai para um filho. Somente leitura no filho. No React 19, `ref` também é uma prop. |
| **Estado (state)** | Dados que podem mudar ao longo do tempo e que, ao serem atualizados, causam nova renderização do componente. Gerenciado por `useState`, `useReducer` ou `useActionState`. |
| **Hook** | Função especial do React que permite usar estado, efeitos e outros recursos em componentes funcionais. Ex.: `useState`, `useEffect`, `useContext`, `useActionState`, `use`. |
| **JSX** | Sintaxe que mistura JavaScript com marcação semelhante a HTML. É transformada em chamadas ao JSX runtime. |
| **Virtual DOM** | Representação em memória da árvore do DOM. O React compara com a árvore anterior e atualiza apenas o necessário no DOM real. |
| **Fiber** | Arquitetura interna do React que permite render interrompível e priorizado. |
| **Ciclo de vida** | Fases pelas quais um componente passa: montagem, atualização, desmontagem. Em funcionais, usa-se `useEffect`. |
| **Context (Contexto)** | Mecanismo do React para repassar dados pela árvore sem passar props em cada nível. Usa `createContext`, `<Context value={...}>` (React 19) e `useContext` ou `use`. |
| **SPA** | Single Page Application — aplicação que carrega uma página HTML e atualiza o conteúdo via JavaScript, sem recarregar. |
| **Rota** | Associação entre um caminho de URL e um componente. No React Router v7: `Route`, `path`, `element`, `Outlet`. |
| **Effect (efeito)** | Lógica que deve rodar após a renderização ou em resposta a mudanças (fetch, subscriptions, timers). Implementada com `useEffect`. |
| **Ref** | Referência a um elemento DOM ou a um valor que persiste entre renderizações sem causar re-render. Criada com `useRef`. No React 19, `ref` é passado como prop comum. |
| **Renderização** | Processo em que o React chama a função do componente, obtém o JSX e atualiza o DOM. |
| **Re-renderização** | Nova execução da função do componente (por mudança de estado/props), gerando nova árvore e possíveis atualizações no DOM. |
| **CSS Module** | Arquivo `.module.css` cujas classes são escopadas ao componente; evita conflito de nomes. |
| **Action** ⭐ | Função (síncrona ou assíncrona) passada a `<form action={...}>` ou disparada via `formAction`. Gerencia automaticamente o estado pendente e integra com `useActionState`, `useFormStatus`, `useOptimistic`. |
| **useActionState** ⭐ | Hook que associa uma Action a um estado; retorna `[state, formAction, isPending]`. |
| **useFormStatus** ⭐ | Hook (de `react-dom`) que lê, em um componente filho, o `pending`/`data` do `<form>` pai. |
| **useOptimistic** ⭐ | Hook que permite mostrar um estado otimista durante uma Action assíncrona. |
| **use** ⭐ | Hook do React 19 que lê o valor de uma Promise (suspende) ou de um Context. Pode ser usado em condicionais. |
| **Suspense** | Componente que mostra um `fallback` enquanto filhos estão "suspensos" (aguardando Promise, lazy, data). |
| **ErrorBoundary** | Componente que captura erros em sua subárvore e renderiza uma UI de fallback. |
| **React Compiler** ⭐ | Otimizador opt-in (React 19) que memoriza componentes/valores automaticamente em tempo de build. |
| **Document Metadata** | Em React 19, você pode renderizar `<title>`, `<meta>` e `<link>` em qualquer componente; o React hoista para o `<head>`. |
| **Server Components** | Componentes que executam no servidor, enviando apenas o JSX serializado ao cliente (usado em Next.js, etc.). |
| **Server Actions** | Funções marcadas com `"use server"` que executam no servidor mas podem ser chamadas do cliente como Actions. |
| **StrictMode** | Componente de desenvolvimento que ajuda a detectar efeitos sem cleanup ao montar/desmontar o componente duas vezes. |
| **Prop drilling** | Passar props por muitos níveis. Context e hooks customizados ajudam a evitar. |
| **createRoot** | API de `react-dom/client` usada para montar uma árvore React no DOM. Substituiu `ReactDOM.render`. |
