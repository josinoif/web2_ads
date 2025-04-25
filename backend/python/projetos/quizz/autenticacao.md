# Protegendo uma API com Tokens JWT e Autorização Baseada em Papéis

Neste tutorial, vamos aprender como proteger uma API utilizando tokens JWT (JSON Web Tokens) e implementar autorização baseada em papéis. O exemplo será feito em Python com o framework Flask. Antes de mergulharmos no código, vamos entender os conceitos fundamentais de autenticação e autorização, bem como as vantagens e desvantagens dessa abordagem.

---

## Fundamentos de Autenticação e Autorização

### O que é Autenticação?
Autenticação é o processo de verificar a identidade de um usuário ou sistema. Em aplicações web, isso geralmente envolve o fornecimento de credenciais, como nome de usuário e senha, para provar que o usuário é quem diz ser.

### O que é Autorização?
Autorização é o processo de determinar quais recursos ou ações um usuário autenticado tem permissão para acessar. Enquanto a autenticação responde à pergunta "Quem é você?", a autorização responde à pergunta "O que você pode fazer?".

### Diferença entre Autenticação e Autorização
- **Autenticação**: Confirma a identidade do usuário.
- **Autorização**: Define os privilégios do usuário após a autenticação.

---

## JSON Web Tokens (JWT)

### O que é um JWT?
Um JSON Web Token (JWT) é um padrão aberto (RFC 7519) que define uma maneira compacta e segura de transmitir informações entre partes como um objeto JSON. Ele é amplamente utilizado para autenticação e troca de informações em aplicações web.

### Estrutura de um JWT
Um JWT é composto por três partes, separadas por pontos (`.`):
1. **Header**: Contém o tipo do token (JWT) e o algoritmo de assinatura, como HMAC SHA256 ou RSA.
2. **Payload**: Contém as informações (claims) que estão sendo transmitidas, como o ID do usuário, o papel (role) e outros dados personalizados.
3. **Signature**: Garante a integridade do token, sendo gerada a partir do header, payload e uma chave secreta ou um par de chaves pública/privada.

Exemplo de um JWT:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Quando decodificado, o token acima se transforma no seguinte JSON:

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

**Signature**:
A assinatura é uma string gerada a partir do header, payload e uma chave secreta, e não pode ser decodificada diretamente.

### Visualizando o Conteúdo de um JWT
O conteúdo de um JWT pode ser decodificado e visualizado facilmente em ferramentas como [jwt.io](https://jwt.io). Basta colar o token na ferramenta para ver o header, payload e a assinatura. É importante lembrar que decodificar um JWT não significa verificar sua autenticidade, pois qualquer pessoa pode visualizar o conteúdo, mas apenas quem possui a chave secreta pode validar a assinatura.

### Escopos em um Token
Os escopos em um token são usados para definir os limites de acesso de um usuário ou sistema. Eles especificam quais recursos ou ações o portador do token tem permissão para acessar. Por exemplo, um token pode conter um escopo como `read:users` ou `write:posts`. Isso resolve o problema de controle granular de permissões, permitindo que diferentes tokens tenham diferentes níveis de acesso, dependendo do contexto.

### Expiração do Token
Os tokens JWT geralmente possuem um tempo de expiração definido no claim `exp` (expiration). Isso é importante para limitar a janela de tempo em que um token pode ser usado, reduzindo o impacto de um token comprometido. Após a expiração, o cliente precisará obter um novo token, geralmente por meio de um processo de renovação (refresh token) ou reautenticação.

### Considerações de Segurança
- **Não armazene informações sensíveis no payload**: O conteúdo do JWT pode ser decodificado por qualquer pessoa.
- **Use HTTPS**: Sempre transmita tokens em conexões seguras para evitar interceptação.
- **Revogação**: Combine o uso de listas de revogação ou tokens de curta duração com refresh tokens para maior controle.

Com esses conceitos, você pode implementar tokens JWT de forma mais segura e eficaz em suas aplicações.
```

### Vantagens do JWT
- **Compacto**: Pode ser transmitido via URL, cabeçalhos HTTP ou armazenado em cookies.
- **Autossuficiente**: Contém todas as informações necessárias para autenticação.
- **Escalável**: Ideal para sistemas distribuídos, pois não exige armazenamento de sessão no servidor.

### Desvantagens do JWT
- **Revogação Complexa**: Não é trivial invalidar um token antes de seu vencimento.
- **Tamanho**: Pode ser maior que outros métodos de autenticação, dependendo da quantidade de informações no payload.
- **Segurança**: Se a chave secreta for comprometida, todos os tokens gerados com ela também estarão comprometidos.

---

## Cenários de Uso

### Quando Usar JWT?
- **APIs RESTful**: JWT é ideal para autenticação em APIs sem estado.
- **Sistemas Distribuídos**: Permite autenticação sem necessidade de um armazenamento centralizado de sessões.
- **Autenticação entre Serviços**: Facilita a comunicação segura entre microserviços.

### Quando Não Usar JWT?
- **Sessões Longas**: Para aplicações onde o usuário permanece logado por longos períodos, o gerenciamento de sessões pode ser mais eficiente.
- **Necessidade de Revogação Imediata**: Se for necessário invalidar tokens frequentemente, JWT pode não ser a melhor escolha.

---

## Pré-requisitos

- Python 3.7 ou superior instalado.
- Biblioteca `Flask` instalada.
- Biblioteca `PyJWT` instalada.
- Biblioteca `Flask-JWT-Extended` instalada.

Para instalar as dependências, execute:

```bash
pip install flask flask-jwt-extended
```

---

## 1. Configurando o Projeto

Crie um arquivo chamado `app.py` e adicione o seguinte código básico:

```python
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta'  # Substitua por uma chave segura
jwt = JWTManager(app)
```

---

## 2. Criando o Endpoint de Login

Adicione um endpoint para autenticação e geração de tokens JWT:

```python
# Usuários de exemplo com papéis
users = {
  "admin": {"password": "admin123", "role": "admin"},
  "user": {"password": "user123", "role": "user"}
}

@app.route('/login', methods=['POST'])
def login():
  username = request.json.get('username')
  password = request.json.get('password')

  user = users.get(username)
  if not user or user['password'] != password:
    return jsonify({"msg": "Credenciais inválidas"}), 401

  # Gerar token com informações do papel
  access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})
  return jsonify(access_token=access_token)
```

---

## 3. Protegendo Endpoints com JWT

Use o decorador `@jwt_required()` para proteger endpoints:

```python
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
  return jsonify({"msg": "Você acessou um endpoint protegido!"})
```

---

## 4. Implementando Autorização Baseada em Papéis

Adicione uma função para verificar o papel do usuário:

```python
def role_required(required_role):
  def wrapper(fn):
    @jwt_required()
    def decorator(*args, **kwargs):
      claims = get_jwt()
      if claims.get("role") != required_role:
        return jsonify({"msg": "Acesso negado"}), 403
      return fn(*args, **kwargs)
    return decorator
  return wrapper
```

Agora, crie endpoints com restrições baseadas em papéis:

```python
@app.route('/admin', methods=['GET'])
@role_required('admin')
def admin_only():
  return jsonify({"msg": "Bem-vindo, administrador!"})

@app.route('/user', methods=['GET'])
@role_required('user')
def user_only():
  return jsonify({"msg": "Bem-vindo, usuário!"})
```

---

## 5. Testando a API

1. Faça login enviando um `POST` para `/login` com um corpo JSON contendo `username` e `password`.
2. Use o token JWT retornado para acessar os endpoints protegidos, adicionando-o no cabeçalho `Authorization` como `Bearer <token>`.

---

## Conclusão

Neste tutorial, aprendemos como proteger uma API com tokens JWT e implementar autorização baseada em papéis. Também exploramos os conceitos fundamentais de autenticação e autorização, bem como as vantagens e desvantagens do uso de JWT. Essa abordagem é útil para garantir que apenas usuários autorizados possam acessar determinados recursos da sua aplicação. No entanto, é importante avaliar cuidadosamente os requisitos do seu sistema antes de escolher JWT como solução de autenticação.
