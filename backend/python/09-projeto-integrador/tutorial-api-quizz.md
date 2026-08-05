# Tutorial: Projeto integrador – API de Quiz

Este tutorial integra os conceitos dos módulos 04 a 07: você vai construir uma API para o domínio **Quiz**, com CRUD, autenticação JWT, autorização por papéis e documentação. O modelo de domínio está descrito no diagrama [classes.puml](../projetos/quizz/classes.puml) (Usuario, Questionario, Questao, Alternativa, Tentativa, Resposta).

## Objetivos

- Aplicar CRUD com SQLAlchemy e Pydantic (módulo 04).
- Implementar registro e login com JWT e hash de senha (módulo 05).
- Restringir algumas rotas por papel (ex.: apenas admin pode remover questionários) (módulo 06).
- Documentar a API com tags e descrições (módulo 07).

## Domínio (resumo)

Consulte o arquivo [projetos/quizz/classes.puml](../projetos/quizz/classes.puml) para o diagrama completo. Relacionamentos principais:

- **Usuario**: cria Questionarios e realiza Tentativas. Na API, Usuario terá também `senha` (hash) e `role` (ex.: "user", "admin").
- **Questionario**: pertence a um Usuario; contém Questoes.
- **Questao**: pertence a um Questionario; possui Alternativas.
- **Alternativa**: pertence a uma Questao; tem flag `correta`.
- **Tentativa**: feita por um Usuario em um Questionario; contém Respostas.
- **Resposta**: associa Tentativa, Questao e Alternativa escolhida; indica se a resposta foi correta.

## Estrutura do projeto sugerida

```
quizz-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py      # Usuario, Questionario, Questao, Alternativa, Tentativa, Resposta
│   ├── schemas.py     # Pydantic v2 para todos
│   ├── security.py    # JWT, hash de senha
│   ├── auth.py        # get_current_user, role_required
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py    # register, token, me
│   │   ├── usuarios.py
│   │   ├── questionarios.py
│   │   ├── questoes.py
│   │   └── ...
│   └── crud/          # opcional: funções por entidade
├── projetos/
│   └── quizz/
│       └── classes.puml
├── venv/
└── requirements.txt
```

## Passo 1: Ambiente e dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart
pip freeze > requirements.txt
```

## Passo 2: Banco de dados e modelos

- **database.py**: engine SQLite (ou MySQL), `SessionLocal`, `Base`, `get_db()` (igual aos módulos 03 e 04).
- **models.py**: defina os modelos SQLAlchemy conforme o diagrama. Para **Usuario**, inclua:
  - `id`, `nome`, `email` (unique), `hashed_password`, `role` (String, default `"user"`).
  - Relacionamentos: `questionarios`, `tentativas`.
- Demais entidades: **Questionario** (com `usuario_id`, `criado_em`), **Questao** (com `questionario_id`), **Alternativa** (com `questao_id`, `correta`), **Tentativa** (com `usuario_id`, `questionario_id`, `data_hora`, `score`), **Resposta** (com `alternativa_id`, `questao_id`, `tentativa_id`, `correta`). Use `relationship` e `ForeignKey` conforme o diagrama.

Em `main.py`, chame `models.Base.metadata.create_all(bind=database.engine)` na inicialização.

## Passo 3: Schemas Pydantic (v2)

Use **Pydantic v2**: `ConfigDict(from_attributes=True)` nos schemas de resposta e `model_dump()` onde for converter para dict.

- **Usuario**: `UsuarioBase` (nome, email), `UsuarioCreate` (nome, email, senha, role opcional), `Usuario` (id, nome, email, role; sem senha). Nos schemas de resposta, não exponha a senha.
- **Questionario**, **Questao**, **Alternativa**, **Tentativa**, **Resposta**: padrão Base / Create / Update / Response conforme o módulo 04. Inclua IDs e campos de relacionamento quando fizer sentido (ex.: `questionario_id` em QuestaoCreate).

## Passo 4: Autenticação e autorização

- **security.py**: funções para hash de senha (`get_password_hash`, `verify_password`), criação e decodificação de JWT (`create_access_token`, `decode_token`). Inclua no payload o `sub` (username ou email) e, se quiser, o `role`.
- **auth.py**: `OAuth2PasswordBearer(tokenUrl="token")`, dependência `get_current_user` (lê token, decodifica, busca usuário no banco e retorna; 401 se inválido). Dependência `role_required("admin")` que usa `get_current_user` e verifica o role (403 se não for admin).

Recomendação: usar `email` ou `username` como identificador no login. Se usar email, o formulário de login (OAuth2PasswordRequestForm) envia `username`; você pode tratar esse campo como email no backend.

## Passo 5: Rotas de autenticação

Router **auth** (tags=["Autenticação"]):

- **POST /register**: recebe `UsuarioCreate`; verifica se email já existe; hasheia a senha; persiste usuário; retorna usuário (sem senha).
- **POST /token**: recebe `OAuth2PasswordRequestForm`; busca usuário por email/username; verifica senha com `verify_password`; gera JWT com `create_access_token(data={"sub": ...})`; retorna `{"access_token": ..., "token_type": "bearer"}`.
- **GET /me**: `Depends(get_current_user)`; retorna o usuário atual.

Inclua o router no `app` com `app.include_router(router_auth)`.

## Passo 6: CRUD de Usuários (e opcional restrição por role)

- **POST /usuarios/**, **GET /usuarios/**, **GET /usuarios/{id}**, **PUT /usuarios/{id}**, **DELETE /usuarios/{id}**.
- Para criação de usuário, use hash de senha (nunca salve senha em texto plano).
- Decida quais rotas são públicas e quais exigem autenticação. Exemplo: listar e obter por ID podem ser apenas para autenticados; deletar pode exigir `Depends(role_required("admin"))`.

## Passo 7: CRUD de Questionários, Questões, Alternativas, Tentativas e Respostas

Siga o mesmo padrão do módulo 04 e do CRUD de Usuários:

- Um router por recurso (ou um router com prefixos) com tags (ex.: "Questionários", "Questões").
- Rotas que alteram ou removem dados podem exigir `Depends(get_current_user)` e, se fizer sentido, apenas o dono do recurso ou um admin (por exemplo, só o dono do questionário pode editá-lo; admin pode deletar qualquer um).
- Para **Tentativa** e **Resposta**, a lógica de negócio pode incluir: ao criar uma tentativa, registrar data_hora; ao registrar respostas, calcular se a alternativa escolhida é correta e atualizar o score da tentativa.

Implemente pelo menos o CRUD completo para **Questionario** e **Questao** (e alternativas de uma questão); Tentativa e Resposta podem ser um segundo passo com regras de pontuação.

## Passo 8: Documentação

- No `FastAPI()`, defina `title`, `description`, `version`.
- Use `tags` em cada router. Use `summary` e `description` nas rotas.
- Garanta que o esquema Bearer (OAuth2) apareça no Swagger; assim o aluno pode usar "Authorize" em `/docs` para testar rotas protegidas.

## Passo 9: Testar o fluxo completo

1. Subir a API: `uvicorn app.main:app --reload`.
2. Registrar um usuário (POST /register) com role "user" e outro com role "admin".
3. Fazer login (POST /token) e obter o token.
4. Em `/docs`, clicar em "Authorize" e colocar o token; testar GET /me, depois CRUD de questionários e questões.
5. Testar que rotas restritas a admin retornam 403 quando o token for de usuário comum.

## Conclusão

Este projeto integra persistência (ORM), schemas (Pydantic v2), CRUD, autenticação JWT, autorização por papel e documentação. O diagrama em [projetos/quizz/classes.puml](../projetos/quizz/classes.puml) define o domínio; a implementação segue os padrões dos módulos 04 a 07. Expandir para todas as entidades (incluindo Tentativa e Resposta com regras de negócio) é um bom exercício para consolidar o curso.
