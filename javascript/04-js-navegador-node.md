# 4. JavaScript no navegador e no Node.js: recursos e diferenças

A **linguagem** é a mesma nos dois ambientes; o que muda são as **APIs e o contexto** em que o código roda. Este arquivo resume o que o JavaScript pode acessar no navegador e no Node.js e faz o link com o material de front-end que já cobre DOM, eventos e requisições HTTP.

---

## JavaScript no navegador

No navegador, o código roda no contexto de uma **página**: há um documento HTML (DOM), uma janela (BOM), rede (Fetch) e eventos do usuário. Não há acesso ao sistema de arquivos nem a processos do sistema.

### Principais recursos

| Recurso | Descrição | Material no repositório |
|---------|-----------|--------------------------|
| **DOM (Document Object Model)** | Interface para acessar e modificar o documento HTML (elementos, atributos, estilos, árvore). | [../frontend/dom.md](../frontend/dom.md) — conceitos, métodos úteis e exercícios. |
| **BOM (Browser Object Model)** | Objetos globais do navegador: `window`, `location`, `navigator`, `localStorage`, `sessionStorage`, `history`, etc. | Usado em conjunto com DOM e eventos; não há arquivo dedicado; pode ser citado em exercícios. |
| **Eventos** | Cliques, teclado, formulário, rede, etc. Registro com `addEventListener`; propagação e remoção. | [../frontend/events_js.md](../frontend/events_js.md) — tipos de eventos, `addEventListener`/`removeEventListener`, exercícios. |
| **Fetch API** | Requisições HTTP baseadas em Promises (GET, POST, PUT, DELETE, headers). | [../frontend/http_requests_fetch_api.md](../frontend/http_requests_fetch_api.md) — exemplos e tratamento de erros. |
| **Axios** | Biblioteca para HTTP (Promises); interceptors, cancelamento, tratamento de erro. | [../frontend/http_requests_axios.md](../frontend/http_requests_axios.md) — comparação com Fetch e exemplos. |
| **Outros** | `setTimeout`/`setInterval`, `requestAnimationFrame` (animações), Web Storage, `console`, etc. | Aparecem nos exemplos de DOM, eventos e HTTP. |

### Web APIs: APIs disponibilizadas pelo navegador

Além do DOM, BOM e Fetch, o navegador expõe **Web APIs**: interfaces padronizadas (geralmente pelo W3C e pelo WHATWG) para acessar recursos do dispositivo e do sistema, como localização, câmera, microfone, notificações e armazenamento. Essas APIs são acionadas via JavaScript (por exemplo, `navigator.geolocation`, `navigator.mediaDevices`) e costumam exigir **permissão do usuário** e **contexto seguro** (HTTPS ou localhost). O suporte varia por navegador e por dispositivo; em mobile (navegador ou WebView), muitas delas permitem que um site ou app web se comporte de forma parecida com um app nativo.

Algumas Web APIs comuns e exemplos de uso:

| API | O que oferece | Exemplo de uso no código |
|-----|----------------|---------------------------|
| **Geolocation** | Posição do dispositivo (latitude, longitude, precisão). | `navigator.geolocation.getCurrentPosition(sucesso, erro)` — retorna a posição de forma assíncrona. |
| **MediaDevices (getUserMedia)** | Acesso à câmera e ao microfone (stream de áudio/vídeo). | `navigator.mediaDevices.getUserMedia({ video: true, audio: true })` — retorna uma Promise com o stream; usado em videoconferência, gravação, fotos. |
| **Notifications** | Notificações nativas do sistema (mesmo com a aba em segundo plano). | `new Notification('Título', { body: 'Mensagem' })` (após permissão); útil para lembretes, mensagens, alertas. |
| **Clipboard** | Ler e escrever na área de transferência. | `navigator.clipboard.writeText(texto)` ou `readText()` — copiar/colar sem depender de atalhos do usuário. |
| **Storage (localStorage / sessionStorage)** | Armazenamento persistente ou por sessão no navegador. | Já citado no BOM; usado para preferências, cache leve, token. |
| **Canvas / WebGL** | Desenho 2D e 3D; processamento de imagem. | Gráficos, jogos, edição de foto, visualizações. |
| **Web Speech** | Reconhecimento de fala e síntese de voz (text-to-speech). | `SpeechRecognition`, `speechSynthesis` — acessibilidade, comandos por voz, leitura em voz alta. |
| **Device Orientation / Motion** | Acelerômetro e giroscópio (em dispositivos que possuem). | Jogos, realidade aumentada, gestos; `deviceorientation`, `devicemotion`. |
| **Screen Orientation** | Orientação da tela (retrato, paisagem). | Ajustar layout ou conteúdo conforme o usuário gira o dispositivo. |

#### Contextos de uso: web e mobile

- **Web (desktop e mobile):** Sites que precisam de localização (entrega, mapas, clima, “perto de você”), vídeo ao vivo ou gravação (reuniões, stories, upload de vídeo), notificações (e-mail, mensagens, lembretes), reconhecimento de fala (busca por voz, legendas) ou desenho/processamento de imagem (ferramentas de design, jogos) usam essas Web APIs. Tudo roda no navegador, sem instalação obrigatória.
- **Mobile (PWA ou WebView):** Em **PWAs** (Progressive Web Apps) ou apps híbridos (Cordova, Capacitor, WebView no Android/iOS), o mesmo JavaScript e as mesmas Web APIs são usados dentro de uma “janela” web. Assim, um único código pode acessar câmera, microfone, geolocalização e notificações no celular, oferecendo experiência próxima à de um app nativo (com as limitações de permissão e suporte de cada plataforma).

**Exemplo mínimo — Geolocation:** pedir a posição do usuário e exibir no console (em produção, você usaria as coordenadas para um mapa ou para enviar ao backend):

```javascript
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    (pos) => console.log('Lat:', pos.coords.latitude, 'Lon:', pos.coords.longitude),
    (err) => console.error('Erro ao obter localização:', err.message)
  );
} else {
  console.log('Geolocalização não suportada');
}
```

**Exemplo mínimo — permissão para notificações:** muitas Web APIs exigem que o usuário aceite uma permissão antes do primeiro uso:

```javascript
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission().then((permission) => {
    if (permission === 'granted') {
      new Notification('Olá!', { body: 'Notificações ativadas.' });
    }
  });
}
```

Em resumo: as **Web APIs** estendem o que o JavaScript pode fazer no navegador, permitindo aplicações web e mobile (PWA/WebView) que usam câmera, microfone, geolocalização, notificações e outros recursos do dispositivo de forma padronizada e controlada pelo usuário (permissões).

### Ordem sugerida de estudo

1. Fundamentos da linguagem (tipos, variáveis, Promises, async/await) — arquivos 01 a 03 deste módulo.
2. DOM e eventos — [dom.md](../frontend/dom.md) e [events_js.md](../frontend/events_js.md).
3. Requisições HTTP com Fetch e/ou Axios — [http_requests_fetch_api.md](../frontend/http_requests_fetch_api.md) e [http_requests_axios.md](../frontend/http_requests_axios.md).
4. Exercícios que integram HTTP + DOM + eventos — [exercicio_fixacao_http_dom.md](../frontend/exercicio_fixacao_http_dom.md).

Assim você aplica a linguagem (incluindo assincronismo) no ambiente do navegador sem repetir teoria já vista aqui.

---

## JavaScript no Node.js

No Node.js não há **DOM** nem **window**. O ambiente oferece módulos para sistema de arquivos, rede, caminhos, variáveis de ambiente, etc. O **event loop** e o modelo assíncrono (Promises, async/await) são os mesmos; a diferença está nas APIs disponíveis.

### Módulos built-in (resumo)

| Módulo | Uso principal |
|--------|----------------|
| `fs` | Leitura e escrita de arquivos (síncrono e assíncrono); `fs.promises` para API com Promises. |
| `path` | Montagem e normalização de caminhos (`join`, `resolve`, `extname`, etc.). |
| `http` / `https` | Criar servidor HTTP ou fazer requisições cliente (baixo nível). |
| `url` | Parse e construção de URLs. |
| `events` | API de eventos (EventEmitter) para padrão pub/sub. |
| `stream` | Leitura e escrita em fluxo (arquivos grandes, rede). |
| `crypto` | Hash, criptografia, aleatoriedade. |
| `os` | Informações do sistema (plataforma, memória, etc.). |
| `process` | Argumentos, env, saída, sinais. |

### Módulos: CommonJS e ES modules

- **CommonJS:** `require('modulo')` e `module.exports` — padrão tradicional do Node.
- **ES modules:** `import ... from '...'` e `export` — habilitado com `"type": "module"` no `package.json` ou extensão `.mjs`.

Em projetos novos é comum usar ES modules; em código legado ou em muitos pacotes da comunidade ainda se usa CommonJS. Saber os dois ajuda a ler documentação e a integrar bibliotecas.

### Exemplo mínimo (servidor HTTP)

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Olá, Node!\n');
});

server.listen(3000, () => {
  console.log('Servidor em http://localhost:3000');
});
```

Na prática, muitas aplicações usam **Express** (ou outro framework) em cima de `http`; o importante é entender que por baixo está o módulo `http` e o modelo assíncrono da linguagem.

---

## Comparação rápida: navegador x Node

| Aspecto | Navegador | Node.js |
|--------|-----------|---------|
| Objeto global | `window` | `global` (ou `globalThis`) |
| DOM / document | Sim | Não |
| Sistema de arquivos | Não | Sim (`fs`) |
| Rede (cliente) | Fetch, XHR, Axios | `http`/`https`, Fetch (versões recentes), Axios |
| Rede (servidor) | Não | Sim (`http`, `net`, etc.) |
| Event loop | Sim | Sim (libuv) |
| Módulos | ES modules (scripts type="module") | CommonJS e ES modules |

Usar **`globalThis`** garante referência ao objeto global em ambos os ambientes (código que precise rodar no browser e no Node).

---

## Resumo da seção

- **Navegador:** DOM, BOM, eventos, Fetch (e Axios) e **Web APIs** (Geolocation, câmera/microfone, notificações, clipboard, etc.) para recursos do dispositivo em contexto web e mobile (PWA, WebView). O material de front-end ([dom.md](../frontend/dom.md), [events_js.md](../frontend/events_js.md), [http_requests_fetch_api.md](../frontend/http_requests_fetch_api.md), [http_requests_axios.md](../frontend/http_requests_axios.md)) cobre DOM, eventos e HTTP em detalhe; este módulo dá a base da linguagem e o panorama das APIs do navegador.
- **Node.js:** sem DOM; com `fs`, `path`, `http`, `url`, `events`, `stream`, `crypto`, `os`, `process`; CommonJS e ES modules.
- **Linguagem:** mesma em ambos (tipos, Promises, async/await, event loop); o que muda são as APIs e o uso (UI e rede no browser; servidor, arquivos e CLI no Node).

**Próximo:** [05-decisao-e-pratica.md](05-decisao-e-pratica.md) — Decisão e prática: quando usar o quê.
