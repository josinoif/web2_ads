# Tutorial: CORS e Segurança no FastAPI

## 🎯 Objetivos de Aprendizado

- Configurar CORS corretamente
- Implementar rate limiting
- Adicionar headers de segurança
- Proteger contra ataques comuns
- Configurar ambientes diferentes

## 📖 Conteúdo

### 1. Instalar Dependências

```bash
pip install slowapi python-jose[cryptography]
```

**Atualizar `requirements.txt`:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
slowapi==0.1.9
```

### 2. Configurar CORS

**Atualizar `app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings

app = FastAPI(
    title="Crítica Receita API",
    version="1.0.0",
)

# CORS - Configuração por ambiente
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
] if settings.ENVIRONMENT == "development" else [
    "https://tasterank.com",
    "https://www.tasterank.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
    max_age=3600,
)

# Trusted Host
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["tasterank.com", "www.tasterank.com"]
    )
```

### 3. Rate Limiting

**Arquivo `app/middleware/rate_limit.py`:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
```

**Aplicar em `app/main.py`:**

```python
from app.middleware.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Muitas requisições. Tente novamente mais tarde."}
    )
```

**Usar em rotas:**

```python
from app.middleware.rate_limit import limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

### 4. Headers de Segurança

**Arquivo `app/middleware/security_headers.py`:**

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
```

**Registrar em `main.py`:**

```python
from app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

### 5. Validação de Entrada

**Configuração já existente com Pydantic, adicionar sanitização:**

```python
from pydantic import BaseModel, validator
import html

class RestauranteCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    
    @validator('nome', 'descricao')
    def sanitize_html(cls, v):
        if v:
            return html.escape(v)
        return v
```

## 🔨 Atividade Prática

**Arquivo `tests/security-tests.http`:**

```http
### Teste rate limiting - Execute 6+ vezes rapidamente
GET http://localhost:8000/api/restaurantes

### Verificar headers de segurança
GET http://localhost:8000/api/restaurantes
```

## 💡 Conceitos-Chave

- **CORS**: Cross-Origin Resource Sharing
- **Rate Limiting**: Limite de requisições
- **Security Headers**: Headers HTTP de segurança
- **Input Sanitization**: Limpeza de entrada
- **Middleware**: Processamento intermediário

## 📚 Recursos

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [SlowAPI](https://slowapi.readthedocs.io/)
- [OWASP Security](https://owasp.org/)
