# Tutorial: CRUD Fullstack - Sistema de Receitas Culinárias

## Sobre o Projeto

Este tutorial guia você na construção de um sistema completo de gerenciamento de receitas culinárias, do zero até uma aplicação funcional com backend e frontend.

### O que você vai construir:

Um sistema web onde é possível:
- ✅ Cadastrar receitas com múltiplos ingredientes
- ✅ Visualizar receitas com todos os detalhes
- ✅ Editar receitas e seus ingredientes
- ✅ Excluir receitas
- ✅ Filtrar receitas por categoria
- ✅ Gerenciar ingredientes do sistema

### Tecnologias Utilizadas:

**Backend:**
- Node.js
- Express.js
- MySQL
- CORS

**Frontend:**
- React.js
- Axios
- Bootstrap
- React-Toastify

### Estrutura do Banco de Dados:

O projeto utiliza 3 tabelas relacionadas:
- `receitas` - Armazena informações das receitas
- `ingredientes` - Catálogo de ingredientes
- `receita_ingredientes` - Relacionamento N:N entre receitas e ingredientes

### Pré-requisitos:

Antes de começar, você precisa ter instalado:
- Node.js (versão 14 ou superior)
- MySQL (versão 5.7 ou superior)
- Editor de código (VS Code recomendado)
- Navegador web moderno
- Postman (para testar a API)

### Como usar este tutorial:

Siga os módulos na ordem apresentada:

1. **[01 - Configuração do Ambiente](01-configuracao-ambiente.md)**
   - Preparação do ambiente de desenvolvimento
   - Instalação de ferramentas necessárias

2. **[02 - Banco de Dados](02-banco-de-dados.md)**
   - Criação do banco de dados MySQL
   - Definição das tabelas e relacionamentos

3. **[03 - Backend: Configuração Inicial](03-backend-configuracao.md)**
   - Estrutura do projeto backend
   - Configuração do Express e conexão com MySQL

4. **[04 - Backend: CRUD de Ingredientes](04-backend-ingredientes.md)**
   - Implementação do CRUD simples
   - Rotas e controllers de ingredientes

5. **[05 - Backend: CRUD de Receitas](05-backend-receitas.md)**
   - Implementação do CRUD complexo com relacionamentos
   - Queries com JOIN e transações

6. **[06 - Frontend: Configuração Inicial](06-frontend-configuracao.md)**
   - Criação do projeto React
   - Configuração do Bootstrap e Axios

7. **[07 - Frontend: Listagem de Receitas](07-frontend-listagem.md)**
   - Componentes de listagem
   - Integração com a API

8. **[08 - Frontend: Formulário de Receitas](08-frontend-formulario.md)**
   - Formulário dinâmico com múltiplos ingredientes
   - Validações e feedback ao usuário

9. **[09 - Integração Final e Testes](09-integracao-final.md)**
   - Testes completos da aplicação
   - Melhorias de UX e deploy

### Estrutura Final do Projeto:

```
crud-fullstack/
├── backend/
│   ├── config/
│   │   └── database.js
│   ├── controllers/
│   │   ├── ingredientesController.js
│   │   └── receitasController.js
│   ├── routes/
│   │   ├── ingredientes.js
│   │   └── receitas.js
│   ├── .env
│   ├── server.js
│   └── package.json
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── tutorial/
    └── (arquivos do tutorial)
```

### Tempo Estimado:

- **Iniciante:** 8-12 horas
- **Intermediário:** 5-8 horas
- **Avançado:** 3-5 horas

### Suporte:

Em caso de dúvidas ou problemas:
1. Revise o módulo atual cuidadosamente
2. Verifique os logs de erro no console
3. Consulte a documentação oficial das tecnologias
4. Peça ajuda ao instrutor

---

**Pronto para começar?** Vá para o [Módulo 01 - Configuração do Ambiente](01-configuracao-ambiente.md)
