# Tutorial 4: Modelagem de Dados e ORM

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Compreender o conceito de ORM (Object-Relational Mapping)
- Configurar o Sequelize
- Criar modelos de dados
- Definir relacionamentos entre modelos
- Sincronizar modelos com o banco de dados
- Entender validações e constraints

## 📖 Conteúdo

### 1. O que é ORM?

**ORM (Object-Relational Mapping)** é uma técnica que permite interagir com o banco de dados usando objetos JavaScript ao invés de SQL puro.

**Sem ORM (SQL puro):**
```javascript
const query = `
  INSERT INTO restaurantes (nome, categoria, endereco) 
  VALUES ($1, $2, $3) 
  RETURNING *
`;
const result = await client.query(query, ['Pizza Bella', 'Italiana', 'Rua X']);
```

**Com ORM (Sequelize):**
```javascript
const restaurante = await Restaurante.create({
  nome: 'Pizza Bella',
  categoria: 'Italiana',
  endereco: 'Rua X'
});
```

**Vantagens do ORM:**
- ✅ Código mais limpo e legível
- ✅ Proteção contra SQL Injection
- ✅ Abstração do banco de dados
- ✅ Validações integradas
- ✅ Gerenciamento de relacionamentos
- ✅ Migrations automáticas

### 2. Configurando o Sequelize

**Arquivo `src/config/database.js`:**

```javascript
const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(
  process.env.DB_NAME,
  process.env.DB_USER,
  process.env.DB_PASSWORD,
  {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging: process.env.NODE_ENV === 'development' ? console.log : false,
    pool: {
      max: 5,           // Máximo de conexões simultâneas
      min: 0,           // Mínimo de conexões
      acquire: 30000,   // Tempo máximo para obter conexão (ms)
      idle: 10000       // Tempo máximo de conexão ociosa (ms)
    },
    define: {
      timestamps: true,        // Adiciona createdAt e updatedAt
      underscored: true,      // Usa snake_case para colunas
      freezeTableName: true   // Não pluraliza nomes de tabelas
    }
  }
);

// Testar conexão
async function testConnection() {
  try {
    await sequelize.authenticate();
    console.log('✅ Conexão com banco de dados estabelecida com sucesso!');
  } catch (error) {
    console.error('❌ Erro ao conectar ao banco de dados:', error);
    process.exit(1);
  }
}

testConnection();

module.exports = sequelize;
```

### 3. Criando o Modelo Restaurante

**Arquivo `src/models/Restaurante.js`:**

```javascript
const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Restaurante = sequelize.define('restaurante', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  nome: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: {
        msg: 'Nome não pode ser vazio'
      },
      len: {
        args: [3, 100],
        msg: 'Nome deve ter entre 3 e 100 caracteres'
      }
    }
  },
  categoria: {
    type: DataTypes.STRING(50),
    allowNull: false,
    validate: {
      notEmpty: {
        msg: 'Categoria não pode ser vazia'
      },
      isIn: {
        args: [['Italiana', 'Japonesa', 'Brasileira', 'Mexicana', 'Árabe', 'Hamburgueria', 'Pizzaria', 'Vegetariana', 'Outra']],
        msg: 'Categoria inválida'
      }
    }
  },
  endereco: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  telefone: {
    type: DataTypes.STRING(20),
    allowNull: true,
    validate: {
      is: {
        args: /^[\d\s\(\)\-\+]+$/i,
        msg: 'Telefone inválido'
      }
    }
  },
  descricao: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  ativo: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  avaliacao_media: {
    type: DataTypes.DECIMAL(3, 2),
    defaultValue: 0,
    validate: {
      min: 0,
      max: 5
    }
  },
  image_url: {
    type: DataTypes.STRING(500),
    allowNull: true,
    validate: {
      isUrl: {
        msg: 'URL da imagem inválida'
      }
    }
  }
}, {
  tableName: 'restaurantes',
  timestamps: true,
  underscored: true
});

module.exports = Restaurante;
```

### 4. Criando o Modelo Avaliacao

**Arquivo `src/models/Avaliacao.js`:**

```javascript
const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Avaliacao = sequelize.define('avaliacao', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  nota: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: {
        args: 1,
        msg: 'Nota mínima é 1'
      },
      max: {
        args: 5,
        msg: 'Nota máxima é 5'
      },
      isInt: {
        msg: 'Nota deve ser um número inteiro'
      }
    }
  },
  comentario: {
    type: DataTypes.TEXT,
    allowNull: true,
    validate: {
      len: {
        args: [0, 500],
        msg: 'Comentário deve ter no máximo 500 caracteres'
      }
    }
  },
  autor: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: {
        msg: 'Nome do autor não pode ser vazio'
      }
    }
  },
  restaurante_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'restaurantes',
      key: 'id'
    }
  }
}, {
  tableName: 'avaliacoes',
  timestamps: true,
  underscored: true
});

module.exports = Avaliacao;
```

### 5. Definindo Relacionamentos

**Arquivo `src/models/index.js`:**

```javascript
const Restaurante = require('./Restaurante');
const Avaliacao = require('./Avaliacao');

// Relacionamento 1:N
// Um restaurante tem muitas avaliações
Restaurante.hasMany(Avaliacao, {
  foreignKey: 'restaurante_id',
  as: 'avaliacoes',
  onDelete: 'CASCADE'  // Se restaurante for deletado, deleta avaliações
});

// Cada avaliação pertence a um restaurante
Avaliacao.belongsTo(Restaurante, {
  foreignKey: 'restaurante_id',
  as: 'restaurante'
});

module.exports = {
  Restaurante,
  Avaliacao
};
```

### 6. Tipos de Relacionamentos

**1:N (Um para Muitos) - hasMany / belongsTo**
```javascript
// Um restaurante tem muitas avaliações
Restaurante.hasMany(Avaliacao, { foreignKey: 'restaurante_id' });
Avaliacao.belongsTo(Restaurante, { foreignKey: 'restaurante_id' });
```

**N:M (Muitos para Muitos) - belongsToMany**
```javascript
// Exemplo: Receitas e Ingredientes
Receita.belongsToMany(Ingrediente, { 
  through: 'ReceitaIngrediente',
  foreignKey: 'receita_id' 
});
Ingrediente.belongsToMany(Receita, { 
  through: 'ReceitaIngrediente',
  foreignKey: 'ingrediente_id' 
});
```

**1:1 (Um para Um) - hasOne / belongsTo**
```javascript
// Exemplo: Usuário e Perfil
Usuario.hasOne(Perfil, { foreignKey: 'usuario_id' });
Perfil.belongsTo(Usuario, { foreignKey: 'usuario_id' });
```

### 7. Sincronizando com o Banco de Dados

**Atualizar `server.js`:**

```javascript
const app = require('./src/app');
const sequelize = require('./src/config/database');
const { Restaurante, Avaliacao } = require('./src/models');

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    // Sincronizar modelos com banco de dados
    // force: true -> DROP e CREATE (cuidado em produção!)
    // alter: true -> ALTER TABLE (ajusta colunas)
    await sequelize.sync({ 
      force: process.env.NODE_ENV === 'development' 
    });
    
    console.log('✅ Modelos sincronizados com banco de dados');
    
    app.listen(PORT, () => {
      console.log(`🚀 Servidor rodando na porta ${PORT}`);
      console.log(`📍 http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('❌ Erro ao iniciar servidor:', error);
    process.exit(1);
  }
}

startServer();
```

### 8. Testando os Modelos

**Criar arquivo `src/test-models.js`:**

```javascript
const { Restaurante, Avaliacao } = require('./models');

async function testarModelos() {
  try {
    // Criar restaurante
    const restaurante = await Restaurante.create({
      nome: 'Pizza Bella',
      categoria: 'Italiana',
      endereco: 'Rua das Flores, 123',
      telefone: '(11) 98765-4321',
      descricao: 'Melhor pizza da cidade!'
    });
    
    console.log('✅ Restaurante criado:', restaurante.toJSON());
    
    // Criar avaliação
    const avaliacao = await Avaliacao.create({
      restaurante_id: restaurante.id,
      nota: 5,
      comentario: 'Excelente! Recomendo muito!',
      autor: 'João Silva'
    });
    
    console.log('✅ Avaliação criada:', avaliacao.toJSON());
    
    // Buscar restaurante com avaliações
    const restauranteComAvaliacoes = await Restaurante.findByPk(restaurante.id, {
      include: [{
        model: Avaliacao,
        as: 'avaliacoes'
      }]
    });
    
    console.log('✅ Restaurante com avaliações:', 
      JSON.stringify(restauranteComAvaliacoes, null, 2)
    );
    
  } catch (error) {
    console.error('❌ Erro:', error);
  }
}

testarModelos();
```

**Executar app:**

Na primeira vez que a aplicação for executada as tabelas de banco de dados serão criadas.   
```bash
node run dev
```

Pare a execução da aplicação. Agora você pode ir no seu banco de dados e visualizar que as tabelas foram criadas. Execute o script a seguir para validar se está conseguindo inserir dados no seu banco. Após a execução deverá existir um registro em cada tabela. 

**Executar teste:**
```bash
node src/test-models.js
```

### 9. Validações Comuns

```javascript
// String
nome: {
  type: DataTypes.STRING(100),
  allowNull: false,           // Campo obrigatório
  validate: {
    notEmpty: true,           // Não pode ser string vazia
    len: [3, 100],            // Tamanho entre 3 e 100
    is: /^[a-zA-Z\s]+$/i     // Regex: apenas letras e espaços
  }
}

// Email
email: {
  type: DataTypes.STRING(100),
  unique: true,               // Valor único
  validate: {
    isEmail: true            // Valida formato de email
  }
}

// Número
preco: {
  type: DataTypes.DECIMAL(10, 2),
  validate: {
    min: 0,                  // Valor mínimo
    max: 10000               // Valor máximo
  }
}

// Enum
status: {
  type: DataTypes.ENUM('ativo', 'inativo', 'pendente'),
  defaultValue: 'ativo'
}

// Data
data_nascimento: {
  type: DataTypes.DATEONLY,
  validate: {
    isDate: true,
    isBefore: new Date().toISOString()  // Antes de hoje
  }
}
```

## 🔨 Atividade Prática

### Exercício 1: Criar Modelo de Receita

Crie um modelo `Receita` com os seguintes campos:
- nome (string, obrigatório, 3-100 caracteres)
- tempo_preparo (inteiro, minutos, 1-500)
- dificuldade (enum: 'fácil', 'média', 'difícil')
- porcoes (inteiro, 1-20)
- instrucoes (texto longo)
- ativo (boolean, padrão true)

<details>
<summary>Ver solução</summary>

```javascript
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Receita = sequelize.define('receita', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  nome: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [3, 100]
    }
  },
  tempo_preparo: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1,
      max: 500
    }
  },
  dificuldade: {
    type: DataTypes.ENUM('fácil', 'média', 'difícil'),
    allowNull: false
  },
  porcoes: {
    type: DataTypes.INTEGER,
    validate: {
      min: 1,
      max: 20
    }
  },
  instrucoes: {
    type: DataTypes.TEXT,
    allowNull: false
  },
  ativo: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  }
}, {
  tableName: 'receitas',
  timestamps: true,
  underscored: true
});

module.exports = Receita;
```

</details>

### Exercício 2: Adicionar Relacionamento

Crie um relacionamento onde uma Receita pode ter muitas Avaliações.

<details>
<summary>Ver solução</summary>

```javascript
// Em models/index.js
const Receita = require('./Receita');
const Avaliacao = require('./Avaliacao');

// Adicionar campo polimórfico em Avaliacao
// ou criar modelo AvaliacaoReceita separado

Receita.hasMany(Avaliacao, {
  foreignKey: 'receita_id',
  as: 'avaliacoes'
});

Avaliacao.belongsTo(Receita, {
  foreignKey: 'receita_id',
  as: 'receita'
});
```

</details>

## 💡 Conceitos-Chave

- **ORM** abstrai operações SQL em métodos JavaScript
- **Modelos** representam tabelas do banco de dados
- **DataTypes** definem o tipo de cada coluna
- **Validações** garantem integridade dos dados antes de salvar
- **Relacionamentos** conectam modelos (hasMany, belongsTo, etc.)
- **sync()** cria/atualiza tabelas baseado nos modelos
- **Timestamps** adicionam created_at e updated_at automaticamente

## ➡️ Próximos Passos

Com os modelos definidos, no próximo módulo vamos começar a construir a **API REST**, criando os controllers e rotas para operações CRUD de restaurantes.

[➡️ Ir para Tutorial 5: Configuração do ORM e Conexão com BD](../modulo2/05-configuracao-orm-conexao.md)

---

**Dica:** Use o DBeaver ou pgAdmin para visualizar as tabelas criadas no PostgreSQL!
