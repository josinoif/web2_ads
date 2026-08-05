# Conceitos: Rotas e dependências no FastAPI

## Rotas e métodos HTTP

No FastAPI, uma **rota** associa um padrão de URL e um método HTTP (GET, POST, PUT, DELETE, etc.) a uma função que processa a requisição e devolve a resposta. Os decoradores `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()` (e outros) definem essas associações.

Cada função de rota pode receber:

- **Parâmetros de path** (ex.: `/items/{item_id}`): parte da URL.
- **Parâmetros de query** (ex.: `?skip=0&limit=10`): query string.
- **Corpo da requisição (body)**: normalmente JSON, validado por um modelo Pydantic.
- **Cabeçalhos**: headers HTTP quando necessário.

O FastAPI usa as **type hints** para saber de onde cada parâmetro vem e como validá-lo.

## APIRouter: organizando rotas

Em projetos maiores, não é recomendável registrar todas as rotas diretamente no `app`. O **APIRouter** permite agrupar rotas por domínio (itens, usuários, etc.) e depois incluí-las na aplicação com `app.include_router(router, prefix="/api")`. Isso melhora a organização e a manutenção.

Exemplo:

```python
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def list_items():
    ...

@router.get("/{item_id}")
def get_item(item_id: int):
    ...
```

Com `include_router(router)`, as rotas ficam `/items/` e `/items/{item_id}`.

## Depends: injeção de dependências

O FastAPI possui um sistema de **dependências** acessado por `Depends()`. Uma dependência é uma função (ou classe) que pode:

- Ser reutilizada em várias rotas (ex.: obter a sessão do banco de dados).
- Fazer validação ou lógica comum (ex.: obter o usuário autenticado a partir do token).
- Garantir que recursos sejam criados e liberados corretamente (ex.: abrir e fechar a conexão com o banco).

Quando uma rota declara um parâmetro com `Depends(get_db)`, o FastAPI chama `get_db` antes de executar a rota e injeta o resultado (por exemplo, a sessão do banco) no parâmetro. Se a dependência usar `yield`, o código após o `yield` roda depois que a rota terminar (útil para fechar conexões).

Exemplo típico de dependência para banco de dados:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

Assim, cada requisição recebe sua própria sessão e ela é fechada ao final.

## Path, query e body

- **Path** (`item_id` em `/items/{item_id}`): declare na função com o mesmo nome. O FastAPI interpreta como path parameter.
- **Query** (`skip`, `limit` em `?skip=0&limit=10`): parâmetros da função que não estão no path nem em um modelo de body são tratados como query parameters.
- **Body**: use um modelo Pydantic como tipo do parâmetro. O FastAPI lê o corpo da requisição JSON e valida com esse modelo.

Essa convenção por tipo e nome reduz configuração manual e mantém a documentação OpenAPI alinhada ao código.
