# Exemplos de Testes HTTP

Este diretório contém arquivos `.http` para testar as APIs dos diferentes backends do projeto Crítica Receita.

## 🚀 Como Usar

### 1. Instalar Extensão REST Client

No VS Code, instale a extensão **REST Client**:
- Abra o VS Code
- Vá em Extensions (Ctrl+Shift+X)
- Busque por "REST Client" (por Huachao Mao)
- Clique em Install

### 2. Executar Requisições

1. Abra qualquer arquivo `.http`
2. Clique em "Send Request" que aparece acima de cada requisição
3. A resposta aparecerá em um painel lateral

### 3. Usar Variáveis

Cada arquivo define variáveis no topo:

```http
### Variáveis
@baseUrl = http://localhost:3000/api
@token = seu_token_jwt_aqui
```

Para requisições autenticadas:
1. Execute a requisição de login
2. Copie o `access_token` da resposta
3. Cole na variável `@token`
4. Todas as requisições autenticadas usarão automaticamente esse token

## 📁 Arquivos Disponíveis

### Express (`express-api-tests.http`)
- **Porta:** 3000
- **Características:** 
  - CRUD completo de restaurantes
  - Sistema de avaliações
  - Upload de imagens
  - Estatísticas
- **Auth:** Não implementada (opcional nos tutoriais)

### NestJS (`nestjs-api-tests.http`)
- **Porta:** 3000
- **Características:**
  - CRUD completo com TypeORM
  - Autenticação JWT obrigatória
  - Upload de imagens
  - Soft delete
  - Validação com class-validator
- **Auth:** JWT com Passport

### FastAPI (`fastapi-api-tests.http`)
- **Porta:** 8000
- **Características:**
  - CRUD completo com SQLAlchemy
  - Autenticação JWT com roles
  - Upload de imagens
  - Documentação automática (Swagger/ReDoc)
  - Validação Pydantic
- **Auth:** JWT com OAuth2PasswordBearer

## 🔐 Autenticação

### Express
Não requer autenticação por padrão (pode ser adicionada).

### NestJS
```http
### Login
POST http://localhost:3000/api/auth/login
Content-Type: application/json

{
  "email": "joao@email.com",
  "password": "Senha123!"
}

### Usar token
GET http://localhost:3000/api/restaurantes
Authorization: Bearer {{token}}
```

### FastAPI
```http
### Login
POST http://localhost:8000/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=senha123

### Usar token
GET http://localhost:8000/api/restaurantes
Authorization: Bearer {{token}}
```

## 📤 Upload de Arquivos

Para upload de imagens, a sintaxe REST Client funciona, mas é mais fácil usar:

### Alternativas Recomendadas:

1. **Thunder Client** (extensão VS Code)
   - Interface visual para APIs
   - Upload de arquivos simplificado
   - Salva coleções de requisições

2. **Postman**
   - Ferramenta completa para APIs
   - Interface gráfica
   - Suporte completo a multipart/form-data

### Sintaxe REST Client para Upload:

```http
POST http://localhost:3000/api/restaurantes/1/imagem
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="imagem"; filename="foto.jpg"
Content-Type: image/jpeg

< ./foto.jpg
------WebKitFormBoundary--
```

## 🎯 Fluxo de Testes Recomendado

### 1. Setup Inicial
```http
# 1. Verificar se API está rodando
GET http://localhost:3000/health

# 2. (Se necessário) Registrar usuário
POST /auth/register

# 3. Fazer login e copiar token
POST /auth/login
```

### 2. CRUD Básico
```http
# 1. Criar restaurante
POST /restaurantes

# 2. Listar restaurantes
GET /restaurantes

# 3. Obter por ID
GET /restaurantes/1

# 4. Atualizar
PUT /restaurantes/1

# 5. Adicionar avaliação
POST /restaurantes/1/avaliacoes
```

### 3. Recursos Avançados
```http
# 1. Upload de imagem
POST /restaurantes/1/imagem

# 2. Filtros e busca
GET /restaurantes?categoria=Italiana&busca=pizza

# 3. Deletar recursos
DELETE /avaliacoes/1
```

## 🛠️ Troubleshooting

### Erro 401 Unauthorized
- Verifique se o token está correto
- Token pode ter expirado (faça login novamente)
- Verifique se o header `Authorization: Bearer {{token}}` está presente

### Erro 404 Not Found
- Verifique se a API está rodando
- Confirme a porta correta (3000 ou 8000)
- Verifique se o ID do recurso existe

### Erro 422/400 Validation Error
- Verifique os campos obrigatórios
- Confirme os tipos de dados (string, number)
- Veja a resposta para detalhes do erro

### Upload não funciona
- Use Thunder Client ou Postman
- Verifique se o arquivo existe no caminho especificado
- Confirme que o tipo de arquivo é permitido
- Verifique o tamanho máximo (geralmente 2MB)

## 💡 Dicas

1. **Organize por contexto**: Agrupe requisições relacionadas
2. **Use comentários**: `# Comentário` ou `### Seção`
3. **Variáveis de ambiente**: Defina no topo do arquivo
4. **Salve respostas**: REST Client permite salvar para referência
5. **Keyboard shortcuts**: 
   - `Ctrl+Alt+R`: Send Request
   - `Ctrl+Alt+C`: Cancel Request
   - `Ctrl+Alt+E`: Switch Environment

## 📚 Recursos

- [REST Client Documentation](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
- [HTTP Request Syntax](https://github.com/Huachao/vscode-restclient/blob/master/README.md)
- [Thunder Client](https://www.thunderclient.com/)
- [Postman](https://www.postman.com/)
