# Módulo 04 - Backend: CRUD de Ingredientes

Neste módulo, você vai implementar o CRUD completo de ingredientes. Este é um CRUD mais simples que servirá de base para entender o CRUD de receitas.

## Objetivos do Módulo

- ✅ Criar o controller de ingredientes
- ✅ Criar as rotas de ingredientes
- ✅ Implementar CREATE (criar ingrediente)
- ✅ Implementar READ (listar e buscar)
- ✅ Implementar UPDATE (atualizar ingrediente)
- ✅ Implementar DELETE (deletar ingrediente)
- ✅ Testar todas as operações no Postman

---

## 1. Criando o Controller de Ingredientes

O controller contém toda a lógica de negócio para manipular ingredientes.

### Crie o arquivo `controllers/ingredientesController.js`:

```javascript
// ============================================
// CONTROLLER DE INGREDIENTES
// ============================================

const { pool } = require('../config/database');

// ============================================
// 1. LISTAR TODOS OS INGREDIENTES
// ============================================

exports.listarTodos = async (req, res) => {
    try {
        // Query SQL para buscar todos os ingredientes
        const [ingredientes] = await pool.query(
            'SELECT * FROM ingredientes ORDER BY nome'
        );

        // Retorna os ingredientes em formato JSON
        res.json({
            success: true,
            total: ingredientes.length,
            data: ingredientes
        });
    } catch (error) {
        console.error('Erro ao listar ingredientes:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao listar ingredientes',
            error: error.message
        });
    }
};

// ============================================
// 2. BUSCAR INGREDIENTE POR ID
// ============================================

exports.buscarPorId = async (req, res) => {
    try {
        const { id } = req.params;

        // Query SQL para buscar um ingrediente específico
        const [ingredientes] = await pool.query(
            'SELECT * FROM ingredientes WHERE id = ?',
            [id]
        );

        // Verifica se o ingrediente foi encontrado
        if (ingredientes.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Ingrediente não encontrado'
            });
        }

        res.json({
            success: true,
            data: ingredientes[0]
        });
    } catch (error) {
        console.error('Erro ao buscar ingrediente:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao buscar ingrediente',
            error: error.message
        });
    }
};

// ============================================
// 3. CRIAR NOVO INGREDIENTE
// ============================================

exports.criar = async (req, res) => {
    try {
        const { nome, unidade_medida } = req.body;

        // Validação dos dados
        if (!nome || !unidade_medida) {
            return res.status(400).json({
                success: false,
                message: 'Nome e unidade de medida são obrigatórios'
            });
        }

        // Verifica se o ingrediente já existe (nome é único)
        const [existente] = await pool.query(
            'SELECT id FROM ingredientes WHERE nome = ?',
            [nome]
        );

        if (existente.length > 0) {
            return res.status(400).json({
                success: false,
                message: 'Já existe um ingrediente com este nome'
            });
        }

        // Insere o novo ingrediente
        const [resultado] = await pool.query(
            'INSERT INTO ingredientes (nome, unidade_medida) VALUES (?, ?)',
            [nome, unidade_medida]
        );

        // Busca o ingrediente recém-criado
        const [novoIngrediente] = await pool.query(
            'SELECT * FROM ingredientes WHERE id = ?',
            [resultado.insertId]
        );

        res.status(201).json({
            success: true,
            message: 'Ingrediente criado com sucesso',
            data: novoIngrediente[0]
        });
    } catch (error) {
        console.error('Erro ao criar ingrediente:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao criar ingrediente',
            error: error.message
        });
    }
};

// ============================================
// 4. ATUALIZAR INGREDIENTE
// ============================================

exports.atualizar = async (req, res) => {
    try {
        const { id } = req.params;
        const { nome, unidade_medida } = req.body;

        // Validação dos dados
        if (!nome || !unidade_medida) {
            return res.status(400).json({
                success: false,
                message: 'Nome e unidade de medida são obrigatórios'
            });
        }

        // Verifica se o ingrediente existe
        const [ingredienteExistente] = await pool.query(
            'SELECT id FROM ingredientes WHERE id = ?',
            [id]
        );

        if (ingredienteExistente.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Ingrediente não encontrado'
            });
        }

        // Verifica se outro ingrediente já usa esse nome
        const [nomeExistente] = await pool.query(
            'SELECT id FROM ingredientes WHERE nome = ? AND id != ?',
            [nome, id]
        );

        if (nomeExistente.length > 0) {
            return res.status(400).json({
                success: false,
                message: 'Já existe outro ingrediente com este nome'
            });
        }

        // Atualiza o ingrediente
        await pool.query(
            'UPDATE ingredientes SET nome = ?, unidade_medida = ? WHERE id = ?',
            [nome, unidade_medida, id]
        );

        // Busca o ingrediente atualizado
        const [ingredienteAtualizado] = await pool.query(
            'SELECT * FROM ingredientes WHERE id = ?',
            [id]
        );

        res.json({
            success: true,
            message: 'Ingrediente atualizado com sucesso',
            data: ingredienteAtualizado[0]
        });
    } catch (error) {
        console.error('Erro ao atualizar ingrediente:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao atualizar ingrediente',
            error: error.message
        });
    }
};

// ============================================
// 5. DELETAR INGREDIENTE
// ============================================

exports.deletar = async (req, res) => {
    try {
        const { id } = req.params;

        // Verifica se o ingrediente existe
        const [ingrediente] = await pool.query(
            'SELECT * FROM ingredientes WHERE id = ?',
            [id]
        );

        if (ingrediente.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Ingrediente não encontrado'
            });
        }

        // Verifica se o ingrediente está sendo usado em alguma receita
        const [receitasUsando] = await pool.query(
            'SELECT COUNT(*) as total FROM receita_ingredientes WHERE ingrediente_id = ?',
            [id]
        );

        if (receitasUsando[0].total > 0) {
            return res.status(400).json({
                success: false,
                message: `Este ingrediente está sendo usado em ${receitasUsando[0].total} receita(s) e não pode ser deletado`
            });
        }

        // Deleta o ingrediente
        await pool.query('DELETE FROM ingredientes WHERE id = ?', [id]);

        res.json({
            success: true,
            message: 'Ingrediente deletado com sucesso',
            data: ingrediente[0]
        });
    } catch (error) {
        console.error('Erro ao deletar ingrediente:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao deletar ingrediente',
            error: error.message
        });
    }
};
```

### Explicação dos conceitos importantes:

**1. Async/Await com MySQL:**
```javascript
const [ingredientes] = await pool.query('SELECT * FROM ingredientes');
```
- `pool.query()` retorna um array: `[rows, fields]`
- Usamos destructuring `[ingredientes]` para pegar apenas as linhas

**2. Prepared Statements (proteção contra SQL Injection):**
```javascript
pool.query('SELECT * FROM ingredientes WHERE id = ?', [id]);
```
- O `?` é substituído de forma segura pelo valor em `[id]`
- Previne ataques de SQL Injection

**3. Status HTTP corretos:**
- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Erro do cliente (dados inválidos)
- `404`: Não encontrado
- `500`: Erro do servidor

**4. Validações:**
- Verifica se campos obrigatórios foram enviados
- Verifica se o ingrediente existe antes de atualizar/deletar
- Verifica se há duplicatas antes de criar/atualizar

---

## 2. Criando as Rotas de Ingredientes

Agora vamos criar as rotas que conectam as URLs aos métodos do controller.

### Crie o arquivo `routes/ingredientes.js`:

```javascript
// ============================================
// ROTAS DE INGREDIENTES
// ============================================

const express = require('express');
const router = express.Router();
const ingredientesController = require('../controllers/ingredientesController');

// ============================================
// DEFINIÇÃO DAS ROTAS
// ============================================

// GET /api/ingredientes - Listar todos os ingredientes
router.get('/', ingredientesController.listarTodos);

// GET /api/ingredientes/:id - Buscar ingrediente por ID
router.get('/:id', ingredientesController.buscarPorId);

// POST /api/ingredientes - Criar novo ingrediente
router.post('/', ingredientesController.criar);

// PUT /api/ingredientes/:id - Atualizar ingrediente
router.put('/:id', ingredientesController.atualizar);

// DELETE /api/ingredientes/:id - Deletar ingrediente
router.delete('/:id', ingredientesController.deletar);

// ============================================
// EXPORTAÇÃO
// ============================================

module.exports = router;
```

### Explicação:

**1. Router do Express:**
```javascript
const router = express.Router();
```
- Cria um roteador modular
- Permite organizar rotas em arquivos separados

**2. Métodos HTTP:**
- `GET`: Buscar/listar dados
- `POST`: Criar novos dados
- `PUT`: Atualizar dados existentes
- `DELETE`: Remover dados

**3. Parâmetros de rota:**
```javascript
router.get('/:id', ...)
```
- `:id` é um parâmetro dinâmico
- Acessível via `req.params.id`

---

## 3. Conectando as Rotas ao Servidor

Agora precisamos importar as rotas no arquivo principal.

### Abra `server.js` e adicione as rotas:

Encontre este comentário:
```javascript
// AQUI VIRÃO AS ROTAS DE INGREDIENTES E RECEITAS
```

Substitua por:
```javascript
// ============================================
// IMPORTAÇÃO DAS ROTAS
// ============================================

const ingredientesRoutes = require('./routes/ingredientes');

// ============================================
// USO DAS ROTAS
// ============================================

// Rotas de ingredientes
app.use('/api/ingredientes', ingredientesRoutes);

// AQUI VIRÃO AS ROTAS DE RECEITAS
// app.use('/api/receitas', receitasRoutes);
```

### O arquivo `server.js` completo ficará assim (parte relevante):

```javascript
// ... código anterior ...

// Importação das rotas
const ingredientesRoutes = require('./routes/ingredientes');

// Rotas
app.get('/', (req, res) => {
    // ... código da rota raiz ...
});

app.get('/api/test-db', async (req, res) => {
    // ... código de teste do banco ...
});

// Rotas de ingredientes
app.use('/api/ingredientes', ingredientesRoutes);

// ... código posterior ...
```

---

## 4. Testando no Postman

Agora vamos testar todas as operações CRUD.

### Certifique-se de que o servidor está rodando:

```bash
npm run dev
```

### 4.1. Teste 1: Listar Todos os Ingredientes

**Método:** GET  
**URL:** `http://localhost:3001/api/ingredientes`

**Resposta esperada:**
```json
{
  "success": true,
  "total": 20,
  "data": [
    {
      "id": 1,
      "nome": "Farinha de Trigo",
      "unidade_medida": "g",
      "criado_em": "2024-01-01T00:00:00.000Z"
    },
    // ... mais ingredientes
  ]
}
```

### 4.2. Teste 2: Buscar Ingrediente por ID

**Método:** GET  
**URL:** `http://localhost:3001/api/ingredientes/1`

**Resposta esperada:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nome": "Farinha de Trigo",
    "unidade_medida": "g",
    "criado_em": "2024-01-01T00:00:00.000Z"
  }
}
```

### 4.3. Teste 3: Criar Novo Ingrediente

**Método:** POST  
**URL:** `http://localhost:3001/api/ingredientes`  
**Headers:**
```
Content-Type: application/json
```
**Body (raw JSON):**
```json
{
  "nome": "Canela em Pó",
  "unidade_medida": "g"
}
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Ingrediente criado com sucesso",
  "data": {
    "id": 21,
    "nome": "Canela em Pó",
    "unidade_medida": "g",
    "criado_em": "2024-01-01T12:00:00.000Z"
  }
}
```

### 4.4. Teste 4: Atualizar Ingrediente

**Método:** PUT  
**URL:** `http://localhost:3001/api/ingredientes/21`  
**Headers:**
```
Content-Type: application/json
```
**Body (raw JSON):**
```json
{
  "nome": "Canela em Pó Fina",
  "unidade_medida": "gramas"
}
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Ingrediente atualizado com sucesso",
  "data": {
    "id": 21,
    "nome": "Canela em Pó Fina",
    "unidade_medida": "gramas",
    "criado_em": "2024-01-01T12:00:00.000Z"
  }
}
```

### 4.5. Teste 5: Deletar Ingrediente

**Método:** DELETE  
**URL:** `http://localhost:3001/api/ingredientes/21`

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Ingrediente deletado com sucesso",
  "data": {
    "id": 21,
    "nome": "Canela em Pó Fina",
    "unidade_medida": "gramas",
    "criado_em": "2024-01-01T12:00:00.000Z"
  }
}
```

### 4.6. Teste 6: Validações

**Teste criar sem nome:**

**Método:** POST  
**URL:** `http://localhost:3001/api/ingredientes`  
**Body:**
```json
{
  "unidade_medida": "g"
}
```

**Resposta esperada:**
```json
{
  "success": false,
  "message": "Nome e unidade de medida são obrigatórios"
}
```

**Teste criar nome duplicado:**

**Método:** POST  
**URL:** `http://localhost:3001/api/ingredientes`  
**Body:**
```json
{
  "nome": "Farinha de Trigo",
  "unidade_medida": "g"
}
```

**Resposta esperada:**
```json
{
  "success": false,
  "message": "Já existe um ingrediente com este nome"
}
```

---

## 5. Criando uma Coleção no Postman

Para organizar os testes, crie uma coleção.

### Passo a passo:

1. **No Postman, clique em "New" → "Collection"**
2. **Nome da coleção:** `Sistema de Receitas - API`
3. **Clique em "Create"**

4. **Adicione as requisições:**
   - Clique nos "..." da coleção → "Add Request"
   - Nome: `Listar Ingredientes`
   - Método: GET
   - URL: `http://localhost:3001/api/ingredientes`
   - Clique em "Save"

5. **Repita para todas as operações:**
   - Listar Ingredientes (GET)
   - Buscar Ingrediente por ID (GET)
   - Criar Ingrediente (POST)
   - Atualizar Ingrediente (PUT)
   - Deletar Ingrediente (DELETE)

---

## 6. Testando Erros Comuns

### Erro 404 - Ingrediente não encontrado:

**URL:** `http://localhost:3001/api/ingredientes/9999`

**Resposta:**
```json
{
  "success": false,
  "message": "Ingrediente não encontrado"
}
```

### Erro 400 - Ingrediente em uso:

Tente deletar um ingrediente que está em uma receita:

**URL:** `http://localhost:3001/api/ingredientes/1`  
**Método:** DELETE

**Resposta:**
```json
{
  "success": false,
  "message": "Este ingrediente está sendo usado em 1 receita(s) e não pode ser deletado"
}
```

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou o controller de ingredientes com todas as operações CRUD
- ✅ Criou as rotas de ingredientes
- ✅ Conectou as rotas ao servidor Express
- ✅ Implementou validações de dados
- ✅ Implementou tratamento de erros
- ✅ Testou todas as operações no Postman
- ✅ Aprendeu sobre prepared statements e segurança

---

## Próximo Passo

Agora que você dominou o CRUD básico, vamos para o desafio maior: CRUD de receitas com relacionamentos!

**➡️ Próximo:** [Módulo 05 - Backend: CRUD de Receitas](05-backend-receitas.md)

---

## Dicas Importantes

💡 **Sempre valide os dados** antes de inserir no banco de dados.

💡 **Use status HTTP corretos** para facilitar o debug.

💡 **Prepared statements** protegem contra SQL Injection.

💡 **Teste todas as situações:** sucesso, erro, validações, etc.

💡 **Salve sua coleção do Postman** para reutilizar os testes.
