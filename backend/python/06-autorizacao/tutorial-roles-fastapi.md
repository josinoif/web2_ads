# Tutorial: Autorização por papéis (roles) com FastAPI

Este tutorial adiciona um campo **role** ao usuário e uma dependência que exige um papel específico. Partimos do projeto com autenticação JWT do módulo 05.

## Passo 1: Campo `role` no modelo e no schema

Em `app/models.py`, adicione a coluna ao usuário:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # "user" ou "admin"
```

Inclua `role` no schema de criação e de resposta. Em `app/schemas.py`:

```python
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"  # opcional no cadastro; default "user"


class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    model_config = ConfigDict(from_attributes=True)
```

Ao criar o usuário no registro, salve também `role` (vindo do schema ou default "user"). Se você usar migrations, crie uma para adicionar a coluna `role`; com `create_all`, recrie o banco ou adicione a coluna manualmente para não perder dados.

## Passo 2: Incluir `role` no JWT (opcional)

Se quiser que o papel venha do token (evitando consultar o banco em toda rota protegida por role), inclua no payload em `app/security.py`:

```python
def create_access_token(data: dict, role: str = "user") -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": role})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

No login, ao chamar `create_access_token`, passe `user.role`. Na dependência de autorização você pode ler `role` do payload do token ou do usuário carregado do banco (como abaixo).

## Passo 3: Dependência que exige um role

Crie ou edite `app/auth.py` e adicione uma dependência que recebe o usuário atual e o role exigido:

```python
from fastapi import Depends, HTTPException, status

# ... (get_current_user já existe)


def role_required(required_role: str):
    def dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para este recurso",
            )
        return current_user
    return dependency
```

Uso: `Depends(role_required("admin"))`.

## Passo 4: Rotas por papel

Exemplo: rota só para admin e rota só para usuário autenticado (qualquer role).

```python
from app.auth import get_current_user, role_required

# Apenas autenticado
@router.get("/items/", response_model=list[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Item).offset(skip).limit(limit).all()


# Apenas admin
@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(role_required("admin")),
):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deletado com sucesso"}
```

## Passo 5: Testar

1. Crie um usuário com `role: "user"` (registro) e outro com `role: "admin"` (ou atualize no banco).
2. Faça login com cada um e obtenha o token.
3. Com token de **user**: GET em `/items/` deve funcionar; DELETE em `/items/1` deve retornar 403.
4. Com token de **admin**: ambos devem funcionar.

## Resumo

- Usuário tem campo `role`; JWT pode incluir `role` no payload para evitar consulta extra.
- Dependência `role_required("admin")` usa `get_current_user` e verifica o role; 403 se não autorizado.
- Rotas que exigem apenas autenticação usam `Depends(get_current_user)`; rotas restritas a admin usam `Depends(role_required("admin"))`.

No próximo módulo você melhora a documentação da API (tags, descrições, Bearer no Swagger).
