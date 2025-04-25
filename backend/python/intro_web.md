# Introdução ao Desenvolvimento de APIs com FastAPI

FastAPI é um framework moderno, rápido e eficiente para a criação de APIs em Python. Ele é baseado no padrão OpenAPI e utiliza tipagem para oferecer validação automática, documentação interativa e desempenho otimizado. Neste tutorial, vamos explorar como estruturar um projeto seguindo boas práticas e criar uma API CRUD com persistência em um banco de dados em memória.

## Estruturação do Projeto

Uma boa estrutura de diretórios facilita a manutenção e escalabilidade do projeto. Vamos organizar nosso projeto da seguinte forma:

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

### Passo 1: Criando o Projeto

1. Crie um diretório para o projeto:
  ```bash
  mkdir fastapi-crud
  cd fastapi-crud
  ```

2. Crie e ative um ambiente virtual:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # No Windows: venv\Scripts\activate
  ```

3. Instale as dependências:
  ```bash
  pip install fastapi uvicorn sqlalchemy
  ```

4. Salve as dependências no arquivo `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```

### Passo 2: Criando os Arquivos

#### `main.py`
Este arquivo será o ponto de entrada da aplicação.

```python
from fastapi import FastAPI
from app import models, database
from app.crud import router

app = FastAPI()

# Inicializa o banco de dados
models.Base.metadata.create_all(bind=database.engine)

# Inclui as rotas
app.include_router(router)
```

#### `database.py`
Configuração do banco de dados em memória.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Criação do engine para conexão com o banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Configuração da sessão para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para definição dos modelos do SQLAlchemy
Base = declarative_base()
```

#### `models.py`
Definição das tabelas do banco de dados.

```python
from sqlalchemy import Column, Integer, String
from .database import Base

# Definição do modelo da tabela "items" no banco de dados
class Item(Base):
   # Nome da tabela no banco de dados
   __tablename__ = "items"

   # Coluna "id" como chave primária, do tipo inteiro, com índice
   id = Column(Integer, primary_key=True, index=True)
   
   # Coluna "name" do tipo string, com índice
   name = Column(String, index=True)
   
   # Coluna "description" do tipo string, com índice
   description = Column(String, index=True)
   
   # Coluna "price" do tipo inteiro
   price = Column(Integer)
```

#### `schemas.py`
Definição dos esquemas de entrada e saída.

```python
from pydantic import BaseModel

# Classe base para os esquemas de entrada e saída
class ItemBase(BaseModel):
   # Nome do item (obrigatório)
   name: str
   # Descrição do item (opcional)
   description: str = None
   # Preço do item (obrigatório)
   price: int

# Esquema para criação de um novo item (herda de ItemBase)
class ItemCreate(ItemBase):
   pass

# Esquema para atualização de um item existente (herda de ItemBase)
class ItemUpdate(ItemBase):
   pass

# Esquema para representar um item completo, incluindo o ID
class Item(ItemBase):
   # ID do item (gerado automaticamente pelo banco de dados)
   id: int

   # Configuração para permitir a conversão de objetos ORM para modelos Pydantic
   class Config:
      orm_mode = True
```

#### `crud.py`
Operações de CRUD.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database

# Criação do roteador para gerenciar as rotas da aplicação
router = APIRouter()

# Função para obter uma sessão do banco de dados
def get_db():
   db = database.SessionLocal()
   try:
      yield db
   finally:
      db.close()

# Rota para criar um novo item
@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
   # Cria um novo item a partir dos dados recebidos
   db_item = models.Item(**item.dict())
   # Adiciona o item ao banco de dados
   db.add(db_item)
   db.commit()
   # Atualiza o estado do item com os dados do banco
   db.refresh(db_item)
   return db_item

# Rota para obter um item pelo ID
@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
   # Busca o item no banco de dados pelo ID
   db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
   # Verifica se o item foi encontrado
   if db_item is None:
      raise HTTPException(status_code=404, detail="Item não encontrado")
   return db_item

# Rota para listar todos os itens com paginação
@router.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
   # Retorna uma lista de itens com base nos parâmetros de paginação
   return db.query(models.Item).offset(skip).limit(limit).all()

# Rota para atualizar um item existente
@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
   # Busca o item no banco de dados pelo ID
   db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
   # Verifica se o item foi encontrado
   if db_item is None:
      raise HTTPException(status_code=404, detail="Item não encontrado")
   # Atualiza os campos do item com os dados recebidos
   for key, value in item.dict(exclude_unset=True).items():
      setattr(db_item, key, value)
   db.commit()
   # Atualiza o estado do item com os dados do banco
   db.refresh(db_item)
   return db_item

# Rota para deletar um item pelo ID
@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
   # Busca o item no banco de dados pelo ID
   db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
   # Verifica se o item foi encontrado
   if db_item is None:
      raise HTTPException(status_code=404, detail="Item não encontrado")
   # Remove o item do banco de dados
   db.delete(db_item)
   db.commit()
   return {"message": "Item deletado com sucesso"}
```

### Passo 3: Executando o Projeto

1. Execute o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Acesse a API em [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. Explore a documentação interativa em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### O que você pode fazer nesta aplicação

Esta aplicação permite gerenciar itens em um banco de dados em memória. Abaixo estão os endpoints disponíveis e suas funcionalidades:

- **POST /items/**: Criar um novo item.
- **GET /items/{item_id}**: Obter detalhes de um item específico pelo ID.
- **GET /items/**: Listar todos os itens com suporte a paginação (parâmetros `skip` e `limit`).
- **PUT /items/{item_id}**: Atualizar um item existente pelo ID.
- **DELETE /items/{item_id}**: Deletar um item pelo ID.

Você pode testar a API utilizando a documentação interativa disponível em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) ou ferramentas como Postman, Insomnia ou qualquer aplicação semelhante para realizar requisições HTTP.

## Conclusão

Com esta estrutura, você pode facilmente expandir sua aplicação. FastAPI, combinado com SQLAlchemy, oferece uma base sólida para criar APIs modernas e escaláveis. Explore mais recursos na [documentação oficial](https://fastapi.tiangolo.com/).