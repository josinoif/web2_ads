# Tutorial 10: Consultas com Relacionamentos

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Realizar consultas com JOINs usando Sequelize
- Usar include para carregar dados relacionados
- Entender eager vs lazy loading
- Fazer consultas com agregações
- Otimizar queries com relacionamentos

## 📖 Conteúdo

### 1. Include Básico (Eager Loading)

**Buscar restaurante com suas avaliações:**

```javascript
const restaurante = await Restaurante.findByPk(1, {
  include: [{
    model: Avaliacao,
    as: 'avaliacoes'
  }]
});
```

**SQL equivalente:**
```sql
SELECT * FROM restaurantes
LEFT JOIN avaliacoes ON restaurantes.id = avaliacoes.restaurante_id
WHERE restaurantes.id = 1;
```

### 2. Include com Filtros

**Apenas avaliações com nota alta:**

```javascript
const restaurante = await Restaurante.findByPk(1, {
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    where: { nota: { [Op.gte]: 4 } },
    required: false  // LEFT JOIN (inclui mesmo sem avaliações)
  }]
});
```

**Com `required: true` vira INNER JOIN:**

```javascript
// Apenas restaurantes que TÊM avaliações com nota >= 4
const restaurantes = await Restaurante.findAll({
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    where: { nota: { [Op.gte]: 4 } },
    required: true  // INNER JOIN
  }]
});
```

### 3. Include com Atributos Selecionados

**Selecionar apenas campos específicos:**

```javascript
const restaurante = await Restaurante.findByPk(1, {
  attributes: ['id', 'nome', 'categoria'], // Campos do restaurante
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    attributes: ['id', 'nota', 'comentario', 'created_at'] // Campos da avaliação
  }]
});
```

### 4. Include com Ordenação e Limite

**Últimas 5 avaliações:**

```javascript
const restaurante = await Restaurante.findByPk(1, {
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    order: [['created_at', 'DESC']],
    limit: 5,
    separate: true  // Executa query separada para conseguir limitar
  }]
});
```

### 5. Agregações com Relacionamentos

**Contar avaliações por restaurante:**

```javascript
const restaurantes = await Restaurante.findAll({
  attributes: [
    'id',
    'nome',
    [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes']
  ],
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    attributes: []  // Não retornar dados, apenas contar
  }],
  group: ['restaurante.id'],
  subQuery: false
});
```

**Calcular média de notas:**

```javascript
const restaurantes = await Restaurante.findAll({
  attributes: [
    'id',
    'nome',
    [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes'],
    [sequelize.fn('AVG', sequelize.col('avaliacoes.nota')), 'media_avaliacoes']
  ],
  include: [{
    model: Avaliacao,
    as: 'avaliacoes',
    attributes: []
  }],
  group: ['restaurante.id'],
  having: sequelize.where(
    sequelize.fn('COUNT', sequelize.col('avaliacoes.id')),
    { [Op.gt]: 0 }
  )
});
```

### 6. Controller com Consultas Avançadas

**Adicionar ao `restauranteController.js`:**

```javascript
// ... imports antigos 
const { sequelize } = require('../config/database');


// ... rotas já implementadas ... 

/**
 * Restaurantes mais bem avaliados
 * GET /api/restaurantes/top-rated
 */
exports.getTopRated = async (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  
  const restaurantes = await Restaurante.findAll({
    where: { ativo: true },
    attributes: [
      'id',
      'nome',
      'categoria',
      [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes'],
      [sequelize.fn('AVG', sequelize.col('avaliacoes.nota')), 'media_notas']
    ],
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      attributes: []
    }],
    group: ['restaurante.id'],
    having: sequelize.where(
      sequelize.fn('COUNT', sequelize.col('avaliacoes.id')),
      { [Op.gte]: 3 }  // Mínimo 3 avaliações
    ),
    order: [[sequelize.literal('media_notas'), 'DESC']],
    limit,
    subQuery: false
  });
  
  res.json({
    mensagem: `Top ${limit} restaurantes mais bem avaliados`,
    restaurantes
  });
};

/**
 * Restaurantes com mais avaliações
 * GET /api/restaurantes/mais-avaliados
 */
exports.getMostReviewed = async (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  
  const restaurantes = await Restaurante.findAll({
    where: { ativo: true },
    attributes: [
      'id',
      'nome',
      'categoria',
      [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes']
    ],
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      attributes: []
    }],
    group: ['restaurante.id'],
    order: [[sequelize.literal('total_avaliacoes'), 'DESC']],
    limit,
    subQuery: false
  });
  
  res.json({
    mensagem: `Top ${limit} restaurantes mais avaliados`,
    restaurantes
  });
};

/**
 * Restaurantes por categoria com estatísticas
 * GET /api/restaurantes/por-categoria
 */
exports.getByCategoria = async (req, res) => {
  const categorias = await Restaurante.findAll({
    where: { ativo: true },
    attributes: [
      'categoria',
      [sequelize.fn('COUNT', sequelize.col('restaurante.id')), 'total_restaurantes'],
      [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes'],
      [sequelize.fn('AVG', sequelize.col('avaliacoes.nota')), 'media_categoria']
    ],
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      attributes: []
    }],
    group: ['categoria'],
    order: [[sequelize.literal('total_restaurantes'), 'DESC']]
  });
  
  res.json({
    mensagem: 'Estatísticas por categoria',
    categorias
  });
};

/**
 * Buscar restaurantes com detalhes completos
 * GET /api/restaurantes/:id/completo
 */
exports.findOneComplete = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id, {
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      order: [['created_at', 'DESC']],
      limit: 10,
      separate: true
    }]
  });
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  // Calcular estatísticas manualmente
  const avaliacoes = await Avaliacao.findAll({
    where: { restaurante_id: id },
    attributes: ['nota']
  });
  
  const distribuicao = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  avaliacoes.forEach(a => distribuicao[a.nota]++);
  
  const stats = {
    total: avaliacoes.length,
    media: avaliacoes.length > 0 
      ? (avaliacoes.reduce((sum, a) => sum + a.nota, 0) / avaliacoes.length).toFixed(2)
      : 0,
    distribuicao
  };
  
  res.json({
    ...restaurante.toJSON(),
    estatisticas: stats
  });
};
```

### 7. Eager vs Lazy Loading

**Eager Loading (Carrega tudo de uma vez):**

```javascript
// Uma única query com JOIN
const restaurante = await Restaurante.findByPk(1, {
  include: [{ model: Avaliacao, as: 'avaliacoes' }]
});

console.log(restaurante.avaliacoes); // ✅ Já carregado
```

**Lazy Loading (Carrega sob demanda):**

```javascript
// Primeira query: apenas restaurante
const restaurante = await Restaurante.findByPk(1);

// Segunda query: busca avaliações quando necessário
const avaliacoes = await restaurante.getAvaliacoes();

console.log(avaliacoes); // ✅ Carregado agora
```

### 8. Otimizando Queries

**❌ Problema N+1:**

```javascript
// 1 query para restaurantes
const restaurantes = await Restaurante.findAll();

// N queries para avaliações (uma para cada restaurante)
for (const restaurante of restaurantes) {
  const avaliacoes = await restaurante.getAvaliacoes(); // ❌ Ruim!
}
```

**✅ Solução com Eager Loading:**

```javascript
// 1 query com JOIN
const restaurantes = await Restaurante.findAll({
  include: [{ model: Avaliacao, as: 'avaliacoes' }]
});

// Acesso direto
restaurantes.forEach(r => {
  console.log(r.avaliacoes); // ✅ Bom!
});
```

### 9. Rotas para Consultas Avançadas

**Adicionar em `restauranteRoutes.js`:**

```javascript
// Endpoints de estatísticas (antes das rotas com :id)
router.get('/top-rated',
  asyncHandler(restauranteController.getTopRated)
);

router.get('/mais-avaliados',
  asyncHandler(restauranteController.getMostReviewed)
);

router.get('/por-categoria',
  asyncHandler(restauranteController.getByCategoria)
);

// Detalhes completos
router.get('/:id/completo',
  idValidation,
  validate,
  asyncHandler(restauranteController.findOneComplete)
);
```

### 10. Testando Consultas Relacionais

**Arquivo `test-queries.http`:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api

### Top 10 Mais Bem Avaliados
GET {{baseUrl}}/restaurantes/top-rated?limit=10

### Top 5 Mais Avaliados
GET {{baseUrl}}/restaurantes/mais-avaliados?limit=5

### Estatísticas por Categoria
GET {{baseUrl}}/restaurantes/por-categoria

### Detalhes Completos de Restaurante
GET {{baseUrl}}/restaurantes/1/completo

### Buscar Restaurantes com Avaliações Alta
GET {{baseUrl}}/restaurantes?avaliacaoMin=4
```

## 🔨 Atividade Prática

### Exercício 1: Endpoint de Busca Avançada

Crie um endpoint que busca restaurantes por múltiplos critérios:
- Categoria
- Faixa de avaliação
- Mínimo de avaliações
- Ordenação customizável

<details>
<summary>Ver solução</summary>

```javascript
exports.advancedSearch = async (req, res) => {
  const {
    categoria,
    avaliacaoMin,
    avaliacaoMax,
    minimoAvaliacoes,
    ordenar = 'media_notas',
    direcao = 'DESC'
  } = req.query;
  
  const where = { ativo: true };
  if (categoria) where.categoria = categoria;
  
  let having = null;
  const havingConditions = [];
  
  if (avaliacaoMin) {
    havingConditions.push(
      sequelize.where(
        sequelize.fn('AVG', sequelize.col('avaliacoes.nota')),
        { [Op.gte]: parseFloat(avaliacaoMin) }
      )
    );
  }
  
  if (avaliacaoMax) {
    havingConditions.push(
      sequelize.where(
        sequelize.fn('AVG', sequelize.col('avaliacoes.nota')),
        { [Op.lte]: parseFloat(avaliacaoMax) }
      )
    );
  }
  
  if (minimoAvaliacoes) {
    havingConditions.push(
      sequelize.where(
        sequelize.fn('COUNT', sequelize.col('avaliacoes.id')),
        { [Op.gte]: parseInt(minimoAvaliacoes) }
      )
    );
  }
  
  if (havingConditions.length > 0) {
    having = { [Op.and]: havingConditions };
  }
  
  const restaurantes = await Restaurante.findAll({
    where,
    attributes: [
      'id', 'nome', 'categoria',
      [sequelize.fn('COUNT', sequelize.col('avaliacoes.id')), 'total_avaliacoes'],
      [sequelize.fn('AVG', sequelize.col('avaliacoes.nota')), 'media_notas']
    ],
    include: [{
      model: Avaliacao,
      as: 'avaliacoes',
      attributes: []
    }],
    group: ['restaurante.id'],
    having,
    order: [[sequelize.literal(ordenar), direcao]],
    subQuery: false
  });
  
  res.json({
    total: restaurantes.length,
    restaurantes
  });
};
```

</details>

## 💡 Conceitos-Chave

- **Include** carrega dados relacionados (eager loading)
- **required: true** = INNER JOIN
- **required: false** = LEFT JOIN
- **separate: true** executa query separada
- **Agregações** (COUNT, AVG, SUM) com GROUP BY
- **HAVING** filtra resultados após agregação
- Evitar **problema N+1** com eager loading
- **subQuery: false** para queries complexas

## ➡️ Próximos Passos

Com consultas relacionais dominadas, no próximo tutorial vamos implementar o **cálculo automático de médias** e atualização em cascata.

[➡️ Ir para Tutorial 11: Cálculo de Médias e Agregações](11-calculo-media.md)
