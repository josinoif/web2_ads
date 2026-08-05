# Tutorial: Autenticação JWT com FastAPI

Este tutorial adiciona login com JWT e proteção de rotas ao projeto CRUD do módulo 04. Usamos **OAuth2PasswordBearer**, **python-jose** para JWT e **passlib** com bcrypt para hash de senha.

## Passo 1: Dependências

```bash
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart
pip freeze > requirements.txt
```

- `python-multipart`: necessário para o FastAPI receber formulários (OAuth2 usa form no fluxo password).

## Passo 2: Modelo de usuário e tabela

Em `app/models.py`, adicione o modelo de usuário (e mantenha o `Item` se já existir):

```python
from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Item(Base):
    __tablename__ = "items"
    # ... (id, name, description, price)
```

Rode `create_all` no `main.py` (já deve existir) para criar a tabela `users`.

## Passo 3: Configuração de segurança e JWT

Crie `app/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Altere em produção; use variável de ambiente
SECRET_KEY = "sua-chave-secreta-mude-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

## Passo 4: Schemas de usuário e token

Em `app/schemas.py` (ou em um arquivo separado para auth), adicione:

```python
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class User(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
```

## Passo 5: Dependência OAuth2 e obtenção do usuário atual

Crie `app/auth.py` (ou adicione ao arquivo onde estão as rotas de auth):

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

- `OAuth2PasswordBearer(tokenUrl="token")`: indica que o token será obtido no endpoint `/token` (formulário com username/password) e que rotas protegidas esperam o header `Authorization: Bearer <token>`.

## Passo 6: Rotas de registro, login e rota protegida

Em `app/main.py` (ou em um router de auth), adicione:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_password_hash, verify_password, create_access_token
from app.auth import get_current_user

# Router de autenticação
router_auth = APIRouter(tags=["auth"])


@router_auth.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nome de usuário já existe")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router_auth.post("/token", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router_auth.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
```

Inclua o router no `app`:

```python
app.include_router(router_auth)
```

## Passo 7: Proteger uma rota do CRUD

Para exigir usuário autenticado em uma rota (ex.: criar item), use `Depends(get_current_user)`:

```python
@router.post("/items/", response_model=schemas.Item)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

## Passo 8: Testar

1. Suba a API: `uvicorn app.main:app --reload`
2. Em `/docs`: use **POST /register** com `{"username":"admin","email":"admin@example.com","password":"secret"}`.
3. Use **POST /token** com username e password (formulário no Swagger); copie o `access_token`.
4. Clique em "Authorize", informe `Bearer <token>` (ou só o token, conforme a UI).
5. Chame **GET /me** e **POST /items/**; devem funcionar apenas com token válido. Sem token ou com token inválido: 401.

## Resumo

- Senhas armazenadas com **passlib** (bcrypt); login verifica com `verify_password`.
- **JWT** gerado com `create_access_token` (claim `sub` = username) e validado em `get_current_user`.
- **OAuth2PasswordBearer** + dependência `get_current_user` protegem rotas; use `Depends(get_current_user)` onde for necessário.

No próximo módulo você adiciona **autorização** por papel (role), restringindo acesso a certas rotas (ex.: apenas admin).
