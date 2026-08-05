# Tutorial: CRUD completo com FastAPI e SQLAlchemy

Este tutorial monta uma API CRUD de itens com persistência em SQLite, reaproveitando a estrutura dos módulos 02 e 03. Os schemas usam **Pydantic v2** (`model_config`, `model_dump()`).

## Estrutura do projeto

```
fastapi-crud/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── database.py
├── venv/
└── requirements.txt
```

## Passo 1: Dependências e ambiente

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy
pip freeze > requirements.txt
```

## Passo 2: `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Passo 3: `app/models.py`

```python
from sqlalchemy import Column, Integer, String
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)
```

## Passo 4: `app/schemas.py` (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

- `from_attributes=True`: permite criar o schema a partir de um objeto ORM (ex.: `Item(**db_item.__dict__)` ou passando o objeto diretamente no FastAPI).

## Passo 5: `app/crud.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, database
from app.database import get_db

router = APIRouter()


@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return db_item


@router.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Item).offset(skip).limit(limit).all()


@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deletado com sucesso"}
```

- `model_dump()` substitui `dict()` do Pydantic v1; `exclude_unset=True` em update atualiza só os campos enviados.

## Passo 6: `app/main.py`

```python
from fastapi import FastAPI
from app import models, database
from app.crud import router

app = FastAPI(title="API CRUD", description="CRUD de itens com FastAPI e SQLAlchemy")

models.Base.metadata.create_all(bind=database.engine)
app.include_router(router)
```

## Passo 7: Executar e testar

1. Execute: `uvicorn app.main:app --reload`
2. Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) e teste:
   - **POST /items/** – body: `{"name": "Item A", "description": "Desc", "price": 100}`
   - **GET /items/** – lista com `skip` e `limit`
   - **GET /items/{item_id}** – um item
   - **PUT /items/{item_id}** – atualizar
   - **DELETE /items/{item_id}** – remover

## Resumo

- **Schemas** em Pydantic v2 com `ConfigDict(from_attributes=True)` e `model_dump()`.
- **CRUD** em um único roteador com `get_db` injetado; 404 quando o item não existe.
- **main.py** cria as tabelas e inclui o router.

No próximo módulo você adiciona autenticação JWT e protege rotas com dependências.
