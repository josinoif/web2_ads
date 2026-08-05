# Tutorial: Player de áudio/vídeo e galeria de imagens (React 19)

Neste tutorial você vai criar um **player** simples com play/pause e barra de progresso para áudio ou vídeo, e uma **galeria** que exibe imagens (com URLs de exemplo). Tudo controlado por estado e refs no React — com a novidade de `ref` como prop comum do React 19.

## Passo 1: Configurar o projeto

```bash
npm create vite@latest tutorial-multimidia -- --template react
cd tutorial-multimidia
npm install
```

## Passo 2: Componente Player (CSS Module + inline para valor dinâmico)

Crie a pasta `src/components` e o arquivo `src/components/Player.module.css`:

```css
.section {
  margin-bottom: 24px;
}

.progressTrack {
  margin-top: 8px;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progressBar {
  height: 100%;
  background: #4caf50;
  transition: width 0.2s ease;
}
```

Crie o arquivo `src/components/Player.jsx`:

```jsx
import { useRef, useState, useEffect } from 'react';
import styles from './Player.module.css';

function Player({ src, type = 'video' }) {
  const ref = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [progresso, setProgresso] = useState(0);
  const [duracao, setDuracao] = useState(0);

  const toggle = () => {
    if (!ref.current) return;
    if (playing) {
      ref.current.pause();
    } else {
      ref.current.play();
    }
    setPlaying(!playing);
  };

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onTimeUpdate = () => setProgresso(el.currentTime);
    const onLoadedMetadata = () => setDuracao(el.duration);
    const onEnded = () => { setPlaying(false); setProgresso(0); };
    el.addEventListener('timeupdate', onTimeUpdate);
    el.addEventListener('loadedmetadata', onLoadedMetadata);
    el.addEventListener('ended', onEnded);
    return () => {
      el.removeEventListener('timeupdate', onTimeUpdate);
      el.removeEventListener('loadedmetadata', onLoadedMetadata);
      el.removeEventListener('ended', onEnded);
    };
  }, []);

  const Tag = type === 'audio' ? 'audio' : 'video';
  const percent = duracao ? (progresso / duracao) * 100 : 0;

  return (
    <div className={styles.section}>
      <Tag ref={ref} src={src} controls={false} />
      <div>
        <button onClick={toggle}>{playing ? 'Pausar' : 'Reproduzir'}</button>
        <div className={styles.progressTrack}>
          <div className={styles.progressBar} style={{ width: `${percent}%` }} />
        </div>
        <small>{progresso.toFixed(1)}s / {duracao ? duracao.toFixed(1) : '0'}s</small>
      </div>
    </div>
  );
}

export default Player;
```

A largura da barra de progresso depende do estado (`progresso`, `duracao`), então usa-se `style={{ width }}` (valor dinâmico). O restante fica no CSS Module.

## Passo 3: Componente Galeria (com CSS Module)

Crie `src/components/Galeria.module.css`:

```css
.grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.thumbButton {
  padding: 0;
  border: none;
  cursor: pointer;
}

.thumb {
  width: 120px;
  height: 90px;
  object-fit: cover;
  display: block;
}

.highlight {
  margin-top: 16px;
}

.highlightImg {
  max-width: 100%;
  height: auto;
}
```

Crie `src/components/Galeria.jsx`:

```jsx
import { useState } from 'react';
import styles from './Galeria.module.css';

const IMAGENS_EXEMPLO = [
  'https://picsum.photos/400/300?random=1',
  'https://picsum.photos/400/300?random=2',
  'https://picsum.photos/400/300?random=3',
];

function Galeria() {
  const [selecionada, setSelecionada] = useState(null);

  return (
    <div>
      <h3>Galeria de imagens</h3>
      <div className={styles.grid}>
        {IMAGENS_EXEMPLO.map((url, i) => (
          <button
            key={i}
            onClick={() => setSelecionada(url)}
            className={styles.thumbButton}
          >
            <img src={url} alt={`Imagem ${i + 1}`} className={styles.thumb} />
          </button>
        ))}
      </div>
      {selecionada && (
        <div className={styles.highlight}>
          <p>Imagem em destaque:</p>
          <img src={selecionada} alt="Destaque" className={styles.highlightImg} />
        </div>
      )}
    </div>
  );
}

export default Galeria;
```

## Passo 4: Integrar no App (com CSS Module)

Crie `src/App.module.css`:

```css
.container {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.title {
  margin-bottom: 24px;
}
```

Edite `src/App.jsx`:

```jsx
import styles from './App.module.css';
import Player from './components/Player';
import Galeria from './components/Galeria';

const VIDEO_EXEMPLO = 'https://www.w3schools.com/html/mov_bbb.mp4';

function App() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Multimídia em React</h1>
      <section>
        <h2>Player de vídeo</h2>
        <Player src={VIDEO_EXEMPLO} type="video" />
      </section>
      <section>
        <Galeria />
      </section>
    </div>
  );
}

export default App;
```

## Passo 5: Executar a aplicação

```bash
npm run dev
```

O player permite play/pause e exibe a barra de progresso; a galeria exibe miniaturas e, ao clicar, mostra a imagem em destaque.

## Explicação dos principais elementos

- **useRef**: a ref no `<video>` ou `<audio>` dá acesso ao elemento DOM para chamar `play()` e `pause()` e ler `currentTime` e `duration`.
- **Eventos**: `timeupdate` atualiza o progresso; `loadedmetadata` preenche a duração; `ended` reseta o estado ao terminar.
- **Galeria**: estado `selecionada` guarda a URL da imagem clicada; as miniaturas são botões que atualizam esse estado; a imagem em destaque é condicional (`selecionada && <img ... />`).
- **Estilos**: CSS Modules para layout e aparência fixa; a largura da barra de progresso (`width: ${percent}%`) permanece em `style` por ser um valor calculado a partir do estado (boa prática para valores dinâmicos).

## Próximos passos

No módulo [12 - Bibliotecas](../12-bibliotecas/) você terá uma visão do ecossistema React e de bibliotecas úteis para UI, formulários e mais.
