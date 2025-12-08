# Tutorial: Testes Automatizados

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Escrever testes unitários, integração e E2E
- Usar Jest e Supertest
- Mockar dependências externas
- Medir cobertura de testes
- Implementar TDD básico

## 📖 Conteúdo

### 1. Configurando Jest

```bash
npm install --save-dev jest supertest
npm install --save-dev @types/jest @types/supertest
```

**Arquivo `jest.config.js`:**

```javascript
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/server.js',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  testMatch: [
    '**/__tests__/**/*.js',
    '**/*.test.js',
  ],
};
```

**Scripts no `package.json`:**

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration"
  }
}
```

### 2. Testes Unitários

**Testando Service:**

```javascript
// src/services/__tests__/restaurante.service.test.js
const RestauranteService = require('../restaurante.service');
const { Restaurante } = require('../../models');

jest.mock('../../models');

describe('RestauranteService', () => {
  let service;

  beforeEach(() => {
    service = new RestauranteService();
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('deve criar restaurante com dados válidos', async () => {
      const dadosMock = {
        nome: 'Pizza Bella',
        categoria: 'Italiana',
        endereco: 'Rua X, 123',
      };

      const restauranteMock = { id: 1, ...dadosMock };
      Restaurante.create.mockResolvedValue(restauranteMock);

      const resultado = await service.create(dadosMock);

      expect(Restaurante.create).toHaveBeenCalledWith(dadosMock);
      expect(resultado).toEqual(restauranteMock);
    });

    it('deve lançar erro se nome for inválido', async () => {
      const dadosInvalidos = {
        nome: 'Ab', // Muito curto
        categoria: 'Italiana',
      };

      await expect(service.create(dadosInvalidos))
        .rejects
        .toThrow('Nome deve ter pelo menos 3 caracteres');
    });
  });

  describe('calcularMedia', () => {
    it('deve calcular média corretamente', async () => {
      const avaliacoesMock = [
        { nota: 5 },
        { nota: 4 },
        { nota: 3 },
      ];

      Avaliacao.findAll.mockResolvedValue(avaliacoesMock);

      const media = await service.calcularMedia(1);

      expect(media).toBe(4);
    });

    it('deve retornar 0 se não houver avaliações', async () => {
      Avaliacao.findAll.mockResolvedValue([]);

      const media = await service.calcularMedia(1);

      expect(media).toBe(0);
    });
  });
});
```

### 3. Testes de Integração

**Testando API completa:**

```javascript
// src/__tests__/integration/restaurante.test.js
const request = require('supertest');
const app = require('../../app');
const { sequelize } = require('../../config/database');
const { Restaurante } = require('../../models');

describe('Restaurante API', () => {
  beforeAll(async () => {
    await sequelize.sync({ force: true });
  });

  afterAll(async () => {
    await sequelize.close();
  });

  afterEach(async () => {
    await Restaurante.destroy({ where: {} });
  });

  describe('POST /api/restaurantes', () => {
    it('deve criar restaurante com dados válidos', async () => {
      const novoRestaurante = {
        nome: 'Pizza Bella',
        categoria: 'Italiana',
        endereco: 'Rua X, 123',
        telefone: '(11) 1234-5678',
      };

      const response = await request(app)
        .post('/api/restaurantes')
        .send(novoRestaurante)
        .expect(201);

      expect(response.body).toHaveProperty('restaurante');
      expect(response.body.restaurante.nome).toBe(novoRestaurante.nome);
      expect(response.body.mensagem).toBe('Restaurante criado com sucesso');
    });

    it('deve retornar 400 com dados inválidos', async () => {
      const dadosInvalidos = {
        nome: 'Ab', // Muito curto
      };

      const response = await request(app)
        .post('/api/restaurantes')
        .send(dadosInvalidos)
        .expect(400);

      expect(response.body).toHaveProperty('erros');
    });
  });

  describe('GET /api/restaurantes', () => {
    beforeEach(async () => {
      await Restaurante.bulkCreate([
        { nome: 'Pizza Bella', categoria: 'Italiana' },
        { nome: 'Sushi House', categoria: 'Japonesa' },
        { nome: 'Churrascaria Gaúcha', categoria: 'Brasileira' },
      ]);
    });

    it('deve listar todos os restaurantes', async () => {
      const response = await request(app)
        .get('/api/restaurantes')
        .expect(200);

      expect(response.body.restaurantes).toHaveLength(3);
      expect(response.body.total).toBe(3);
    });

    it('deve filtrar por categoria', async () => {
      const response = await request(app)
        .get('/api/restaurantes?categoria=Italiana')
        .expect(200);

      expect(response.body.restaurantes).toHaveLength(1);
      expect(response.body.restaurantes[0].categoria).toBe('Italiana');
    });

    it('deve paginar resultados', async () => {
      const response = await request(app)
        .get('/api/restaurantes?page=1&limit=2')
        .expect(200);

      expect(response.body.restaurantes).toHaveLength(2);
      expect(response.body.paginaAtual).toBe(1);
      expect(response.body.totalPaginas).toBe(2);
    });
  });

  describe('PUT /api/restaurantes/:id', () => {
    let restaurante;

    beforeEach(async () => {
      restaurante = await Restaurante.create({
        nome: 'Pizza Bella',
        categoria: 'Italiana',
      });
    });

    it('deve atualizar restaurante existente', async () => {
      const atualizacao = {
        nome: 'Pizza Bella Napolitana',
        endereco: 'Rua Nova, 456',
      };

      const response = await request(app)
        .put(`/api/restaurantes/${restaurante.id}`)
        .send(atualizacao)
        .expect(200);

      expect(response.body.restaurante.nome).toBe(atualizacao.nome);
      expect(response.body.restaurante.endereco).toBe(atualizacao.endereco);
    });

    it('deve retornar 404 para ID inexistente', async () => {
      await request(app)
        .put('/api/restaurantes/99999')
        .send({ nome: 'Teste' })
        .expect(404);
    });
  });
});
```

### 4. Testes de Upload

```javascript
// src/__tests__/integration/upload.test.js
const request = require('supertest');
const path = require('path');
const fs = require('fs').promises;
const app = require('../../app');
const { uploadDir } = require('../../config/upload');

describe('Upload de Imagens', () => {
  let restaurante;
  const imagemTeste = path.join(__dirname, '../fixtures/test-image.jpg');

  beforeEach(async () => {
    restaurante = await Restaurante.create({
      nome: 'Teste',
      categoria: 'Italiana',
    });
  });

  afterEach(async () => {
    // Limpar uploads de teste
    try {
      const files = await fs.readdir(uploadDir);
      await Promise.all(
        files.map(file => fs.unlink(path.join(uploadDir, file)))
      );
    } catch (error) {
      // Ignore
    }
  });

  it('deve fazer upload de imagem válida', async () => {
    const response = await request(app)
      .post(`/api/restaurantes/${restaurante.id}/image`)
      .attach('image', imagemTeste)
      .expect(200);

    expect(response.body).toHaveProperty('imageUrl');
    expect(response.body.imageUrl).toMatch(/\/uploads\/.+\.jpg$/);

    // Verificar se arquivo foi criado
    const filename = path.basename(response.body.imageUrl);
    const filePath = path.join(uploadDir, filename);
    await expect(fs.access(filePath)).resolves.not.toThrow();
  });

  it('deve rejeitar arquivo muito grande', async () => {
    // Criar arquivo grande temporário (> 2MB)
    const arquivoGrande = path.join(__dirname, '../fixtures/large.jpg');
    await fs.writeFile(arquivoGrande, Buffer.alloc(3 * 1024 * 1024));

    await request(app)
      .post(`/api/restaurantes/${restaurante.id}/image`)
      .attach('image', arquivoGrande)
      .expect(400);

    await fs.unlink(arquivoGrande);
  });

  it('deve rejeitar tipo de arquivo inválido', async () => {
    const arquivoTexto = path.join(__dirname, '../fixtures/test.txt');
    await fs.writeFile(arquivoTexto, 'Conteúdo de teste');

    const response = await request(app)
      .post(`/api/restaurantes/${restaurante.id}/image`)
      .attach('image', arquivoTexto)
      .expect(400);

    expect(response.body.erro).toMatch(/não permitido/i);

    await fs.unlink(arquivoTexto);
  });
});
```

### 5. Testes com Banco de Dados em Memória

**Configuração para testes:**

```javascript
// src/config/database.test.js
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('sqlite::memory:', {
  logging: false,
});

module.exports = sequelize;
```

**Usar no Jest:**

```javascript
// jest.config.js
module.exports = {
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.js'],
};

// src/__tests__/setup.js
const { sequelize } = require('../config/database.test');

beforeAll(async () => {
  await sequelize.sync({ force: true });
});

afterAll(async () => {
  await sequelize.close();
});
```

### 6. Mockar Dependências Externas

```javascript
// Mockar serviço de email
jest.mock('../../services/email.service', () => ({
  enviarEmail: jest.fn().mockResolvedValue(true),
}));

// Mockar API externa
const axios = require('axios');
jest.mock('axios');

describe('IntegracaoExterna', () => {
  it('deve buscar dados de API externa', async () => {
    const dadosMock = { id: 1, nome: 'Teste' };
    axios.get.mockResolvedValue({ data: dadosMock });

    const resultado = await service.buscarDadosExternos();

    expect(axios.get).toHaveBeenCalledWith('https://api.example.com/data');
    expect(resultado).toEqual(dadosMock);
  });
});
```

### 7. Testes E2E (End-to-End)

```javascript
// Fluxo completo: criar restaurante -> adicionar avaliação -> calcular média
describe('Fluxo completo de avaliação', () => {
  it('deve criar restaurante, adicionar avaliações e calcular média', async () => {
    // 1. Criar restaurante
    const criarRes = await request(app)
      .post('/api/restaurantes')
      .send({
        nome: 'Pizza Bella',
        categoria: 'Italiana',
      })
      .expect(201);

    const restauranteId = criarRes.body.restaurante.id;

    // 2. Adicionar avaliações
    await request(app)
      .post(`/api/restaurantes/${restauranteId}/avaliacoes`)
      .send({ nota: 5, comentario: 'Excelente!' })
      .expect(201);

    await request(app)
      .post(`/api/restaurantes/${restauranteId}/avaliacoes`)
      .send({ nota: 4, comentario: 'Muito bom' })
      .expect(201);

    // 3. Verificar média
    const detalheRes = await request(app)
      .get(`/api/restaurantes/${restauranteId}`)
      .expect(200);

    expect(detalheRes.body.restaurante.avaliacao_media).toBe('4.50');
    expect(detalheRes.body.restaurante.total_avaliacoes).toBe(2);
  });
});
```

## 🔨 Atividade Prática

### Exercício 1: Testes Unitários de Validação

Escreva testes para:
- Validação de email
- Validação de telefone
- Validação de categoria
- Cálculo de média

### Exercício 2: Testes de Integração

Implemente testes para:
- CRUD completo de restaurantes
- CRUD de avaliações
- Upload e remoção de imagens
- Filtros e paginação

### Exercício 3: Medir Cobertura

Execute:
```bash
npm run test:coverage
```

Meta: atingir 80% de cobertura.

## 💡 Conceitos-Chave

- **AAA Pattern**: Arrange, Act, Assert
- **Mocking**: Substituir dependências reais por simulações
- **Test Doubles**: Mocks, Stubs, Spies, Fakes
- **Coverage**: Porcentagem de código testado
- **TDD**: Test-Driven Development

## ➡️ Próximos Passos

- CI/CD com testes automatizados
- Performance testing
- Testes de carga

## 📚 Recursos

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Supertest](https://github.com/visionmedia/supertest)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
