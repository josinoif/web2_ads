### Introdução ao `useEffect`

O `useEffect` é um hook fundamental no React, introduzido na versão 16.8, que permite lidar com efeitos colaterais em componentes funcionais. Antes da sua introdução, os componentes de classe dependiam de métodos do ciclo de vida, como `componentDidMount`, `componentDidUpdate` e `componentWillUnmount`, para executar lógica após a renderização. Embora funcionais, esses métodos frequentemente tornavam o código confuso e difícil de manter, pois concentravam várias responsabilidades em um único local.

O `useEffect` resolve esse problema ao oferecer uma abordagem declarativa e flexível para gerenciar efeitos colaterais, como requisições HTTP, manipulação do DOM, subscrições a eventos e limpeza de recursos. Com ele, os componentes funcionais podem lidar com tarefas complexas de maneira mais organizada e intuitiva.

---

### **Vantagens e Desvantagens de Usar o `useEffect`**

#### **Vantagens:**
1. **API Simples e Unificada**: Substitui múltiplos métodos de ciclo de vida por uma única função, simplificando a lógica de efeitos.
2. **Flexibilidade**: Permite configurar facilmente quando o efeito deve ser executado, usando dependências.
3. **Separação de Lógicas**: É possível declarar múltiplos `useEffect` no mesmo componente, dividindo as responsabilidades.
4. **Limpeza de Recursos**: Oferece suporte nativo à limpeza de efeitos, evitando problemas de memória.

#### **Desvantagens:**
1. **Re-renderizações Desnecessárias**: Dependências mal configuradas podem causar re-execuções frequentes e afetar a performance.
2. **Complexidade com Estados Relacionados**: Quando há muitos estados relacionados, os efeitos podem ficar difíceis de gerenciar.
3. **Cuidado com Efeitos Assíncronos**: Lidar com funções assíncronas dentro do `useEffect` pode gerar comportamento inesperado se não for bem projetado.

---

### **Casos de Uso Comuns do `useEffect`**

1. **Requisições HTTP**: Buscar dados de uma API ao carregar um componente.
   ```jsx
   useEffect(() => {
     fetch("https://api.example.com/data")
       .then(response => response.json())
       .then(data => setData(data));
   }, []); // Executa apenas na montagem do componente.
   ```

2. **Manipulação do DOM**: Atualizar o título da página com base em um estado.
   ```jsx
   useEffect(() => {
     document.title = `Você tem ${count} notificações`;
   }, [count]); // Executa quando o estado 'count' muda.
   ```

3. **Subscrições a Eventos**: Adicionar e remover ouvintes de eventos.
   ```jsx
   useEffect(() => {
     const handleResize = () => setWidth(window.innerWidth);
     window.addEventListener("resize", handleResize);

     return () => {
       window.removeEventListener("resize", handleResize);
     }; // Limpeza ao desmontar o componente.
   }, []);
   ```

4. **Temporizadores**: Configurar e limpar intervalos.
   ```jsx
   useEffect(() => {
     const interval = setInterval(() => {
       setTime((prev) => prev + 1);
     }, 1000);

     return () => clearInterval(interval); // Limpa o intervalo.
   }, []);
   ```

5. **Integrações com APIs de Terceiros**: Inicializar bibliotecas ou SDKs de terceiros.
6. **Sincronização de Estados**: Atualizar estados relacionados em resposta a mudanças em outros estados ou props.

---

### **Conclusão**

O `useEffect` é uma ferramenta indispensável no desenvolvimento de aplicações React modernas, permitindo que componentes funcionais lidem com efeitos colaterais de forma eficiente e organizada. Apesar de sua flexibilidade, seu uso requer cuidado, especialmente em cenários complexos com dependências e estados relacionados. Bem utilizado, o `useEffect` simplifica o código, melhora a legibilidade e aumenta a produtividade no desenvolvimento.


## Casos de Uso 

Aqui está uma lista de casos de uso comuns para o `useEffect` com exemplos de código:

---

### **1. Buscar Dados de uma API**
Exemplo de requisição a uma API ao carregar um componente.

```jsx
import React, { useState, useEffect } from "react";

const FetchData = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("https://pokeapi.co/api/v2/pokemon")
      .then((response) => response.json())
      .then((result) => {
        setData(result.results);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      {loading ? <p>Loading...</p> : data.map((item) => <p key={item.name}>{item.name}</p>)}
    </div>
  );
};

export default FetchData;
```

---

### **2. Atualizar o Título da Página**
Alterar o título do documento dinamicamente.

```jsx
import React, { useState, useEffect } from "react";

const DynamicTitle = () => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `Contagem: ${count}`;
  }, [count]);

  return (
    <div>
      <p>Você clicou {count} vezes.</p>
      <button onClick={() => setCount(count + 1)}>Clique aqui</button>
    </div>
  );
};

export default DynamicTitle;
```

---

### **3. Adicionar e Remover Listeners de Eventos**
Gerenciar eventos como redimensionamento da janela.

```jsx
import React, { useState, useEffect } from "react";

const WindowResize = () => {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <p>Largura da janela: {width}px</p>;
};

export default WindowResize;
```

---

### **4. Temporizadores**
Usar intervalos ou temporizadores e limpá-los corretamente.

```jsx
import React, { useState, useEffect } from "react";

const Timer = () => {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  return <p>Segundos: {seconds}</p>;
};

export default Timer;
```

---

### **5. Limpeza de Recursos**
Exemplo com uma simulação de subscrição.

```jsx
import React, { useEffect } from "react";

const SubscriptionComponent = () => {
  useEffect(() => {
    const subscribe = () => console.log("Subscrito");
    const unsubscribe = () => console.log("Desinscrito");

    subscribe();
    return () => {
      unsubscribe();
    };
  }, []);

  return <p>Veja o console para subscrição/desinscrição.</p>;
};

export default SubscriptionComponent;
```

---

### **6. Sincronizar Estados**
Sincronizar dois estados relacionados.

```jsx
import React, { useState, useEffect } from "react";

const SyncStates = () => {
  const [text, setText] = useState("");
  const [uppercase, setUppercase] = useState("");

  useEffect(() => {
    setUppercase(text.toUpperCase());
  }, [text]);

  return (
    <div>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <p>Maiúsculas: {uppercase}</p>
    </div>
  );
};

export default SyncStates;
```

---

### **7. Carregar Dados de Cache**
Carregar dados de cache, como o `localStorage`.

```jsx
import React, { useState, useEffect } from "react";

const LocalStorageComponent = () => {
  const [name, setName] = useState("");

  useEffect(() => {
    const savedName = localStorage.getItem("name");
    if (savedName) {
      setName(savedName);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("name", name);
  }, [name]);

  return (
    <div>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <p>Nome salvo: {name}</p>
    </div>
  );
};

export default LocalStorageComponent;
```

---

### **8. Autenticação Simples**
Simular o controle de autenticação do usuário.

```jsx
import React, { useState, useEffect } from "react";

const AuthExample = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  }, []);

  return (
    <div>
      {isAuthenticated ? (
        <p>Bem-vindo de volta!</p>
      ) : (
        <p>Por favor, faça login.</p>
      )}
    </div>
  );
};

export default AuthExample;
```

---

Esses exemplos mostram como o `useEffect` pode ser usado para lidar com efeitos colaterais em diferentes contextos, desde manipulação de DOM até interação com APIs ou limpeza de recursos. Cada caso demonstra a flexibilidade e importância desse hook no React.