# ✅ Projeto Final – Sistema de Gerenciamento de Produtos

## 🎯 Objetivo

Desenvolver uma aplicação **web fullstack** com autenticação via **JWT**, listagem e gerenciamento de produtos via **CRUD**, e estrutura modular, utilizando **Angular no frontend** e uma **API backend desenvolvida em Node.js (Express ou NestJS) ou Python (Flask ou FastAPI)**.

------

## 🧑‍💻 Tecnologias permitidas

- **Frontend:** Angular 15 ou superior
- **Backend (à escolha do aluno):**
  - Node.js com **Express**
  - Node.js com **NestJS**
  - Python com **Flask** ou **FastAPI**

------

## 📌 Descrição Geral

O projeto será composto por:

- Um **frontend Angular** com:
  - Autenticação com JWT
  - Telas de login, listagem, cadastro e edição de produtos
  - Navegação protegida por autenticação
  - Formulários reativos com validação
  - Tratamento de erros e exibição de mensagens
- Um **backend RESTful** com:
  - Endpoint de login que gera um token JWT
  - Endpoints protegidos para listar, criar, editar e excluir produtos
  - Validações e mensagens de erro adequadas

------

## 🖧 Backend – Especificação da API

### 1. `POST /auth/login`

Autentica o usuário e retorna um token JWT.

**Request:**

```json
{ "username": "admin", "password": "123456" }
```

**Response (200):**

```json
{ "token": "<jwt_token>" }
```

**Response (401):**

```json
{ "erro": "Usuário ou senha inválidos" }
```

------

### 2. `GET /produtos`

Lista todos os produtos.

**Cabeçalho:** `Authorization: Bearer <token>`

**Response (200):**

```json
[
  { "id": 1, "nome": "Notebook", "preco": 3500.0, "categoria": "Informática" }
]
```

------

### 3. `GET /produtos/:id`

Busca um produto específico pelo ID.

**Response (200):**

```json
{ "id": 1, "nome": "Notebook", "preco": 3500.0, "categoria": "Informática" }
```

**Response (404):**

```json
{ "erro": "Produto não encontrado" }
```

------

### 4. `POST /produtos`

Cria um novo produto.

**Request Body:**

```json
{ "nome": "Mouse", "preco": 89.9, "categoria": "Acessórios" }
```

**Response (201):**

```json
{ "id": 2, "nome": "Mouse", "preco": 89.9, "categoria": "Acessórios" }
```

------

### 5. `PUT /produtos/:id`

Atualiza os dados de um produto.

**Request Body:**

```json
{ "nome": "Mouse sem fio", "preco": 99.9, "categoria": "Acessórios" }
```

**Response (200):**

```json
{ "id": 2, "nome": "Mouse sem fio", "preco": 99.9, "categoria": "Acessórios" }
```

------

### 6. `DELETE /produtos/:id`

Remove um produto.

**Response (204):** (sem corpo)

**Response (404):**

```json
{ "erro": "Produto não encontrado" }
```

------

## ✅ Regras de Negócio

- Todos os endpoints de produto devem exigir token JWT
- Validações obrigatórias:
  - `nome`: mínimo 3 caracteres
  - `preco`: maior que 0
  - `categoria`: obrigatório
- Mensagens de erro devem ser claras e padronizadas

------

## 🖥️ Frontend – Angular

### Telas obrigatórias

| Tela                     | Funcionalidade                                               |
| ------------------------ | ------------------------------------------------------------ |
| **Login**                | Formulário para envio de usuário e senha, integração com a rota `/auth/login`. Armazena token e redireciona para listagem. |
| **Listagem de produtos** | Lista os produtos retornados da API com botões de editar e excluir. Exibe mensagens em caso de erro. |
| **Cadastro de produto**  | Formulário reativo com validação. Ao submeter, chama `POST /produtos`. |
| **Edição de produto**    | Formulário reativo preenchido via `GET /produtos/:id`. Atualiza via `PUT`. |
| **Logout**               | Remove o token JWT do `localStorage` e redireciona para login. |
| **Feedback visual**      | Mensagens de erro e sucesso devem ser exibidas na interface de forma clara e amigável. |

### Funcionalidades técnicas exigidas

- Uso de **Reactive Forms**
- Validações no formulário (ex: campos obrigatórios, preços válidos)
- Uso de `HttpClient` para comunicação com a API
- Proteção de rotas com **`AuthGuard`**
- Uso de **interceptor HTTP** para enviar o token nas requisições
- Organização modular: `auth`, `produtos`, `core`, `shared`

------

## 📦 Entregáveis

1. Repositório no GitHub contendo:
   - Código do frontend Angular
   - Código do backend (Express, NestJS, Flask ou FastAPI)
   - README com instruções claras para rodar o projeto
2. Link para vídeo curto de demonstração do projeto (3 a 5 minutos), explicando:
   - Fluxo de autenticação
   - CRUD de produtos
   - Estrutura do projeto

------

## 🧮 Critérios de Avaliação

| Critério                                            | Peso |
| --------------------------------------------------- | ---- |
| Autenticação funcional com JWT                      | 2.0  |
| Proteção de rotas com `AuthGuard` e verificação JWT | 1.0  |
| CRUD completo de produtos                           | 2.0  |
| Formulários reativos com validações                 | 1.0  |
| Tratamento de erros no frontend e backend           | 1.0  |
| Feedback visual (mensagens de sucesso/erro)         | 0.5  |
| Estrutura modular e boas práticas no frontend       | 1.0  |
| Organização geral, clareza de código e README       | 1.0  |
| Apresentação em vídeo                               | 0.5  |

> **Nota máxima: 10.0 pontos**

------

## 💡 Extras (opcionais para nota bônus ou portfólio)

- Filtro e busca na listagem
- Paginação
- Upload de imagem (com base64 ou multipart)
- Testes unitários simples para serviços e componentes
- Layout com Angular Material ou Bootstrap
- Deploy do frontend (ex: Vercel) e backend (ex: Render, Railway, Heroku)

