# Tutorial: Configuração do banco de dados e primeiro modelo

Neste tutorial você configura o SQLAlchemy (engine, sessão), define um modelo de exemplo e cria a tabela no banco. O projeto pode ser o mesmo do módulo 02 ou um novo.

## Passo 1: Dependências

No ambiente virtual:

```bash
pip install fastapi uvicorn sqlalchemy
```

Se usar SQLite (recomendado para seguir o curso sem instalar outro banco), não é necessário driver adicional. Para MySQL depois: `pip install pymysql` e URL `mysql+pymysql://...`.

## Passo 2: Estrutura do projeto

```
fastapi-orm/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   └── models.py
├── venv/
└── requirements.txt
```

## Passo 3: `app/database.py`

Crie o arquivo com a URL do banco, o engine, a classe base e a fábrica de sessões:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

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

- **SQLite**: o arquivo `app.db` será criado no diretório de onde você rodar a aplicação (em geral a raiz do projeto).
- **get_db**: dependência para injetar a sessão nas rotas (já usada no módulo 02).

## Passo 4: `app/models.py` – primeiro modelo

Defina uma tabela `items` como no exemplo do curso:

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

## Passo 5: Criar as tabelas no `main.py`

Importe os modelos e o engine, e crie as tabelas ao subir a aplicação:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db

app = FastAPI(title="API com ORM", version="1.0.0")

# Cria todas as tabelas definidas nos modelos (apenas para desenvolvimento)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API com banco configurado"}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    # Teste rápido: contar itens (tabela pode estar vazia)
    count = db.query(models.Item).count()
    return {"items_count": count}
```

Garanta que `app.models` está carregado antes de `create_all`, para que a tabela `items` exista no esquema.

## Passo 6: Executar e testar

1. Na raiz do projeto: `uvicorn app.main:app --reload`
2. Acesse `http://127.0.0.1:8000/` e depois `http://127.0.0.1:8000/db-test`. Deve retornar `items_count: 0`.
3. Verifique se o arquivo `app.db` foi criado na raiz do projeto.

## Resumo

- **database.py**: engine, `SessionLocal`, `Base`, e dependência `get_db`.
- **models.py**: modelo `Item` mapeando a tabela `items`.
- **main.py**: `create_all(bind=engine)` para criar as tabelas; rota `/db-test` usando `Depends(get_db)` para obter a sessão.

No módulo 04 você vai adicionar schemas Pydantic e as rotas de CRUD completo (criar, listar, obter por ID, atualizar e deletar itens).
