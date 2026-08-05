# Tutorial: Documentação da API com FastAPI

O FastAPI já gera OpenAPI e as interfaces `/docs` (Swagger) e `/redoc`. Este tutorial mostra como melhorar título, descrição, tags, summary e como expor a autenticação Bearer na documentação.

## Passo 1: Título, descrição e versão no `FastAPI()`

Em `app/main.py`, ao criar a aplicação:

```python
app = FastAPI(
    title="API de Itens",
    description="API REST para gerenciar itens, com autenticação JWT e autorização por papéis.",
    version="1.0.0",
)
```

Isso aparece no topo do Swagger e do ReDoc.

## Passo 2: Tags nos roteadores

Agrupe os endpoints por domínio usando `tags` no `APIRouter`:

```python
router_items = APIRouter(prefix="/items", tags=["Itens"])
router_auth = APIRouter(tags=["Autenticação"])
```

No Swagger, os endpoints aparecerão agrupados por "Itens" e "Autenticação".

## Passo 3: Summary e description nas rotas

Em cada endpoint, use `summary` e opcionalmente `description`:

```python
@router_items.get(
    "/",
    response_model=list[schemas.Item],
    summary="Listar itens",
    description="Retorna uma lista paginada de itens. Requer autenticação.",
)
def read_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Item).offset(skip).limit(limit).all()
```

## Passo 4: Exemplos nos schemas Pydantic

Para que o Swagger mostre exemplos no "Try it out", use `Field` com `example` ou `json_schema_extra`:

```python
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., example="Mouse")
    description: str | None = Field(None, example="Mouse sem fio")
    price: int = Field(..., example=89)
```

## Passo 5: Autenticação Bearer no Swagger

Se você usa `OAuth2PasswordBearer` (como no módulo 05), o FastAPI já inclui o esquema de segurança no OpenAPI. Para que o Swagger ofereça o botão "Authorize" e envie o token nas requisições, é preciso declarar que os endpoints protegidos usam esse esquema.

Uma forma é definir no próprio `FastAPI()` os esquemas de segurança disponíveis e, nas rotas que exigem autenticação, referenciar esse esquema. O FastAPI associa automaticamente o `OAuth2PasswordBearer` ao nome `OAuth2PasswordBearer` (ou ao que você passar em `scheme_name`). Na prática, ao usar `Depends(oauth2_scheme)` ou `Depends(get_current_user)`, o OpenAPI já costuma mostrar a opção de segurança.

Para garantir que o Bearer apareça na UI:

1. No `FastAPI()`, adicione:

```python
app = FastAPI(
    title="API de Itens",
    description="...",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},  # opcional: mantém o token ao recarregar
)
```

2. Se a sua versão do FastAPI expõe o esquema apenas quando há `responses` com 401, você pode marcar uma rota protegida com:

```python
@router_items.get(
    "/",
    response_model=list[schemas.Item],
    summary="Listar itens",
    responses={401: {"description": "Não autenticado"}},
)
def read_items(...):
    ...
```

Em muitas versões, o uso de `OAuth2PasswordBearer` e `Depends(get_current_user)` já faz o Swagger mostrar "Authorize" e o campo para o token Bearer.

## Passo 6: Verificar o resultado

1. Suba a API: `uvicorn app.main:app --reload`
2. Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Verifique título, descrição, tags e summaries.
3. Clique em "Authorize", informe o token (obtido em POST /token) e teste um endpoint protegido.
4. Acesse [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) para ver a documentação em formato ReDoc.

## Resumo

- **FastAPI(title, description, version)** melhora o cabeçalho da documentação.
- **Tags** nos routers organizam os endpoints no Swagger/ReDoc.
- **summary** e **description** nas rotas explicam cada endpoint.
- **Field(example=...)** nos schemas preenche exemplos no "Try it out".
- Uso de **OAuth2PasswordBearer** e dependências de auth faz o Swagger expor autenticação Bearer para testar rotas protegidas.
