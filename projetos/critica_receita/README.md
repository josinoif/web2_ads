# TasteRank - Tutorial Completo de Desenvolvimento Full-Stack

Bem-vindo ao **TasteRank**, um projeto educacional completo para aprender desenvolvimento web através da criação de um sistema de avaliação de restaurantes e receitas.

## 🎯 Sobre o Projeto

Este tutorial guia você passo a passo na construção de uma aplicação CRUD completa, cobrindo desde os fundamentos de HTTP e bancos de dados até práticas avançadas de UX e otimização de código.

### O que você vai aprender:
- 🌐 Protocolo HTTP e APIs REST
- 🗄️ Bancos de dados relacionais e SQL
- 🔧 Backends: Express (Node.js), NestJS (Node.js) e FastAPI (Python)
- 🖼️ Upload e gestão de imagens de perfil dos restaurantes
- ⚛️ Frontend com React + Next.js (App Router)
- 🔄 Comunicação entre frontend e backend
- ✅ Validação, autenticação e autorização básicas
- 🎨 Experiência do usuário (UX) e acessibilidade
- 📦 Boas práticas de código e preparação para produção

## 📚 Estrutura do Curso

### Fundamentos
Base conceitual para desenvolvimento full-stack.

1. [Introdução ao Desenvolvimento Full-Stack e HTTP](tutoriais/fundamentos/01-introducao-fullstack-http.md)
2. [Bancos de Dados Relacionais](tutoriais/fundamentos/02-bancos-dados-relacionais.md)
3. [Setup do Ambiente de Desenvolvimento](tutoriais/fundamentos/03-setup-ambiente.md)
4. [Modelagem de Dados e ORM](tutoriais/fundamentos/04-modelagem-orm.md)

### Backend - Express (Node.js)
API REST completa com ORM, relacionamentos e upload de imagens.

1. [Configuração do ORM e Conexão com BD](tutoriais/backend-express/01-configuracao-orm-conexao.md)
2. [CRUD - Create e Read](tutoriais/backend-express/02-crud-create-read.md)
3. [CRUD - Update e Delete](tutoriais/backend-express/03-crud-update-delete.md)
4. [CORS e Middlewares de Segurança](tutoriais/backend-express/04-cors-middleware.md)
5. [Criando Sistema de Avaliações](tutoriais/backend-express/05-create-avaliacoes.md)
6. [Consultas com Relacionamentos](tutoriais/backend-express/06-consultas-relacionais.md)
7. [Cálculo de Médias e Agregações](tutoriais/backend-express/07-calculo-media.md)
8. [Tratamento de Erros de Banco de Dados](tutoriais/backend-express/08-tratamento-erros-db.md)
9. [Upload de Imagens (Express)](tutoriais/backend-express/09-upload-imagens.md)

### Backend - NestJS (Node.js)
Estrutura modular, validação, CRUD, segurança e funcionalidades avançadas.

- [01 - Setup NestJS](tutoriais/backend-nest/01-setup-nest.md)
- [02 - CRUD Básico](tutoriais/backend-nest/02-crud-basico.md)
- [03 - Upload de Imagens](tutoriais/backend-nest/03-upload-imagens.md)
- [04 - Autenticação e Autorização](tutoriais/backend-nest/04-autenticacao-autorizacao.md)
- [05 - CORS e Segurança](tutoriais/backend-nest/05-cors-seguranca.md)
- [06 - Cálculo Automático de Médias](tutoriais/backend-nest/06-calculo-medias.md)
- [07 - Tratamento Avançado de Erros](tutoriais/backend-nest/07-tratamento-erros.md)

### Backend - FastAPI (Python)
APIs rápidas com Pydantic/SQLAlchemy, CRUD, segurança e funcionalidades avançadas.

- [01 - Setup FastAPI](tutoriais/backend-fastapi/01-setup-fastapi.md)
- [02 - CRUD Básico](tutoriais/backend-fastapi/02-crud-basico.md)
- [03 - Upload de Imagens](tutoriais/backend-fastapi/03-upload-imagens.md)
- [04 - Autenticação e Autorização](tutoriais/backend-fastapi/04-autenticacao-autorizacao.md)
- [05 - CORS e Segurança](tutoriais/backend-fastapi/05-cors-seguranca.md)
- [06 - Cálculo Automático de Médias](tutoriais/backend-fastapi/06-calculo-medias.md)
- [07 - Tratamento Avançado de Erros](tutoriais/backend-fastapi/07-tratamento-erros.md)

### Frontend - Next.js (React)
Interface, consumo de API, UX e upload de imagem de perfil.

1. [Setup do Projeto (React/Next)](tutoriais/frontend-next/01-setup-react.md)
2. [Consumo da API e Listagem](tutoriais/frontend-next/02-consumo-api-listagem.md)
3. [Página de Detalhes do Item](tutoriais/frontend-next/03-detalhe-item.md)
4. [Formulário de Avaliação](tutoriais/frontend-next/04-formulario-avaliacao.md)
5. [Feedback de Erros no Frontend](tutoriais/frontend-next/05-feedback-erros-frontend.md)
6. [Otimização de UX](tutoriais/frontend-next/06-otimizacao-ux.md)
7. [Refatoração e Código Assíncrono](tutoriais/frontend-next/07-refatoracao-async.md)
8. [Revisão e Boas Práticas](tutoriais/frontend-next/08-revisao-boas-praticas.md)
9. [Upload de Imagem de Perfil (Next.js)](tutoriais/frontend-next/09-upload-imagem-perfil.md)

### Boas Práticas e Qualidade
Padrões profissionais e preparação para produção.

- [01 - Organização de Código e Arquitetura](tutoriais/boas-praticas/01-organizacao-codigo.md)
- [02 - Segurança Essencial](tutoriais/boas-praticas/02-seguranca.md)
- [03 - Testes Automatizados](tutoriais/boas-praticas/03-testes.md)

## 🛠️ Tecnologias Utilizadas

### Backend
- **Node.js + Express** - API REST
- **Node.js + NestJS** - Framework modular
- **Python 3 + FastAPI** - APIs rápidas
- **PostgreSQL** - Banco de dados relacional
- **Sequelize** (Express) | **TypeORM** (NestJS) | **SQLAlchemy** (FastAPI)
- **Multer / UploadFile** - Upload e servir imagens
- **Axios** - Cliente HTTP (uso compartilhado em serviços)

### Frontend
- **Next.js (App Router)** - Framework React full-stack
- **React** - Biblioteca para interfaces
- **Axios** - Cliente HTTP
- **React Toastify** - Notificações
- **date-fns** - Formatação de datas

### Ferramentas
- **Git** - Controle de versão
- **Postman/Insomnia** - Teste de APIs
- **VS Code** - Editor de código

## 📋 Pré-requisitos

- Conhecimento básico de JavaScript e Python
- Familiaridade com linha de comando e Git
- Node.js instalado (versão 18+)
- Python instalado (3.10+)
- PostgreSQL instalado e acessível
- Espaço em disco para diretório de uploads (dev)
- Editor de código (VS Code recomendado)

## 🚀 Como Usar Este Tutorial

1. **Siga a ordem dos módulos** - Cada tutorial constrói sobre o conhecimento anterior
2. **Faça os exercícios práticos** - A prática é essencial para fixar os conceitos
3. **Experimente e modifique** - Não tenha medo de explorar além do tutorial
4. **Consulte a documentação oficial** - Use este tutorial como guia, mas aprofunde-se nas tecnologias

## 🎓 Metodologia

Cada tutorial segue uma estrutura consistente:

- **🎯 Objetivos de Aprendizado** - O que você vai dominar
- **📖 Conteúdo** - Conceitos teóricos e exemplos práticos
- **🔨 Atividade Prática** - Exercício hands-on
- **💡 Conceitos-Chave** - Resumo dos principais pontos
- **➡️ Próximos Passos** - O que vem a seguir

## 📊 Progresso Estimado

- **Fundamentos**: 4-6 horas
- **Backend - Express**: 8-10 horas
- **Backend - NestJS**: 8-10 horas
- **Backend - FastAPI**: 8-10 horas
- **Frontend - Next.js**: 8-10 horas
- **UX e Boas Práticas**: 6-8 horas

**Total**: ~42-54 horas de aprendizado prático (ajuste conforme sua carga horária)

## 💪 Ao Final Deste Tutorial

Você será capaz de:

✅ Projetar e implementar APIs REST completas em Express, NestJS ou FastAPI  
✅ Trabalhar com PostgreSQL e ORMs (Sequelize, TypeORM, SQLAlchemy)  
✅ Gerenciar upload e exibição de imagens de perfil de restaurantes  
✅ Criar interfaces Next.js/React modernas e responsivas  
✅ Implementar autenticação e autorização básicas  
✅ Validar dados de entrada e tratar erros de forma profissional  
✅ Otimizar a experiência do usuário e acessibilidade  
✅ Aplicar boas práticas de desenvolvimento e preparar para produção  

## 🆘 Suporte

Se encontrar dificuldades:
1. Revise o tutorial anterior
2. Consulte a documentação oficial das tecnologias
3. Verifique se seguiu todos os passos corretamente
4. Procure ajuda da comunidade (Stack Overflow, fóruns, etc.)

## 📝 Licença

Este material é educacional e pode ser usado livremente para fins de aprendizado.

---

**Pronto para começar?** Vá para o [Tutorial 1: Introdução ao Desenvolvimento Full-Stack e HTTP](tutoriais/fundamentos/01-introducao-fullstack-http.md)

Boa jornada de aprendizado! 🚀
