# Tutorial 2: Bancos de Dados Relacionais

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Compreender o conceito de bancos de dados relacionais
- Entender a diferença entre SQL e NoSQL
- Conhecer os componentes básicos: tabelas, colunas, linhas
- Compreender chaves primárias e estrangeiras
- Entender relacionamentos entre tabelas
- Escrever consultas SQL básicas

## 📖 Conteúdo

### 1. O que são Bancos de Dados?

Um banco de dados é um sistema organizado para armazenar, gerenciar e recuperar informações.

**Por que precisamos de bancos de dados?**
- ✅ Persistência de dados (sobrevivem ao reinício do servidor)
- ✅ Organização estruturada
- ✅ Consultas eficientes
- ✅ Integridade dos dados
- ✅ Suporte a múltiplos usuários simultâneos
- ✅ Backup e recuperação

### 2. SQL vs NoSQL

**SQL (Relacional)**
- Estrutura em tabelas com linhas e colunas
- Schema rígido e predefinido
- Relacionamentos entre tabelas
- ACID (Atomicidade, Consistência, Isolamento, Durabilidade)
- Exemplos: PostgreSQL, MySQL, SQLite

**NoSQL (Não-Relacional)**
- Estruturas flexíveis (documentos, grafos, chave-valor)
- Schema dinâmico
- Escalabilidade horizontal
- Exemplos: MongoDB, Redis, Cassandra

**Para nosso projeto usaremos PostgreSQL (SQL)** porque:
- Dados estruturados e relacionados
- Integridade referencial importante
- Consultas complexas necessárias

### 3. Estrutura de Tabelas

**Tabela** = Coleção de dados relacionados

```
Tabela: restaurantes
┌────┬─────────────────┬────────────┬──────────────────────┐
│ id │      nome       │ categoria  │       endereco       │
├────┼─────────────────┼────────────┼──────────────────────┤
│ 1  │ Pizza Bella     │ Italiana   │ Rua das Flores, 123  │
│ 2  │ Sushi Master    │ Japonesa   │ Av. Paulista, 456    │
│ 3  │ Burger House    │ Hamburguer │ Rua Central, 789     │
└────┴─────────────────┴────────────┴──────────────────────┘
```

**Componentes:**
- **Colunas** (campos): Definem os atributos (nome, categoria, endereço)
- **Linhas** (registros): Cada linha é uma instância (um restaurante específico)
- **Células**: Interseção de coluna e linha (valor específico)

### 4. Tipos de Dados

Cada coluna tem um tipo de dado:

```sql
CREATE TABLE restaurantes (
  id SERIAL PRIMARY KEY,           -- Número inteiro auto-incrementado
  nome VARCHAR(100) NOT NULL,      -- Texto até 100 caracteres
  categoria VARCHAR(50),           -- Texto até 50 caracteres
  endereco TEXT,                   -- Texto longo
  telefone VARCHAR(20),            -- Texto para telefone
  ativo BOOLEAN DEFAULT true,      -- Verdadeiro/Falso
  criado_em TIMESTAMP DEFAULT NOW() -- Data e hora
);
```

**Tipos comuns:**
- `INTEGER` / `SERIAL` - Números inteiros
- `VARCHAR(n)` - Texto limitado
- `TEXT` - Texto ilimitado
- `BOOLEAN` - Verdadeiro/Falso
- `DATE` / `TIMESTAMP` - Datas
- `DECIMAL` / `NUMERIC` - Números decimais
- `JSON` / `JSONB` - Dados JSON

### 5. Chaves Primárias (Primary Key)

**Chave Primária** = Identificador único de cada registro

```sql
CREATE TABLE restaurantes (
  id SERIAL PRIMARY KEY,  -- Esta é a chave primária
  nome VARCHAR(100),
  categoria VARCHAR(50)
);
```

**Características:**
- ✅ Única (não pode repetir)
- ✅ Não nula (sempre tem valor)
- ✅ Imutável (não deve mudar)
- 🎯 Geralmente é um número auto-incrementado

### 6. Relacionamentos entre Tabelas

**Relacionamento 1:N (Um para Muitos)**

Um restaurante pode ter várias avaliações, mas cada avaliação pertence a um restaurante.

```
restaurantes                    avaliacoes
┌────┬──────────┐               ┌────┬────────────────┬──────┬──────────┐
│ id │   nome   │               │ id │   comentario   │ nota │ rest_id  │
├────┼──────────┤               ├────┼────────────────┼──────┼──────────┤
│ 1  │ Pizza    │ ───┐          │ 1  │ Muito bom!     │  5   │    1     │
│ 2  │ Sushi    │    │          │ 2  │ Excelente      │  5   │    1     │
└────┴──────────┘    └─────────→│ 3  │ Recomendo      │  4   │    1     │
                                 │ 4  │ Top!           │  5   │    2     │
                                 └────┴────────────────┴──────┴──────────┘
```

### 7. Chaves Estrangeiras (Foreign Key)

**Chave Estrangeira** = Referência a uma chave primária de outra tabela

```sql
CREATE TABLE avaliacoes (
  id SERIAL PRIMARY KEY,
  restaurante_id INTEGER NOT NULL,
  nota INTEGER NOT NULL,
  comentario TEXT,
  criado_em TIMESTAMP DEFAULT NOW(),
  
  -- Chave estrangeira: referencia a tabela restaurantes
  FOREIGN KEY (restaurante_id) REFERENCES restaurantes(id)
);
```

**Benefícios:**
- ✅ Garante integridade referencial
- ✅ Impede dados órfãos
- ✅ Facilita consultas relacionadas

### 8. Consultas SQL Básicas

**SELECT - Buscar dados**

```sql
-- Buscar todos os restaurantes
SELECT * FROM restaurantes;

-- Buscar colunas específicas
SELECT nome, categoria FROM restaurantes;

-- Buscar com filtro
SELECT * FROM restaurantes WHERE categoria = 'Italiana';

-- Buscar com ordenação
SELECT * FROM restaurantes ORDER BY nome ASC;

-- Buscar com limite
SELECT * FROM restaurantes LIMIT 10;
```

**INSERT - Inserir dados**

```sql
INSERT INTO restaurantes (nome, categoria, endereco)
VALUES ('Pizza Bella', 'Italiana', 'Rua das Flores, 123');
```

**UPDATE - Atualizar dados**

```sql
UPDATE restaurantes
SET categoria = 'Pizzaria', endereco = 'Rua Nova, 456'
WHERE id = 1;
```

**DELETE - Deletar dados**

```sql
DELETE FROM restaurantes WHERE id = 1;
```

### 9. Consultas com JOIN

**INNER JOIN** - Combinar dados de múltiplas tabelas

```sql
-- Buscar restaurante com suas avaliações
SELECT 
  r.nome,
  r.categoria,
  a.nota,
  a.comentario
FROM restaurantes r
INNER JOIN avaliacoes a ON r.id = a.restaurante_id
WHERE r.id = 1;
```

**LEFT JOIN** - Incluir restaurantes mesmo sem avaliações

```sql
SELECT 
  r.nome,
  COUNT(a.id) as total_avaliacoes,
  AVG(a.nota) as media_notas
FROM restaurantes r
LEFT JOIN avaliacoes a ON r.id = a.restaurante_id
GROUP BY r.id, r.nome;
```

### 10. Agregações

```sql
-- Contar total de restaurantes
SELECT COUNT(*) FROM restaurantes;

-- Média de notas por restaurante
SELECT 
  restaurante_id,
  AVG(nota) as media,
  COUNT(*) as total_avaliacoes
FROM avaliacoes
GROUP BY restaurante_id;

-- Nota máxima e mínima
SELECT 
  MAX(nota) as maior_nota,
  MIN(nota) as menor_nota
FROM avaliacoes;
```

## 🔨 Atividade Prática

### Exercício 1: Modelando Dados

Crie a estrutura SQL para um sistema de receitas que contém:
- Receitas (nome, tempo de preparo, dificuldade, instruções)
- Ingredientes (nome, unidade de medida)
- ReceitaIngredientes (relacionamento N:N - quantidade)

<details>
<summary>Ver solução</summary>

```sql
CREATE TABLE receitas (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  tempo_preparo INTEGER,  -- em minutos
  dificuldade VARCHAR(20),  -- fácil, média, difícil
  instrucoes TEXT,
  criado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ingredientes (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  unidade_medida VARCHAR(20)  -- kg, litros, unidades
);

CREATE TABLE receita_ingredientes (
  id SERIAL PRIMARY KEY,
  receita_id INTEGER NOT NULL,
  ingrediente_id INTEGER NOT NULL,
  quantidade DECIMAL(10,2),
  
  FOREIGN KEY (receita_id) REFERENCES receitas(id),
  FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
);
```

</details>

### Exercício 2: Escrevendo Consultas

Usando as tabelas de restaurantes e avaliações, escreva consultas SQL para:

1. Listar todos os restaurantes da categoria "Italiana"
2. Contar quantas avaliações cada restaurante tem
3. Buscar restaurantes com média de nota acima de 4
4. Listar as 5 avaliações mais recentes

<details>
<summary>Ver soluções</summary>

```sql
-- 1. Restaurantes italianos
SELECT * FROM restaurantes 
WHERE categoria = 'Italiana';

-- 2. Contar avaliações
SELECT 
  r.nome,
  COUNT(a.id) as total_avaliacoes
FROM restaurantes r
LEFT JOIN avaliacoes a ON r.id = a.restaurante_id
GROUP BY r.id, r.nome;

-- 3. Média acima de 4
SELECT 
  r.nome,
  AVG(a.nota) as media
FROM restaurantes r
INNER JOIN avaliacoes a ON r.id = a.restaurante_id
GROUP BY r.id, r.nome
HAVING AVG(a.nota) > 4;

-- 4. 5 avaliações mais recentes
SELECT 
  r.nome,
  a.nota,
  a.comentario,
  a.criado_em
FROM avaliacoes a
INNER JOIN restaurantes r ON a.restaurante_id = r.id
ORDER BY a.criado_em DESC
LIMIT 5;
```

</details>

## 💡 Conceitos-Chave

- **Tabelas** armazenam dados em linhas e colunas
- **Chave Primária** (PK) identifica unicamente cada registro
- **Chave Estrangeira** (FK) cria relacionamentos entre tabelas
- **Relacionamento 1:N** é o mais comum (um para muitos)
- **JOIN** combina dados de múltiplas tabelas
- **Agregações** (COUNT, AVG, SUM) calculam estatísticas
- **Integridade referencial** garante consistência dos dados

## ➡️ Próximos Passos

Agora que você compreende bancos de dados relacionais e SQL, vamos configurar nosso ambiente de desenvolvimento no próximo tutorial, instalando e configurando todas as ferramentas necessárias.

[➡️ Ir para Tutorial 3: Setup do Ambiente de Desenvolvimento](03-setup-ambiente.md)

---

**Dica:** Pratique SQL usando ferramentas online como [SQLFiddle](http://sqlfiddle.com/) ou [DB Fiddle](https://www.db-fiddle.com/) antes de prosseguir!
