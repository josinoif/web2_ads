# Módulo 02 - Banco de Dados

Neste módulo, você vai criar o banco de dados MySQL que armazenará todas as informações do sistema de receitas.

## Objetivos do Módulo

- ✅ Entender a estrutura do banco de dados
- ✅ Criar o banco de dados `sistema_receitas`
- ✅ Criar as tabelas com relacionamentos
- ✅ Inserir dados iniciais de ingredientes
- ✅ Testar o banco de dados

---

## 1. Entendendo a Estrutura do Banco

### Visão Geral:

Nosso sistema terá **3 tabelas**:

1. **`receitas`** - Armazena as receitas
2. **`ingredientes`** - Catálogo de ingredientes disponíveis
3. **`receita_ingredientes`** - Relaciona receitas com ingredientes (N:N)

### Por que 3 tabelas?

**Problema:** Uma receita pode ter vários ingredientes, e um ingrediente pode aparecer em várias receitas.

**Solução:** Usamos uma **tabela intermediária** para criar um relacionamento **muitos-para-muitos (N:N)**.

### Diagrama do Relacionamento:

```
┌───────────-──┐         ┌────────────────────────┐         ┌──────────────┐
│  receitas    │         │ receita_ingredientes   │         │ ingredientes │
├──────────── ─┤         ├────────────────────────┤         ├──────────────┤
│ id (PK)      │─────────│ receita_id (FK)        │─────────│ id (PK)      │
│ nome         │    1:N  │ ingrediente_id (FK)    │  N:1    │ nome         │
│ categoria    │         │ quantidade             │         │ unidade_     │
│ modo_preparo │         └────────────────────────┘         │   medida     │
│ tempo_preparo│                                            └──────────────┘
│ rendimento   │
│ criado_em    │
└─────────────-┘
```

---

## 2. Acessando o MySQL

### Opção 1: Linha de Comando (Terminal)

Abra o terminal e conecte-se ao MySQL:

```bash
mysql -u root -p
```

Digite a senha que você definiu na instalação.

Você verá o prompt do MySQL:
```
mysql>
```

### Opção 2: phpMyAdmin (XAMPP)

Se você usa XAMPP:

1. Inicie o Apache e MySQL no XAMPP Control Panel
2. Abra o navegador: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
3. Clique na aba "SQL" para executar comandos

---

## 3. Criando o Banco de Dados

### Passo 1: Criar o banco

No prompt do MySQL, execute:

```sql
CREATE DATABASE sistema_receitas;
```

**Resultado esperado:**
```
Query OK, 1 row affected (0.01 sec)
```

### Passo 2: Selecionar o banco

```sql
USE sistema_receitas;
```

**Resultado esperado:**
```
Database changed
```

### Passo 3: Verificar bancos existentes

```sql
SHOW DATABASES;
```

Você deve ver `sistema_receitas` na lista.

---

## 4. Criando a Tabela de Ingredientes

Vamos começar pela tabela mais simples.

### Script SQL:

```sql
CREATE TABLE ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    unidade_medida VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Explicação linha por linha:

- `id INT AUTO_INCREMENT PRIMARY KEY` 
  - Campo numérico que incrementa automaticamente
  - É a chave primária (identificador único)

- `nome VARCHAR(100) NOT NULL UNIQUE`
  - Texto com até 100 caracteres
  - Não pode ser vazio (NOT NULL)
  - Não pode ter duplicatas (UNIQUE)

- `unidade_medida VARCHAR(20) NOT NULL`
  - Armazena a unidade (g, kg, ml, unidade, xícara, etc.)
  - Não pode ser vazio

- `criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
  - Data e hora de criação
  - Preenchido automaticamente com a data/hora atual

### Verificar a criação:

```sql
DESCRIBE ingredientes;
```

**Resultado esperado:**
```
+----------------+--------------+------+-----+-------------------+
| Field          | Type         | Null | Key | Default           |
+----------------+--------------+------+-----+-------------------+
| id             | int          | NO   | PRI | NULL              |
| nome           | varchar(100) | NO   | UNI | NULL              |
| unidade_medida | varchar(20)  | NO   |     | NULL              |
| criado_em      | timestamp    | YES  |     | CURRENT_TIMESTAMP |
+----------------+--------------+------+-----+-------------------+
```

---

## 5. Criando a Tabela de Receitas

### Script SQL:

```sql
CREATE TABLE receitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    modo_preparo TEXT NOT NULL,
    tempo_preparo INT NOT NULL,
    rendimento VARCHAR(50) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Explicação dos novos campos:

- `modo_preparo TEXT NOT NULL`
  - Permite texto longo (instruções de preparo)
  
- `tempo_preparo INT NOT NULL`
  - Tempo em minutos (número inteiro)

- `rendimento VARCHAR(50) NOT NULL`
  - Exemplo: "4 porções", "8 pedaços"

- `atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`
  - Atualiza automaticamente quando a receita for modificada

### Verificar a criação:

```sql
DESCRIBE receitas;
```

---

## 6. Criando a Tabela de Relacionamento

Esta é a tabela mais importante! Ela conecta receitas com ingredientes.

### Script SQL:

```sql
CREATE TABLE receita_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receita_id INT NOT NULL,
    ingrediente_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (receita_id) REFERENCES receitas(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE RESTRICT
);
```

### Explicação detalhada:

- `quantidade DECIMAL(10,2) NOT NULL`
  - Número decimal com até 10 dígitos e 2 casas decimais
  - Exemplo: 250.50, 3.00, 1000.00

- `FOREIGN KEY (receita_id) REFERENCES receitas(id) ON DELETE CASCADE`
  - Cria uma chave estrangeira apontando para a tabela `receitas`
  - **ON DELETE CASCADE**: Se a receita for deletada, seus ingredientes também serão removidos

- `FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE RESTRICT`
  - Cria uma chave estrangeira apontando para a tabela `ingredientes`
  - **ON DELETE RESTRICT**: Não permite deletar um ingrediente se ele estiver sendo usado em alguma receita

### Verificar a criação:

```sql
DESCRIBE receita_ingredientes;
```

### Verificar todas as tabelas:

```sql
SHOW TABLES;
```

**Resultado esperado:**
```
+----------------------------+
| Tables_in_sistema_receitas |
+----------------------------+
| ingredientes               |
| receita_ingredientes       |
| receitas                   |
+----------------------------+
```

---

## 7. Inserindo Dados Iniciais

Vamos popular a tabela de ingredientes com alguns itens comuns.

### Script SQL:

```sql
INSERT INTO ingredientes (nome, unidade_medida) VALUES
('Farinha de Trigo', 'g'),
('Açúcar', 'g'),
('Ovos', 'unidade'),
('Leite', 'ml'),
('Manteiga', 'g'),
('Sal', 'g'),
('Fermento em Pó', 'g'),
('Chocolate em Pó', 'g'),
('Óleo', 'ml'),
('Água', 'ml'),
('Tomate', 'unidade'),
('Cebola', 'unidade'),
('Alho', 'dente'),
('Arroz', 'g'),
('Feijão', 'g'),
('Carne Moída', 'g'),
('Frango', 'g'),
('Queijo Mussarela', 'g'),
('Presunto', 'g'),
('Massa para Lasanha', 'unidade');
```

### Verificar os dados inseridos:

```sql
SELECT * FROM ingredientes;
```

Você deve ver 20 ingredientes cadastrados.

### Contando registros:

```sql
SELECT COUNT(*) as total FROM ingredientes;
```

**Resultado:**
```
+-------+
| total |
+-------+
|    20 |
+-------+
```

---

## 8. Testando Relacionamentos

Vamos criar uma receita de teste para garantir que tudo está funcionando.

### Passo 1: Inserir uma receita

```sql
INSERT INTO receitas (nome, categoria, modo_preparo, tempo_preparo, rendimento) 
VALUES (
    'Bolo de Chocolate',
    'Sobremesa',
    '1. Misture os ingredientes secos\n2. Adicione os líquidos\n3. Asse por 40 minutos',
    45,
    '10 fatias'
);
```

### Passo 2: Verificar o ID da receita criada

```sql
SELECT * FROM receitas;
```

Anote o `id` (provavelmente será 1).

### Passo 3: Adicionar ingredientes à receita

```sql
INSERT INTO receita_ingredientes (receita_id, ingrediente_id, quantidade) VALUES
(1, 1, 300),   -- 300g de Farinha de Trigo
(1, 2, 250),   -- 250g de Açúcar
(1, 3, 3),     -- 3 Ovos
(1, 4, 200),   -- 200ml de Leite
(1, 8, 50);    -- 50g de Chocolate em Pó
```

### Passo 4: Consultar a receita com ingredientes

```sql
SELECT 
    r.nome as receita,
    i.nome as ingrediente,
    ri.quantidade,
    i.unidade_medida
FROM receitas r
INNER JOIN receita_ingredientes ri ON r.id = ri.receita_id
INNER JOIN ingredientes i ON ri.ingrediente_id = i.id
WHERE r.id = 1;
```

**Resultado esperado:**
```
+-------------------+------------------+------------+----------------+
| receita           | ingrediente      | quantidade | unidade_medida |
+-------------------+------------------+------------+----------------+
| Bolo de Chocolate | Farinha de Trigo |     300.00 | g              |
| Bolo de Chocolate | Açúcar           |     250.00 | g              |
| Bolo de Chocolate | Ovos             |       3.00 | unidade        |
| Bolo de Chocolate | Leite            |     200.00 | ml             |
| Bolo de Chocolate | Chocolate em Pó  |      50.00 | g              |
+-------------------+------------------+------------+----------------+
```

---

## 9. Script Completo para Criação

Aqui está o script completo que você pode executar de uma vez:

```sql
-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS sistema_receitas;
USE sistema_receitas;

-- Criar tabela de ingredientes
CREATE TABLE ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    unidade_medida VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de receitas
CREATE TABLE receitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    modo_preparo TEXT NOT NULL,
    tempo_preparo INT NOT NULL,
    rendimento VARCHAR(50) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Criar tabela de relacionamento
CREATE TABLE receita_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receita_id INT NOT NULL,
    ingrediente_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (receita_id) REFERENCES receitas(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE RESTRICT
);

-- Inserir ingredientes iniciais
INSERT INTO ingredientes (nome, unidade_medida) VALUES
('Farinha de Trigo', 'g'),
('Açúcar', 'g'),
('Ovos', 'unidade'),
('Leite', 'ml'),
('Manteiga', 'g'),
('Sal', 'g'),
('Fermento em Pó', 'g'),
('Chocolate em Pó', 'g'),
('Óleo', 'ml'),
('Água', 'ml'),
('Tomate', 'unidade'),
('Cebola', 'unidade'),
('Alho', 'dente'),
('Arroz', 'g'),
('Feijão', 'g'),
('Carne Moída', 'g'),
('Frango', 'g'),
('Queijo Mussarela', 'g'),
('Presunto', 'g'),
('Massa para Lasanha', 'unidade');
```

---

## 10. Comandos Úteis para Gerenciamento

### Limpar todas as tabelas (cuidado!):

```sql
DROP TABLE IF EXISTS receita_ingredientes;
DROP TABLE IF EXISTS receitas;
DROP TABLE IF EXISTS ingredientes;
```

### Visualizar estrutura de uma tabela:

```sql
DESCRIBE nome_da_tabela;
```

### Listar todas as receitas:

```sql
SELECT * FROM receitas;
```

### Listar todos os ingredientes:

```sql
SELECT * FROM ingredientes;
```

### Deletar um registro específico:

```sql
DELETE FROM receitas WHERE id = 1;
```

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou o banco de dados `sistema_receitas`
- ✅ Criou 3 tabelas com relacionamentos corretos
- ✅ Inseriu 20 ingredientes iniciais
- ✅ Testou o relacionamento entre tabelas
- ✅ Aprendeu comandos SQL básicos

---

## Próximo Passo

Agora que o banco está pronto, vamos criar o backend com Express.js!

**➡️ Próximo:** [Módulo 03 - Backend: Configuração Inicial](03-backend-configuracao.md)

---

## Dicas Importantes

💡 **Backup:** Sempre faça backup do banco antes de fazer alterações importantes.

💡 **ON DELETE CASCADE:** Use com cuidado! Pode deletar dados relacionados automaticamente.

💡 **UNIQUE:** O campo `nome` em `ingredientes` é único para evitar duplicatas.

💡 **DECIMAL vs FLOAT:** Usamos DECIMAL para quantidades porque ele é mais preciso.
