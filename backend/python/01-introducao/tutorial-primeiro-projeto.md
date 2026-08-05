# Tutorial: Primeiro projeto com FastAPI

Neste tutorial você vai criar um projeto mínimo com FastAPI: um "Hello World" e a estrutura de pastas que usaremos ao longo do curso.

## Passo 1: Ambiente e dependências

1. Crie um diretório para o projeto e entre nele:

   ```bash
   mkdir fastapi-primeiro
   cd fastapi-primeiro
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # No Windows: venv\Scripts\activate
   ```

3. Instale o FastAPI e o servidor ASGI Uvicorn:

   ```bash
   pip install fastapi uvicorn
   ```

4. Salve as dependências (opcional, mas recomendado):

   ```bash
   pip freeze > requirements.txt
   ```

## Passo 2: Estrutura de pastas

Crie a pasta `app` e o arquivo principal:

```
fastapi-primeiro/
├── app/
│   ├── __init__.py
│   └── main.py
├── venv/
└── requirements.txt
```

- `app/`: pacote Python que conterá a aplicação.
- `app/main.py`: ponto de entrada onde a instância do FastAPI e as rotas são definidas.

## Passo 3: Código em `app/main.py`

Crie o arquivo `app/main.py` com o seguinte conteúdo:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Minha primeira API",
    description="API criada no curso de FastAPI",
    version="1.0.0",
)


@app.get("/")
def read_root():
    """Rota raiz: retorna uma mensagem de boas-vindas."""
    return {"message": "Olá, bem-vindo à API!"}


@app.get("/health")
def health():
    """Rota de saúde: útil para checagem por balanceadores e monitoramento."""
    return {"status": "ok"}
```

## Passo 4: Executar o servidor

Na raiz do projeto (onde está a pasta `app`), execute:

```bash
uvicorn app.main:app --reload
```

- `app.main:app`: módulo `app.main`, objeto `app` (instância de FastAPI).
- `--reload`: recarrega o servidor quando você alterar o código (apenas em desenvolvimento).

Você deve ver algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Passo 5: Testar a API

1. **Navegador**: acesse [http://127.0.0.1:8000](http://127.0.0.1:8000). Deve retornar `{"message": "Olá, bem-vindo à API!"}`.
2. **Documentação interativa**: acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI). Você pode testar os endpoints diretamente na página.
3. **ReDoc**: acesse [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) para ver a documentação em formato alternativo.

## Resumo

- Você criou um projeto com FastAPI e Uvicorn.
- A aplicação está organizada no pacote `app` com `main.py` como entrada.
- Duas rotas GET foram definidas: `/` e `/health`.
- A documentação OpenAPI (Swagger e ReDoc) é gerada automaticamente.

No próximo módulo você verá rotas com parâmetros e o sistema de dependências (`Depends`), que são a base para conectar banco de dados e autenticação.
