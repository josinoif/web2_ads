# Tutorial: CRUD Completo com FastAPI

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar routers organizados por recurso
- Implementar CRUD completo com SQLAlchemy
- Usar Pydantic para validação automática
- Implementar paginação e filtros
- Tratar erros com HTTPException
- Aplicar dependency injection

## 📖 Conteúdo

### 1. Completando os Modelos

**Arquivo `app/models/avaliacao.py`:**

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    nota = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    nome_avaliador = Column(String(100), nullable=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento
    restaurante = relationship("Restaurante", back_populates="avaliacoes")
```

### 2. Schemas Completos

**Arquivo `app/schemas/avaliacao.py`:**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AvaliacaoBase(BaseModel):
    nota: int = Field(..., ge=1, le=5, description="Nota de 1 a 5")
    comentario: Optional[str] = Field(None, max_length=500)
    nome_avaliador: Optional[str] = Field(None, max_length=100)

class AvaliacaoCreate(AvaliacaoBase):
    pass

class AvaliacaoResponse(AvaliacaoBase):
    id: int
    restaurante_id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**Arquivo `app/schemas/__init__.py`:**

```python
from app.schemas.restaurante import (
    RestauranteCreate,
    RestauranteUpdate,
    RestauranteResponse,
)
from app.schemas.avaliacao import (
    AvaliacaoCreate,
    AvaliacaoResponse,
)

__all__ = [
    "RestauranteCreate",
    "RestauranteUpdate",
    "RestauranteResponse",
    "AvaliacaoCreate",
    "AvaliacaoResponse",
]
```

### 3. Service Layer (Opcional mas Recomendado)

**Arquivo `app/services/restaurante.py`:**

```python
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from app.models.restaurante import Restaurante
from app.models.avaliacao import Avaliacao
from app.schemas.restaurante import RestauranteCreate, RestauranteUpdate

class RestauranteService:
    @staticmethod
    def create(db: Session, data: RestauranteCreate) -> Restaurante:
        restaurante = Restaurante(**data.model_dump())
        db.add(restaurante)
        db.commit()
        db.refresh(restaurante)
        return restaurante

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        categoria: Optional[str] = None,
        busca: Optional[str] = None,
    ):
        query = db.query(Restaurante).filter(Restaurante.ativo == True)

        if categoria:
            query = query.filter(Restaurante.categoria == categoria)

        if busca:
            query = query.filter(
                or_(
                    Restaurante.nome.ilike(f"%{busca}%"),
                    Restaurante.descricao.ilike(f"%{busca}%"),
                )
            )

        total = query.count()
        items = query.order_by(Restaurante.avaliacao_media.desc()).offset(skip).limit(limit).all()

        return {"items": items, "total": total}

    @staticmethod
    def get_by_id(db: Session, id: int) -> Optional[Restaurante]:
        return db.query(Restaurante).filter(Restaurante.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data: RestauranteUpdate) -> Optional[Restaurante]:
        restaurante = RestauranteService.get_by_id(db, id)
        if not restaurante:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(restaurante, key, value)

        db.commit()
        db.refresh(restaurante)
        return restaurante

    @staticmethod
    def delete(db: Session, id: int) -> bool:
        restaurante = RestauranteService.get_by_id(db, id)
        if not restaurante:
            return False

        # Soft delete
        restaurante.ativo = False
        db.commit()
        return True

    @staticmethod
    def calcular_media(db: Session, restaurante_id: int):
        result = db.query(func.avg(Avaliacao.nota)).filter(
            Avaliacao.restaurante_id == restaurante_id
        ).scalar()

        media = float(result) if result else 0

        restaurante = RestauranteService.get_by_id(db, restaurante_id)
        if restaurante:
            restaurante.avaliacao_media = media
            db.commit()
```

### 4. Router de Restaurantes

**Arquivo `app/routers/restaurante.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.restaurante import RestauranteCreate, RestauranteUpdate, RestauranteResponse
from app.services.restaurante import RestauranteService

router = APIRouter()

@router.post("/", response_model=RestauranteResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurante(
    data: RestauranteCreate,
    db: Session = Depends(get_db),
):
    """Criar novo restaurante"""
    restaurante = RestauranteService.create(db, data)
    return restaurante

@router.get("/", response_model=dict)
async def list_restaurantes(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    busca: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    db: Session = Depends(get_db),
):
    """Listar restaurantes com paginação e filtros"""
    skip = (page - 1) * limit
    result = RestauranteService.get_all(db, skip=skip, limit=limit, categoria=categoria, busca=busca)

    return {
        "data": result["items"],
        "meta": {
            "total": result["total"],
            "page": page,
            "limit": limit,
            "total_pages": (result["total"] + limit - 1) // limit,
        },
    }

@router.get("/{id}", response_model=RestauranteResponse)
async def get_restaurante(
    id: int,
    db: Session = Depends(get_db),
):
    """Obter restaurante por ID"""
    restaurante = RestauranteService.get_by_id(db, id)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {id} não encontrado",
        )
    return restaurante

@router.put("/{id}", response_model=RestauranteResponse)
async def update_restaurante(
    id: int,
    data: RestauranteUpdate,
    db: Session = Depends(get_db),
):
    """Atualizar restaurante"""
    restaurante = RestauranteService.update(db, id, data)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {id} não encontrado",
        )
    return restaurante

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurante(
    id: int,
    db: Session = Depends(get_db),
):
    """Excluir restaurante (soft delete)"""
    success = RestauranteService.delete(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {id} não encontrado",
        )
```

### 5. Router de Avaliações

**Arquivo `app/routers/avaliacao.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from app.models.avaliacao import Avaliacao
from app.services.restaurante import RestauranteService

router = APIRouter()

@router.post(
    "/restaurantes/{restaurante_id}/avaliacoes",
    response_model=AvaliacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_avaliacao(
    restaurante_id: int,
    data: AvaliacaoCreate,
    db: Session = Depends(get_db),
):
    """Criar avaliação para um restaurante"""
    # Verificar se restaurante existe
    restaurante = RestauranteService.get_by_id(db, restaurante_id)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {restaurante_id} não encontrado",
        )

    # Criar avaliação
    avaliacao = Avaliacao(**data.model_dump(), restaurante_id=restaurante_id)
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)

    # Recalcular média
    RestauranteService.calcular_media(db, restaurante_id)

    return avaliacao

@router.get(
    "/restaurantes/{restaurante_id}/avaliacoes",
    response_model=List[AvaliacaoResponse],
)
async def list_avaliacoes(
    restaurante_id: int,
    db: Session = Depends(get_db),
):
    """Listar avaliações de um restaurante"""
    # Verificar se restaurante existe
    restaurante = RestauranteService.get_by_id(db, restaurante_id)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {restaurante_id} não encontrado",
        )

    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.restaurante_id == restaurante_id)
        .order_by(Avaliacao.created_at.desc())
        .all()
    )

    return avaliacoes

@router.delete("/avaliacoes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avaliacao(
    id: int,
    db: Session = Depends(get_db),
):
    """Excluir avaliação"""
    avaliacao = db.query(Avaliacao).filter(Avaliacao.id == id).first()
    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avaliação com ID {id} não encontrada",
        )

    restaurante_id = avaliacao.restaurante_id
    db.delete(avaliacao)
    db.commit()

    # Recalcular média
    RestauranteService.calcular_media(db, restaurante_id)
```

### 6. Registrar Routers no Main

**Atualizar `app/main.py`:**

```python
from app.routers import restaurante, avaliacao

# ... código anterior ...

# Registrar routers
app.include_router(restaurante.router, prefix="/api/restaurantes", tags=["restaurantes"])
app.include_router(avaliacao.router, prefix="/api", tags=["avaliacoes"])
```

## 🔨 Atividade Prática

### Exercício 1: Testar CRUD

**Crie o arquivo `tests/api-tests.http` no VS Code:**

```http
### Variáveis
@baseUrl = http://localhost:8000/api

### Criar restaurante
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "endereco": "Rua X, 123"
}

### Listar com paginação
GET {{baseUrl}}/restaurantes?page=1&limit=10

### Filtrar por categoria
GET {{baseUrl}}/restaurantes?categoria=Italiana

### Buscar por nome
GET {{baseUrl}}/restaurantes?busca=pizza

### Obter por ID
GET {{baseUrl}}/restaurantes/1

### Atualizar restaurante
PUT {{baseUrl}}/restaurantes/1
Content-Type: application/json

{
  "telefone": "(11) 1234-5678"
}

### Adicionar avaliação
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Excelente!",
  "nome_avaliador": "João"
}

### Listar avaliações do restaurante
GET {{baseUrl}}/restaurantes/1/avaliacoes

### Deletar avaliação
DELETE {{baseUrl}}/avaliacoes/1
```

**💡 Como usar:**
1. Instale a extensão **REST Client** no VS Code
2. Clique em "Send Request" acima de cada requisição
3. Veja a resposta no painel lateral

### Exercício 2: Validação

Teste cenários de erro:
- Campo obrigatório faltando
- Nota fora do range (< 1 ou > 5)
- ID inexistente

### Exercício 3: Adicionar Ordenação

Adicione parâmetro `order_by` para ordenar por:
- nome
- avaliacao_media
- created_at

## 💡 Conceitos-Chave

- **Dependency Injection**: Injeção de dependências com `Depends`
- **Path Parameters**: Parâmetros na URL
- **Query Parameters**: Parâmetros de consulta
- **Request Body**: Corpo da requisição validado por Pydantic
- **HTTPException**: Exceções HTTP automáticas
- **ORM**: Object-Relational Mapping com SQLAlchemy

## ➡️ Próximos Passos

No próximo tutorial:
- Upload de imagens
- Validação de arquivos
- Servir estáticos

## 📚 Recursos

- [FastAPI Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- [SQLAlchemy Queries](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
