# Ecossistema React e bibliotecas úteis (2026)

## Introdução

O React é uma biblioteca focada em interface; para roteamento, formulários, UI pronta e gerenciamento de estado avançado, a comunidade oferece **bibliotecas** que se integram bem. Esta é uma visão panorâmica do ecossistema moderno em torno do **React 19**.

---

## Roteamento

- **React Router v7** (`react-router-dom`): padrão de fato para SPA. Unificação com Remix trouxe `loader`, `action`, `defer`, `RouterProvider` e modo "Data Router". Fornece `BrowserRouter`, `Routes`, `Route`, `Link`, `NavLink`, `useNavigate`, `useParams`, `Outlet`.
- **TanStack Router**: alternativa com tipagem de rotas forte (TypeScript-first).

---

## UI e componentes prontos

| Biblioteca | Destaque |
|------------|----------|
| **Material-UI (MUI)** | Ecossistema maduro, Material Design, dashboards |
| **Chakra UI** | Acessibilidade, temas fáceis, boa DX |
| **Ant Design** | Componentes ricos para apps internos/admin |
| **shadcn/ui** | Radix + Tailwind, componentes copiados para seu projeto |
| **Radix UI** | Primitivos não estilizados (ótimo para design systems) |
| **Mantine** | Grande conjunto, inclui hooks utilitários |
| **React Bootstrap** | Bootstrap em React |

Escolha conforme o visual desejado, a integração com seu design system e o trade-off entre customização e produtividade.

---

## Formulários

- **React Hook Form**: foca em performance com renderizações mínimas; integra com **Zod**/**Yup** para validação via `zodResolver`.
- **Formik**: alternativa clássica com API declarativa.
- **No React 19**: para formulários simples, **`useActionState` + `<form action>`** dispensa lib em muitos casos.

---

## Estado global avançado

- **Zustand**: store leve, API minimalista; excelente substituto para Context em casos médios.
- **Jotai**: estado atômico (cada peça é um `atom`), útil para apps com muitos estados independentes.
- **Redux Toolkit**: Redux moderno, com `createSlice` e `RTK Query` (cache de API).
- **Valtio**: estado proxy-based, leitura "natural".

> Regra prática: comece com `useState`/`useReducer`, promova para Context quando compartilhar, passe para Zustand/Redux Toolkit quando Context virar gargalo.

---

## Dados de servidor (cache de API)

- **TanStack Query (React Query)**: *o padrão* para fetch com cache, revalidação, retry, invalidação e suspense. Use em listagens/detalhes de API.
- **SWR** (Vercel): simples, inspirado em "stale-while-revalidate"; boa opção mais leve.
- **RTK Query** (Redux Toolkit): se você já usa Redux, vale aproveitar.

---

## HTTP

- **Axios**: cliente com interceptors, cancelamento, suporte a FormData, bem conhecido.
- **ky** / **ofetch**: wrappers modernos sobre `fetch` com melhor DX.
- **`fetch`** nativo é suficiente para muitos casos.

---

## Testes

- **Vitest**: runner rápido, compatível com Jest, integra com Vite.
- **React Testing Library**: testes do ponto de vista do usuário (render, interação).
- **Playwright** / **Cypress**: testes E2E no navegador.

---

## Tipagem e qualidade

- **TypeScript**: quase padrão em projetos novos.
- **Zod**: validação com inferência de tipos.
- **ESLint** + `eslint-plugin-react-hooks`: lint de hooks e boas práticas.
- **Prettier**: formatação automática.

---

## Performance e otimização

- **React Compiler** (opt-in no React 19): memorização automática. Quando ativo, reduz muito o uso manual de `useMemo`/`useCallback`.
- **React DevTools**: inspeção da árvore, props, estado.
- **React Scan**: visualiza re-renders em tempo real.

---

## Frameworks full-stack sobre React

- **Next.js**: SSR, SSG, Server Components, Server Actions. É praticamente o "Rails" do React.
- **Remix** (agora integrado ao React Router v7): loaders/actions no servidor, foco em web standards.
- **RedwoodJS**, **Waku**: alternativas emergentes.

Se o projeto precisa de SEO, SSR e Server Components, **Next.js** é o caminho mais trilhado.

---

## Ferramentas de build

- **Vite 8**: recomendação para SPAs em React 19; build rápido com Rolldown (Rust) em beta.
- **Turbopack** (dentro do Next.js): substituirá gradualmente o Webpack.
- **esbuild** / **swc**: transpilers que o Vite e Next usam por baixo.

---

## Conclusão

O ecossistema React em 2026 é maduro e ofertas bem consolidadas cobrem cada necessidade: **React Router v7** para rotas, **TanStack Query** para dados de API, **Zustand/Redux Toolkit** para estado global avançado, **shadcn/ui + Tailwind** ou **MUI/Chakra** para UI, **React Hook Form + Zod** para formulários complexos, **Vitest + RTL** para testes. Consulte a pasta [recursos](../recursos/) para glossário e referências.
