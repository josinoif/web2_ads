# Web APIs: conceito, principais APIs e uso em projetos

Este documento aborda em profundidade as **Web APIs**: o que são, quais problemas ajudam a resolver, como funcionam e como usá-las em projetos web e mobile. Para fundamentos da linguagem JavaScript (Promises, async/await), consulte o módulo [../javascript/](../javascript/).

---

## O que são Web APIs?

**Web APIs** são interfaces padronizadas que o **navegador** expõe para que o JavaScript acesse recursos do dispositivo e do sistema operacional: localização, câmera, microfone, notificações, área de transferência, armazenamento persistente, sensores, entre outros. Elas são definidas por padrões como **W3C** e **WHATWG** e implementadas pelos fabricantes dos navegadores (Chrome, Firefox, Safari, Edge), o que garante um contrato comum entre código e ambiente.

### Por que existem?

- **Problema:** O JavaScript que roda na página não pode, por segurança, acessar diretamente hardware ou sistema de arquivos. Sem um contrato bem definido, cada site se comportaria de forma imprevisível e insegura.
- **Solução:** As Web APIs oferecem um **contrato estável**: o desenvolvedor chama métodos definidos (ex.: `navigator.geolocation.getCurrentPosition`) e o navegador cuida de permissões, privacidade e acesso real ao recurso. O usuário mantém controle (permissões, configurações) e o desenvolvedor tem um comportamento previsível entre navegadores compatíveis.

### Como funcionam em termos gerais

1. **Contexto seguro:** A maioria das Web APIs sensíveis só funciona em **HTTPS** (ou `localhost` em desenvolvimento). Em HTTP, muitas chamadas falham ou não estão disponíveis.
2. **Permissão do usuário:** Acesso a câmera, microfone, localização e notificações exige que o usuário **autorize** (pop-up de permissão). O código pode verificar o estado atual (ex.: `Notification.permission`) e solicitar permissão quando necessário.
3. **Assincronismo:** Muitas Web APIs retornam resultados de forma assíncrona (callbacks ou Promises), pois o hardware ou o sistema pode demorar para responder.
4. **Detecção de suporte:** Nem todo navegador ou dispositivo suporta todas as APIs. É boa prática verificar se a API existe antes de usá-la (ex.: `if ('geolocation' in navigator)`).

---

## Principais Web APIs: visão geral

A tabela abaixo resume as principais Web APIs, o **problema** que cada uma ajuda a resolver e **como** ela funciona em uma frase.

| API | Problema que ajuda a resolver | Como funciona |
|-----|-------------------------------|----------------|
| **Geolocation** | Saber onde o usuário está (mapas, entrega, clima, “perto de você”). | `navigator.geolocation`: `getCurrentPosition` (uma vez) ou `watchPosition` (contínuo); retorna latitude, longitude e precisão via callback. |
| **MediaDevices (getUserMedia)** | Acessar câmera e microfone (vídeo ao vivo, gravação, videoconferência, foto). | `navigator.mediaDevices.getUserMedia({ video, audio })` retorna Promise com **MediaStream**; você exibe em `<video>` ou processa com outras APIs. |
| **Notifications** | Alertar o usuário mesmo com a aba em segundo plano (lembretes, mensagens, e-mail). | `Notification.requestPermission()` e depois `new Notification(título, opções)`; integração com notificações do sistema. |
| **Clipboard** | Copiar ou colar texto (ou dados) programaticamente, sem depender de Ctrl+C/Ctrl+V. | `navigator.clipboard.writeText()` / `readText()` (async); escrita de imagens com `write()`; exige foco ou gesto do usuário em alguns casos. |
| **Web Storage (localStorage / sessionStorage)** | Persistir dados no navegador (preferências, cache, token) entre recarregamentos ou sessões. | `localStorage` (persistente) e `sessionStorage` (por aba/sessão); chave-valor em string; síncrono. |
| **Web Speech (SpeechRecognition / speechSynthesis)** | Entrada por voz (comandos, busca, legendas) e saída por voz (leitura em voz alta, acessibilidade). | `SpeechRecognition` para reconhecer fala; `speechSynthesis` para falar texto; suporte e qualidade variam por navegador. |
| **Device Orientation / Motion** | Usar orientação e movimento do dispositivo (jogos, realidade aumentada, gestos). | Eventos `deviceorientation` (alfa, beta, gama) e `devicemotion` (aceleração); não disponível em todos os dispositivos. |
| **Screen Orientation** | Saber ou forçar orientação da tela (retrato/paisagem) para ajustar layout. | `screen.orientation` (leitura e lock); útil em apps que rodam em tela cheia (ex.: vídeo, apresentação). |
| **Intersection Observer** | Saber quando um elemento entra ou sai da viewport (scroll infinito, lazy load, analytics). | `new IntersectionObserver(callback, options)` observa elementos e dispara quando cruzam um limite (ex.: visibilidade). |
| **Page Visibility** | Saber se a aba está visível ou em segundo plano (pausar vídeo, reduzir polling). | `document.visibilityState` e evento `visibilitychange`; evita desperdício de recurso quando o usuário não está vendo a página. |
| **Canvas / WebGL** | Desenho 2D/3D e processamento de imagem (gráficos, jogos, edição de foto). | `<canvas>` com contexto 2D ou WebGL; desenho e manipulação de pixels via JavaScript. |

Abaixo entramos em detalhe nas mais usadas no dia a dia (Geolocation, MediaDevices, Notifications, Clipboard, Storage) e depois em **Problema + Solução** com código pronto para colar no projeto.

---

## Geolocation API

**Problema:** Preciso da localização do usuário para mostrar no mapa, calcular distância, filtrar “perto de mim” ou enviar ao backend (entrega, agendamento).

**Como funciona:** O navegador usa GPS, rede ou WiFi para obter coordenadas. O usuário precisa autorizar; em mobile a precisão costuma ser maior.

### Métodos principais

- **getCurrentPosition(sucesso, erro?, opções?):** Obtém a posição uma vez. Callbacks recebem um objeto `Position` (ou `PositionError`).
- **watchPosition(...):** Obtém a posição continuamente (útil para navegação); retorna um ID que pode ser passado para **clearWatch(id)** para parar.

### Exemplo: obter coordenadas e tratar erro

```javascript
function obterLocalizacao() {
  if (!('geolocation' in navigator)) {
    console.error('Geolocalização não suportada');
    return;
  }

  const opcoes = {
    enableHighAccuracy: true,  // GPS quando disponível
    timeout: 10000,
    maximumAge: 60000          // cache em ms (1 min)
  };

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude, accuracy } = pos.coords;
      console.log('Lat:', latitude, 'Lon:', longitude, 'Precisão (m):', accuracy);
      // Enviar ao backend ou exibir no mapa
    },
    (err) => {
      switch (err.code) {
        case err.PERMISSION_DENIED:
          console.error('Usuário negou a localização');
          break;
        case err.POSITION_UNAVAILABLE:
          console.error('Posição indisponível');
          break;
        case err.TIMEOUT:
          console.error('Tempo esgotado');
          break;
      }
    },
    opcoes
  );
}
obterLocalizacao();
```

---

## MediaDevices API (getUserMedia): câmera e microfone

**Problema:** Preciso da câmera para tirar foto, escanear QR code ou transmitir vídeo; do microfone para gravação ou chamada de voz.

**Como funciona:** Você pede um **MediaStream** com restrições (apenas vídeo, apenas áudio, resolução). O navegador pede permissão ao usuário e retorna uma Promise com o stream. O stream pode ser exibido em `<video>` ou enviado para WebRTC/MediaRecorder.

### Exemplo: exibir a câmera em um `<video>`

```html
<video id="preview" autoplay playsinline></video>
<button id="parar">Parar câmera</button>
```

```javascript
let streamAtual = null;

async function iniciarCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720 },
      audio: false
    });
    streamAtual = stream;
    document.getElementById('preview').srcObject = stream;
  } catch (err) {
    console.error('Erro ao acessar câmera:', err.name, err.message);
    if (err.name === 'NotAllowedError') {
      alert('Permissão de câmera negada.');
    }
  }
}

document.getElementById('parar').addEventListener('click', () => {
  if (streamAtual) {
    streamAtual.getTracks().forEach((track) => track.stop());
    document.getElementById('preview').srcObject = null;
    streamAtual = null;
  }
});

iniciarCamera();
```

### Exemplo: apenas microfone (áudio)

```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
// Usar stream com MediaRecorder, Web Audio API ou WebRTC
```

---

## Notifications API

**Problema:** Preciso avisar o usuário de algo (nova mensagem, lembrete, alerta) mesmo quando a aba está em segundo plano ou o navegador minimizado.

**Como funciona:** Você solicita permissão com `Notification.requestPermission()`. Se for `granted`, pode criar `new Notification(título, opções)`. As notificações aparecem no sistema (bandeja do SO) e podem incluir ícone, corpo de texto e ações (dependendo do navegador).

### Exemplo: pedir permissão e enviar uma notificação

```javascript
async function pedirPermissaoENotificar() {
  if (!('Notification' in window)) {
    console.log('Notificações não suportadas');
    return;
  }

  if (Notification.permission === 'granted') {
    new Notification('Título', {
      body: 'Mensagem da notificação.',
      icon: '/icone.png'
    });
    return;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      new Notification('Permissão concedida!', { body: 'Você receberá avisos aqui.' });
    }
  }
}
```

---

## Clipboard API

**Problema:** Preciso copiar um texto para a área de transferência (ex.: link de compartilhamento, código) ou ler o que o usuário colou, sem depender apenas de Ctrl+C/Ctrl+V.

**Como funciona:** `navigator.clipboard.writeText(texto)` e `readText()` retornam Promises. Em muitos navegadores, `readText()` exige que a página tenha foco ou que a leitura seja disparada por um gesto do usuário (ex.: clique em um botão).

### Exemplo: botão “Copiar link”

```javascript
async function copiarParaAreaTransferencia(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    console.log('Copiado!');
    return true;
  } catch (err) {
    console.error('Falha ao copiar:', err);
    return false;
  }
}

// No clique do botão
document.getElementById('btnCopiar').addEventListener('click', async () => {
  const ok = await copiarParaAreaTransferencia('https://meusite.com/compartilhar/123');
  if (ok) alert('Link copiado!');
});
```

### Exemplo: colar (ler da área de transferência)

```javascript
async function colarDaAreaTransferencia() {
  try {
    const texto = await navigator.clipboard.readText();
    console.log('Colado:', texto);
    return texto;
  } catch (err) {
    console.error('Falha ao colar ou permissão negada:', err);
    return null;
  }
}
```

---

## Web Storage (localStorage e sessionStorage)

**Problema:** Preciso guardar dados no navegador entre recarregamentos (preferências, token, cache simples) sem enviar tudo ao servidor.

**Como funciona:** Ambos são objetos que armazenam pares **chave-valor** em string. `localStorage` persiste até o usuário limpar os dados ou o site alterar; `sessionStorage` dura apenas enquanto a aba/sessão estiver aberta. Acesso síncrono: `getItem`, `setItem`, `removeItem`, `clear`.

### Exemplo: salvar e recuperar preferência

```javascript
const CHAVE_TEMA = 'tema';

function salvarTema(tema) {
  localStorage.setItem(CHAVE_TEMA, tema);
}

function obterTema() {
  return localStorage.getItem(CHAVE_TEMA) || 'claro';
}

// Ao carregar a página
document.documentElement.setAttribute('data-tema', obterTema());

// Ao mudar o tema (ex.: toggle)
document.getElementById('toggleTema').addEventListener('click', () => {
  const novo = obterTema() === 'claro' ? 'escuro' : 'claro';
  salvarTema(novo);
  document.documentElement.setAttribute('data-tema', novo);
});
```

---

## Lista Problema + Solução (exemplos para usar no projeto)

Cada item abaixo descreve um **problema** real e uma **solução** com exemplo de código que você pode adaptar ao seu projeto.

---

### 1. Preciso obter a localização do usuário para mostrar no mapa ou enviar ao backend

**Solução:** Usar a Geolocation API com `getCurrentPosition`, tratar permissão e erros, e usar as coordenadas no seu fluxo (mapa, API, etc.).

```javascript
function obterCoordenadas() {
  return new Promise((resolve, reject) => {
    if (!('geolocation' in navigator)) {
      reject(new Error('Geolocalização não suportada'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        precisao: pos.coords.accuracy
      }),
      (err) => reject(err),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  });
}

// Uso
obterCoordenadas()
  .then((coords) => console.log('Coordenadas:', coords))
  .catch((err) => console.error('Erro:', err.message));
```

---

### 2. Preciso exibir a câmera do usuário em tempo real na página

**Solução:** `getUserMedia` com `video: true` (ou com restrições de tamanho) e atribuir o stream a `video.srcObject`.

```javascript
const video = document.querySelector('video');
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
video.srcObject = stream;
video.play();
// Para parar depois: stream.getTracks().forEach(t => t.stop());
```

---

### 3. Preciso tirar uma foto (frame) da câmera e enviar ou exibir

**Solução:** Desenhar o frame atual do `<video>` em um `<canvas>`, depois obter o blob ou Data URL para enviar ou mostrar.

```javascript
const video = document.querySelector('video');
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
canvas.getContext('2d').drawImage(video, 0, 0);

canvas.toBlob((blob) => {
  const formData = new FormData();
  formData.append('foto', blob, 'foto.jpg');
  fetch('/api/upload', { method: 'POST', body: formData });
}, 'image/jpeg', 0.9);
```

---

### 4. Preciso enviar notificações ao usuário mesmo com a aba em segundo plano

**Solução:** Verificar suporte, pedir permissão com `Notification.requestPermission()` e criar `new Notification(...)` quando permitido.

```javascript
async function mostrarNotificacao(titulo, corpo) {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    await Notification.requestPermission();
  }
  if (Notification.permission === 'granted') {
    new Notification(titulo, { body: corpo });
  }
}
mostrarNotificacao('Lembrete', 'Reunião em 5 minutos.');
```

---

### 5. Preciso de um botão “Copiar” que coloque um texto na área de transferência

**Solução:** No clique do botão, chamar `navigator.clipboard.writeText(texto)` e dar feedback ao usuário.

```javascript
document.getElementById('btnCopiar').addEventListener('click', async () => {
  const texto = document.getElementById('codigo').innerText;
  try {
    await navigator.clipboard.writeText(texto);
    alert('Copiado!');
  } catch (e) {
    console.error(e);
  }
});
```

---

### 6. Preciso guardar o token de autenticação no navegador para reutilizar após recarregar

**Solução:** Salvar no `localStorage` após o login e ler ao inicializar o app; remover no logout.

```javascript
const CHAVE_TOKEN = 'token';

function salvarToken(token) {
  localStorage.setItem(CHAVE_TOKEN, token);
}
function obterToken() {
  return localStorage.getItem(CHAVE_TOKEN);
}
function removerToken() {
  localStorage.removeItem(CHAVE_TOKEN);
}

// Após login bem-sucedido
salvarToken(resposta.token);

// No carregamento da aplicação
const token = obterToken();
if (token) {
  // Incluir no header das requisições ou restaurar sessão
}
```

---

### 7. Preciso saber quando um elemento entra na tela (lazy load de imagem ou “infinite scroll”)

**Solução:** Usar **Intersection Observer** para observar o elemento e carregar conteúdo quando ele ficar visível.

```javascript
const img = document.querySelector('img[data-src]');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const el = entry.target;
        el.src = el.dataset.src || el.getAttribute('data-src');
        observer.unobserve(el);
      }
    });
  },
  { rootMargin: '50px' }
);

observer.observe(img);
```

---

### 8. Preciso pausar um vídeo ou parar de fazer requisições quando o usuário troca de aba

**Solução:** Usar a **Page Visibility API**: escutar `visibilitychange` e verificar `document.visibilityState`.

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    video.pause();
    clearInterval(intervaloPolling);
  } else {
    video.play();
    iniciarPolling();
  }
});
```

---

### 9. Preciso verificar se o navegador suporta uma Web API antes de usá-la

**Solução:** Testar a existência da API no objeto global (ex.: `navigator`, `window`) antes de chamar métodos.

```javascript
function usarGeolocation() {
  if (!('geolocation' in navigator)) {
    alert('Seu navegador não suporta geolocalização.');
    return;
  }
  navigator.geolocation.getCurrentPosition(/* ... */);
}

function usarClipboard() {
  if (!navigator.clipboard || !navigator.clipboard.writeText) {
    alert('Copiar não suportado. Use Ctrl+C.');
    return;
  }
  navigator.clipboard.writeText(texto);
}
```

---

### 10. Preciso pedir permissão de microfone e gravar áudio

**Solução:** `getUserMedia({ audio: true })` para obter o stream; usar **MediaRecorder** para gravar em blob (ex.: WebM) e depois enviar ou reproduzir.

```javascript
let mediaRecorder;
let chunks = [];

const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
mediaRecorder = new MediaRecorder(stream);
mediaRecorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);
mediaRecorder.onstop = () => {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  const url = URL.createObjectURL(blob);
  document.querySelector('audio').src = url;
  stream.getTracks().forEach((t) => t.stop());
};
mediaRecorder.start();
// Para parar: mediaRecorder.stop();
```

---

## Resumo

- **Web APIs** são interfaces padronizadas do navegador para acessar localização, câmera, microfone, notificações, clipboard, armazenamento e outros recursos, com permissão do usuário e em contexto seguro (HTTPS).
- As principais que você usará em projetos são: **Geolocation**, **MediaDevices (getUserMedia)**, **Notifications**, **Clipboard**, **Web Storage**, além de **Intersection Observer** e **Page Visibility** para comportamento de página.
- Sempre verifique suporte (`in navigator`, etc.) e trate permissão e erros; use async/await ou Promises onde a API for assíncrona.
- A lista **Problema + Solução** acima cobre cenários comuns (localização, câmera, foto, notificação, copiar, token, lazy load, visibility, detecção de suporte, gravação de áudio) com código que você pode adaptar ao seu projeto.

Para um panorama de onde as Web APIs se encaixam em relação ao JavaScript no navegador e no Node, veja [../javascript/04-js-navegador-node.md](../javascript/04-js-navegador-node.md).
