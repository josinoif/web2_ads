# Conceitos: Documentação de API

## OpenAPI (ex-Swagger)

**OpenAPI** (antigo Swagger 2.0 evoluído) é uma especificação aberta para descrever APIs REST: endpoints, métodos HTTP, parâmetros (path, query, header, body), respostas (códigos e esquemas) e segurança. A partir dessa descrição, ferramentas geram documentação legível e até clientes/servidores.

O FastAPI gera automaticamente um esquema OpenAPI a partir das rotas, dos tipos dos parâmetros e dos modelos Pydantic. Não é obrigatório escrever o OpenAPI à mão; ele é mantido em sincronia com o código.

## Swagger UI e ReDoc

O FastAPI expõe duas interfaces para a mesma especificação:

- **Swagger UI** (`/docs`): interface interativa onde você pode executar as requisições (try it out). Ideal para testar a API durante o desenvolvimento.
- **ReDoc** (`/redoc`): documentação em formato de leitura, organizada por tags e endpoints. Útil para compartilhar com consumidores da API.

Ambas leem o mesmo esquema OpenAPI; a diferença é a apresentação.

## Boas práticas na documentação

- **Título e descrição**: configurar no `FastAPI(title=..., description=...)` ajuda a identificar a API e seu propósito.
- **Tags**: agrupar endpoints por domínio (ex.: "items", "auth", "users") melhora a navegação no Swagger/ReDoc. No FastAPI isso é feito com `APIRouter(..., tags=["items"])` ou `@router.get(..., tags=["items"])`.
- **Summary e description**: em cada rota, usar `summary` (título curto) e opcionalmente `description` (texto longo) deixa claro o que cada endpoint faz.
- **response_model**: declarar o schema de resposta nas rotas não só valida a saída como documenta o formato no OpenAPI.
- **Exemplos**: em modelos Pydantic, é possível adicionar exemplos (`json_schema_extra` ou `Field(example=...)`) que aparecem na documentação e podem ser usados no "Try it out".
- **Segurança (Bearer)**: se a API usa JWT, configurar o esquema de segurança (Bearer) no OpenAPI permite que o Swagger UI ofereça o botão "Authorize" e envie o token nas requisições. No FastAPI isso é obtido usando `OAuth2PasswordBearer` e, se necessário, declarando `responses` e segurança no app ou nas rotas.

Com isso, a documentação fica útil tanto para quem desenvolve quanto para quem consome a API.
