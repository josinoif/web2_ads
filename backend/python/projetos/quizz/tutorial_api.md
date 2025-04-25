# Tutorial: Implementando uma API de Backend para o Modelo de Quiz com FastAPI

Este tutorial descreve como implementar uma API de backend em Python utilizando o framework **FastAPI** para o modelo descrito no arquivo `classes.puml`. A API persistirá os dados em um banco de dados SQLite.

## Estrutura do Projeto

Organize o projeto com a seguinte estrutura de diretórios:

```
quizz/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── database.py
├── classes.puml
├── tutorial.md
└── requirements.txt
```

## Passo 1: Configuração do Ambiente

1. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. Instale as dependências:
   ```bash
   pip install fastapi uvicorn sqlalchemy
   ```

3. Salve as dependências no arquivo `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

## Passo 2: Configuração do Banco de Dados

## Passo 2: Configuração do Banco de Dados

Você pode configurar o banco de dados de acordo com suas necessidades. Este tutorial oferece dois caminhos: usar o SQLite (banco de dados leve e embutido) ou o MySQL (banco de dados robusto e escalável).

### Opção 1: Usando SQLite

Crie o arquivo `database.py` para configurar o banco de dados SQLite:

```python
# filepath: app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

O SQLite é ideal para desenvolvimento local ou aplicações simples, pois não requer configuração adicional.

### Opção 2: Usando MySQL

Se preferir usar o MySQL, instale o driver necessário:

```bash
pip install pymysql
```

Em seguida, configure o arquivo `database.py` para conectar-se ao MySQL:

```python
# filepath: app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://usuario:senha@localhost/nome_do_banco"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

Substitua `usuario`, `senha` e `nome_do_banco` pelas credenciais e nome do banco de dados configurados no MySQL.

Com essas opções, você pode escolher o banco de dados que melhor atende às suas necessidades.

## Passo 3: Definição dos Modelos

Crie o arquivo `models.py` para definir as tabelas do banco de dados:

```python
# filepath: app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)

    questionarios = relationship("Questionario", back_populates="usuario")
    tentativas = relationship("Tentativa", back_populates="usuario")

class Questionario(Base):
    __tablename__ = "questionarios"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(String)
    criado_em = Column(DateTime)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="questionarios")
    questoes = relationship("Questao", back_populates="questionario")
    tentativas = relationship("Tentativa", back_populates="questionario")

class Questao(Base):
    __tablename__ = "questoes"

    id = Column(Integer, primary_key=True, index=True)
    enunciado = Column(String)
    assunto = Column(String)
    questionario_id = Column(Integer, ForeignKey("questionarios.id"))

    questionario = relationship("Questionario", back_populates="questoes")
    alternativas = relationship("Alternativa", back_populates="questao")
    respostas = relationship("Resposta", back_populates="questao")

class Alternativa(Base):
    __tablename__ = "alternativas"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String)
    correta = Column(Boolean, default=False)
    questao_id = Column(Integer, ForeignKey("questoes.id"))

    questao = relationship("Questao", back_populates="alternativas")
    respostas = relationship("Resposta", back_populates="alternativa")

class Tentativa(Base):
    __tablename__ = "tentativas"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime)
    score = Column(Integer)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    questionario_id = Column(Integer, ForeignKey("questionarios.id"))

    usuario = relationship("Usuario", back_populates="tentativas")
    questionario = relationship("Questionario", back_populates="tentativas")
    respostas = relationship("Resposta", back_populates="tentativa")

class Resposta(Base):
    __tablename__ = "respostas"

    id = Column(Integer, primary_key=True, index=True)
    alternativa_id = Column(Integer, ForeignKey("alternativas.id"))
    questao_id = Column(Integer, ForeignKey("questoes.id"))
    tentativa_id = Column(Integer, ForeignKey("tentativas.id"))
    correta = Column(Boolean)

    alternativa = relationship("Alternativa", back_populates="respostas")
    questao = relationship("Questao", back_populates="respostas")
    tentativa = relationship("Tentativa", back_populates="respostas")
```

## Passo 4: Definição dos Schemas

Crie o arquivo `schemas.py` para definir os esquemas de entrada e saída:

```python
# filepath: app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class UsuarioBase(BaseModel):
    nome: str
    email: str

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

class QuestionarioBase(BaseModel):
    titulo: str
    descricao: str

class QuestionarioCreate(QuestionarioBase):
    usuario_id: int

class Questionario(QuestionarioBase):
    id: int
    criado_em: datetime

    class Config:
        orm_mode = True

class QuestaoBase(BaseModel):
    enunciado: str
    assunto: str

class QuestaoCreate(QuestaoBase):
    questionario_id: int

class Questao(QuestaoBase):
    id: int

    class Config:
        orm_mode = True

class AlternativaBase(BaseModel):
    texto: str
    correta: bool

class AlternativaCreate(AlternativaBase):
    questao_id: int

class Alternativa(AlternativaBase):
    id: int

    class Config:
        orm_mode = True

class TentativaBase(BaseModel):
    data_hora: datetime
    score: int
    usuario_id: int
    questionario_id: int

class TentativaCreate(TentativaBase):
    pass

class Tentativa(TentativaBase):
    id: int

    class Config:
        orm_mode = True

class RespostaBase(BaseModel):
    alternativa_id: int
    questao_id: int
    tentativa_id: int
    correta: bool

class RespostaCreate(RespostaBase):
    pass

class Resposta(RespostaBase):
    id: int

    class Config:
        orm_mode = True
```

## Passo 5: Operações CRUD

Crie o arquivo `crud.py` para implementar as operações CRUD:

```python
# filepath: app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

# Create
def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
  db_usuario = models.Usuario(**usuario.dict())
  db.add(db_usuario)
  db.commit()
  db.refresh(db_usuario)
  return db_usuario

# Read (Get by ID)
def get_usuario(db: Session, usuario_id: int):
  return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

# Read (Get all)
def get_usuarios(db: Session, skip: int = 0, limit: int = 10):
  return db.query(models.Usuario).offset(skip).limit(limit).all()

# Update
def update_usuario(db: Session, usuario_id: int, usuario: schemas.UsuarioCreate):
  db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
  if db_usuario:
    for key, value in usuario.dict().items():
      setattr(db_usuario, key, value)
    db.commit()
    db.refresh(db_usuario)
  return db_usuario

# Delete
def delete_usuario(db: Session, usuario_id: int):
  db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
  if db_usuario:
    db.delete(db_usuario)
    db.commit()
  return db_usuario
```

## Passo 6: Configuração do FastAPI

Crie o arquivo `main.py` para configurar o FastAPI:

```python
# filepath: app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# Dependency to get the database session
def get_db():
  db = database.SessionLocal()
  try:
    yield db
  finally:
    db.close()

@app.get("/")
def read_root():
  return {"message": "Bem-vindo à API de Quiz!"}

# CRUD endpoints for Usuario

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
  return crud.create_usuario(db=db, usuario=usuario)

@app.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
  db_usuario = crud.get_usuario(db=db, usuario_id=usuario_id)
  if db_usuario is None:
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
  return db_usuario

@app.get("/usuarios/", response_model=list[schemas.Usuario])
def read_usuarios(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  return crud.get_usuarios(db=db, skip=skip, limit=limit)

@app.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def update_usuario(usuario_id: int, usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
  db_usuario = crud.update_usuario(db=db, usuario_id=usuario_id, usuario=usuario)
  if db_usuario is None:
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
  return db_usuario

@app.delete("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
  db_usuario = crud.delete_usuario(db=db, usuario_id=usuario_id)
  if db_usuario is None:
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
  return db_usuario

# Nota: Agora que você tem os endpoints CRUD para o modelo de usuário, siga o mesmo padrão para criar endpoints para os outros modelos, como Questionário, Questão, Alternativa, Tentativa e Resposta.
```

## Passo 7: Executando o Servidor

Execute o servidor com o comando:

```bash
uvicorn app.main:app --reload
```

Acesse a API em [http://127.0.0.1:8000](http://127.0.0.1:8000).

A documentação interativa da API gerada pelo FastAPI pode ser acessada em:

- [Swagger UI](http://127.0.0.1:8000/docs)
- [ReDoc](http://127.0.0.1:8000/redoc)

## Conclusão

Com esta estrutura, você pode expandir sua API para incluir todas as operações necessárias para gerenciar usuários, questionários, questões, alternativas, tentativas e respostas.