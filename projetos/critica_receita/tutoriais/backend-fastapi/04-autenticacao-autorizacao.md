# Tutorial: Autenticação e Autorização com FastAPI

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar autenticação JWT
- Usar OAuth2PasswordBearer
- Criar sistema de permissões por role
- Proteger rotas com dependencies
- Usar bcrypt para hash de senhas
- Criar decoradores customizados

## 📖 Conteúdo

### 1. Instalação de Dependências

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Atualizar `requirements.txt`:**

```txt
# ... dependências anteriores ...
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### 2. Configurar Variáveis de Ambiente

**Atualizar `.env`:**

```env
DATABASE_URL=postgresql://user:password@localhost/critica_receita

# JWT
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Atualizar `app/config.py`:**

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 2 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

### 3. Modelo de Usuário

**Arquivo `app/models/user.py`:**

```python
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
```

**Migration:**

```bash
# Gerar migration
alembic revision --autogenerate -m "add users table"

# Aplicar
alembic upgrade head
```

### 4. Schemas de Autenticação

**Arquivo `app/schemas/user.py`:**

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
```

### 5. Service de Autenticação

**Arquivo `app/services/auth.py`:**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, TokenData
from app.config import settings

# Configurar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar senha"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Criar token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> TokenData:
        """Decodificar token JWT"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            username: str = payload.get("sub")
            role: str = payload.get("role")

            if username is None:
                raise credentials_exception

            return TokenData(username=username, role=role)

        except JWTError:
            raise credentials_exception

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Autenticar usuário"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Criar novo usuário"""
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

        # Verificar se username já existe
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já cadastrado",
            )

        # Criar usuário
        hashed_password = AuthService.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
```

### 6. Dependencies de Autenticação

**Arquivo `app/dependencies/auth.py`:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import AuthService
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Obter usuário autenticado"""
    token_data = AuthService.decode_token(token)

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Obter usuário ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )
    return current_user

class RoleChecker:
    """Verificar role do usuário"""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada",
            )
        return user

# Atalhos para roles específicas
require_admin = RoleChecker([UserRole.ADMIN])
require_user = RoleChecker([UserRole.USER, UserRole.ADMIN])
```

### 7. Router de Autenticação

**Arquivo `app/routers/auth.py`:**

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    user = AuthService.create_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login e geração de token"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obter dados do usuário autenticado"""
    return current_user
```

### 8. Proteger Rotas Existentes

**Atualizar `app/routers/restaurante.py`:**

```python
from app.dependencies.auth import require_admin, get_current_user
from app.models.user import User

# Criar: apenas admin
@router.post("/", response_model=RestauranteResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurante(
    data: RestauranteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  # Proteger rota
):
    """Criar novo restaurante (apenas admin)"""
    restaurante = RestauranteService.create(db, data)
    return restaurante

# Listar: público (sem proteção)
@router.get("/", response_model=dict)
async def list_restaurantes(
    # ... parâmetros ...
    db: Session = Depends(get_db),
):
    """Listar restaurantes (público)"""
    # ... código ...

# Atualizar: apenas admin
@router.put("/{id}", response_model=RestauranteResponse)
async def update_restaurante(
    id: int,
    data: RestauranteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar restaurante (apenas admin)"""
    # ... código ...

# Deletar: apenas admin
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurante(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Excluir restaurante (apenas admin)"""
    # ... código ...
```

### 9. Registrar Router no Main

**Atualizar `app/main.py`:**

```python
from app.routers import restaurante, avaliacao, upload, auth

# ... código anterior ...

# Registrar routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(restaurante.router, prefix="/api/restaurantes", tags=["restaurantes"])
app.include_router(avaliacao.router, prefix="/api", tags=["avaliacoes"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
```

## 🔨 Atividade Prática

### Exercício 1: Fluxo Completo

```bash
# 1. Registrar usuário
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "senha123",
    "full_name": "Admin User"
  }'

# 2. Login (obter token)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=senha123" \
  | jq -r '.access_token')

# 3. Ver perfil
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Criar restaurante (com autenticação)
curl -X POST http://localhost:8000/api/restaurantes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Pizza Bella",
    "categoria": "Italiana"
  }'

# 5. Tentar criar sem token (deve falhar)
curl -X POST http://localhost:8000/api/restaurantes \
  -H "Content-Type: application/json" \
  -d '{"nome": "Test"}'
```

### Exercício 2: Tornar Usuário Admin (SQL)

```sql
-- Conectar no banco
psql -U user -d critica_receita

-- Atualizar role
UPDATE users SET role = 'admin' WHERE username = 'admin';
```

### Exercício 3: Testar Autorização

```bash
# Usuário comum tentando criar restaurante (deve falhar 403)
curl -X POST http://localhost:8000/api/restaurantes \
  -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Test"}'
```

## 💡 Conceitos-Chave

- **JWT**: JSON Web Tokens para autenticação stateless
- **OAuth2**: Padrão de autorização
- **Bearer Token**: Token enviado no header Authorization
- **bcrypt**: Algoritmo de hash para senhas
- **Dependency Injection**: Injeção de dependências para proteção de rotas
- **Role-Based Access Control (RBAC)**: Controle de acesso baseado em papéis

## 🛡️ Boas Práticas

1. **Senhas**:
   - Sempre use hash (bcrypt)
   - Nunca retorne senhas em responses
   - Exija senhas fortes (min 6-8 chars)

2. **Tokens**:
   - Use SECRET_KEY forte (min 32 chars)
   - Configure expiração adequada
   - Armazene tokens de forma segura no cliente

3. **Autorização**:
   - Valide permissões em cada rota
   - Use RBAC para organizar permissões
   - Retorne 403 para acesso negado

4. **Segurança**:
   - Use HTTPS em produção
   - Implemente rate limiting
   - Log tentativas de acesso inválidas

## ➡️ Próximos Passos

- Documentação automática com Swagger
- Testes automatizados
- Deploy em produção

## 📚 Recursos

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with Password](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Python Jose JWT](https://python-jose.readthedocs.io/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
