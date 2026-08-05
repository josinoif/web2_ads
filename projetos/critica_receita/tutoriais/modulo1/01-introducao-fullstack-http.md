# Tutorial 1: Introdução ao Desenvolvimento Full-Stack e HTTP

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Compreender a arquitetura cliente-servidor
- Entender o protocolo HTTP e seus métodos
- Conhecer os principais status codes HTTP
- Entender o conceito de API REST
- Identificar as diferenças entre frontend e backend

## 📖 Conteúdo

### 1. Arquitetura Cliente-Servidor

O desenvolvimento web moderno se baseia na arquitetura cliente-servidor:

**Cliente (Frontend)**
- Interface visual que o usuário interage
- Executa no navegador (browser)
- Tecnologias: HTML, CSS, JavaScript, React, Angular, Vue

**Servidor (Backend)**
- Processa requisições e gerencia dados
- Executa em servidores remotos
- Tecnologias: Node.js, Python, Java, PHP

```
┌─────────────┐                    ┌─────────────┐
│   Cliente   │ ←──── HTTP ────→  │  Servidor   │
│  (Browser)  │                    │   (API)     │
└─────────────┘                    └─────────────┘
       ↑                                  ↓
   Visualiza                         Processa
    Dados                            e Armazena
```

### 2. O Protocolo HTTP

HTTP (HyperText Transfer Protocol) é o protocolo de comunicação da web.

**Estrutura de uma Requisição HTTP:**
```
GET /api/restaurantes HTTP/1.1
Host: localhost:3000
Content-Type: application/json
Authorization: Bearer token123

{ corpo da requisição (se houver) }
```

**Componentes principais:**
- **Método** (GET, POST, PUT, DELETE)
- **URL/Endpoint** (/api/restaurantes)
- **Headers** (metadados da requisição)
- **Body** (dados enviados, quando aplicável)

### 3. Métodos HTTP

Os métodos HTTP definem a ação a ser realizada:

| Método | Propósito | Exemplo de Uso |
|--------|-----------|----------------|
| **GET** | Recuperar dados | Listar restaurantes |
| **POST** | Criar novo recurso | Adicionar novo restaurante |
| **PUT** | Atualizar recurso completo | Atualizar todos os dados |
| **PATCH** | Atualizar parcialmente | Atualizar apenas o nome |
| **DELETE** | Remover recurso | Deletar restaurante |

**Exemplo prático:**

```javascript
// GET - Buscar todos os restaurantes
GET /api/restaurantes

// GET - Buscar um restaurante específico
GET /api/restaurantes/5

// POST - Criar novo restaurante
POST /api/restaurantes
Body: {
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "endereco": "Rua das Flores, 123"
}

// PUT - Atualizar restaurante
PUT /api/restaurantes/5
Body: {
  "nome": "Pizza Bella Premium",
  "categoria": "Italiana",
  "endereco": "Rua das Flores, 123"
}

// DELETE - Remover restaurante
DELETE /api/restaurantes/5
```

### 4. Status Codes HTTP

Os códigos de status indicam o resultado da requisição:

**2xx - Sucesso**
- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Sucesso sem conteúdo de resposta

**4xx - Erro do Cliente**
- `400 Bad Request` - Requisição inválida
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado

**5xx - Erro do Servidor**
- `500 Internal Server Error` - Erro interno do servidor
- `503 Service Unavailable` - Serviço indisponível

### 5. API REST

REST (Representational State Transfer) é um estilo arquitetural para APIs.

**Princípios REST:**

1. **Cliente-Servidor**: Separação de responsabilidades
2. **Stateless**: Cada requisição é independente
3. **Cacheable**: Respostas podem ser cacheadas
4. **Interface Uniforme**: Endpoints padronizados
5. **Sistema em Camadas**: Arquitetura modular

**Boas práticas REST:**

```javascript
// ✅ BOM - URLs claras e recursos bem definidos
GET    /api/restaurantes           // Listar todos
GET    /api/restaurantes/5         // Buscar um
POST   /api/restaurantes           // Criar
PUT    /api/restaurantes/5         // Atualizar
DELETE /api/restaurantes/5         // Deletar

// ✅ BOM - Relacionamentos aninhados
GET    /api/restaurantes/5/avaliacoes    // Avaliações do restaurante 5
POST   /api/restaurantes/5/avaliacoes    // Criar avaliação

// ❌ RUIM - Verbos na URL
GET /api/getRestaurantes
POST /api/createRestaurante
GET /api/deleteRestaurante/5
```

### 6. Formato JSON

APIs REST geralmente usam JSON para trocar dados:

```json
{
  "id": 5,
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "endereco": "Rua das Flores, 123",
  "telefone": "(11) 98765-4321",
  "avaliacaoMedia": 4.5,
  "criadoEm": "2024-01-15T10:30:00Z"
}
```

### 7. Exemplo de Fluxo Completo

```javascript
// 1. Cliente faz requisição
fetch('http://localhost:3000/api/restaurantes', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nome: 'Pizza Bella',
    categoria: 'Italiana'
  })
})

// 2. Servidor recebe e processa
app.post('/api/restaurantes', (req, res) => {
  const novoRestaurante = req.body;
  // Salva no banco de dados
  // ...
  res.status(201).json(novoRestaurante);
})

// 3. Cliente recebe resposta
.then(response => response.json())
.then(data => {
  console.log('Restaurante criado:', data);
})
```

## 🔨 Atividade Prática

### Exercício 1: Identificando Métodos HTTP

Para cada cenário, identifique o método HTTP correto:

1. Visualizar a lista de receitas
2. Adicionar uma nova receita
3. Atualizar a descrição de uma receita
4. Remover uma receita
5. Buscar receitas por categoria

<details>
<summary>Ver respostas</summary>

1. GET /api/receitas
2. POST /api/receitas
3. PUT ou PATCH /api/receitas/:id
4. DELETE /api/receitas/:id
5. GET /api/receitas?categoria=doces

</details>

### Exercício 2: Interpretando Status Codes

Qual status code você usaria para:

1. Usuário tentou acessar um recurso que não existe
2. Senha incorreta no login
3. Receita criada com sucesso
4. Erro de sintaxe no JSON enviado
5. Servidor fora do ar para manutenção

<details>
<summary>Ver respostas</summary>

1. 404 Not Found
2. 401 Unauthorized
3. 201 Created
4. 400 Bad Request
5. 503 Service Unavailable

</details>

### Exercício 3: Projetando Endpoints REST

Projete os endpoints REST para um sistema de biblioteca que gerencia:
- Livros
- Autores
- Empréstimos

Liste os endpoints principais com seus métodos HTTP.

<details>
<summary>Ver exemplo de solução</summary>

```
# Livros
GET    /api/livros
GET    /api/livros/:id
POST   /api/livros
PUT    /api/livros/:id
DELETE /api/livros/:id

# Autores
GET    /api/autores
GET    /api/autores/:id
POST   /api/autores
PUT    /api/autores/:id
DELETE /api/autores/:id

# Relacionamentos
GET    /api/autores/:id/livros
GET    /api/livros/:id/autor

# Empréstimos
GET    /api/emprestimos
POST   /api/emprestimos
PUT    /api/emprestimos/:id (devolver livro)
```

</details>

## 💡 Conceitos-Chave

- **HTTP** é o protocolo de comunicação da web
- **Métodos HTTP** definem a ação (GET, POST, PUT, DELETE)
- **Status codes** indicam o resultado da operação
- **REST** é um padrão arquitetural para APIs
- **JSON** é o formato padrão para troca de dados
- APIs devem ser **stateless** (sem estado)
- URLs devem representar **recursos**, não ações

## ➡️ Próximos Passos

Agora que você compreende os fundamentos do HTTP e APIs REST, no próximo tutorial vamos mergulhar em **Bancos de Dados Relacionais**, entendendo como estruturar e armazenar os dados da nossa aplicação.

[➡️ Ir para Tutorial 2: Bancos de Dados Relacionais](02-bancos-dados-relacionais.md)

---

**Dúvidas?** Revise os conceitos acima e certifique-se de entender cada um antes de prosseguir. A compreensão sólida destes fundamentos é essencial para o resto do curso!
