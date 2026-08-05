# Conceitos: Persistência e ORM com SQLAlchemy

## O que é um ORM?

**ORM** (Object-Relational Mapping) é uma técnica que mapeia estruturas de um banco de dados relacional (tabelas, colunas, chaves) para **objetos** na linguagem de programação. Em vez de escrever SQL manualmente para cada operação, você trabalha com classes e instâncias; o ORM gera as queries e traduz os resultados em objetos.

Vantagens:

- Código mais legível e menos repetitivo.
- Menor risco de erros de SQL (injeção, typos).
- Facilidade para trocar de banco (com cuidado com dialetos).
- Suporte a relacionamentos (one-to-many, many-to-many) de forma declarativa.

Desvantagens e cuidados:

- Consultas complexas podem ser mais fáceis ou mais performáticas em SQL puro.
- É preciso entender o que o ORM gera (queries N+1, transações) para APIs escaláveis.

## SQLAlchemy no ecossistema Python

O **SQLAlchemy** é o ORM mais usado em Python. Ele oferece:

- **Core**: construção de SQL e conexão com o banco (engine, connection).
- **ORM**: mapeamento de classes para tabelas (models), sessões, relacionamentos.

No contexto FastAPI, usamos o ORM: definimos **modelos** (classes que herdam de uma base declarativa) e interagimos com o banco através de uma **sessão** (Session), que gerencia transações e identidade dos objetos.

## Engine e conexão

O **engine** é o ponto de entrada para falar com o banco. Ele guarda a URL de conexão e o pool de conexões. Você cria o engine uma vez (por exemplo em `database.py`):

```python
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
```

Para SQLite em aplicações síncronas, `check_same_thread=False` é comum; para MySQL/PostgreSQL isso em geral não é necessário.

## Session (sessão)

A **sessão** representa uma “unidade de trabalho”: um conjunto de operações (leitura/escrita) que podem ser confirmadas (commit) ou desfeitas (rollback). Em APIs web, o padrão é **uma sessão por requisição**: abrir no início, usar na rota, fechar (ou fazer commit) no final. No FastAPI isso é feito com uma dependência que usa `yield` (como no tutorial de rotas).

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Assim, cada rota que declara `db: Session = Depends(get_db)` recebe sua própria sessão e a libera ao terminar.

## Modelos (tabelas)

Os **modelos** são classes Python cujos atributos correspondem a colunas. A classe base é criada com `declarative_base()`; cada modelo define `__tablename__` e as colunas (Column, Integer, String, ForeignKey, etc.). O SQLAlchemy traduz isso em CREATE TABLE e em queries INSERT/UPDATE/SELECT/DELETE.

Exemplo:

```python
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
```

## create_all e migrations

`Base.metadata.create_all(bind=engine)` cria no banco todas as tabelas definidas nos modelos que herdam de `Base`. É prático para desenvolvimento e exemplos. Em produção e em projetos que evoluem, o ideal é usar **migrations** (ex.: Alembic) para versionar alterações do esquema. Neste curso usamos `create_all` para simplicidade; o conceito de migrations pode ser abordado como aprofundamento.

## Próximo passo

No tutorial deste módulo você vai criar `database.py` com engine e `SessionLocal`, definir um modelo simples (por exemplo `Item`) e chamar `create_all` na inicialização da aplicação. No módulo 04, essa base será usada para implementar o CRUD completo com Pydantic (schemas) e rotas.
