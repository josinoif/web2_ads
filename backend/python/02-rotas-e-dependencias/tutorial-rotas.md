# Tutorial: Rotas e dependências

Neste tutorial você vai adicionar rotas com parâmetros (path e query) e uma dependência que simula a "sessão do banco" (o `get_db` real virá no módulo de persistência). O projeto parte do primeiro projeto com FastAPI (módulo 01).

## Passo 1: Estrutura do projeto

Se ainda não tiver o projeto do módulo 01, crie:

```
fastapi-rotas/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── database.py   # apenas simulação por enquanto
├── venv/
└── requirements.txt
```

Em `app/database.py`, coloque um placeholder para a dependência de banco (será substituído no módulo 03):

```python
# Simulação: no módulo 03 isso será a sessão real do SQLAlchemy
def get_db():
    yield None  # por enquanto não usamos banco
```

## Passo 2: Usar APIRouter e Depends em `main.py`

Atualize `app/main.py` para usar um roteador e a dependência `get_db`:

```python
from fastapi import FastAPI, Depends, APIRouter

from app.database import get_db

app = FastAPI(title="API com Rotas e Dependências", version="1.0.0")

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def list_items(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    """Lista itens com paginação (parâmetros de query)."""
    # db ainda é None; no módulo 04 usaremos para buscar no banco
    return {
        "skip": skip,
        "limit": limit,
        "message": "Lista de itens (banco será usado no módulo 04)",
    }


@router.get("/{item_id}")
def get_item(item_id: int, db=Depends(get_db)):
    """Obtém um item pelo ID (parâmetro de path)."""
    return {"item_id": item_id, "message": "Item (banco no módulo 04)"}


app.include_router(router)
```

## Passo 3: Rota com body (POST)

Para aceitar um corpo JSON, usamos um modelo Pydantic. Crie `app/schemas.py`:

```python
from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: int
```

Em `app/main.py`, adicione o import e a rota POST:

```python
from app.schemas import ItemCreate

# ... dentro do mesmo router ...

@router.post("/", status_code=201)
def create_item(item: ItemCreate, db=Depends(get_db)):
    """Cria um item (corpo da requisição validado por Pydantic)."""
    return {"created": item.model_dump()}
```

## Passo 4: Executar e testar

1. Instale as dependências (se ainda não tiver): `pip install fastapi uvicorn`
2. Execute: `uvicorn app.main:app --reload`
3. Acesse:
   - `GET http://127.0.0.1:8000/items/?skip=0&limit=5` (query)
   - `GET http://127.0.0.1:8000/items/42` (path)
   - `POST http://127.0.0.1:8000/items/` com body JSON: `{"name": "Item A", "description": "Desc", "price": 100}`
4. Use também `/docs` para testar os três endpoints e ver a documentação gerada.

## Resumo

- **APIRouter** agrupa rotas com prefixo e tag.
- **Path** e **query** são inferidos pelos type hints e pelos nomes dos parâmetros.
- **Body** é definido por um modelo Pydantic (`ItemCreate`).
- **Depends(get_db)** injeta a “dependência” em cada rota; no próximo módulo `get_db` será a sessão real do banco.

No módulo 03 você configurará o banco de dados real e, no 04, usará essa mesma estrutura para implementar o CRUD completo.
