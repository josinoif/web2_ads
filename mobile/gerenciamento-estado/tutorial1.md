# 📘 Tutorial Prático: Gerenciamento de Estado em React Native (com Expo + Context + useReducer)

## 0) Pré-requisitos

- Node.js LTS instalado (>= 18)
- NPM ou Yarn
- Dispositivo físico com o app **Expo Go** ou emulador/simulador instalado

------

## 1) Criar o projeto

```bash
# Crie o projeto com Expo (template TypeScript recomendado pelo mercado)
npx create-expo-app rn-state-demo --template
# Quando perguntar o template, escolha: "Blank (TypeScript)"
cd rn-state-demo
```

### Instalar dependências de navegação e persistência

```bash
# React Navigation (stack) e dependências
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context

# Persistência opcional (para mostrar estado persistente)
npm install @react-native-async-storage/async-storage
```

No iOS/Android bare é preciso steps extras; **no Expo** essas libs já funcionam sem `pod install`.

------

## 2) Estrutura de pastas

Crie a seguinte estrutura:

```
rn-state-demo/
├─ app.json
├─ package.json
├─ tsconfig.json
├─ App.tsx
└─ src/
   ├─ state/
   │  ├─ TodoContext.tsx
   │  └─ storage.ts
   ├─ navigation/
   │  └─ RootNavigator.tsx
   ├─ screens/
   │  ├─ HomeScreen.tsx
   │  ├─ NewTodoScreen.tsx
   │  └─ TodoDetailScreen.tsx
   └─ components/
      └─ TodoItem.tsx
```

Crie os diretórios/arquivos conforme abaixo.

------

## 3) Estado Global com Context + useReducer

### `src/state/TodoContext.tsx`

Expõe um **Provider** com reducer (adicionar, alternar concluído, remover) e **hooks** para consumir o estado.

```tsx
import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { getTodosFromStorage, saveTodosToStorage } from './storage';
import { Alert } from 'react-native';

export type Todo = {
  id: string;
  title: string;
  done: boolean;
  createdAt: number;
};

type State = {
  todos: Todo[];
  isHydrated: boolean; // indica se carregou do storage
};

type Action =
  | { type: 'ADD'; payload: { title: string } }
  | { type: 'TOGGLE'; payload: { id: string } }
  | { type: 'REMOVE'; payload: { id: string } }
  | { type: 'HYDRATE'; payload: { todos: Todo[] } };

const initialState: State = { todos: [], isHydrated: false };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'HYDRATE':
      return { todos: action.payload.todos, isHydrated: true };
    case 'ADD': {
      const newTodo: Todo = {
        id: crypto.randomUUID(),
        title: action.payload.title.trim(),
        done: false,
        createdAt: Date.now(),
      };
      if (!newTodo.title) return state;
      return { ...state, todos: [newTodo, ...state.todos] };
    }
    case 'TOGGLE': {
      const todos = state.todos.map(t => t.id === action.payload.id ? { ...t, done: !t.done } : t);
      return { ...state, todos };
    }
    case 'REMOVE': {
      const todos = state.todos.filter(t => t.id !== action.payload.id);
      return { ...state, todos };
    }
    default:
      return state;
  }
}

type TodoContextType = {
  state: State;
  addTodo: (title: string) => void;
  toggleTodo: (id: string) => void;
  removeTodo: (id: string) => void;
};

const TodoContext = createContext<TodoContextType | undefined>(undefined);

export function TodoProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Hidratar do AsyncStorage ao iniciar
  useEffect(() => {
    (async () => {
      try {
        const todos = await getTodosFromStorage();
        dispatch({ type: 'HYDRATE', payload: { todos } });
      } catch (e) {
        Alert.alert('Erro', 'Não foi possível carregar suas tarefas.');
        dispatch({ type: 'HYDRATE', payload: { todos: [] } });
      }
    })();
  }, []);

  // Salvar sempre que a lista mudar e já estiver hidratado
  useEffect(() => {
    if (state.isHydrated) {
      saveTodosToStorage(state.todos).catch(() =>
        Alert.alert('Aviso', 'Falha ao persistir tarefas.')
      );
    }
  }, [state.todos, state.isHydrated]);

  const addTodo = (title: string) => dispatch({ type: 'ADD', payload: { title } });
  const toggleTodo = (id: string) => dispatch({ type: 'TOGGLE', payload: { id } });
  const removeTodo = (id: string) => dispatch({ type: 'REMOVE', payload: { id } });

  return (
    <TodoContext.Provider value={{ state, addTodo, toggleTodo, removeTodo }}>
      {children}
    </TodoContext.Provider>
  );
}

export function useTodos() {
  const ctx = useContext(TodoContext);
  if (!ctx) throw new Error('useTodos precisa estar dentro de <TodoProvider>');
  return ctx;
}
```

### `src/state/storage.ts`

Persistência (opcional) com AsyncStorage.

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { Todo } from './TodoContext';

const KEY = '@rn_state_demo/todos';

export async function getTodosFromStorage(): Promise<Todo[]> {
  const raw = await AsyncStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function saveTodosToStorage(todos: Todo[]) {
  await AsyncStorage.setItem(KEY, JSON.stringify(todos));
}
```

------

## 4) Navegação (Stack) + Container

### `src/navigation/RootNavigator.tsx`

Define as 3 telas e seus parâmetros.

```tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator, NativeStackScreenProps } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import NewTodoScreen from '../screens/NewTodoScreen';
import TodoDetailScreen from '../screens/TodoDetailScreen';

export type RootStackParamList = {
  Home: undefined;
  NewTodo: undefined;
  TodoDetail: { id: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Minhas Tarefas' }} />
        <Stack.Screen name="NewTodo" component={NewTodoScreen} options={{ title: 'Nova Tarefa' }} />
        <Stack.Screen name="TodoDetail" component={TodoDetailScreen} options={{ title: 'Detalhe da Tarefa' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Tip helpers para telas (se quiser)
export type HomeProps = NativeStackScreenProps<RootStackParamList, 'Home'>;
export type NewTodoProps = NativeStackScreenProps<RootStackParamList, 'NewTodo'>;
export type DetailProps = NativeStackScreenProps<RootStackParamList, 'TodoDetail'>;
```

------

## 5) Telas

### `src/screens/HomeScreen.tsx`

Lista as tarefas (estado global) e navega para criar/visualizar.

```tsx
import React, { useMemo } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import type { HomeProps } from '../navigation/RootNavigator';
import { useTodos } from '../state/TodoContext';
import TodoItem from '../components/TodoItem';

export default function HomeScreen({ navigation }: HomeProps) {
  const { state } = useTodos();

  const sorted = useMemo(
    () => [...state.todos].sort((a, b) => b.createdAt - a.createdAt),
    [state.todos]
  );

  if (!state.isHydrated) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 8 }}>Carregando tarefas...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={sorted}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={<Text style={styles.empty}>Sem tarefas. Adicione a primeira!</Text>}
        renderItem={({ item }) => (
          <TodoItem
            todo={item}
            onPress={() => navigation.navigate('TodoDetail', { id: item.id })}
          />
        )}
      />

      <TouchableOpacity style={styles.fab} onPress={() => navigation.navigate('NewTodo')}>
        <Text style={styles.fabText}>＋</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  empty: { textAlign: 'center', marginTop: 24, color: '#666' },
  fab: {
    position: 'absolute', right: 20, bottom: 30,
    width: 56, height: 56, borderRadius: 28, backgroundColor: '#0a84ff',
    justifyContent: 'center', alignItems: 'center', elevation: 4
  },
  fabText: { color: '#fff', fontSize: 28, lineHeight: 30 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
```

### `src/screens/NewTodoScreen.tsx`

Demonstra **estado local** com `useState` e, ao salvar, usa **estado global**.

```tsx
import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import type { NewTodoProps } from '../navigation/RootNavigator';
import { useTodos } from '../state/TodoContext';

export default function NewTodoScreen({ navigation }: NewTodoProps) {
  const [title, setTitle] = useState('');
  const { addTodo } = useTodos();

  const save = () => {
    addTodo(title);
    navigation.goBack();
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.select({ ios: 'padding', android: undefined })}
    >
      <TextInput
        style={styles.input}
        placeholder="Descrição da tarefa"
        value={title}
        onChangeText={setTitle}
        autoFocus
        returnKeyType="done"
        onSubmitEditing={save}
      />
      <Button title="Salvar" onPress={save} disabled={!title.trim()} />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12, justifyContent: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, fontSize: 16 },
});
```

### `src/screens/TodoDetailScreen.tsx`

Recebe **parâmetros de rota** (id), lê do **estado global** e permite **toggle/remover**.

```tsx
import React, { useMemo } from 'react';
import { View, Text, Button, StyleSheet, Alert } from 'react-native';
import type { DetailProps } from '../navigation/RootNavigator';
import { useTodos } from '../state/TodoContext';

export default function TodoDetailScreen({ route, navigation }: DetailProps) {
  const { id } = route.params;
  const { state, toggleTodo, removeTodo } = useTodos();

  const todo = useMemo(() => state.todos.find(t => t.id === id), [state.todos, id]);

  if (!todo) {
    return (
      <View style={styles.container}>
        <Text style={{ color: '#666' }}>Tarefa não encontrada.</Text>
      </View>
    );
  }

  const onRemove = () => {
    Alert.alert('Remover', 'Deseja remover esta tarefa?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Remover', style: 'destructive', onPress: () => {
          removeTodo(todo.id);
          navigation.goBack();
        }
      },
    ]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{todo.title}</Text>
      <Text style={styles.meta}>
        Criada em: {new Date(todo.createdAt).toLocaleString()}
      </Text>
      <Text style={[styles.badge, { backgroundColor: todo.done ? '#34c759' : '#ff9f0a' }]}>
        {todo.done ? 'Concluída' : 'Pendente'}
      </Text>

      <View style={styles.row}>
        <Button title={todo.done ? 'Marcar como pendente' : 'Marcar como concluída'} onPress={() => toggleTodo(todo.id)} />
      </View>
      <View style={styles.row}>
        <Button title="Remover" color="#ff3b30" onPress={onRemove} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12 },
  title: { fontSize: 20, fontWeight: '600' },
  meta: { color: '#666' },
  badge: { alignSelf: 'flex-start', color: '#fff', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  row: { marginTop: 8 }
});
```

------

## 6) Componente de Item

### `src/components/TodoItem.tsx`

Pequeno componente clicável da lista.

```tsx
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import type { Todo } from '../state/TodoContext';
import { useTodos } from '../state/TodoContext';

export default function TodoItem({ todo, onPress }: { todo: Todo; onPress?: () => void }) {
  const { toggleTodo } = useTodos();

  return (
    <TouchableOpacity onPress={onPress} style={styles.row}>
      <View style={[styles.dot, { backgroundColor: todo.done ? '#34c759' : '#ff9f0a' }]} />
      <View style={{ flex: 1 }}>
        <Text style={[styles.title, todo.done && styles.done]} numberOfLines={1}>
          {todo.title}
        </Text>
        <Text style={styles.subtitle} numberOfLines={1}>
          {new Date(todo.createdAt).toLocaleString()}
        </Text>
      </View>
      <TouchableOpacity onPress={() => toggleTodo(todo.id)} style={styles.toggle}>
        <Text style={{ color: '#0a84ff' }}>{todo.done ? '↺' : '✓'}</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, gap: 10, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#eee' },
  dot: { width: 10, height: 10, borderRadius: 5 },
  title: { fontSize: 16 },
  done: { textDecorationLine: 'line-through', color: '#999' },
  subtitle: { color: '#666', fontSize: 12 },
  toggle: { paddingHorizontal: 8, paddingVertical: 6 },
});
```

------

## 7) App Root

### `App.tsx`

Envolva tudo com o **Provider** e o **Navigator**.

```tsx
import React from 'react';
import { TodoProvider } from './src/state/TodoContext';
import RootNavigator from './src/navigation/RootNavigator';

export default function App() {
  return (
    <TodoProvider>
      <RootNavigator />
    </TodoProvider>
  );
}
```

------

## 8) Executar o projeto

```bash
npm run start
# ou
npx expo start
```

- Abra o **Expo Go** no celular e escaneie o QR code, ou
- Pressione `i` (iOS) / `a` (Android) no terminal para abrir no simulador/emulador.

------

## 9) O que você ensinou (e por quê isso é “mercado”)

- **Estado local (useState)** para formulários e UI imediata.
- **Estado global (Context + useReducer)** para dados de negócio compartilhados (tarefas).
- **Navegação** com **React Navigation (Stack)** — padrão de mercado.
- **Passagem de parâmetros** (rota `TodoDetail` recebe `id`).
- **Persistência com AsyncStorage** para manter dados mesmo após fechar o app.
- **Boas práticas**: separar UI de “estado de negócio”, organizar rotas, evitar “prop drilling”, hidratação de estado, `useMemo` para listas.

------

## 10) Extensões (para lição de casa)

- **Filtro**: adicionar filtro “todas / pendentes / concluídas” (estado local da Home).
- **Busca**: adicionar TextInput para buscar por título.
- **Redux Toolkit ou Zustand**: reimplementar a store com uma dessas libs (padrão muito usado em apps grandes).
- **Teste**: criar testes de reducer (puro) com Jest.

### Bônus – mesmo reducer com **Zustand** (exemplo rápido)

```bash
npm install zustand
// src/state/useTodoStore.ts
import { create } from 'zustand';

type Todo = { id: string; title: string; done: boolean; createdAt: number };
type State = {
  todos: Todo[];
  add: (title: string) => void;
  toggle: (id: string) => void;
  remove: (id: string) => void;
};

export const useTodoStore = create<State>((set) => ({
  todos: [],
  add: (title) =>
    set((s) => ({
      todos: [{ id: crypto.randomUUID(), title: title.trim(), done: false, createdAt: Date.now() }, ...s.todos],
    })),
  toggle: (id) =>
    set((s) => ({ todos: s.todos.map(t => t.id === id ? { ...t, done: !t.done } : t) })),
  remove: (id) =>
    set((s) => ({ todos: s.todos.filter(t => t.id !== id) })),
}));
```

Depois, nas telas, troque `useTodos()` por `useTodoStore()` (ex.: `const todos = useTodoStore(s => s.todos)`), e ajuste chamadas `add/toggle/remove`.

> **Quando usar o quê?**
>
> - **Context + useReducer**: ótimo para apps pequenos/médios, sem dependências extras.
> - **Redux Toolkit**: padrão em apps grandes, integra middleware (thunk/sagas), devtools, persist, etc.
> - **Zustand**: API simples e leve, adoção crescente, ótimo DX.

------

## 11) Troubleshooting rápido

- **Tela branca/erro de import**: confira os caminhos dos arquivos e extensões `.tsx`.
- **Erro de navegação**: garanta que `NavigationContainer` envolve o Stack e que `@react-navigation/native` e `@react-navigation/native-stack` estão instalados.
- **AsyncStorage não funciona**: verifique se instalou `@react-native-async-storage/async-storage` e reinicie o bundler (`r`).
- **Typescript reclama de tipos de rota**: confira `RootStackParamList` e os tipos `NativeStackScreenProps` importados.

------

Se quiser, eu transformo este tutorial em **PDF** ou **PPTX com código destacado** — e também posso gerar um **repositório zipado** com a estrutura pronta para você compartilhar com a turma. Quer?