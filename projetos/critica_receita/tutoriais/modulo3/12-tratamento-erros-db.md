# Tutorial 12: Tratamento de Erros de Banco de Dados

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Identificar e tratar erros específicos do Sequelize
- Implementar tratamento de erros de constraint
- Lidar com timeouts e perda de conexão
- Criar mensagens de erro amigáveis
- Implementar retry logic para operações críticas

## 📖 Conteúdo

### 1. Tipos de Erros do Sequelize

**Principais erros:**
- `SequelizeValidationError` - Erro de validação de modelo
- `SequelizeUniqueConstraintError` - Violação de unicidade
- `SequelizeForeignKeyConstraintError` - Violação de FK
- `SequelizeDatabaseError` - Erro genérico do banco
- `SequelizeConnectionError` - Erro de conexão
- `SequelizeTimeoutError` - Timeout de query

### 2. Handler de Erros do Sequelize

**Atualizar `src/middlewares/errorHandler.js`:**

```javascript

//... codigo existente ... 
const sequelizeErrorHandler = (err, req, res, next) => {
  console.error('❌ Erro do Sequelize:', err.name);
  
  // Erro de validação
  if (err.name === 'SequelizeValidationError') {
    const errors = err.errors.map(e => ({
      campo: e.path,
      mensagem: e.message,
      tipo: e.type,
      valorInvalido: e.value
    }));
    
    return res.status(400).json({
      error: 'Erro de validação',
      detalhes: errors
    });
  }
  
  // Violação de unicidade
  if (err.name === 'SequelizeUniqueConstraintError') {
    const camposDuplicados = err.errors.map(e => e.path);
    
    return res.status(409).json({
      error: 'Registro duplicado',
      mensagem: `Já existe um registro com ${camposDuplicados.join(', ')}`,
      campos: camposDuplicados
    });
  }
  
  // Violação de chave estrangeira
  if (err.name === 'SequelizeForeignKeyConstraintError') {
    let mensagem = 'Violação de integridade referencial';
    
    // Detectar tipo de violação
    if (err.parent.code === '23503') { // PostgreSQL FK violation
      if (err.original.message.includes('insert') || err.original.message.includes('update')) {
        mensagem = 'O registro relacionado não existe';
      } else if (err.original.message.includes('delete')) {
        mensagem = 'Não é possível deletar pois existem registros relacionados';
      }
    }
    
    return res.status(400).json({
      error: 'Erro de integridade referencial',
      mensagem,
      detalhes: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
  }
  
  // Erro de conexão
  if (err.name === 'SequelizeConnectionError' || 
      err.name === 'SequelizeConnectionRefusedError') {
    console.error('❌ Erro de conexão com banco de dados');
    
    return res.status(503).json({
      error: 'Serviço temporariamente indisponível',
      mensagem: 'Não foi possível conectar ao banco de dados. Tente novamente em instantes.'
    });
  }
  
  // Timeout
  if (err.name === 'SequelizeTimeoutError') {
    return res.status(408).json({
      error: 'Timeout',
      mensagem: 'A operação demorou muito tempo. Tente novamente.'
    });
  }
  
  // Erro de sintaxe SQL
  if (err.name === 'SequelizeDatabaseError') {
    console.error('SQL Error:', err.parent?.message);
    
    return res.status(500).json({
      error: 'Erro no banco de dados',
      mensagem: process.env.NODE_ENV === 'development' 
        ? err.message 
        : 'Erro ao processar a operação'
    });
  }
  
  // Erro não tratado do Sequelize
  if (err.name && err.name.startsWith('Sequelize')) {
    return res.status(500).json({
      error: 'Erro no banco de dados',
      tipo: err.name,
      mensagem: process.env.NODE_ENV === 'development' 
        ? err.message 
        : 'Erro interno do servidor'
    });
  }
  
  // Passar para o próximo handler se não for erro do Sequelize
  next(err);
};

module.exports = { ApiError, errorHandler, asyncHandler, sequelizeErrorHandler };
```

**Registrar no app.js:**

```javascript
const { errorHandler, sequelizeErrorHandler } = require('./middlewares/errorHandler');

// ... outras configurações ...

// Error handlers (ordem importa!)
app.use(errorLogger);
app.use(sequelizeErrorHandler); // Antes do errorHandler geral
app.use(errorHandler);
```

### 3. Retry Logic para Operações Críticas

**Criar utilitário de retry:**

```javascript
// src/utils/retry.js
async function retry(fn, options = {}) {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 2,
    shouldRetry = () => true
  } = options;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      console.log(`❌ Tentativa ${attempt}/${maxAttempts} falhou:`, error.message);
      
      // Não fazer retry se não deve tentar novamente
      if (!shouldRetry(error)) {
        throw error;
      }
      
      // Última tentativa - lançar erro
      if (attempt === maxAttempts) {
        console.error(`❌ Todas as ${maxAttempts} tentativas falharam`);
        throw error;
      }
      
      // Aguardar antes de tentar novamente
      const waitTime = delay * Math.pow(backoff, attempt - 1);
      console.log(`⏳ Aguardando ${waitTime}ms antes de tentar novamente...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
}

// Função helper específica para operações de BD
async function retryDatabaseOperation(fn) {
  return retry(fn, {
    maxAttempts: 3,
    delay: 500,
    backoff: 2,
    shouldRetry: (error) => {
      // Retry apenas para erros temporários
      return error.name === 'SequelizeConnectionError' ||
             error.name === 'SequelizeTimeoutError' ||
             error.name === 'SequelizeConnectionRefusedError';
    }
  });
}

module.exports = { retry, retryDatabaseOperation };
```

**Usar nos controllers:**

```javascript
const { retryDatabaseOperation } = require('../utils/retry');

exports.create = async (req, res) => {
  const { nome, categoria, endereco, telefone, descricao } = req.body;
  
  const restaurante = await retryDatabaseOperation(async () => {
    return await Restaurante.create({
      nome,
      categoria,
      endereco,
      telefone,
      descricao
    });
  });
  
  res.status(201).json({
    mensagem: 'Restaurante criado com sucesso',
    restaurante
  });
};
```

### 4. Validação de Dados Antes de Salvar

**Criar middleware de validação de negócio:**

```javascript
// src/middlewares/businessValidation.js
const { Restaurante } = require('../models');
const { ApiError } = require('./errorHandler');

exports.validateRestauranteUnique = async (req, res, next) => {
  const { nome, endereco } = req.body;
  const { id } = req.params;
  
  // Verificar se já existe restaurante com mesmo nome e endereço
  const where = {
    nome,
    endereco,
    ativo: true
  };
  
  // Se for update, excluir o próprio registro da busca
  if (id) {
    where.id = { [Op.ne]: id };
  }
  
  const existente = await Restaurante.findOne({ where });
  
  if (existente) {
    throw new ApiError(409, 
      'Já existe um restaurante com este nome neste endereço',
      { restauranteExistente: existente.id }
    );
  }
  
  next();
};

exports.validateAvaliacaoUnica = async (req, res, next) => {
  const { restauranteId } = req.params;
  const { autor } = req.body;
  
  const existente = await Avaliacao.findOne({
    where: {
      restaurante_id: restauranteId,
      autor: autor.trim()
    }
  });
  
  if (existente) {
    throw new ApiError(409,
      'Você já avaliou este restaurante',
      { avaliacaoExistente: existente.id }
    );
  }
  
  next();
};
```

### 5. Health Check do Banco

**Endpoint para monitoramento:**

```javascript
// No app.js ou em controller separado
app.get('/api/health/database', async (req, res) => {
  try {
    // Testar conexão
    await sequelize.authenticate();
    
    // Fazer query simples
    await sequelize.query('SELECT 1+1 AS result');
    
    // Verificar pool de conexões
    const pool = sequelize.connectionManager.pool;
    
    res.json({
      status: 'healthy',
      database: 'connected',
      timestamp: new Date().toISOString(),
      poolInfo: {
        size: pool.size,
        available: pool.available,
        using: pool.using,
        waiting: pool.waiting
      }
    });
  } catch (error) {
    console.error('Health check falhou:', error);
    
    res.status(503).json({
      status: 'unhealthy',
      database: 'disconnected',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});
```

### 6. Logging de Erros de BD

**Logger específico para banco:**

```javascript
// src/utils/dbLogger.js
const fs = require('fs');
const path = require('path');

const dbErrorLogStream = fs.createWriteStream(
  path.join(__dirname, '../../logs/db-errors.log'),
  { flags: 'a' }
);

function logDatabaseError(error, context = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    errorName: error.name,
    errorMessage: error.message,
    sql: error.sql,
    parameters: error.parameters,
    context,
    stack: error.stack
  };
  
  dbErrorLogStream.write(JSON.stringify(logEntry) + '\n');
  
  // Em desenvolvimento, também logar no console
  if (process.env.NODE_ENV === 'development') {
    console.error('🗄️ Erro de BD:', logEntry);
  }
}

module.exports = { logDatabaseError };
```

### 7. Transaction com Tratamento de Erro

**Usar transactions para operações críticas:**

```javascript
exports.createComAvaliacao = async (req, res) => {
  const { restaurante, avaliacao } = req.body;
  
  // Iniciar transaction
  const t = await sequelize.transaction();
  
  try {
    // Criar restaurante
    const novoRestaurante = await Restaurante.create(restaurante, { transaction: t });
    
    // Criar avaliação
    const novaAvaliacao = await Avaliacao.create({
      ...avaliacao,
      restaurante_id: novoRestaurante.id
    }, { transaction: t });
    
    // Commit se tudo deu certo
    await t.commit();
    
    res.status(201).json({
      mensagem: 'Restaurante e avaliação criados com sucesso',
      restaurante: novoRestaurante,
      avaliacao: novaAvaliacao
    });
  } catch (error) {
    // Rollback em caso de erro
    await t.rollback();
    console.error('❌ Erro na transaction, rollback executado');
    throw error;
  }
};
```

### 8. Testando Erros

**Arquivo `test-errors.http`:**

```http
### Teste - Validação de campo obrigatório
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "categoria": "Italiana"
}

### Teste - Nota inválida
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 10,
  "autor": "Teste"
}

### Teste - Restaurante duplicado
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "endereco": "Rua das Flores, 123"
}

### Teste - FK inválida
POST {{baseUrl}}/restaurantes/9999/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Teste",
  "autor": "João"
}

### Teste - Deletar com relacionamentos
DELETE {{baseUrl}}/restaurantes/1/permanente

### Health check do banco
GET {{baseUrl}}/health/database
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Circuit Breaker

Crie um circuit breaker para proteger contra falhas contínuas do BD:

<details>
<summary>Ver solução</summary>

```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failureCount = 0;
    this.threshold = threshold;
    this.timeout = timeout;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }
  
  async execute(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }
  
  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
      console.warn(`⚠️  Circuit breaker OPEN. Próxima tentativa em ${this.timeout}ms`);
    }
  }
}

const dbCircuitBreaker = new CircuitBreaker();
module.exports = dbCircuitBreaker;
```

</details>

## 💡 Conceitos-Chave

- Cada tipo de erro do Sequelize requer **tratamento específico**
- **Retry logic** para erros temporários
- **Transactions** garantem atomicidade
- **Health checks** monitoram saúde do BD
- **Circuit breaker** previne sobrecarga
- Mensagens de erro devem ser **amigáveis** em produção
- **Log** detalhado em desenvolvimento

## ➡️ Próximos Passos

Com o backend robusto e completo, no próximo módulo vamos começar a construir o **frontend com React**, consumindo nossa API.

[➡️ Ir para Tutorial 13: Setup do Projeto React](../modulo4/13-setup-react.md)
