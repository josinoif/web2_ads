# Módulo 01 - Configuração do Ambiente

Neste módulo, você vai preparar todo o ambiente de desenvolvimento necessário para construir o sistema de receitas.

## Objetivos do Módulo

- ✅ Instalar Node.js e npm
- ✅ Instalar e configurar MySQL
- ✅ Instalar Postman para testes de API
- ✅ Criar a estrutura de pastas do projeto
- ✅ Verificar se tudo está funcionando

---

## 1. Instalação do Node.js

O Node.js é necessário para executar JavaScript no servidor e gerenciar pacotes com npm.

### Passo a Passo:

1. **Acesse o site oficial:** [https://nodejs.org](https://nodejs.org)

2. **Baixe a versão LTS** (Long Term Support) - é a versão mais estável e recomendada

3. **Execute o instalador** e siga as instruções na tela

4. **Verifique a instalação** abrindo o terminal e executando:

```bash
node --version
```

Você deve ver algo como: `v18.17.0` ou superior

```bash
npm --version
```

Você deve ver algo como: `9.6.7` ou superior

### Solução de Problemas:

**Se os comandos não funcionarem:**
- Windows: Reinicie o computador após a instalação
- Mac/Linux: Feche e abra o terminal novamente
- Verifique se o Node.js foi adicionado ao PATH do sistema

---

## 2. Instalação do MySQL

O MySQL será nosso banco de dados para armazenar receitas e ingredientes.

### Opção 1: MySQL Community Server (Recomendado)

1. **Acesse:** [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)

2. **Baixe o instalador** para seu sistema operacional

3. **Durante a instalação:**
   - Escolha "Developer Default" como tipo de instalação
   - Defina uma senha para o usuário `root` (ANOTE ESSA SENHA!)
   - Configure o MySQL para iniciar automaticamente

4. **Verifique a instalação:**

Abra o terminal e execute:
```bash
mysql --version
```

Deve exibir algo como: `mysql Ver 8.0.33`

### Opção 2: XAMPP (Mais fácil para iniciantes)

1. **Acesse:** [https://www.apachefriends.org](https://www.apachefriends.org)

2. **Baixe e instale o XAMPP**

3. **Inicie o XAMPP Control Panel**

4. **Clique em "Start" no MySQL**

5. **Acesse o phpMyAdmin:** [http://localhost/phpmyadmin](http://localhost/phpmyadmin)

### Testando a Conexão:

**Se instalou MySQL direto:**
```bash
mysql -u root -p
```
Digite a senha que você definiu.

**Se instalou XAMPP:**
Apenas acesse o phpMyAdmin no navegador.

---

## 3. Instalação do Postman

O Postman é uma ferramenta essencial para testar APIs durante o desenvolvimento.

### Passo a Passo:

1. **Acesse:** [https://www.postman.com/downloads/](https://www.postman.com/downloads/)

2. **Baixe o Postman Desktop**

3. **Instale e abra o Postman**

4. **Crie uma conta gratuita** (opcional, mas recomendado)

5. **Familiarize-se com a interface:**
   - Barra de URL para fazer requisições
   - Abas GET, POST, PUT, DELETE
   - Área de visualização de respostas

---

## 4. Editor de Código

Recomendamos o **Visual Studio Code** (VS Code).

### Instalação:

1. **Acesse:** [https://code.visualstudio.com](https://code.visualstudio.com)

2. **Baixe e instale**

3. **Extensões recomendadas para o VS Code:**
   - ES7+ React/Redux/React-Native snippets
   - MySQL (por cweijan)
   - Prettier - Code formatter
   - ESLint

**Como instalar extensões:**
1. Abra o VS Code
2. Clique no ícone de extensões (ou Ctrl+Shift+X)
3. Busque pelo nome da extensão
4. Clique em "Install"

---

## 5. Criando a Estrutura do Projeto

Agora vamos criar as pastas para organizar nosso projeto.

### No Terminal:

**Windows (CMD ou PowerShell):**
```bash
cd Documents
mkdir crud-receitas
cd crud-receitas
mkdir backend
mkdir frontend
```

**Mac/Linux:**
```bash
cd ~/Documents
mkdir crud-receitas
cd crud-receitas
mkdir backend
mkdir frontend
```

### Estrutura criada:

```
crud-receitas/
├── backend/     ← Aqui ficará o servidor Express
└── frontend/    ← Aqui ficará a aplicação React
```

---

## 6. Verificação Final

Antes de prosseguir, vamos garantir que tudo está funcionando.

### Checklist:

- [ ] Node.js instalado (comando `node --version` funciona)
- [ ] npm instalado (comando `npm --version` funciona)
- [ ] MySQL instalado e funcionando
- [ ] Postman instalado e abrindo
- [ ] VS Code instalado
- [ ] Pastas do projeto criadas

### Teste Rápido do Node.js:

1. **Crie um arquivo de teste:**

Dentro da pasta `crud-receitas`, crie um arquivo `teste.js`:

```javascript
console.log('Node.js está funcionando!');
console.log('Versão do Node:', process.version);
```

2. **Execute o arquivo:**

```bash
node teste.js
```

Você deve ver:
```
Node.js está funcionando!
Versão do Node: v18.17.0
```

3. **Delete o arquivo de teste:**

```bash
rm teste.js
```

### Teste Rápido do MySQL:

**Conecte ao MySQL via terminal:**

```bash
mysql -u root -p
```

**Execute um comando SQL simples:**

```sql
SHOW DATABASES;
```

Você deve ver uma lista de bancos de dados.

**Saia do MySQL:**

```sql
exit;
```

---

## Solução de Problemas Comuns

### Node.js não reconhecido

**Erro:** `'node' is not recognized as an internal or external command`

**Solução:**
1. Reinstale o Node.js marcando a opção "Add to PATH"
2. Reinicie o computador
3. Verifique novamente

### MySQL não inicia

**Erro:** `Can't connect to MySQL server`

**Solução:**
1. Verifique se o serviço MySQL está rodando
2. Windows: Services → MySQL → Iniciar
3. Mac: System Preferences → MySQL → Start
4. Linux: `sudo systemctl start mysql`

### Porta do MySQL ocupada

**Erro:** `Port 3306 is already in use`

**Solução:**
1. Outro programa está usando a porta 3306
2. Encerre outros serviços MySQL
3. Ou configure o MySQL para usar outra porta

---

## Resumo do Módulo

Neste módulo você:
- ✅ Instalou todas as ferramentas necessárias
- ✅ Verificou que tudo está funcionando
- ✅ Criou a estrutura básica de pastas
- ✅ Está pronto para começar o desenvolvimento

---

## Próximo Passo

Agora que o ambiente está configurado, vamos criar o banco de dados!

**➡️ Próximo:** [Módulo 02 - Banco de Dados](02-banco-de-dados.md)

---

## Dicas Importantes

💡 **Mantenha tudo atualizado:** Verifique se há atualizações das ferramentas periodicamente.

💡 **Anote suas senhas:** Guarde a senha do MySQL em um local seguro.

💡 **Use o terminal:** Familiarize-se com comandos básicos do terminal, você vai usá-los muito!

💡 **Organize seu workspace:** Mantenha as pastas do projeto organizadas desde o início.
