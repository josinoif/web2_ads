# Setup FastAPI

## Objetivos
- Criar app FastAPI com configuração por ambiente
- Conectar Postgres via SQLAlchemy e sessão
- Habilitar CORS e logging básico

## Passo a passo
1. Criar projeto (poetry/pip) e `main.py` com app e rota `/health`
2. Config de env com Pydantic Settings (`DATABASE_URL`, `ALLOWED_ORIGINS`)
3. Engine + SessionLocal; dependência `get_db` com `yield`
4. Montar CORS middleware; configurar logger
5. (Opcional) Alembic para migrações

## Checklist
- `.env.example` criado
- Tabelas criadas em startup ou via migração
- Script de dev com reload
