# Conceitos: FastAPI e APIs escaláveis

## O que é o FastAPI?

O **FastAPI** é um framework moderno, rápido e eficiente para a criação de APIs em Python. Lançado em 2018, ele foi projetado para aproveitar a tipagem do Python (type hints) e o padrão **OpenAPI** para oferecer validação automática de dados, documentação interativa e alto desempenho.

Principais características:

- **Baseado em padrões**: OpenAPI (ex-Swagger) e JSON Schema para documentação e validação.
- **Tipagem**: Uso de type hints para validação automática de requisições e respostas.
- **Performance**: Um dos frameworks mais rápidos para Python, comparável a Node.js e Go, graças ao uso de **ASGI** (Async Server Gateway Interface) e à escolha de ferramentas como **Starlette** e **Pydantic**.
- **Assíncrono**: Suporte nativo a `async`/`await`, ideal para I/O (banco de dados, chamadas HTTP, filas).

## Por que FastAPI para APIs escaláveis?

### 1. APIs sem estado (stateless)

FastAPI não impõe sessão no servidor: cada requisição pode ser tratada de forma independente. Isso facilita escalar horizontalmente (várias instâncias atrás de um balanceador de carga) e usar autenticação por token (JWT), que não depende de estado no servidor.

### 2. Assincronismo

Rotas assíncronas permitem que o servidor atenda a muitas requisições concorrentes sem bloquear em operações de I/O (banco, rede). Isso melhora a utilização de recursos e a capacidade de resposta sob carga.

### 3. Documentação e contrato da API

A documentação OpenAPI é gerada automaticamente a partir dos tipos e dos endpoints. Isso reduz erros de integração, facilita o consumo por clientes e permite testes direto na interface Swagger/ReDoc.

### 4. Validação e segurança

Pydantic valida entrada e saída; FastAPI integra bem com OAuth2 e JWT. Menos bugs de dados e uma base sólida para autenticação e autorização.

### 5. Boas práticas de estrutura

O ecossistema FastAPI (rotas, dependências, schemas separados dos modelos de banco) incentiva uma estrutura modular e testável, o que é fundamental para APIs que crescem.

## OpenAPI e documentação

FastAPI gera automaticamente um esquema **OpenAPI** (versão 3.x) a partir das rotas, parâmetros e modelos Pydantic. Com isso você obtém:

- **Swagger UI** (`/docs`): interface interativa para testar os endpoints.
- **ReDoc** (`/redoc`): documentação legível para humanos.

Não é necessário escrever a documentação à mão; mantê-la atualizada é consequência de definir bem os tipos e os endpoints.

## Quando usar FastAPI?

- **APIs REST** (e também GraphQL com bibliotecas adicionais).
- **Microserviços** que precisam de alta performance e documentação clara.
- **Projetos novos** em Python que priorizam tipagem, validação e documentação automática.

Quando considerar outras opções:

- Aplicações com muitas páginas HTML e pouca API (Django ou Flask podem ser mais adequados).
- Equipe ou ecossistema já consolidados em outro framework.

## Visão geral do curso

Neste curso você verá, em sequência:

1. **Introdução e primeiro projeto**: instalação, estrutura de pastas, primeiro endpoint.
2. **Rotas e dependências**: APIRouter, Depends, parâmetros (path, query, body).
3. **Persistência com ORM**: SQLAlchemy, engine, session, modelos.
4. **CRUD completo**: schemas Pydantic, padrão CRUD com banco de dados.
5. **Autenticação**: JWT, hash de senha, login e proteção de rotas.
6. **Autorização**: papéis (roles), restrição de acesso por perfil.
7. **Documentação**: tags, descrições, exemplos e Bearer no OpenAPI.
8. **WebSocket** (opcional): comunicação em tempo real.
9. **Projeto integrador**: API de Quiz aplicando todos os conceitos.

Com isso você terá base para implementar sozinho uma API escalável em Python usando FastAPI, ORM, autenticação, autorização e documentação.
