# Tutorial 9: Criando Sistema de Avaliações

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar CRUD para entidades relacionadas
- Trabalhar com chaves estrangeiras
- Validar relacionamentos
- Criar rotas aninhadas (nested routes)
- Garantir integridade referencial

## 📖 Conteúdo

### 1. Controller de Avaliações

**Arquivo `src/controllers/avaliacaoController.js`:**

```javascript
const { Avaliacao, Restaurante } = require('../models');
const { ApiError } = require('../middlewares/errorHandler');
const { Op } = require('sequelize');

/**
 * CREATE - Criar avaliação para um restaurante
 * POST /api/restaurantes/:restauranteId/avaliacoes
 */
exports.create = async (req, res) => {
  const { restauranteId } = req.params;
  const { nota, comentario, autor } = req.body;
  
  // Verificar se restaurante existe
  const restaurante = await Restaurante.findByPk(restauranteId);
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  if (!restaurante.ativo) {
    throw new ApiError(400, 'Não é possível avaliar um restaurante inativo');
  }
  
  // Criar avaliação
  const avaliacao = await Avaliacao.create({
    restaurante_id: restauranteId,
    nota,
    comentario,
    autor
  });
  
  res.status(201).json({
    mensagem: 'Avaliação criada com sucesso',
    avaliacao
  });
};

/**
 * READ ALL - Listar avaliações de um restaurante
 * GET /api/restaurantes/:restauranteId/avaliacoes
 */
exports.findByRestaurante = async (req, res) => {
  const { restauranteId } = req.params;
  
  // Verificar se restaurante existe
  const restaurante = await Restaurante.findByPk(restauranteId);
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  // Paginação
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  
  // Filtro por nota
  const where = { restaurante_id: restauranteId };
  if (req.query.notaMin) {
    where.nota = { [Op.gte]: parseInt(req.query.notaMin) };
  }
  
  const { count, rows } = await Avaliacao.findAndCountAll({
    where,
    limit,
    offset,
    order: [['created_at', 'DESC']],
    include: [{
      model: Restaurante,
      as: 'restaurante',
      attributes: ['id', 'nome']
    }]
  });
  
  res.json({
    restaurante: {
      id: restaurante.id,
      nome: restaurante.nome
    },
    total: count,
    totalPaginas: Math.ceil(count / limit),
    paginaAtual: page,
    avaliacoes: rows
  });
};

/**
 * READ ONE - Buscar avaliação específica
 * GET /api/avaliacoes/:id
 */
exports.findOne = async (req, res) => {
  const { id } = req.params;
  
  const avaliacao = await Avaliacao.findByPk(id, {
    include: [{
      model: Restaurante,
      as: 'restaurante',
      attributes: ['id', 'nome', 'categoria']
    }]
  });
  
  if (!avaliacao) {
    throw new ApiError(404, 'Avaliação não encontrada');
  }
  
  res.json(avaliacao);
};

/**
 * UPDATE - Atualizar avaliação
 * PUT /api/avaliacoes/:id
 */
exports.update = async (req, res) => {
  const { id } = req.params;
  const { nota, comentario } = req.body;
  
  const avaliacao = await Avaliacao.findByPk(id);
  
  if (!avaliacao) {
    throw new ApiError(404, 'Avaliação não encontrada');
  }
  
  await avaliacao.update({ nota, comentario });
  
  res.json({
    mensagem: 'Avaliação atualizada com sucesso',
    avaliacao
  });
};

/**
 * DELETE - Deletar avaliação
 * DELETE /api/avaliacoes/:id
 */
exports.delete = async (req, res) => {
  const { id } = req.params;
  
  const avaliacao = await Avaliacao.findByPk(id);
  
  if (!avaliacao) {
    throw new ApiError(404, 'Avaliação não encontrada');
  }
  
  await avaliacao.destroy();
  
  res.json({
    mensagem: 'Avaliação deletada com sucesso'
  });
};

/**
 * Listar todas as avaliações (admin)
 * GET /api/avaliacoes
 */
exports.findAll = async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;
  const offset = (page - 1) * limit;
  
  const { count, rows } = await Avaliacao.findAndCountAll({
    limit,
    offset,
    order: [['created_at', 'DESC']],
    include: [{
      model: Restaurante,
      as: 'restaurante',
      attributes: ['id', 'nome', 'categoria']
    }]
  });
  
  res.json({
    total: count,
    totalPaginas: Math.ceil(count / limit),
    paginaAtual: page,
    avaliacoes: rows
  });
};
```

### 2. Validações para Avaliações

**Arquivo `src/validators/avaliacaoValidator.js`:**

```javascript
const { body, param, query } = require('express-validator');

exports.createValidation = [
  param('restauranteId')
    .isInt({ min: 1 }).withMessage('ID do restaurante inválido'),
  
  body('nota')
    .isInt({ min: 1, max: 5 }).withMessage('Nota deve ser entre 1 e 5'),
  
  body('comentario')
    .optional()
    .trim()
    .isLength({ max: 500 }).withMessage('Comentário deve ter no máximo 500 caracteres'),
  
  body('autor')
    .trim()
    .notEmpty().withMessage('Nome do autor é obrigatório')
    .isLength({ min: 2, max: 100 }).withMessage('Nome deve ter entre 2 e 100 caracteres')
];

exports.updateValidation = [
  param('id')
    .isInt({ min: 1 }).withMessage('ID inválido'),
  
  body('nota')
    .isInt({ min: 1, max: 5 }).withMessage('Nota deve ser entre 1 e 5'),
  
  body('comentario')
    .optional()
    .trim()
    .isLength({ max: 500 }).withMessage('Comentário muito longo')
];

exports.idValidation = [
  param('id')
    .isInt({ min: 1 }).withMessage('ID inválido')
];

exports.restauranteIdValidation = [
  param('restauranteId')
    .isInt({ min: 1 }).withMessage('ID do restaurante inválido')
];

exports.queryValidation = [
  query('page')
    .optional()
    .isInt({ min: 1 }).withMessage('Página inválida'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 }).withMessage('Limite inválido'),
  
  query('notaMin')
    .optional()
    .isInt({ min: 1, max: 5 }).withMessage('Nota mínima deve ser entre 1 e 5')
];
```

### 3. Rotas de Avaliações

**Arquivo `src/routes/avaliacaoRoutes.js`:**

```javascript
const express = require('express');
const router = express.Router();
const avaliacaoController = require('../controllers/avaliacaoController');
const {
  createValidation,
  updateValidation,
  idValidation,
  restauranteIdValidation,
  queryValidation
} = require('../validators/avaliacaoValidator');
const { validate } = require('../middlewares/validator');
const { asyncHandler } = require('../middlewares/errorHandler');

// Rotas aninhadas - avaliações de um restaurante específico
router.post('/:restauranteId/avaliacoes',
  createValidation,
  validate,
  asyncHandler(avaliacaoController.create)
);

router.get('/:restauranteId/avaliacoes',
  restauranteIdValidation,
  queryValidation,
  validate,
  asyncHandler(avaliacaoController.findByRestaurante)
);

module.exports = router;
```

**Arquivo `src/routes/avaliacaoStandaloneRoutes.js`:**

```javascript
const express = require('express');
const router = express.Router();
const avaliacaoController = require('../controllers/avaliacaoController');
const {
  updateValidation,
  idValidation,
  queryValidation
} = require('../validators/avaliacaoValidator');
const { validate } = require('../middlewares/validator');
const { asyncHandler } = require('../middlewares/errorHandler');

// Rotas standalone para avaliações
router.get('/',
  queryValidation,
  validate,
  asyncHandler(avaliacaoController.findAll)
);

router.get('/:id',
  idValidation,
  validate,
  asyncHandler(avaliacaoController.findOne)
);

router.put('/:id',
  updateValidation,
  validate,
  asyncHandler(avaliacaoController.update)
);

router.delete('/:id',
  idValidation,
  validate,
  asyncHandler(avaliacaoController.delete)
);

module.exports = router;
```

### 4. Registrar Rotas no App

**Atualizar `src/app.js`:**

```javascript
const restauranteRoutes = require('./routes/restauranteRoutes');
const avaliacaoRoutes = require('./routes/avaliacaoRoutes');
const avaliacaoStandaloneRoutes = require('./routes/avaliacaoStandaloneRoutes');

// Rotas
app.use('/api/restaurantes', avaliacaoRoutes); // Rotas aninhadas
app.use('/api/restaurantes', restauranteRoutes);
app.use('/api/avaliacoes', avaliacaoStandaloneRoutes); // Rotas standalone
```

### 5. Testando Avaliações

**Arquivo `test-avaliacoes.http`:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api
@restauranteId = 1

### Criar Avaliação para Restaurante
POST {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Excelente! A melhor pizza que já comi!",
  "autor": "João Silva"
}

### Criar Outra Avaliação
POST {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes
Content-Type: application/json

{
  "nota": 4,
  "comentario": "Muito bom, mas o atendimento pode melhorar.",
  "autor": "Maria Santos"
}

### Criar Avaliação Nota Baixa
POST {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes
Content-Type: application/json

{
  "nota": 2,
  "comentario": "Esperava mais pela fama do lugar.",
  "autor": "Pedro Oliveira"
}

### Listar Avaliações de um Restaurante
GET {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes

### Listar com Filtro de Nota Mínima
GET {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes?notaMin=4

### Listar com Paginação
GET {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes?page=1&limit=5

### Listar Todas as Avaliações (Admin)
GET {{baseUrl}}/avaliacoes

### Buscar Avaliação Específica
GET {{baseUrl}}/avaliacoes/1

### Atualizar Avaliação
PUT {{baseUrl}}/avaliacoes/1
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Comentário atualizado: Simplesmente perfeito!"
}

### Deletar Avaliação
DELETE {{baseUrl}}/avaliacoes/2

### Teste - Criar para Restaurante Inexistente
POST {{baseUrl}}/restaurantes/999/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Teste",
  "autor": "Teste"
}

### Teste - Validação (nota inválida)
POST {{baseUrl}}/restaurantes/{{restauranteId}}/avaliacoes
Content-Type: application/json

{
  "nota": 10,
  "autor": "Teste"
}
```

### 6. Verificando Integridade Referencial

**Teste de integridade:**

```javascript
// Tentar deletar restaurante com avaliações
// Deve falhar se CASCADE não estiver configurado

// No modelo, garantir CASCADE:
Restaurante.hasMany(Avaliacao, {
  foreignKey: 'restaurante_id',
  as: 'avaliacoes',
  onDelete: 'CASCADE'  // ← Importante!
});
```

## 🔨 Atividade Prática

### Exercício 1: Endpoint de Estatísticas de Avaliações

Crie um endpoint que retorna:
- Total de avaliações do restaurante
- Média de notas
- Distribuição de notas (quantas de cada nota)

<details>
<summary>Ver solução</summary>

```javascript
exports.getRestauranteStats = async (req, res) => {
  const { restauranteId } = req.params;
  
  const restaurante = await Restaurante.findByPk(restauranteId);
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  const avaliacoes = await Avaliacao.findAll({
    where: { restaurante_id: restauranteId },
    attributes: ['nota']
  });
  
  const total = avaliacoes.length;
  const media = avaliacoes.reduce((sum, a) => sum + a.nota, 0) / total;
  
  const distribuicao = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
  avaliacoes.forEach(a => distribuicao[a.nota]++);
  
  res.json({
    restaurante: {
      id: restaurante.id,
      nome: restaurante.nome
    },
    totalAvaliacoes: total,
    mediaNotas: media.toFixed(2),
    distribuicaoNotas: distribuicao
  });
};
```

</details>

### Exercício 2: Prevenir Avaliações Duplicadas

Implemente validação para impedir que o mesmo autor avalie o restaurante múltiplas vezes:

<details>
<summary>Ver solução</summary>

```javascript
exports.create = async (req, res) => {
  const { restauranteId } = req.params;
  const { nota, comentario, autor } = req.body;
  
  // Verificar se autor já avaliou
  const avaliacaoExistente = await Avaliacao.findOne({
    where: {
      restaurante_id: restauranteId,
      autor: autor.trim()
    }
  });
  
  if (avaliacaoExistente) {
    throw new ApiError(400, 'Você já avaliou este restaurante. Use PUT para atualizar.');
  }
  
  // Continuar com criação...
};
```

</details>

## 💡 Conceitos-Chave

- **Rotas aninhadas** refletem relacionamentos (`/restaurantes/:id/avaliacoes`)
- Sempre **validar existência** do recurso pai
- **Integridade referencial** com chaves estrangeiras
- **CASCADE** para deletar recursos relacionados
- Validar **regras de negócio** (ex: restaurante ativo)
- Usar **include** para carregar dados relacionados

## ➡️ Próximos Passos

Com o sistema de avaliações funcionando, no próximo tutorial vamos aprender a fazer **consultas relacionais avançadas**, incluindo JOINs e agregações.

[➡️ Ir para Tutorial 10: Consultas com Relacionamentos](10-consultas-relacionais.md)
