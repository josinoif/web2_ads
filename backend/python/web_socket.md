# Tutorial: Implementando um WebSocket em Python

## Introdução ao Projeto
Neste tutorial, você aprenderá a criar uma aplicação simples de chat em tempo real utilizando WebSockets. O objetivo é permitir que múltiplos usuários se conectem a um servidor e troquem mensagens instantaneamente. O projeto será dividido em três partes: fundamentação teórica, implementação do backend e implementação do frontend.

---

## 1. Fundamentação Teórica

### O que é WebSocket?
WebSocket é um protocolo de comunicação bidirecional que permite a troca de dados em tempo real entre cliente e servidor. Diferente do HTTP, que é baseado em requisições e respostas, o WebSocket mantém uma conexão aberta, permitindo que dados sejam enviados e recebidos continuamente.

### Vantagens e Desafios do WebSocket

#### Vantagens
- **Comunicação em tempo real**: Permite a troca de mensagens instantaneamente entre cliente e servidor.
- **Redução de latência**: Não há necessidade de abrir novas conexões para cada interação, como ocorre no HTTP tradicional.
- **Eficiência**: Ideal para aplicações que exigem atualizações frequentes, como chats, jogos multiplayer e dashboards em tempo real.

#### Desafios
- **Escalabilidade**: Gerenciar múltiplas conexões WebSocket simultâneas pode ser desafiador, especialmente em aplicações com muitos usuários. Soluções como balanceadores de carga e servidores distribuídos são frequentemente necessárias.
- **Manutenção de Conexões**: Diferente de requisições HTTP, as conexões WebSocket permanecem abertas, o que pode consumir mais recursos do servidor.
- **Firewall e Proxy**: Alguns firewalls e proxies podem bloquear conexões WebSocket, exigindo configurações adicionais.
- **Complexidade de Implementação**: Comparado ao HTTP, o WebSocket pode exigir mais esforço para lidar com reconexões, autenticação e segurança.

Ao considerar o uso de WebSocket, é importante avaliar cuidadosamente os requisitos da aplicação e planejar estratégias para lidar com os desafios, como o uso de serviços de nuvem que oferecem suporte nativo a WebSocket ou a implementação de clusters de servidores para balanceamento de carga.

---

## 2. Implementação do Backend

### Implementando WebSocket com FastAPI

FastAPI é uma framework moderna e eficiente para construir APIs em Python. Ele possui suporte nativo para WebSockets, o que facilita a implementação de comunicação em tempo real. Abaixo está um guia para integrar WebSocket em um projeto FastAPI.

#### Estrutura de Diretórios do Projeto Backend com FastAPI

Organize o projeto de forma modular para facilitar a manutenção:

```
web2_ads/
├── backend/
│   ├── python/
│   │   ├── app/
│   │   │   ├── main.py          # Código principal do servidor FastAPI
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py  # Arquivo para tornar o diretório um pacote Python
│   │   │   │   └── websocket.py # Rota para gerenciar WebSocket
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py  # Arquivo para tornar o diretório um pacote Python
│   │   │   │   └── logger.py    # Funções para registro de logs
│   │   │   └── config/
│   │   │       ├── __init__.py  # Arquivo para tornar o diretório um pacote Python
│   │   │       └── settings.py  # Configurações do servidor (porta, host, etc.)
│   │   └── tests/
│   │       ├── __init__.py      # Arquivo para tornar o diretório um pacote Python
│   │       └── test_websocket.py # Testes unitários para WebSocket
```

#### Código do Servidor FastAPI com WebSocket

Crie um arquivo chamado `main.py` no diretório `app/` com o seguinte conteúdo:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# Gerenciador de conexões WebSocket
class ConnectionManager:
  def __init__(self):
    self.active_connections: List[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def broadcast(self, message: str):
    for connection in self.active_connections:
      await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  """
  Endpoint WebSocket para gerenciar conexões e mensagens.

  Args:
    websocket: Objeto que representa a conexão WebSocket.
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

#### Configurações do Servidor

Crie um arquivo `settings.py` no diretório `config/` para centralizar as configurações:

```python
# Configurações do servidor FastAPI
HOST = "127.0.0.1"
PORT = 8000
```

No `main.py`, importe essas configurações para iniciar o servidor:

```python
if __name__ == "__main__":
  import uvicorn
  from config.settings import HOST, PORT

  uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
```

#### Testes Unitários

Crie um arquivo `test_websocket.py` no diretório `tests/` para validar o comportamento do WebSocket:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection():
  with client.websocket_connect("/ws") as websocket:
    websocket.send_text("Teste")
    response = websocket.receive_text()
    assert "Mensagem recebida: Teste" in response
```

#### Executando o Servidor

1. Instale as dependências necessárias:
   ```bash
   pip install fastapi uvicorn pytest
   ```

2. Inicie o servidor:
   ```bash
   python app/main.py
   ```

3. Teste o WebSocket acessando `ws://127.0.0.1:8000/ws` em um cliente WebSocket ou no frontend.

Essa implementação com FastAPI é eficiente e extensível, permitindo que você adicione facilmente novas funcionalidades ao projeto.
## 3. Implementação do Frontend

### Criando o Frontend com ReactJS

A seguir, você encontrará o passo a passo para criar o frontend utilizando ReactJS.

#### Passo 1: Configurar o Ambiente
1. Certifique-se de ter o Node.js instalado em sua máquina.
2. Crie um novo projeto React utilizando o comando:
  ```bash
  npx create-react-app chat-websocket
  ```
3. Navegue até o diretório do projeto:
  ```bash
  cd chat-websocket
  ```

#### Passo 2: Estrutura do Projeto
A estrutura básica do projeto será a seguinte:
```
chat-websocket/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Chat.js
│   ├── App.js
│   ├── index.js
│   └── App.css
├── package.json
└── README.md
```

#### Passo 3: Criar o Componente `Chat`
1. Crie um diretório `components` dentro de `src/`.
2. Dentro de `components`, crie um arquivo chamado `Chat.js` com o seguinte conteúdo:

```jsx
import React, { useState, useEffect, useRef } from "react";
import "./Chat.css";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const ws = useRef(null);

  useEffect(() => {
   ws.current = new WebSocket("ws://localhost:8000/ws");

   ws.current.onmessage = (event) => {
    setMessages((prevMessages) => [...prevMessages, event.data]);
   };

   ws.current.onclose = () => {
    console.log("WebSocket desconectado");
   };

   return () => {
    ws.current.close();
   };
  }, []);

  const sendMessage = () => {
   if (input.trim() !== "") {
    ws.current.send(input);
    setInput("");
   }
  };

  return (
   <div className="chat-container">
    <h1>Chat em Tempo Real</h1>
    <div className="messages">
      {messages.map((msg, index) => (
       <div key={index} className="message">
        {msg}
       </div>
      ))}
    </div>
    <div className="input-container">
      <input
       type="text"
       value={input}
       onChange={(e) => setInput(e.target.value)}
       placeholder="Digite sua mensagem"
      />
      <button onClick={sendMessage}>Enviar</button>
    </div>
   </div>
  );
};

export default Chat;
```

#### Passo 4: Estilizar o Componente
1. Crie um arquivo `Chat.css` dentro de `src/` com o seguinte conteúdo:

```css
.chat-container {
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.messages {
  border: 1px solid #ccc;
  height: 300px;
  overflow-y: scroll;
  padding: 10px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 5px;
}

.input-container {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
```

#### Passo 5: Atualizar o Arquivo `App.js`
Substitua o conteúdo de `App.js` pelo seguinte:

```jsx
import React from "react";
import Chat from "./components/Chat";

function App() {
  return (
   <div className="App">
    <Chat />
   </div>
  );
}

export default App;
```

#### Passo 6: Executar o Projeto
1. Instale as dependências necessárias:
  ```bash
  npm install
  ```
2. Inicie o servidor de desenvolvimento:
  ```bash
  npm start
  ```
3. Acesse o frontend em `http://localhost:3000`.

Agora, você tem um frontend ReactJS funcional que se conecta ao servidor WebSocket para enviar e receber mensagens em tempo real.

---

## Conclusão
Agora você tem um servidor WebSocket em Python e um frontend simples para enviar e receber mensagens em tempo real. Para testar:
1. Execute o servidor com `python server.py`.
2. Abra o arquivo `index.html` em dois navegadores diferentes.
3. Envie mensagens e veja a mágica acontecer!

Explore e adapte o código para suas necessidades!