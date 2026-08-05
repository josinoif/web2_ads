# Tutorial: WebSocket com FastAPI

Neste tutorial você aprende a criar um endpoint WebSocket com FastAPI para comunicação em tempo real (ex.: chat). O conteúdo está focado no backend; no final há uma sugestão de cliente para testar.

## 1. Conceitos rápidos

**WebSocket** é um protocolo bidirecional: cliente e servidor mantêm uma conexão aberta e podem enviar mensagens a qualquer momento. Diferente do HTTP (requisição-resposta), não é preciso fazer nova requisição para receber dados do servidor. É útil para chats, notificações em tempo real e dashboards ao vivo.

**Vantagens**: baixa latência, menos overhead que várias requisições HTTP. **Desafios**: escalar muitas conexões simultâneas, lidar com reconexões e autenticação na subida da conexão.

## 2. Estrutura do projeto

```
fastapi-websocket/
├── app/
│   ├── __init__.py
│   └── main.py
├── venv/
└── requirements.txt
```

## 3. Dependências

```bash
pip install fastapi uvicorn
```

## 4. Código do servidor FastAPI com WebSocket

Crie `app/main.py`:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI(title="Chat WebSocket", version="1.0.0")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
def root():
    return {"message": "WebSocket disponível em /ws"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket: aceita conexões e repassa mensagens em broadcast.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Mensagem recebida: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Um cliente desconectou.")
```

## 5. Executar o servidor

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O WebSocket estará disponível em `ws://127.0.0.1:8000/ws`.

## 6. Como testar

### Opção A: Swagger UI

1. Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
2. Localize o endpoint **GET /ws** (ou a seção WebSocket, dependendo da versão do FastAPI).
3. Use "Connect" e envie mensagens de texto; as respostas aparecem na mesma tela.

### Opção B: Cliente em JavaScript (navegador)

Abra o console do navegador (F12) em qualquer página e execute:

```javascript
const ws = new WebSocket("ws://127.0.0.1:8000/ws");
ws.onmessage = (event) => console.log("Recebido:", event.data);
ws.onopen = () => ws.send("Olá do navegador");
```

### Opção C: Frontend React (opcional)

Se quiser um cliente completo em React, crie um projeto (ex.: `npx create-react-app chat-websocket` ou Vite + React) e um componente que:

1. Em `useEffect`, cria `new WebSocket("ws://localhost:8000/ws")`.
2. Guarda as mensagens recebidas em um estado e exibe em lista.
3. Tem um campo de texto e um botão que chama `ws.send(texto)`.
4. No cleanup do `useEffect`, chama `ws.close()`.

A lógica é a mesma do exemplo em JavaScript acima; a diferença é a interface com estado e formulário.

## 7. Testes com pytest (opcional)

```bash
pip install pytest httpx
```

Crie `tests/test_websocket.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_websocket_connection():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Teste")
        response = websocket.receive_text()
        assert "Mensagem recebida: Teste" in response
```

Execute: `pytest tests/ -v`.

## Conclusão

Você configurou um WebSocket em FastAPI com um gerenciador de conexões e broadcast. Para evoluir: adicionar autenticação na subida da conexão (ex.: token na query string), salas por canal e persistência de mensagens se precisar de histórico.
