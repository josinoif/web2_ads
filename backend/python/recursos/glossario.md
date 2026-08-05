# Glossário

Termos usados ao longo do curso de APIs com FastAPI.

- **APIRouter**: componente do FastAPI que agrupa rotas sob um prefixo e tags; é incluído na aplicação com `app.include_router()`.

- **ASGI**: Async Server Gateway Interface; padrão de interface entre servidor e aplicação em Python para suporte a async. O FastAPI é uma aplicação ASGI.

- **Autorização**: processo de determinar o que um usuário autenticado pode acessar ou executar (ex.: por papel ou escopo).

- **Autenticação**: processo de verificar a identidade do usuário (ex.: login com senha, validação de token JWT).

- **Bearer token**: token enviado no cabeçalho HTTP `Authorization: Bearer <token>`. Usado para JWT em APIs REST.

- **CRUD**: Create, Read, Update, Delete; operações básicas sobre um recurso.

- **Depends**: função/classe do FastAPI que implementa injeção de dependências; usada para obter sessão do banco, usuário atual, etc.

- **Engine (SQLAlchemy)**: objeto que gerencia o pool de conexões e a URL do banco; criado com `create_engine()`.

- **JWT**: JSON Web Token; padrão para tokens assinados que carregam claims (ex.: identificador do usuário, papel, expiração).

- **Migration**: alteração versionada do esquema do banco (tabelas, colunas); ferramentas como Alembic automatizam isso.

- **Model (ORM)**: classe Python que mapeia uma tabela no banco (SQLAlchemy); atributos são colunas.

- **OpenAPI**: especificação para descrever APIs REST; o FastAPI gera o esquema OpenAPI automaticamente.

- **ORM**: Object-Relational Mapping; técnica que mapeia tabelas para objetos na linguagem de programação.

- **OAuth2PasswordBearer**: esquema de segurança do FastAPI que indica que a rota espera um Bearer token (ex.: JWT) no header Authorization.

- **Pydantic**: biblioteca de validação e serialização baseada em type hints; usada pelo FastAPI para body, query e response_model.

- **RBAC**: Role-Based Access Control; controle de acesso baseado em papéis (ex.: admin, user).

- **ReDoc**: interface de documentação legível gerada a partir do OpenAPI; no FastAPI em `/redoc`.

- **Schema (Pydantic)**: modelo Pydantic que define formato de entrada ou saída da API (validação e documentação).

- **Session (SQLAlchemy)**: unidade de trabalho que agrupa operações no banco; em APIs, normalmente uma sessão por requisição.

- **Swagger UI**: interface interativa para testar a API; no FastAPI em `/docs`.

- **Uvicorn**: servidor ASGI usado para rodar aplicações FastAPI em desenvolvimento e produção.

- **WebSocket**: protocolo de comunicação bidirecional em tempo real; FastAPI expõe endpoints com `@app.websocket()`.
