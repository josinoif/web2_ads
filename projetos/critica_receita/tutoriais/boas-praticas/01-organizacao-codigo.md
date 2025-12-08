# Tutorial: Organização de Código e Arquitetura

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Aplicar princípios SOLID no código
- Estruturar projetos em camadas
- Separar responsabilidades adequadamente
- Criar código reutilizável e testável
- Documentar código de forma eficaz

## 📖 Conteúdo

### 1. Princípios SOLID

#### Single Responsibility Principle (SRP)

❌ **Ruim:**
```javascript
class RestauranteService {
  async create(data) {
    // Valida dados
    if (!data.nome) throw new Error('Nome obrigatório');
    
    // Salva no banco
    const restaurante = await db.create(data);
    
    // Envia email
    await emailService.send('admin@email.com', 'Novo restaurante');
    
    // Loga evento
    console.log('Restaurante criado:', restaurante.id);
    
    return restaurante;
  }
}
```

✅ **Bom:**
```javascript
class RestauranteService {
  constructor(repository, validator, eventBus) {
    this.repository = repository;
    this.validator = validator;
    this.eventBus = eventBus;
  }

  async create(data) {
    // Apenas orquestra as operações
    this.validator.validate(data);
    const restaurante = await this.repository.create(data);
    this.eventBus.emit('restaurante.created', restaurante);
    return restaurante;
  }
}
```

#### Open/Closed Principle

✅ **Extensível sem modificar:**
```javascript
// Base abstrata
class NotificationStrategy {
  async send(message) {
    throw new Error('Method not implemented');
  }
}

// Implementações específicas
class EmailNotification extends NotificationStrategy {
  async send(message) {
    // Lógica de email
  }
}

class SMSNotification extends NotificationStrategy {
  async send(message) {
    // Lógica de SMS
  }
}

// Uso
class NotificationService {
  constructor(strategy) {
    this.strategy = strategy;
  }

  async notify(message) {
    return this.strategy.send(message);
  }
}
```

### 2. Arquitetura em Camadas

```
┌─────────────────────────────────┐
│     Presentation Layer          │  ← Controllers/Routes
│  (HTTP, WebSocket, GraphQL)     │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│      Application Layer          │  ← Services/Use Cases
│   (Business Logic)              │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│       Domain Layer              │  ← Entities/Models
│    (Core Business)              │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│   Infrastructure Layer          │  ← Repositories/DB
│  (External Services)            │
└─────────────────────────────────┘
```

**Exemplo prático:**

```javascript
// Domain Layer - Entidade
class Restaurante {
  constructor(data) {
    this.id = data.id;
    this.nome = data.nome;
    this.categoria = data.categoria;
  }

  podeReceberAvaliacao() {
    return this.ativo === true;
  }
}

// Infrastructure Layer - Repository
class RestauranteRepository {
  constructor(db) {
    this.db = db;
  }

  async findById(id) {
    const data = await this.db.query('SELECT * FROM restaurantes WHERE id = $1', [id]);
    return new Restaurante(data);
  }

  async save(restaurante) {
    // Lógica de persistência
  }
}

// Application Layer - Service
class AdicionarAvaliacaoService {
  constructor(restauranteRepo, avaliacaoRepo) {
    this.restauranteRepo = restauranteRepo;
    this.avaliacaoRepo = avaliacaoRepo;
  }

  async execute(restauranteId, avaliacaoData) {
    const restaurante = await this.restauranteRepo.findById(restauranteId);
    
    if (!restaurante.podeReceberAvaliacao()) {
      throw new Error('Restaurante não aceita avaliações');
    }

    const avaliacao = await this.avaliacaoRepo.create({
      ...avaliacaoData,
      restauranteId,
    });

    await this.atualizarMedia(restaurante);
    
    return avaliacao;
  }

  async atualizarMedia(restaurante) {
    // Lógica de cálculo
  }
}

// Presentation Layer - Controller
class AvaliacaoController {
  constructor(adicionarAvaliacaoService) {
    this.service = adicionarAvaliacaoService;
  }

  async create(req, res) {
    try {
      const avaliacao = await this.service.execute(
        req.params.id,
        req.body
      );
      res.status(201).json(avaliacao);
    } catch (error) {
      res.status(400).json({ erro: error.message });
    }
  }
}
```

### 3. Padrões de Nomenclatura

#### Variáveis e Funções

```javascript
// ✅ Descritivas e específicas
const restaurantesFiltradosPorCategoria = [];
const calcularMediaAvaliacoes = () => {};

// ❌ Genéricas demais
const data = [];
const process = () => {};
```

#### Classes e Interfaces

```javascript
// ✅ PascalCase para classes
class RestauranteService {}
class AvaliacaoRepository {}

// ✅ Interface com "I" ou sufixo descritivo
interface IRestauranteRepository {}
interface RestauranteRepositoryInterface {}
```

#### Constantes

```javascript
// ✅ UPPER_SNAKE_CASE
const MAX_UPLOAD_SIZE = 2 * 1024 * 1024;
const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png'];
```

### 4. Separação de Responsabilidades

#### Validação

```javascript
// validators/restaurante.validator.js
class RestauranteValidator {
  validate(data) {
    const erros = [];

    if (!data.nome || data.nome.length < 3) {
      erros.push('Nome deve ter pelo menos 3 caracteres');
    }

    if (!data.categoria) {
      erros.push('Categoria é obrigatória');
    }

    if (erros.length > 0) {
      throw new ValidationError(erros);
    }
  }
}
```

#### Transformação de Dados

```javascript
// mappers/restaurante.mapper.js
class RestauranteMapper {
  toDTO(entity) {
    return {
      id: entity.id,
      nome: entity.nome,
      categoria: entity.categoria,
      avaliacaoMedia: parseFloat(entity.avaliacao_media).toFixed(2),
      criadoEm: entity.created_at.toISOString(),
    };
  }

  toEntity(dto) {
    return {
      nome: dto.nome,
      categoria: dto.categoria,
      endereco: dto.endereco,
    };
  }
}
```

### 5. Configuração e Constantes

```javascript
// config/categories.js
module.exports = {
  CATEGORIAS: [
    'Italiana',
    'Japonesa',
    'Brasileira',
    'Mexicana',
    'Árabe',
    'Hamburgueria',
    'Pizzaria',
    'Vegetariana',
    'Outra',
  ],
  
  CATEGORIA_PADRAO: 'Outra',
};

// config/pagination.js
module.exports = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100,
};
```

### 6. Documentação com JSDoc

```javascript
/**
 * Calcula a média das avaliações de um restaurante
 * @param {number} restauranteId - ID do restaurante
 * @returns {Promise<number>} Média calculada entre 0 e 5
 * @throws {NotFoundError} Se restaurante não existir
 * @example
 * const media = await calcularMedia(1);
 * console.log(media); // 4.5
 */
async function calcularMediaAvaliacoes(restauranteId) {
  const avaliacoes = await Avaliacao.findAll({
    where: { restaurante_id: restauranteId }
  });

  if (avaliacoes.length === 0) return 0;

  const soma = avaliacoes.reduce((acc, av) => acc + av.nota, 0);
  return soma / avaliacoes.length;
}
```

## 🔨 Atividade Prática

### Exercício 1: Refatorar Controller

Refatore este controller aplicando SRP:

```javascript
// Antes
exports.create = async (req, res) => {
  if (!req.body.nome) {
    return res.status(400).json({ erro: 'Nome obrigatório' });
  }
  
  const restaurante = await Restaurante.create(req.body);
  
  console.log('Restaurante criado:', restaurante.id);
  
  res.status(201).json(restaurante);
};
```

### Exercício 2: Criar Camada de Serviço

Extraia a lógica de negócio para um service:

```javascript
// Sugestão de estrutura
class RestauranteService {
  async criarRestaurante(dados) {
    // 1. Validar
    // 2. Criar
    // 3. Emitir evento
    // 4. Retornar
  }
}
```

### Exercício 3: Implementar Mapper

Crie um mapper que:
- Converte snake_case do banco para camelCase da API
- Formata datas para ISO 8601
- Oculta campos sensíveis

## 💡 Conceitos-Chave

- **SOLID**: Princípios de design orientado a objetos
- **Separation of Concerns**: Cada módulo tem uma responsabilidade
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **Clean Code**: Código legível e mantível

## ➡️ Próximos Passos

- Segurança e Validação Avançada
- Testes Automatizados
- Observabilidade e Logging

## 📚 Recursos

- [Clean Code - Robert Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
