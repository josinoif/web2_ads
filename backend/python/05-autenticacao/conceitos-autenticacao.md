# Conceitos: Autenticação em APIs

## O que é autenticação?

**Autenticação** é o processo de verificar a identidade de um usuário ou sistema. Em APIs web, isso geralmente envolve o fornecimento de credenciais (por exemplo, nome de usuário e senha) para provar que o cliente é quem diz ser. A API então confia em alguma representação dessa identidade (por exemplo, um token) nas requisições seguintes.

## Autenticação por sessão vs por token

- **Sessão (server-side)**: o servidor armazena o estado do login (ex.: em memória ou Redis). O cliente envia um identificador (cookie ou token opaco). Cada requisição é validada consultando esse armazenamento. Revogar o acesso é imediato, mas o servidor precisa de estado e escalar horizontalmente exige sessões compartilhadas ou sticky sessions.

- **Token (stateless)**: o servidor não guarda estado. Após o login, o servidor emite um **token** (ex.: JWT) que contém informações assinadas (quem é o usuário, até quando vale). O cliente envia o token em cada requisição (geralmente no cabeçalho `Authorization: Bearer <token>`). O servidor só valida a assinatura e a expiração. Não há consulta a armazenamento por requisição, o que facilita escalabilidade; a desvantagem é que revogar antes do vencimento exige mecanismos extras (lista de revogação, tokens de vida curta com refresh token).

Para APIs REST e escaláveis, o padrão mais comum é **autenticação por token**, em especial **JWT**.

## JSON Web Token (JWT)

Um **JWT** (RFC 7519) é um padrão compacto para transmitir informações entre partes como um objeto JSON, de forma que possam ser verificadas (assinadas). É muito usado para autenticação em APIs.

### Estrutura

Um JWT tem três partes em Base64URL, separadas por ponto (`.`):

1. **Header**: tipo do token (JWT) e algoritmo de assinatura (ex.: HS256, RS256).
2. **Payload**: claims (dados), por exemplo `sub` (subject, muitas vezes o ID do usuário), `exp` (expiration), `iat` (issued at). Podem ser incluídos papéis (roles) ou escopos.
3. **Signature**: assinatura gerada a partir do header, do payload e de um segredo (ou chave privada). Quem conhece o segredo pode verificar que o token não foi alterado.

O conteúdo do payload pode ser lido por qualquer um (é só decodificar Base64); por isso **não se deve colocar dados sensíveis**. A segurança vem da assinatura: apenas quem possui o segredo (ou a chave) pode gerar ou validar tokens válidos.

### Boas práticas

- **Não armazenar informações sensíveis no payload** (apenas identificador e claims necessários).
- **Usar HTTPS** para não expor o token na rede.
- **Definir expiração** (`exp`) e, se necessário, refresh tokens para renovar sem pedir senha de novo.
- **Guardar o segredo com segurança** (variáveis de ambiente, nunca no código).

## Hash de senha

Senhas **nunca** devem ser armazenadas em texto plano. O servidor deve guardar apenas um **hash** gerado por uma função adequada (ex.: bcrypt, argon2). No login, a senha enviada é hasheada da mesma forma e o resultado é comparado com o hash armazenado.

- **Bcrypt** (ou variantes): com salt e custo configurável; amplamente usado e suportado em Python por bibliotecas como **passlib** com o esquema `bcrypt`.

No curso usamos **passlib** com bcrypt para hashear na criação/atualização de usuário e para verificar no login.

## Fluxo típico na API

1. **Registro (opcional)**: cliente envia usuário/senha; a API hasheia a senha e persiste o usuário.
2. **Login**: cliente envia usuário e senha; a API verifica as credenciais (comparando o hash), gera um JWT com `sub` (e talvez role) e `exp`, e devolve o token.
3. **Requisições autenticadas**: cliente envia `Authorization: Bearer <token>`; a API valida o token (assinatura e expiração), extrai o usuário e usa essa informação na rota (e, no próximo módulo, para autorização).

No FastAPI isso é implementado com **OAuth2PasswordBearer** (esquema que indica que a rota espera um Bearer token), uma dependência que lê o token, decodifica/valida o JWT e retorna o usuário (ou lança 401).
