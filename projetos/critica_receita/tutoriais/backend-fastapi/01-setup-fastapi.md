# Tutorial: Setup do Projeto FastAPI

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar projeto FastAPI com estrutura organizada
- Configurar SQLAlchemy para PostgreSQL
- Implementar validação com Pydantic
- Configurar CORS e middleware
- Criar sistema de logging estruturado
- Usar Alembic para migrações

## 📖 Conteúdo

### 1. Criando o Projeto

```bash
# Criar diretório do projeto
mkdir tasterank-api
cd tasterank-api

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Criar requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic[email]==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
alembic==1.13.0
EOF

# Instalar dependências
pip install -r requirements.txt
```

### 2. Estrutura do Projeto

```
tasterank-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Configurações
│   ├── database.py          # Conexão DB
│   ├── dependencies.py      # Dependências injetáveis
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── restaurante.py
│   │   ├── avaliacao.py
│   │   └── user.py
│   ├── schemas/             # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── restaurante.py
│   │   ├── avaliacao.py
│   │   └── user.py
│   ├── routers/             # Endpoints
│   │   ├── __init__.py
│   │   ├── restaurante.py
│   │   ├── avaliacao.py
│   │   └── auth.py
│   ├── services/            # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── restaurante.py
│   │   └── auth.py
│   └── utils/               # Utilitários
│       ├── __init__.py
│       └── logger.py
├── alembic/                 # Migrações
├── uploads/                 # Arquivos de upload
├── .env
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

### 3. Configuração de Ambiente

**Arquivo `app/config.py`:**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TasteRank API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024  # 2MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Arquivo `.env.example`:**

```env
# App
APP_NAME=TasteRank API
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:senha123@localhost:5432/tasterank_db

# Security
SECRET_KEY=sua_chave_secreta_muito_segura_com_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=2097152
```

### 4. Configurando o Banco de Dados

**Arquivo `app/database.py`:**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para injetar sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5. Criando Modelos Base

**Arquivo `app/models/__init__.py`:**

```python
from app.database import Base
from app.models.restaurante import Restaurante
from app.models.avaliacao import Avaliacao
from app.models.user import User

__all__ = ["Base", "Restaurante", "Avaliacao", "User"]
```

**Arquivo `app/models/restaurante.py`:**

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)
    endereco = Column(Text, nullable=True)
    telefone = Column(String(20), nullable=True)
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    avaliacao_media = Column(DECIMAL(3, 2), default=0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    avaliacoes = relationship("Avaliacao", back_populates="restaurante", cascade="all, delete-orphan")
```

### 6. Criando Schemas Pydantic

**Arquivo `app/schemas/restaurante.py`:**

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from decimal import Decimal

class RestauranteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    categoria: str = Field(..., min_length=1, max_length=50)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, pattern=r'^[\d\s\(\)\-\+]+$')
    descricao: Optional[str] = Field(None, max_length=500)
    image_url: Optional[HttpUrl] = None

class RestauranteCreate(RestauranteBase):
    pass

class RestauranteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    categoria: Optional[str] = Field(None, min_length=1, max_length=50)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, pattern=r'^[\d\s\(\)\-\+]+$')
    descricao: Optional[str] = Field(None, max_length=500)
    image_url: Optional[HttpUrl] = None

class RestauranteResponse(RestauranteBase):
    id: int
    ativo: bool
    avaliacao_media: Decimal
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
```

### 7. Criando Main App

**Arquivo `app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.database import engine, Base
from app.routers import restaurante, avaliacao, auth

settings = get_settings()

# Criar diretório de uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando aplicação...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("👋 Encerrando aplicação...")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Rotas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(restaurante.router, prefix="/api/restaurantes", tags=["restaurantes"])
app.include_router(avaliacao.router, prefix="/api", tags=["avaliacoes"])

@app.get("/")
async def root():
    return {"message": "TasteRank API"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### 8. Configurando Alembic

```bash
# Inicializar Alembic
alembic init alembic

# Editar alembic.ini - linha sqlalchemy.url
# sqlalchemy.url = driver://user:pass@localhost/dbname
# Comentar ou deixar vazio, vamos usar env.py
```

**Editar `alembic/env.py`:**

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Adicionar app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_settings
from app.database import Base
from app.models import *  # Importar todos os modelos

config = context.config
settings = get_settings()

# Sobrescrever URL do banco
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 9. Criando Primeira Migração

```bash
# Gerar migração automática
alembic revision --autogenerate -m "Initial migration"

# Aplicar migração
alembic upgrade head
```

### 10. Testando a Aplicação

```bash
# Rodar servidor
uvicorn app.main:app --reload

# Acessar documentação interativa
# http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

## 🔨 Atividade Prática

### Exercício 1: Configurar Ambiente

1. Criar `.env` baseado no `.env.example`
2. Criar banco de dados PostgreSQL
3. Executar migrações
4. Iniciar servidor

### Exercício 2: Testar Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "app_name": "TasteRank API"
}
```

### Exercício 3: Explorar Docs

Acesse `http://localhost:8000/docs` e explore a interface Swagger gerada automaticamente.

## 💡 Conceitos-Chave

- **FastAPI**: Framework moderno e rápido
- **Pydantic**: Validação de dados com type hints
- **SQLAlchemy**: ORM Python
- **Alembic**: Ferramenta de migrações
- **Uvicorn**: Servidor ASGI
- **Type Hints**: Tipagem estática Python

## ➡️ Próximos Passos

No próximo tutorial:
- Implementar CRUD completo
- Adicionar paginação e filtros
- Criar endpoints de restaurantes e avaliações

## 📚 Recursos

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
