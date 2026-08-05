# Conceitos: Autorização em APIs

## O que é autorização?

**Autorização** é o processo de determinar quais recursos ou ações um usuário (ou sistema) autenticado tem permissão para acessar ou executar. Enquanto a **autenticação** responde à pergunta "Quem é você?", a **autorização** responde "O que você pode fazer?".

Em uma API, após identificar o usuário (por exemplo, via JWT), a autorização decide se ele pode acessar um endpoint, um recurso específico (ex.: editar apenas o próprio perfil) ou um conjunto de dados filtrado por perfil.

## Autenticação vs autorização

- **Autenticação**: verificar identidade (login, token).
- **Autorização**: verificar permissão (papel, escopo, recurso).

Ambas são necessárias: primeiro autenticamos; depois, com a identidade conhecida, aplicamos regras de autorização.

## RBAC (Role-Based Access Control)

**RBAC** é um modelo em que as permissões são agrupadas em **papéis** (roles). Usuários recebem um ou mais papéis (ex.: `admin`, `user`, `moderator`). Cada endpoint ou recurso é protegido por uma regra do tipo "apenas role X pode acessar". A verificação na rota consiste em checar se o usuário atual possui o papel exigido.

Vantagens: simples de entender e implementar; fácil de auditar ("quem é admin?"). Desvantagens: menos flexível que permissões granulares por recurso (ex.: "pode editar apenas o próprio post").

## Escopos (scopes)

Em vez de (ou além de) papéis, alguns sistemas usam **escopos** (scopes): permissões finas como `read:users`, `write:posts`. O token (JWT ou OAuth2) pode carregar uma lista de escopos; a API verifica se o escopo necessário está presente. Isso permite controle mais granular e é comum em APIs públicas e OAuth2.

Para um curso introdutório, RBAC com um campo `role` no usuário (ou no payload do JWT) é suficiente; os mesmos conceitos se estendem para escopos.

## Implementação no FastAPI

1. **Dado do usuário**: o usuário (modelo ou payload do JWT) deve ter um campo `role` (ex.: `admin`, `user`).
2. **Dependência de autorização**: uma função que recebe o usuário atual (via `get_current_user`) e o papel exigido; se o usuário não tiver esse papel, levanta 403 (Forbidden).
3. **Uso nas rotas**: a rota declara `Depends(role_required("admin"))` (ou similar). O FastAPI primeiro resolve `get_current_user` e depois a dependência de role; se alguma falhar, retorna 401 ou 403.

Assim, rotas públicas não usam dependência de auth; rotas apenas autenticadas usam `get_current_user`; rotas restritas a um papel usam a dependência que verifica o role.
