# Tutorial: Tratamento de Erros Avançado no FastAPI

## 🎯 Objetivos de Aprendizado

- Criar exception handlers customizados
- Tratar erros SQLAlchemy
- Implementar logging estruturado
- Validar requisições Pydantic
- Retornar respostas de erro padronizadas

## 📖 Conteúdo

### 1. Exceções Customizadas

**Arquivo `app/exceptions.py`:**

```python
from fastapi import HTTPException, status

class BusinessException(HTTPException):
    """Exceção base para regras de negócio"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ResourceNotFoundException(BusinessException):
    def __init__(self, resource: str, id: int):
        super().__init__(
            detail=f"{resource} com ID {id} não encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )

class DuplicateResourceException(BusinessException):
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            detail=f"{resource} com {field} '{value}' já existe",
            status_code=status.HTTP_409_CONFLICT
        )

class UnauthorizedException(BusinessException):
    def __init__(self, detail: str = "Não autorizado"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
```

### 2. Exception Handlers

**Arquivo `app/middleware/exception_handlers.py`:**

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Trata erros de integridade do banco"""
    logger.error(f"Integrity error: {exc}")
    
    error_msg = str(exc.orig)
    
    # Detectar tipos específicos de erro
    if "UNIQUE constraint failed" in error_msg or "duplicate key" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Registro duplicado. Este recurso já existe.",
                "error_type": "IntegrityError"
            }
        )
    elif "FOREIGN KEY constraint failed" in error_msg or "foreign key constraint" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Referência inválida. O recurso relacionado não existe.",
                "error_type": "IntegrityError"
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Erro de integridade no banco de dados",
            "error_type": "IntegrityError"
        }
    )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Trata erros gerais do SQLAlchemy"""
    logger.error(f"SQLAlchemy error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro no banco de dados",
            "error_type": "DatabaseError"
        }
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    """Trata erros de validação Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": errors
        }
    )

async def generic_error_handler(request: Request, exc: Exception):
    """Handler para exceções não tratadas"""
    logger.exception(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "error_type": type(exc).__name__
        }
    )
```

### 3. Registrar Handlers

**Atualizar `app/main.py`:**

```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
from app.middleware.exception_handlers import (
    integrity_error_handler,
    sqlalchemy_error_handler,
    validation_error_handler,
    generic_error_handler
)

app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)
```

### 4. Logging Middleware

**Arquivo `app/middleware/logging_middleware.py`:**

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} | "
                f"Duration: {duration:.2f}s | "
                f"Path: {request.url.path}"
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {type(e).__name__} | "
                f"Duration: {duration:.2f}s | "
                f"Path: {request.url.path}"
            )
            raise
```

**Configurar logging em `app/main.py`:**

```python
import logging
from app.middleware.logging_middleware import LoggingMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app.add_middleware(LoggingMiddleware)
```

### 5. Usar Exceções nos Services

**Exemplo em `app/routers/restaurantes.py`:**

```python
from app.exceptions import ResourceNotFoundException, DuplicateResourceException

@router.get("/{restaurante_id}", response_model=RestauranteResponse)
async def get_restaurante(restaurante_id: int, db: Session = Depends(get_db)):
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    
    if not restaurante:
        raise ResourceNotFoundException("Restaurante", restaurante_id)
    
    return restaurante

@router.post("/", response_model=RestauranteResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurante(
    restaurante: RestauranteCreate,
    db: Session = Depends(get_db)
):
    # Verificar duplicidade
    existing = db.query(Restaurante).filter(Restaurante.nome == restaurante.nome).first()
    if existing:
        raise DuplicateResourceException("Restaurante", "nome", restaurante.nome)
    
    new_restaurante = Restaurante(**restaurante.dict())
    db.add(new_restaurante)
    db.commit()
    db.refresh(new_restaurante)
    
    return new_restaurante
```

## 🔨 Atividade Prática

**Arquivo `tests/error-tests.http`:**

```http
@baseUrl = http://localhost:8000/api

### 1. Teste 404 - Recurso não encontrado
GET {{baseUrl}}/restaurantes/9999

### 2. Teste 409 - Duplicidade
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Restaurante Existente"
}

### 3. Teste 422 - Validação
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": ""
}

### 4. Teste Foreign Key
POST {{baseUrl}}/avaliacoes
Content-Type: application/json

{
  "restaurante_id": 9999,
  "usuario_id": 1,
  "nota": 5
}
```

## 💡 Conceitos-Chave

- **Exception Handlers**: Interceptadores de exceções
- **Custom Exceptions**: Exceções personalizadas
- **Structured Logging**: Logs estruturados
- **Error Responses**: Respostas padronizadas
- **Database Errors**: Tratamento de erros de BD

## 📚 Recursos

- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [SQLAlchemy Exceptions](https://docs.sqlalchemy.org/en/20/core/exceptions.html)
