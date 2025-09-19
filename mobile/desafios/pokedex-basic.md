# 📱 Mini-Projeto (nível iniciante): “Mini Pokédex”

## 🎯 Objetivo (o que você vai aprender)

Construir um app simples em **React Native (Expo)** que:

1. **Lista** Pokémon (com paginação “Próxima/Anterior”);
2. **Busca por nome** (ex.: “pikachu”);
3. **Mostra detalhes** ao tocar em um item (imagem, tipos, habilidades).

> Foco: **chamar APIs com `fetch`**, **ler JSON**, **mostrar estados de carregamento e erro**, e **navegar entre telas** de forma bem simples.

------

## ✅ Requisitos (funcionais)

1. **Tela Lista (inicial)**

- Carregar a primeira página de Pokémon:
   `GET https://pokeapi.co/api/v2/pokemon?limit=20&offset=0`
- Mostrar **nome** dos Pokémon em uma lista.
- Mostrar botões **“Anterior”** e **“Próxima”** (paginação por `offset`).
- Ao tocar em um item, ir para a **Tela Detalhe**.

1. **Busca por nome**

- Campo de texto + botão **Buscar** no topo.
- Se o campo estiver vazio, mostra a lista paginada normal.
- Se o campo tiver um nome (ex.: `pikachu`), fazer:
   `GET https://pokeapi.co/api/v2/pokemon/{nome}`
- Se encontrar, navegar direto para a **Tela Detalhe** desse Pokémon.
- Se **não** encontrar (ex.: 404), mostrar mensagem “Pokémon não encontrado”.

1. **Tela Detalhe**

- Usar `GET /pokemon/{nome}` (ou `{id}`).
- Exibir:
  - **Imagem** (use `sprites.other['official-artwork'].front_default` se existir, senão `sprites.front_default`);
  - **Tipos** (ex.: electric, fire…);
  - **Habilidades** (abilities);
  - **Stats** principais (ex.: HP, Attack).
- Botão **Voltar** para a lista.

------

## ✅ Requisitos (não funcionais)

- Projeto criado com **Expo**.
- Código organizado e legível (componentes e telas separados).
- Mostrar **estado de carregamento** (ex.: spinner “Carregando…”).
- Mostrar **estado de erro** (mensagem e botão **Tentar novamente**).
- **TypeScript é bem-vindo**, mas opcional (faça como se sentir mais confortável).

------

## 🧩 Passo a passo sugerido

### 1) Criar o projeto

```bash
npx create-expo-app mini-pokedex
cd mini-pokedex
npm start
# Abra no Expo Go (celular) ou no emulador/simulador
```

### 2) (Opcional) Instalar navegação para a tela de detalhe

Se quiser usar duas telas (Lista e Detalhe) com navegação simples:

```bash
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
```

> Dica: também dá para fazer a “tela de detalhe” usando um **Modal** sem instalar nada. Escolha o que preferir.

### 3) Entender as respostas da API

- **Lista** (`/pokemon?limit=20&offset=0`) retorna algo como:

  ```json
  {
    "count": 1302,
    "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
    "previous": null,
    "results": [
      { "name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/" },
      ...
    ]
  }
  ```

- **Detalhe** (`/pokemon/pikachu`) retorna **sprites**, **types**, **abilities**, **stats** etc.

### 4) Exemplo de chamada com `fetch` (lista)

```js
async function loadPage(limit = 20, offset = 0) {
  try {
    setLoading(true);
    setError(null);
    const res = await fetch(`https://pokeapi.co/api/v2/pokemon?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Erro ao buscar lista');
    const data = await res.json(); // data.results é o array de { name, url }
    setPokemonList(data.results);
    setNextUrl(data.next);
    setPrevUrl(data.previous);
  } catch (e) {
    setError('Não foi possível carregar a lista. Tentar novamente?');
  } finally {
    setLoading(false);
  }
}
```

### 5) Exemplo de busca por nome

```js
async function searchByName(name) {
  const query = name.trim().toLowerCase();
  if (!query) {
    // Se vazio, volta para a lista normal (primeira página)
    loadPage(20, 0);
    return;
  }
  try {
    setLoading(true);
    setError(null);
    const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${query}`);
    if (res.status === 404) {
      setError('Pokémon não encontrado');
      return;
    }
    if (!res.ok) throw new Error('Erro ao buscar Pokémon');
    const data = await res.json();
    // Aqui você pode navegar para a tela de detalhe já com os dados
    navigation.navigate('Detalhe', { pokemon: data });
  } catch (e) {
    setError('Erro na busca. Tentar novamente?');
  } finally {
    setLoading(false);
  }
}
```

### 6) Exemplo de detalhe (na tela Detalhe)

```js
// Supondo que você recebeu `pokemon` via params
const image =
  pokemon?.sprites?.other?.['official-artwork']?.front_default ||
  pokemon?.sprites?.front_default;

<Text style={{ fontSize: 20, fontWeight: 'bold' }}>
  {pokemon.name}
</Text>

{image ? <Image source={{ uri: image }} style={{ width: 200, height: 200 }} /> : null}

<Text style={{ fontWeight: 'bold' }}>Tipos:</Text>
<Text>{pokemon.types.map(t => t.type.name).join(', ')}</Text>

<Text style={{ fontWeight: 'bold', marginTop: 8 }}>Habilidades:</Text>
<Text>{pokemon.abilities.map(a => a.ability.name).join(', ')}</Text>

<Text style={{ fontWeight: 'bold', marginTop: 8 }}>Stats:</Text>
{pokemon.stats.map(s => (
  <Text key={s.stat.name}>{s.stat.name}: {s.base_stat}</Text>
))}
```

### 7) Paginação simples com botões

- Guarde seu `offset` atual em um `useState`.
- Botão **Próxima** → `setOffset(offset + 20)` e chama `loadPage(20, offset + 20)`.
- Botão **Anterior** → `Math.max(offset - 20, 0)`.

### 8) Estados de UI (muito importantes!)

- **Carregando**: mostrar `ActivityIndicator` + texto “Carregando…”.
- **Erro**: mostrar a mensagem do estado `error` e um botão **Tentar novamente** que repete a última chamada.
- **Vazio**: se a lista vier vazia, mostrar “Nada por aqui ainda”.

------

## 🗂️ Entrega esperada

- Código do app (pode ser um zip ou repositório).
- Um **README.md** curto com:
  - como rodar (`npm start`, Expo Go etc.);
  - o que foi implementado;
  - prints de tela (se possível).

------

## 💡 Dicas para quem está começando

- Sempre trate os casos: **carregando**, **erro**, **sucesso**.
- Use `try/catch` com `async/await`.
- Converta a busca para **minúsculas**: `name.toLowerCase()`.
- Nem sempre a imagem “oficial” existe; tenha um **plano B** (sprite simples) ou um texto “sem imagem”.

------

## ⭐ Extras (opcionais, se der tempo)

- **Favoritar** um Pokémon (guardar só em memória).
- **Pull to refresh** (puxar a lista para recarregar).
- **Modal** de detalhe (sem instalar navegação).

------

# 🧪 Gabarito de Avaliação (Rubrica – iniciante)

**Pontuação total: 100 pontos**

### 1) Requisições HTTP básicas – 40 pts

- [20] Usa `fetch` corretamente (URL certa, `await res.json()`).
- [10] Trata **carregando** e **erro** (UI visível para o usuário).
- [10] Implementa **paginação** com `limit/offset` e botões Próxima/Anterior.

### 2) Busca por nome – 20 pts

- [10] Faz `GET /pokemon/{nome}` ao buscar.
- [10] Trata **não encontrado (404)** mostrando mensagem amigável.

### 3) Tela de Detalhe – 20 pts

- [10] Mostra **imagem** (oficial ou sprite) e **nome**.
- [5] Mostra **tipos** e **habilidades**.
- [5] Mostra **stats** principais.

### 4) Qualidade do código e UX – 20 pts

- [10] Organização simples e legível (componentes/telas separados, nomes claros).
- [5] Interface limpa, botões funcionam, textos legíveis.
- [5] README com instruções para rodar o projeto.

**Faixas de nota sugeridas**

- 90–100: Mandou muito bem! (todos os requisitos, código limpo)
- 75–89: Muito bom (pequenos ajustes)
- 60–74: Ok (funciona, mas faltam alguns pontos)
- <60: Refaça partes essenciais (requisições, estados ou detalhe)

------

## 🧭 Roteiro de estudo (se travar)

1. Como usar `fetch` e `await res.json()`.
2. Como controlar **loading** e **error** com `useState`.
3. Como **navegar** para outra tela (ou abrir um **Modal**).
4. Como **paginar** com `limit` e `offset`.

------

