# useContext



O `useContext` é um hook do React criado para simplificar o consumo de dados em componentes que precisam compartilhar informações sem a necessidade de passar propriedades por todos os níveis da árvore de componentes. Antes de sua introdução, esse compartilhamento era feito utilizando a API de Contexto combinada com componentes consumidores (`Context.Consumer`), ou por meio de "prop drilling", onde propriedades eram passadas manualmente de um componente pai para os filhos, mesmo quando componentes intermediários não precisavam dessas informações.

Essa abordagem de "prop drilling" tornava o código difícil de manter, especialmente em aplicações grandes, com muitos níveis de componentes. Com o `useContext`, tornou-se possível acessar diretamente o contexto em qualquer componente funcional, eliminando a necessidade de passar propriedades desnecessárias por toda a hierarquia.

------

### **Vantagens e Desvantagens de Usar o `useContext`**

#### **Vantagens:**

1. **Elimina o "prop drilling"**: Facilita o compartilhamento de dados em múltiplos níveis da árvore de componentes sem passar propriedades manualmente.
2. **Sintaxe mais simples**: Substitui o uso do `Context.Consumer` com um hook direto, resultando em código mais limpo e legível.
3. **Integração natural com hooks**: Funciona bem em componentes funcionais e pode ser combinado com outros hooks como `useState` e `useReducer`.
4. **Bom para casos simples**: Ideal para estados globais pequenos, como temas ou autenticação.

#### **Desvantagens:**

1. **Re-renderizações globais**: Sempre que o valor do contexto muda, todos os componentes que o consomem são re-renderizados, o que pode impactar a performance em estados muito grandes ou frequentemente alterados.
2. **Dificuldade em gerenciar estados complexos**: Para cenários onde há muita lógica de gerenciamento de estado, ferramentas como Redux ou Zustand podem ser mais adequadas.
3. **Dependência na hierarquia do provedor**: O componente que usa o `useContext` precisa estar dentro de um provedor do contexto. Esquecer de incluir o provedor pode gerar erros difíceis de debugar.

------

### **Casos de Uso Comuns do `useContext`**

1. **Gerenciamento de tema**: Alternar entre temas claro e escuro em aplicações.
2. **Autenticação**: Compartilhar informações de login e logout entre diferentes componentes.
3. **Carrinho de compras**: Gerenciar o estado global de itens em um carrinho de compras.
4. **Configurações globais**: Compartilhar configurações como preferências de idioma ou moeda.
5. **Gerenciamento de notificações**: Controlar a exibição de mensagens de erro ou sucesso em diferentes partes da aplicação.
6. **Controle de rotas protegidas**: Validar acesso com base no estado de autenticação.

------

O `useContext` é uma ferramenta poderosa para simplificar a comunicação entre componentes, especialmente em estados globais pequenos e moderados. No entanto, como qualquer ferramenta, deve ser utilizado com cautela, especialmente em cenários que exigem escalabilidade e desempenho mais robusto.



## CASOS DE USO 



O `useContext` é um hook do React que permite compartilhar estados e funções entre componentes sem a necessidade de passar propriedades manualmente por cada nível da árvore de componentes. Aqui estão alguns exemplos práticos de uso do `useContext`:

------

### **1. Gerenciamento de Tema**

Você pode usar o `useContext` para alternar entre temas claros e escuros em uma aplicação.

#### Contexto e Provedor:

```jsx
import React, { createContext, useState } from "react";

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState("light");

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

#### Componente Consumidor:

```jsx
import React, { useContext } from "react";
import { ThemeContext } from "./ThemeProvider";

const ThemedComponent = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <div style={{ background: theme === "light" ? "#fff" : "#333", color: theme === "light" ? "#000" : "#fff", padding: "20px" }}>
      <p>Current Theme: {theme}</p>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
};

export default ThemedComponent;
```

#### Uso na Aplicação:

```jsx
import React from "react";
import { ThemeProvider } from "./ThemeProvider";
import ThemedComponent from "./ThemedComponent";

const App = () => (
  <ThemeProvider>
    <ThemedComponent />
  </ThemeProvider>
);

export default App;
```

------

### **2. Gerenciamento de Autenticação**

Gerencie o estado de autenticação em uma aplicação.

#### Contexto e Provedor:

```jsx
import React, { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (username) => setUser({ username });
  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### Componente Consumidor:

```jsx
import React, { useContext } from "react";
import { AuthContext } from "./AuthProvider";

const LoginComponent = () => {
  const { user, login, logout } = useContext(AuthContext);

  return (
    <div>
      {user ? (
        <>
          <p>Welcome, {user.username}</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <p>You are not logged in.</p>
          <button onClick={() => login("JohnDoe")}>Login</button>
        </>
      )}
    </div>
  );
};

export default LoginComponent;
```

#### Uso na Aplicação:

```jsx
import React from "react";
import { AuthProvider } from "./AuthProvider";
import LoginComponent from "./LoginComponent";

const App = () => (
  <AuthProvider>
    <LoginComponent />
  </AuthProvider>
);

export default App;
```

------

### **3. Carrinho de Compras**

Gerencie um carrinho de compras em uma aplicação e-commerce.

#### Contexto e Provedor:

```jsx
import React, { createContext, useState } from "react";

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);

  const addItem = (item) => setCart((prev) => [...prev, item]);
  const removeItem = (id) => setCart((prev) => prev.filter((item) => item.id !== id));

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem }}>
      {children}
    </CartContext.Provider>
  );
};
```

#### Componente Consumidor:

```jsx
import React, { useContext } from "react";
import { CartContext } from "./CartProvider";

const CartComponent = () => {
  const { cart, addItem, removeItem } = useContext(CartContext);

  return (
    <div>
      <h2>Shopping Cart</h2>
      <ul>
        {cart.map((item) => (
          <li key={item.id}>
            {item.name} - ${item.price}
            <button onClick={() => removeItem(item.id)}>Remove</button>
          </li>
        ))}
      </ul>
      <button onClick={() => addItem({ id: 1, name: "Product A", price: 10 })}>
        Add Product A
      </button>
      <button onClick={() => addItem({ id: 2, name: "Product B", price: 20 })}>
        Add Product B
      </button>
    </div>
  );
};

export default CartComponent;
```

#### Uso na Aplicação:

```jsx
import React from "react";
import { CartProvider } from "./CartProvider";
import CartComponent from "./CartComponent";

const App = () => (
  <CartProvider>
    <CartComponent />
  </CartProvider>
);

export default App;
```

------

Esses exemplos mostram como `useContext` pode ser usado para facilitar o compartilhamento de estado e lógica entre componentes React de forma elegante e escalável.

