# Módulo 05 - Backend: CRUD de Receitas

Neste módulo, você vai implementar o CRUD complexo de receitas, incluindo o gerenciamento de múltiplos ingredientes e relacionamentos entre tabelas.

## Objetivos do Módulo

- ✅ Criar o controller de receitas
- ✅ Implementar queries com JOIN
- ✅ Gerenciar transações no MySQL
- ✅ Criar receitas com múltiplos ingredientes
- ✅ Atualizar receitas e seus ingredientes
- ✅ Deletar receitas e relacionamentos
- ✅ Filtrar receitas por categoria
- ✅ Testar no Postman

---

## 1. Criando o Controller de Receitas

Este controller é mais complexo pois lida com múltiplas tabelas simultaneamente.

### Crie o arquivo `controllers/receitasController.js`:

```javascript
// ============================================
// CONTROLLER DE RECEITAS
// ============================================

const { pool } = require('../config/database');

// ============================================
// 1. LISTAR TODAS AS RECEITAS
// ============================================

exports.listarTodas = async (req, res) => {
    try {
        // Query com JOIN para buscar receitas e seus ingredientes
        const [receitas] = await pool.query(`
            SELECT 
                r.*,
                GROUP_CONCAT(
                    CONCAT(
                        i.nome, ' (', 
                        ri.quantidade, 
                        i.unidade_medida, ')'
                    ) SEPARATOR ', '
                ) as ingredientes_resumo
            FROM receitas r
            LEFT JOIN receita_ingredientes ri ON r.id = ri.receita_id
            LEFT JOIN ingredientes i ON ri.ingrediente_id = i.id
            GROUP BY r.id
            ORDER BY r.criado_em DESC
        `);

        res.json({
            success: true,
            total: receitas.length,
            data: receitas
        });
    } catch (error) {
        console.error('Erro ao listar receitas:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao listar receitas',
            error: error.message
        });
    }
};

// ============================================
// 2. BUSCAR RECEITA POR ID (COM INGREDIENTES)
// ============================================

exports.buscarPorId = async (req, res) => {
    try {
        const { id } = req.params;

        // Busca a receita
        const [receitas] = await pool.query(
            'SELECT * FROM receitas WHERE id = ?',
            [id]
        );

        if (receitas.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Receita não encontrada'
            });
        }

        // Busca os ingredientes da receita
        const [ingredientes] = await pool.query(`
            SELECT 
                ri.id,
                ri.quantidade,
                i.id as ingrediente_id,
                i.nome,
                i.unidade_medida
            FROM receita_ingredientes ri
            INNER JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE ri.receita_id = ?
            ORDER BY i.nome
        `, [id]);

        // Monta o objeto de resposta
        const receita = {
            ...receitas[0],
            ingredientes: ingredientes
        };

        res.json({
            success: true,
            data: receita
        });
    } catch (error) {
        console.error('Erro ao buscar receita:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao buscar receita',
            error: error.message
        });
    }
};

// ============================================
// 3. CRIAR NOVA RECEITA
// ============================================

exports.criar = async (req, res) => {
    // Inicia uma conexão para usar transação
    const connection = await pool.getConnection();
    
    try {
        const { nome, categoria, modo_preparo, tempo_preparo, rendimento, ingredientes } = req.body;

        // ========== VALIDAÇÕES ==========
        
        if (!nome || !categoria || !modo_preparo || !tempo_preparo || !rendimento) {
            return res.status(400).json({
                success: false,
                message: 'Todos os campos da receita são obrigatórios'
            });
        }

        if (!ingredientes || !Array.isArray(ingredientes) || ingredientes.length === 0) {
            return res.status(400).json({
                success: false,
                message: 'A receita deve ter pelo menos um ingrediente'
            });
        }

        // Valida cada ingrediente
        for (let ing of ingredientes) {
            if (!ing.ingrediente_id || !ing.quantidade) {
                return res.status(400).json({
                    success: false,
                    message: 'Cada ingrediente deve ter ingrediente_id e quantidade'
                });
            }

            if (ing.quantidade <= 0) {
                return res.status(400).json({
                    success: false,
                    message: 'A quantidade deve ser maior que zero'
                });
            }
        }

        // ========== INICIA TRANSAÇÃO ==========
        await connection.beginTransaction();

        // Insere a receita
        const [resultadoReceita] = await connection.query(
            `INSERT INTO receitas (nome, categoria, modo_preparo, tempo_preparo, rendimento) 
             VALUES (?, ?, ?, ?, ?)`,
            [nome, categoria, modo_preparo, tempo_preparo, rendimento]
        );

        const receitaId = resultadoReceita.insertId;

        // Insere os ingredientes da receita
        for (let ing of ingredientes) {
            await connection.query(
                `INSERT INTO receita_ingredientes (receita_id, ingrediente_id, quantidade) 
                 VALUES (?, ?, ?)`,
                [receitaId, ing.ingrediente_id, ing.quantidade]
            );
        }

        // ========== CONFIRMA TRANSAÇÃO ==========
        await connection.commit();

        // Busca a receita completa para retornar
        const [receitaCriada] = await pool.query(
            'SELECT * FROM receitas WHERE id = ?',
            [receitaId]
        );

        const [ingredientesCriados] = await pool.query(`
            SELECT 
                ri.id,
                ri.quantidade,
                i.id as ingrediente_id,
                i.nome,
                i.unidade_medida
            FROM receita_ingredientes ri
            INNER JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE ri.receita_id = ?
        `, [receitaId]);

        res.status(201).json({
            success: true,
            message: 'Receita criada com sucesso',
            data: {
                ...receitaCriada[0],
                ingredientes: ingredientesCriados
            }
        });

    } catch (error) {
        // ========== REVERTE TRANSAÇÃO EM CASO DE ERRO ==========
        await connection.rollback();
        
        console.error('Erro ao criar receita:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao criar receita',
            error: error.message
        });
    } finally {
        // Libera a conexão de volta para o pool
        connection.release();
    }
};

// ============================================
// 4. ATUALIZAR RECEITA
// ============================================

exports.atualizar = async (req, res) => {
    const connection = await pool.getConnection();
    
    try {
        const { id } = req.params;
        const { nome, categoria, modo_preparo, tempo_preparo, rendimento, ingredientes } = req.body;

        // Verifica se a receita existe
        const [receitaExistente] = await connection.query(
            'SELECT id FROM receitas WHERE id = ?',
            [id]
        );

        if (receitaExistente.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Receita não encontrada'
            });
        }

        // Validações
        if (!nome || !categoria || !modo_preparo || !tempo_preparo || !rendimento) {
            return res.status(400).json({
                success: false,
                message: 'Todos os campos da receita são obrigatórios'
            });
        }

        if (!ingredientes || !Array.isArray(ingredientes) || ingredientes.length === 0) {
            return res.status(400).json({
                success: false,
                message: 'A receita deve ter pelo menos um ingrediente'
            });
        }

        // Inicia transação
        await connection.beginTransaction();

        // Atualiza dados da receita
        await connection.query(
            `UPDATE receitas 
             SET nome = ?, categoria = ?, modo_preparo = ?, tempo_preparo = ?, rendimento = ?
             WHERE id = ?`,
            [nome, categoria, modo_preparo, tempo_preparo, rendimento, id]
        );

        // Remove ingredientes antigos
        await connection.query(
            'DELETE FROM receita_ingredientes WHERE receita_id = ?',
            [id]
        );

        // Insere novos ingredientes
        for (let ing of ingredientes) {
            await connection.query(
                `INSERT INTO receita_ingredientes (receita_id, ingrediente_id, quantidade) 
                 VALUES (?, ?, ?)`,
                [id, ing.ingrediente_id, ing.quantidade]
            );
        }

        // Confirma transação
        await connection.commit();

        // Busca receita atualizada
        const [receitaAtualizada] = await pool.query(
            'SELECT * FROM receitas WHERE id = ?',
            [id]
        );

        const [ingredientesAtualizados] = await pool.query(`
            SELECT 
                ri.id,
                ri.quantidade,
                i.id as ingrediente_id,
                i.nome,
                i.unidade_medida
            FROM receita_ingredientes ri
            INNER JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE ri.receita_id = ?
        `, [id]);

        res.json({
            success: true,
            message: 'Receita atualizada com sucesso',
            data: {
                ...receitaAtualizada[0],
                ingredientes: ingredientesAtualizados
            }
        });

    } catch (error) {
        await connection.rollback();
        
        console.error('Erro ao atualizar receita:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao atualizar receita',
            error: error.message
        });
    } finally {
        connection.release();
    }
};

// ============================================
// 5. DELETAR RECEITA
// ============================================

exports.deletar = async (req, res) => {
    try {
        const { id } = req.params;

        // Verifica se a receita existe
        const [receita] = await pool.query(
            'SELECT * FROM receitas WHERE id = ?',
            [id]
        );

        if (receita.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Receita não encontrada'
            });
        }

        // Deleta a receita (CASCADE deleta os ingredientes automaticamente)
        await pool.query('DELETE FROM receitas WHERE id = ?', [id]);

        res.json({
            success: true,
            message: 'Receita deletada com sucesso',
            data: receita[0]
        });
    } catch (error) {
        console.error('Erro ao deletar receita:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao deletar receita',
            error: error.message
        });
    }
};

// ============================================
// 6. FILTRAR POR CATEGORIA
// ============================================

exports.filtrarPorCategoria = async (req, res) => {
    try {
        const { categoria } = req.params;

        const [receitas] = await pool.query(`
            SELECT 
                r.*,
                GROUP_CONCAT(
                    CONCAT(
                        i.nome, ' (', 
                        ri.quantidade, 
                        i.unidade_medida, ')'
                    ) SEPARATOR ', '
                ) as ingredientes_resumo
            FROM receitas r
            LEFT JOIN receita_ingredientes ri ON r.id = ri.receita_id
            LEFT JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE r.categoria = ?
            GROUP BY r.id
            ORDER BY r.nome
        `, [categoria]);

        res.json({
            success: true,
            categoria: categoria,
            total: receitas.length,
            data: receitas
        });
    } catch (error) {
        console.error('Erro ao filtrar receitas:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao filtrar receitas',
            error: error.message
        });
    }
};

// ============================================
// 7. BUSCAR POR NOME
// ============================================

exports.buscarPorNome = async (req, res) => {
    try {
        const { nome } = req.query;

        if (!nome) {
            return res.status(400).json({
                success: false,
                message: 'Parâmetro "nome" é obrigatório'
            });
        }

        const [receitas] = await pool.query(`
            SELECT 
                r.*,
                GROUP_CONCAT(
                    CONCAT(
                        i.nome, ' (', 
                        ri.quantidade, 
                        i.unidade_medida, ')'
                    ) SEPARATOR ', '
                ) as ingredientes_resumo
            FROM receitas r
            LEFT JOIN receita_ingredientes ri ON r.id = ri.receita_id
            LEFT JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE r.nome LIKE ?
            GROUP BY r.id
            ORDER BY r.nome
        `, [`%${nome}%`]);

        res.json({
            success: true,
            busca: nome,
            total: receitas.length,
            data: receitas
        });
    } catch (error) {
        console.error('Erro ao buscar receitas:', error);
        res.status(500).json({
            success: false,
            message: 'Erro ao buscar receitas',
            error: error.message
        });
    }
};
```

### Conceitos importantes explicados:

**1. Transações MySQL:**
```javascript
await connection.beginTransaction();
// operações...
await connection.commit();
```
- Garante que todas as operações sejam executadas ou nenhuma
- Se houver erro, `rollback()` desfaz tudo

**2. JOIN com GROUP_CONCAT:**
```sql
GROUP_CONCAT(CONCAT(i.nome, ' (', ri.quantidade, i.unidade_medida, ')') SEPARATOR ', ')
```
- Combina múltiplas linhas em uma string
- Exemplo: "Farinha (300g), Açúcar (200g), Ovos (3 unidade)"

**3. LEFT JOIN vs INNER JOIN:**
- `LEFT JOIN`: Inclui receitas mesmo sem ingredientes
- `INNER JOIN`: Só inclui receitas com ingredientes

**4. LIKE para busca:**
```sql
WHERE r.nome LIKE ?
```
- `%${nome}%` busca em qualquer parte do texto
- Exemplo: buscar "bolo" encontra "Bolo de Chocolate"

---

## 2. Criando as Rotas de Receitas

### Crie o arquivo `routes/receitas.js`:

```javascript
// ============================================
// ROTAS DE RECEITAS
// ============================================

const express = require('express');
const router = express.Router();
const receitasController = require('../controllers/receitasController');

// ============================================
// DEFINIÇÃO DAS ROTAS
// ============================================

// GET /api/receitas - Listar todas as receitas
router.get('/', receitasController.listarTodas);

// GET /api/receitas/buscar?nome=bolo - Buscar por nome
router.get('/buscar', receitasController.buscarPorNome);

// GET /api/receitas/categoria/:categoria - Filtrar por categoria
router.get('/categoria/:categoria', receitasController.filtrarPorCategoria);

// GET /api/receitas/:id - Buscar receita por ID
router.get('/:id', receitasController.buscarPorId);

// POST /api/receitas - Criar nova receita
router.post('/', receitasController.criar);

// PUT /api/receitas/:id - Atualizar receita
router.put('/:id', receitasController.atualizar);

// DELETE /api/receitas/:id - Deletar receita
router.delete('/:id', receitasController.deletar);

// ============================================
// EXPORTAÇÃO
// ============================================

module.exports = router;
```

### ⚠️ IMPORTANTE: Ordem das rotas!

```javascript
router.get('/buscar', ...);          // ANTES
router.get('/categoria/:categoria', ...); // ANTES
router.get('/:id', ...);              // DEPOIS
```

**Por quê?**
- Express testa rotas na ordem que foram definidas
- Se `/:id` vier primeiro, ele captura `/buscar` como se fosse um ID
- Rotas específicas devem vir antes de rotas com parâmetros

---

## 3. Conectando as Rotas ao Servidor

### Abra `server.js` e adicione:

Encontre:
```javascript
// AQUI VIRÃO AS ROTAS DE RECEITAS
```

Substitua por:
```javascript
// Importação das rotas de receitas
const receitasRoutes = require('./routes/receitas');

// Rotas de receitas
app.use('/api/receitas', receitasRoutes);
```

---

## 4. Testando no Postman

### 4.1. Teste 1: Criar Receita

**Método:** POST  
**URL:** `http://localhost:3001/api/receitas`  
**Headers:**
```
Content-Type: application/json
```
**Body (raw JSON):**
```json
{
  "nome": "Bolo de Chocolate",
  "categoria": "Sobremesa",
  "modo_preparo": "1. Pré-aqueça o forno a 180°C\n2. Misture os ingredientes secos (farinha, açúcar, chocolate em pó)\n3. Adicione os líquidos (ovos, leite, óleo)\n4. Misture até ficar homogêneo\n5. Despeje em forma untada\n6. Asse por 40 minutos",
  "tempo_preparo": 60,
  "rendimento": "10 fatias",
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "quantidade": 300
    },
    {
      "ingrediente_id": 2,
      "quantidade": 250
    },
    {
      "ingrediente_id": 3,
      "quantidade": 3
    },
    {
      "ingrediente_id": 4,
      "quantidade": 200
    },
    {
      "ingrediente_id": 8,
      "quantidade": 50
    },
    {
      "ingrediente_id": 9,
      "quantidade": 100
    }
  ]
}
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Receita criada com sucesso",
  "data": {
    "id": 2,
    "nome": "Bolo de Chocolate",
    "categoria": "Sobremesa",
    "modo_preparo": "1. Pré-aqueça o forno...",
    "tempo_preparo": 60,
    "rendimento": "10 fatias",
    "criado_em": "2024-01-01T12:00:00.000Z",
    "atualizado_em": "2024-01-01T12:00:00.000Z",
    "ingredientes": [
      {
        "id": 7,
        "quantidade": "300.00",
        "ingrediente_id": 1,
        "nome": "Farinha de Trigo",
        "unidade_medida": "g"
      },
      // ... mais ingredientes
    ]
  }
}
```

### 4.2. Teste 2: Listar Todas as Receitas

**Método:** GET  
**URL:** `http://localhost:3001/api/receitas`

**Resposta esperada:**
```json
{
  "success": true,
  "total": 2,
  "data": [
    {
      "id": 2,
      "nome": "Bolo de Chocolate",
      "categoria": "Sobremesa",
      "tempo_preparo": 60,
      "rendimento": "10 fatias",
      "ingredientes_resumo": "Farinha de Trigo (300g), Açúcar (250g), Ovos (3 unidade), Leite (200ml), Chocolate em Pó (50g), Óleo (100ml)"
    },
    {
      "id": 1,
      "nome": "Bolo de Chocolate",
      "categoria": "Sobremesa",
      "ingredientes_resumo": "Farinha de Trigo (300g), Açúcar (250g)..."
    }
  ]
}
```

### 4.3. Teste 3: Buscar Receita por ID

**Método:** GET  
**URL:** `http://localhost:3001/api/receitas/2`

**Resposta esperada:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "nome": "Bolo de Chocolate",
    "categoria": "Sobremesa",
    "modo_preparo": "1. Pré-aqueça o forno...",
    "tempo_preparo": 60,
    "rendimento": "10 fatias",
    "criado_em": "2024-01-01T12:00:00.000Z",
    "ingredientes": [
      {
        "id": 7,
        "quantidade": "300.00",
        "ingrediente_id": 1,
        "nome": "Farinha de Trigo",
        "unidade_medida": "g"
      }
      // ... mais ingredientes
    ]
  }
}
```

### 4.4. Teste 4: Filtrar por Categoria

**Método:** GET  
**URL:** `http://localhost:3001/api/receitas/categoria/Sobremesa`

### 4.5. Teste 5: Buscar por Nome

**Método:** GET  
**URL:** `http://localhost:3001/api/receitas/buscar?nome=bolo`

### 4.6. Teste 6: Atualizar Receita

**Método:** PUT  
**URL:** `http://localhost:3001/api/receitas/2`  
**Body:**
```json
{
  "nome": "Bolo de Chocolate Fofinho",
  "categoria": "Sobremesa",
  "modo_preparo": "Modo de preparo atualizado...",
  "tempo_preparo": 65,
  "rendimento": "12 fatias",
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "quantidade": 350
    },
    {
      "ingrediente_id": 2,
      "quantidade": 300
    }
  ]
}
```

### 4.7. Teste 7: Deletar Receita

**Método:** DELETE  
**URL:** `http://localhost:3001/api/receitas/2`

---

## 5. Testando Validações

### Teste 1: Criar sem ingredientes

**Body:**
```json
{
  "nome": "Teste",
  "categoria": "Teste",
  "modo_preparo": "Teste",
  "tempo_preparo": 10,
  "rendimento": "1 porção",
  "ingredientes": []
}
```

**Resposta:**
```json
{
  "success": false,
  "message": "A receita deve ter pelo menos um ingrediente"
}
```

### Teste 2: Ingrediente com quantidade inválida

**Body:**
```json
{
  "nome": "Teste",
  "categoria": "Teste",
  "modo_preparo": "Teste",
  "tempo_preparo": 10,
  "rendimento": "1 porção",
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "quantidade": -5
    }
  ]
}
```

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou o controller de receitas com queries complexas
- ✅ Implementou transações para operações atômicas
- ✅ Usou JOIN para buscar dados relacionados
- ✅ Implementou validações robustas
- ✅ Criou filtros e buscas
- ✅ Testou todas as operações no Postman

---

## Próximo Passo

Backend completo! Agora vamos criar o frontend com React.

**➡️ Próximo:** [Módulo 06 - Frontend: Configuração Inicial](06-frontend-configuracao.md)

---

## Dicas Importantes

💡 **Transações** são essenciais quando você opera em múltiplas tabelas.

💡 **GROUP_CONCAT** é útil para visualizações resumidas.

💡 **Sempre teste rollback** forçando erros propositalmente.

💡 **Ordem das rotas** importa no Express!
