# Tutorial 11: Cálculo de Médias e Agregações

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar cálculo automático de médias
- Usar hooks do Sequelize para atualização em cascata
- Criar campos calculados
- Otimizar queries com índices
- Implementar desnormalização controlada

## 📖 Conteúdo

### 1. Hooks do Sequelize

**Hooks** são funções executadas automaticamente em momentos específicos do ciclo de vida dos modelos.

**Momentos disponíveis:**
- `beforeCreate`, `afterCreate`
- `beforeUpdate`, `afterUpdate`
- `beforeDestroy`, `afterDestroy`
- `beforeBulkCreate`, `afterBulkCreate`
- `beforeValidate`, `afterValidate`

### 2. Implementando Atualização Automática de Média

**Atualizar `src/models/Avaliacao.js`:**

```javascript
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Avaliacao = sequelize.define('avaliacao', {
  // ... campos existentes ...
}, {
  tableName: 'avaliacoes',
  timestamps: true,
  underscored: true,
  hooks: {
    // Após criar avaliação, atualizar média do restaurante
    afterCreate: async (avaliacao, options) => {
      await atualizarMediaRestaurante(avaliacao.restaurante_id);
    },
    
    // Após atualizar nota, recalcular média
    afterUpdate: async (avaliacao, options) => {
      if (avaliacao.changed('nota')) {
        await atualizarMediaRestaurante(avaliacao.restaurante_id);
      }
    },
    
    // Após deletar, recalcular média
    afterDestroy: async (avaliacao, options) => {
      await atualizarMediaRestaurante(avaliacao.restaurante_id);
    }
  }
});

// Função auxiliar para atualizar média
async function atualizarMediaRestaurante(restauranteId) {
  const Restaurante = require('./Restaurante');
  
  // Buscar todas as avaliações do restaurante
  const avaliacoes = await Avaliacao.findAll({
    where: { restaurante_id: restauranteId },
    attributes: ['nota']
  });
  
  // Calcular média
  let media = 0;
  if (avaliacoes.length > 0) {
    const soma = avaliacoes.reduce((acc, av) => acc + av.nota, 0);
    media = soma / avaliacoes.length;
  }
  
  // Atualizar restaurante
  await Restaurante.update(
    { avaliacao_media: media.toFixed(2) },
    { where: { id: restauranteId } }
  );
  
  console.log(`✅ Média do restaurante ${restauranteId} atualizada: ${media.toFixed(2)}`);
}

module.exports = Avaliacao;
```

### 3. Alternativa: Recalcular sob Demanda

**Método mais seguro para ambientes com alta concorrência:**

```javascript
// Adicionar ao Restaurante model
const Restaurante = sequelize.define('restaurante', {
  // ... campos existentes ...
}, {
  // ... configurações existentes ...
});

// Método de instância para recalcular média
Restaurante.prototype.recalcularMedia = async function() {
  const Avaliacao = require('./Avaliacao');
  
  const result = await Avaliacao.findOne({
    where: { restaurante_id: this.id },
    attributes: [
      [sequelize.fn('AVG', sequelize.col('nota')), 'media'],
      [sequelize.fn('COUNT', sequelize.col('id')), 'total']
    ],
    raw: true
  });
  
  const media = result.media ? parseFloat(result.media).toFixed(2) : 0;
  
  await this.update({ avaliacao_media: media });
  
  return media;
};

// Método estático para recalcular múltiplos
Restaurante.recalcularMedias = async function(restauranteIds) {
  for (const id of restauranteIds) {
    const restaurante = await Restaurante.findByPk(id);
    if (restaurante) {
      await restaurante.recalcularMedia();
    }
  }
};
```

**Usar nos controllers:**

```javascript
// Após criar avaliação
exports.create = async (req, res) => {
  // ... código de criação ...
  
  const avaliacao = await Avaliacao.create({...});
  
  // Recalcular média
  const restaurante = await Restaurante.findByPk(restauranteId);
  await restaurante.recalcularMedia();
  
  res.status(201).json({
    mensagem: 'Avaliação criada com sucesso',
    avaliacao
  });
};
```

### 4. Endpoint para Recalcular Médias

**Útil para manutenção e correção de dados:**

```javascript
// No restauranteController.js
exports.recalcularMedia = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  const mediaAtualizada = await restaurante.recalcularMedia();
  
  res.json({
    mensagem: 'Média recalculada com sucesso',
    restaurante: {
      id: restaurante.id,
      nome: restaurante.nome,
      avaliacaoMedia: mediaAtualizada
    }
  });
};

// Recalcular todas as médias (admin)
exports.recalcularTodasMedias = async (req, res) => {
  const restaurantes = await Restaurante.findAll({
    where: { ativo: true }
  });
  
  let contador = 0;
  for (const restaurante of restaurantes) {
    await restaurante.recalcularMedia();
    contador++;
  }
  
  res.json({
    mensagem: `${contador} médias recalculadas com sucesso`
  });
};
```

**Adicionar rotas:**

```javascript
// Em restauranteRoutes.js
router.post('/:id/recalcular-media',
  idValidation,
  validate,
  asyncHandler(restauranteController.recalcularMedia)
);

router.post('/recalcular-todas-medias',
  asyncHandler(restauranteController.recalcularTodasMedias)
);
```

### 5. Índices para Performance

**Adicionar índices ao modelo:**

```javascript
// No modelo Avaliacao
const Avaliacao = sequelize.define('avaliacao', {
  // ... campos ...
}, {
  // ... configurações ...
  indexes: [
    {
      fields: ['restaurante_id'] // Índice para FK
    },
    {
      fields: ['nota'] // Índice para filtros por nota
    },
    {
      fields: ['created_at'] // Índice para ordenação por data
    },
    {
      fields: ['restaurante_id', 'nota'] // Índice composto
    }
  ]
});

// No modelo Restaurante
const Restaurante = sequelize.define('restaurante', {
  // ... campos ...
}, {
  // ... configurações ...
  indexes: [
    {
      fields: ['categoria'] // Busca por categoria
    },
    {
      fields: ['avaliacao_media'] // Ordenação por média
    },
    {
      fields: ['nome'] // Busca por nome
    },
    {
      fields: ['ativo'] // Filtro de ativos
    }
  ]
});
```

### 6. Query Otimizada com Cache

**Implementar cache simples em memória:**

```javascript
// src/utils/cache.js
class SimpleCache {
  constructor(ttl = 60000) { // TTL padrão 1 minuto
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
  
  get(key) {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    // Verificar se expirou
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  delete(key) {
    this.cache.delete(key);
  }
  
  clear() {
    this.cache.clear();
  }
}

module.exports = new SimpleCache();
```

**Usar no controller:**

```javascript
const cache = require('../utils/cache');

exports.findAll = async (req, res) => {
  const cacheKey = `restaurantes:${JSON.stringify(req.query)}`;
  
  // Verificar cache
  const cached = cache.get(cacheKey);
  if (cached) {
    console.log('✅ Retornando do cache');
    return res.json(cached);
  }
  
  // Buscar do banco
  const { count, rows } = await Restaurante.findAndCountAll({...});
  
  result = {
    total: count,
    totalPaginas: Math.ceil(count / limit),
    paginaAtual: page,
    limite: limit,
    restaurantes: rows
  }
  
  // Armazenar no cache por 5 minutos
  cache.set(cacheKey, result, 300);
  console.log('✅ Armazenado no cache');
  
  res.json(result);
};
```

### 7. Estatísticas Agregadas

**Controller com estatísticas complexas:**

```javascript
exports.getDashboardStats = async (req, res) => {
  // Total de restaurantes
  const totalRestaurantes = await Restaurante.count({
    where: { ativo: true }
  });
  
  // Total de avaliações
  const totalAvaliacoes = await Avaliacao.count();
  
  // Média geral de todas as avaliações
  const mediaGeral = await Avaliacao.findOne({
    attributes: [
      [sequelize.fn('AVG', sequelize.col('nota')), 'media']
    ],
    raw: true
  });
  
  // Distribuição de notas
  const distribuicaoNotas = await Avaliacao.findAll({
    attributes: [
      'nota',
      [sequelize.fn('COUNT', sequelize.col('id')), 'quantidade']
    ],
    group: ['nota'],
    order: [['nota', 'ASC']],
    raw: true
  });
  
  // Top 5 categorias
  const topCategorias = await Restaurante.findAll({
    where: { ativo: true },
    attributes: [
      'categoria',
      [sequelize.fn('COUNT', sequelize.col('restaurante.id')), 'quantidade'],
      [sequelize.fn('AVG', sequelize.col('avaliacao_media')), 'media']
    ],
    group: ['categoria'],
    order: [[sequelize.literal('quantidade'), 'DESC']],
    limit: 5,
    raw: true
  });
  
  // Avaliações por mês (últimos 6 meses)
  const seisMesesAtras = new Date();
  seisMesesAtras.setMonth(seisMesesAtras.getMonth() - 6);
  
  const avaliacoesPorMes = await Avaliacao.findAll({
    where: {
      created_at: { [Op.gte]: seisMesesAtras }
    },
    attributes: [
      [sequelize.fn('DATE_TRUNC', 'month', sequelize.col('created_at')), 'mes'],
      [sequelize.fn('COUNT', sequelize.col('id')), 'quantidade']
    ],
    group: [sequelize.fn('DATE_TRUNC', 'month', sequelize.col('created_at'))],
    order: [[sequelize.fn('DATE_TRUNC', 'month', sequelize.col('created_at')), 'ASC']],
    raw: true
  });
  
  res.json({
    resumo: {
      totalRestaurantes,
      totalAvaliacoes,
      mediaGeral: parseFloat(mediaGeral.media || 0).toFixed(2)
    },
    distribuicaoNotas,
    topCategorias,
    avaliacoesPorMes
  });
};
```

### 8. Testando Atualização de Médias

```http

@baseUrl = http://localhost:3000/api

### Criar primeira avaliação
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Excelente!",
  "autor": "João"
}

### Verificar média atualizada
GET {{baseUrl}}/restaurantes/1

### Criar segunda avaliação
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 3,
  "comentario": "Regular",
  "autor": "Maria"
}

### Verificar nova média (deve ser 4.0)
GET {{baseUrl}}/restaurantes/1

### Recalcular média manualmente
POST {{baseUrl}}/restaurantes/1/recalcular-media

### Dashboard de estatísticas
GET {{baseUrl}}/restaurantes/stats
```

## 🔨 Atividade Prática

### Exercício 1: Adicionar Contagem de Avaliações

Além da média, mantenha um contador de avaliações no modelo Restaurante:

<details>
<parameter name="summary">Ver solução</summary>

```javascript
// Adicionar campo ao modelo
total_avaliacoes: {
  type: DataTypes.INTEGER,
  defaultValue: 0
}

// Atualizar hook
async function atualizarEstatisticas(restauranteId) {
  const avaliacoes = await Avaliacao.findAll({
    where: { restaurante_id: restauranteId },
    attributes: ['nota']
  });
  
  const total = avaliacoes.length;
  const media = total > 0
    ? avaliacoes.reduce((sum, a) => sum + a.nota, 0) / total
    : 0;
  
  await Restaurante.update(
    {
      avaliacao_media: media.toFixed(2),
      total_avaliacoes: total
    },
    { where: { id: restauranteId } }
  );
}
```

</details>

### Exercício 2: Ranking de Restaurantes

Crie um endpoint que retorna restaurantes com ranking baseado em:
- 70% média de avaliações
- 30% total de avaliações

## 💡 Conceitos-Chave

- **Hooks** automatizam ações em eventos do modelo
- **Desnormalização** melhora performance (média cached)
- **Índices** aceleram queries comuns
- **Cache** reduz carga do banco
- Sempre validar **integridade** após hooks
- **Recalcular sob demanda** é mais seguro que hooks
- Usar **agregações SQL** ao invés de loop JavaScript

## ➡️ Próximos Passos

Com médias calculadas automaticamente, no próximo tutorial vamos implementar **tratamento robusto de erros de banco de dados**.

[➡️ Ir para Tutorial 12: Tratamento de Erros de BD](12-tratamento-erros-db.md)
