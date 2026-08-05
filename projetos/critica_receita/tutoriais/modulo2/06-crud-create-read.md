# Tutorial 6: CRUD - Create e Read

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar controllers para operações CRUD
- Implementar rotas POST e GET
- Validar dados de entrada com express-validator
- Implementar paginação e filtros
- Tratar erros de forma adequada
- Testar endpoints com ferramentas REST

## 📖 Conteúdo

### 1. Criando o Controller de Restaurantes

**Arquivo `src/controllers/restauranteController.js`:**

```javascript
const { Restaurante, Avaliacao } = require('../models');
const { ApiError } = require('../middlewares/errorHandler');
const { Op } = require('sequelize');

/**
 * CREATE - Criar novo restaurante
 * POST /api/restaurantes
 */
exports.create = async (req, res) => {
  const { nome, categoria, endereco, telefone, descricao } = req.body;
  
  const restaurante = await Restaurante.create({
    nome,
    categoria,
    endereco,
    telefone,
    descricao
  });
  
  res.status(201).json({
    mensagem: 'Restaurante criado com sucesso',
    restaurante
  });
};

/**
 * READ ALL - Listar todos os restaurantes
 * GET /api/restaurantes
 * Query params: page, limit, categoria, busca
 */
exports.findAll = async (req, res) => {
  // Paginação
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  
  // Filtros
  const where = { ativo: true };
  
  // Filtro por categoria
  if (req.query.categoria) {
    where.categoria = req.query.categoria;
  }
  
  // Busca por nome
  if (req.query.busca) {
    where.nome = {
      [Op.iLike]: `%${req.query.busca}%` // iLike = case-insensitive
    };
  }
  
  // Ordenação
  const order = [];
  if (req.query.ordenar) {
    const campo = req.query.ordenar;
    const direcao = req.query.direcao || 'ASC';
    order.push([campo, direcao]);
  } else {
    order.push(['avaliacao_media', 'DESC']);
  }
  
  const { count, rows } = await Restaurante.findAndCountAll({
    where,
    limit,
    offset,
    order,
    attributes: { 
      exclude: ['ativo'] // Não retornar campo ativo
    }
  });
  
  res.json({
    total: count,
    totalPaginas: Math.ceil(count / limit),
    paginaAtual: page,
    limite: limit,
    restaurantes: rows
  });
};

/**
 * READ ONE - Buscar restaurante por ID
 * GET /api/restaurantes/:id
 */
exports.findOne = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id, {
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      attributes: ['id', 'nota', 'comentario', 'autor', 'created_at'],
      order: [['created_at', 'DESC']],
      limit: 10  // Últimas 10 avaliações
    }]
  });
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  res.json(restaurante);
};

/**
 * Buscar por categoria
 * GET /api/restaurantes/categoria/:categoria
 */
exports.findByCategoria = async (req, res) => {
  const { categoria } = req.params;
  
  const restaurantes = await Restaurante.findAll({
    where: { 
      categoria,
      ativo: true 
    },
    order: [['avaliacao_media', 'DESC']]
  });
  
  res.json({
    categoria,
    total: restaurantes.length,
    restaurantes
  });
};

/**
 * Estatísticas gerais
 * GET /api/restaurantes/stats
 */
exports.getStats = async (req, res) => {
  const total = await Restaurante.count({ where: { ativo: true } });
  
  const porCategoria = await Restaurante.findAll({
    where: { ativo: true },
    attributes: [
      'categoria',
      [sequelize.fn('COUNT', sequelize.col('id')), 'total']
    ],
    group: ['categoria'],
    raw: true
  });
  
  res.json({
    totalRestaurantes: total,
    porCategoria
  });
};
```

### 2. Validações com Express-Validator

**Arquivo `src/validators/restauranteValidator.js`:**

```javascript
const { body, param, query } = require('express-validator');

exports.createValidation = [
  body('nome')
    .trim()
    .notEmpty().withMessage('Nome é obrigatório')
    .isLength({ min: 3, max: 100 }).withMessage('Nome deve ter entre 3 e 100 caracteres'),
  
  body('categoria')
    .trim()
    .notEmpty().withMessage('Categoria é obrigatória')
    .isIn(['Italiana', 'Japonesa', 'Brasileira', 'Mexicana', 'Árabe', 'Hamburgueria', 'Pizzaria', 'Vegetariana', 'Outra'])
    .withMessage('Categoria inválida'),
  
  body('endereco')
    .optional()
    .trim()
    .isLength({ max: 500 }).withMessage('Endereço muito longo'),
  
  body('telefone')
    .optional()
    .trim()
    .matches(/^[\d\s\(\)\-\+]+$/).withMessage('Telefone inválido'),
  
  body('descricao')
    .optional()
    .trim()
    .isLength({ max: 1000 }).withMessage('Descrição muito longa')
];

exports.idValidation = [
  param('id')
    .isInt({ min: 1 }).withMessage('ID inválido')
];

exports.queryValidation = [
  query('page')
    .optional()
    .isInt({ min: 1 }).withMessage('Página deve ser um número positivo'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 }).withMessage('Limite deve estar entre 1 e 100'),
  
  query('categoria')
    .optional()
    .trim()
    .isIn(['Italiana', 'Japonesa', 'Brasileira', 'Mexicana', 'Árabe', 'Hamburgueria', 'Pizzaria', 'Vegetariana', 'Outra'])
    .withMessage('Categoria inválida'),
  
  query('ordenar')
    .optional()
    .isIn(['nome', 'categoria', 'avaliacao_media', 'created_at'])
    .withMessage('Campo de ordenação inválido'),
  
  query('direcao')
    .optional()
    .isIn(['ASC', 'DESC'])
    .withMessage('Direção deve ser ASC ou DESC')
];
```

### 3. Criando as Rotas

**Arquivo `src/routes/restauranteRoutes.js`:**

```javascript
const express = require('express');
const router = express.Router();
const restauranteController = require('../controllers/restauranteController');
const { 
  createValidation, 
  idValidation, 
  queryValidation 
} = require('../validators/restauranteValidator');
const { validate } = require('../middlewares/validator');
const { asyncHandler } = require('../middlewares/errorHandler');

// CREATE
router.post('/',
  createValidation,
  validate,
  asyncHandler(restauranteController.create)
);

// READ ALL
router.get('/',
  queryValidation,
  validate,
  asyncHandler(restauranteController.findAll)
);

// Estatísticas
router.get('/stats',
  asyncHandler(restauranteController.getStats)
);

// READ por categoria
router.get('/categoria/:categoria',
  asyncHandler(restauranteController.findByCategoria)
);

// READ ONE
router.get('/:id',
  idValidation,
  validate,
  asyncHandler(restauranteController.findOne)
);

module.exports = router;
```

### 4. Registrando as Rotas no App

**Atualizar `src/app.js`:**

```javascript
// ... imports anteriores ...
const restauranteRoutes = require('./routes/restauranteRoutes');

// ... middlewares anteriores ...

// Rotas da API
app.use('/api/restaurantes', restauranteRoutes);

// ... resto do código ...
```

### 5. Testando com cURL

**Criar restaurante (POST):**

```bash
curl -X POST http://localhost:3000/api/restaurantes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Pizza Bella",
    "categoria": "Italiana",
    "endereco": "Rua das Flores, 123",
    "telefone": "(11) 98765-4321",
    "descricao": "Melhor pizza da cidade!"
  }'
```

**Listar todos (GET):**

```bash
curl http://localhost:3000/api/restaurantes
```

**Com paginação e filtros:**

```bash
curl "http://localhost:3000/api/restaurantes?page=1&limit=5&categoria=Italiana&ordenar=nome&direcao=ASC"
```

**Buscar por nome:**

```bash
curl "http://localhost:3000/api/restaurantes?busca=pizza"
```

**Buscar por ID:**

```bash
curl http://localhost:3000/api/restaurantes/1
```

### 6. Testando com Arquivo REST do VS Code

**Criar arquivo `test.http`:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api
@contentType = application/json

### Health Check
GET {{baseUrl}}/../health

### Criar Restaurante
POST {{baseUrl}}/restaurantes
Content-Type: {{contentType}}

{
  "nome": "Sushi Master",
  "categoria": "Japonesa",
  "endereco": "Av. Paulista, 1000",
  "telefone": "(11) 3456-7890",
  "descricao": "Sushi autêntico japonês"
}

### Criar Outro Restaurante
POST {{baseUrl}}/restaurantes
Content-Type: {{contentType}}

{
  "nome": "Burger House",
  "categoria": "Hamburgueria",
  "endereco": "Rua Central, 500"
}

### Listar Todos
GET {{baseUrl}}/restaurantes

### Listar com Paginação
GET {{baseUrl}}/restaurantes?page=1&limit=5

### Buscar por Nome
GET {{baseUrl}}/restaurantes?busca=sushi

### Filtrar por Categoria
GET {{baseUrl}}/restaurantes?categoria=Japonesa

### Buscar por ID
GET {{baseUrl}}/restaurantes/1

### Buscar por Categoria (rota específica)
GET {{baseUrl}}/restaurantes/categoria/Italiana

### Estatísticas
GET {{baseUrl}}/restaurantes/stats

### Teste de Validação (deve falhar)
POST {{baseUrl}}/restaurantes
Content-Type: {{contentType}}

{
  "nome": "AB",
  "categoria": "Inexistente"
}
```

### 7. Operadores do Sequelize

```javascript
const { Op } = require('sequelize');

// Operadores de comparação
where: {
  id: { [Op.eq]: 5 },              // = 5
  idade: { [Op.gt]: 18 },          // > 18
  idade: { [Op.gte]: 18 },         // >= 18
  idade: { [Op.lt]: 65 },          // < 65
  idade: { [Op.lte]: 65 },         // <= 65
  idade: { [Op.ne]: 18 },          // != 18
  idade: { [Op.between]: [18, 65] }, // BETWEEN 18 AND 65
}

// Operadores de string
where: {
  nome: { [Op.like]: '%pizza%' },     // LIKE (case-sensitive)
  nome: { [Op.iLike]: '%pizza%' },    // ILIKE (case-insensitive, PostgreSQL)
  nome: { [Op.startsWith]: 'Pizza' }, // LIKE 'Pizza%'
  nome: { [Op.endsWith]: 'House' },   // LIKE '%House'
}

// Operadores lógicos
where: {
  [Op.and]: [
    { ativo: true },
    { categoria: 'Italiana' }
  ],
  [Op.or]: [
    { categoria: 'Italiana' },
    { categoria: 'Pizzaria' }
  ]
}

// Operador IN
where: {
  categoria: { [Op.in]: ['Italiana', 'Japonesa', 'Brasileira'] }
}
```

## 🔨 Atividade Prática

### Exercício 1: Adicionar Endpoint de Busca Avançada

Crie um endpoint que permite buscar restaurantes por:
- Faixa de avaliação média (ex: entre 4 e 5)
- Data de criação (restaurantes novos)

<details>
<summary>Ver solução</summary>

```javascript
// No controller
exports.advancedSearch = async (req, res) => {
  const where = { ativo: true };
  
  // Filtro por avaliação
  if (req.query.avaliacaoMin || req.query.avaliacaoMax) {
    where.avaliacao_media = {};
    if (req.query.avaliacaoMin) {
      where.avaliacao_media[Op.gte] = parseFloat(req.query.avaliacaoMin);
    }
    if (req.query.avaliacaoMax) {
      where.avaliacao_media[Op.lte] = parseFloat(req.query.avaliacaoMax);
    }
  }
  
  // Filtro por data
  if (req.query.diasRecentes) {
    const dias = parseInt(req.query.diasRecentes);
    const dataLimite = new Date();
    dataLimite.setDate(dataLimite.getDate() - dias);
    
    where.created_at = {
      [Op.gte]: dataLimite
    };
  }
  
  const restaurantes = await Restaurante.findAll({ where });
  
  res.json({ 
    total: restaurantes.length,
    restaurantes 
  });
};

// Na rota
router.get('/busca-avancada',
  asyncHandler(restauranteController.advancedSearch)
);
```

</details>

### Exercício 2: Adicionar Campo de Contagem

Modifique o `findAll` para incluir a contagem de avaliações de cada restaurante:

<details>
<summary>Ver solução</summary>

```javascript
const restaurantes = await Restaurante.findAndCountAll({
  where,
  limit,
  offset,
  order,
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    attributes: []  // Não retornar as avaliações, apenas contar
  }],
  attributes: {
    include: [
      [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes']
    ]
  },
  group: ['restaurante.id'],
  subQuery: false
});
```

</details>

## 💡 Conceitos-Chave

- **Controllers** contêm a lógica de negócio
- **Routes** mapeiam URLs para controllers
- **Validators** validam dados antes de processar
- **Paginação** melhora performance em listas grandes
- **Filtros e busca** permitem consultas específicas
- **asyncHandler** elimina try-catch repetitivo
- **Status 201** indica criação bem-sucedida
- **Status 404** indica recurso não encontrado

## ➡️ Próximos Passos

Com CREATE e READ implementados, no próximo tutorial vamos completar o CRUD implementando as operações **UPDATE e DELETE**.

[➡️ Ir para Tutorial 7: CRUD - Update e Delete](07-crud-update-delete.md)

---

**Dica:** Use o Postman ou Insomnia para testar as rotas de forma mais interativa!
