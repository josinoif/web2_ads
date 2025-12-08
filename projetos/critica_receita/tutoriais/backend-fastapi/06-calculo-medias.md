# Tutorial: Cálculo Automático de Médias no FastAPI

## 🎯 Objetivos de Aprendizado

- Implementar eventos SQLAlchemy
- Calcular médias automaticamente
- Usar aggregations SQL
- Criar endpoints de recálculo
- Otimizar queries

## 📖 Conteúdo

### 1. Event Listeners do SQLAlchemy

**Arquivo `app/models/avaliacao.py`:**

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    
    id = Column(Integer, primary_key=True)
    nota = Column(Float, nullable=False)
    comentario = Column(Text)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    restaurante = relationship("Restaurante", back_populates="avaliacoes")
    usuario = relationship("Usuario", back_populates="avaliacoes")

# Event Listeners
@event.listens_for(Avaliacao, 'after_insert')
def after_insert_avaliacao(mapper, connection, target):
    recalcular_media_restaurante(connection, target.restaurante_id)

@event.listens_for(Avaliacao, 'after_update')
def after_update_avaliacao(mapper, connection, target):
    recalcular_media_restaurante(connection, target.restaurante_id)

@event.listens_for(Avaliacao, 'after_delete')
def after_delete_avaliacao(mapper, connection, target):
    recalcular_media_restaurante(connection, target.restaurante_id)

def recalcular_media_restaurante(connection, restaurante_id: int):
    """Recalcula média usando SQL puro"""
    from sqlalchemy import text
    
    query = text("""
        UPDATE restaurantes
        SET media_avaliacoes = (
            SELECT COALESCE(AVG(nota), 0)
            FROM avaliacoes
            WHERE restaurante_id = :id
        ),
        total_avaliacoes = (
            SELECT COUNT(*)
            FROM avaliacoes
            WHERE restaurante_id = :id
        )
        WHERE id = :id
    """)
    
    connection.execute(query, {"id": restaurante_id})
```

### 2. Atualizar Model Restaurante

**Arquivo `app/models/restaurante.py`:**

```python
class Restaurante(Base):
    __tablename__ = "restaurantes"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    media_avaliacoes = Column(Float, default=0.0)
    total_avaliacoes = Column(Integer, default=0)
    
    avaliacoes = relationship("Avaliacao", back_populates="restaurante", cascade="all, delete-orphan")
```

### 3. Migration

```bash
# Criar migration
alembic revision --autogenerate -m "adiciona campos media e total avaliacoes"

# Aplicar
alembic upgrade head
```

**Ajustar migration se necessário:**

```python
def upgrade():
    op.add_column('restaurantes', sa.Column('media_avaliacoes', sa.Float(), nullable=True))
    op.add_column('restaurantes', sa.Column('total_avaliacoes', sa.Integer(), nullable=True))
    
    # Popular valores iniciais
    op.execute("""
        UPDATE restaurantes r
        SET media_avaliacoes = (
            SELECT COALESCE(AVG(nota), 0)
            FROM avaliacoes a
            WHERE a.restaurante_id = r.id
        ),
        total_avaliacoes = (
            SELECT COUNT(*)
            FROM avaliacoes a
            WHERE a.restaurante_id = r.id
        )
    """)
```

### 4. Atualizar Schemas

**Arquivo `app/schemas/restaurante.py`:**

```python
from pydantic import BaseModel
from typing import Optional, List

class RestauranteBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class RestauranteCreate(RestauranteBase):
    pass

class RestauranteResponse(RestauranteBase):
    id: int
    media_avaliacoes: float
    total_avaliacoes: int
    
    class Config:
        from_attributes = True
```

### 5. Endpoint de Recálculo Manual

**Arquivo `app/routers/admin.py`:**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/recalcular-medias")
async def recalcular_todas_medias(db: Session = Depends(get_db)):
    """Recalcula médias de todos os restaurantes"""
    
    query = text("""
        UPDATE restaurantes r
        SET media_avaliacoes = (
            SELECT COALESCE(AVG(nota), 0)
            FROM avaliacoes a
            WHERE a.restaurante_id = r.id
        ),
        total_avaliacoes = (
            SELECT COUNT(*)
            FROM avaliacoes a
            WHERE a.restaurante_id = r.id
        )
    """)
    
    db.execute(query)
    db.commit()
    
    return {"message": "Médias recalculadas com sucesso"}

@router.post("/recalcular-medias/{restaurante_id}")
async def recalcular_media_restaurante(
    restaurante_id: int,
    db: Session = Depends(get_db)
):
    """Recalcula média de um restaurante específico"""
    
    query = text("""
        UPDATE restaurantes
        SET media_avaliacoes = (
            SELECT COALESCE(AVG(nota), 0)
            FROM avaliacoes
            WHERE restaurante_id = :id
        ),
        total_avaliacoes = (
            SELECT COUNT(*)
            FROM avaliacoes
            WHERE restaurante_id = :id
        )
        WHERE id = :id
    """)
    
    result = db.execute(query, {"id": restaurante_id})
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    return {"message": f"Média recalculada para restaurante {restaurante_id}"}
```

**Registrar em `main.py`:**

```python
from app.routers import admin

app.include_router(admin.router)
```

## 🔨 Atividade Prática

**Arquivo `tests/media-tests.http`:**

```http
@baseUrl = http://localhost:8000/api

### 1. Criar avaliação (média recalcula automaticamente)
POST {{baseUrl}}/avaliacoes
Content-Type: application/json

{
  "restaurante_id": 1,
  "usuario_id": 1,
  "nota": 4.5,
  "comentario": "Muito bom!"
}

### 2. Verificar média atualizada
GET {{baseUrl}}/restaurantes/1

### 3. Recalcular todas as médias
POST {{baseUrl}}/admin/recalcular-medias

### 4. Recalcular média específica
POST {{baseUrl}}/admin/recalcular-medias/1
```

## 💡 Conceitos-Chave

- **Event Listeners**: Eventos SQLAlchemy
- **Aggregations**: Funções SQL AVG, COUNT
- **Denormalization**: Armazenar dados calculados
- **Performance**: Evitar cálculos em tempo real
- **Data Integrity**: Manter consistência

## 📚 Recursos

- [SQLAlchemy Events](https://docs.sqlalchemy.org/en/20/orm/events.html)
- [SQL Aggregations](https://www.postgresql.org/docs/current/functions-aggregate.html)
