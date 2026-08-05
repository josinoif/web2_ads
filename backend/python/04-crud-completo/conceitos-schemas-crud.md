# Conceitos: Schemas Pydantic e padrão CRUD

## Schemas vs modelos de banco

Em uma API com FastAPI e ORM, é útil separar duas representações dos dados:

1. **Modelos (ORM)**: classes do SQLAlchemy que mapeiam tabelas. Contêm tipos e restrições do banco (colunas, chaves, relacionamentos). São usados para ler e escrever no banco.
2. **Schemas (Pydantic)**: classes que definem o formato de **entrada** e **saída** da API. Validam o que o cliente envia (body, query) e o que a API devolve (response). Não precisam refletir todas as colunas (ex.: não expor senha) e podem ter campos computados.

Assim, a rota recebe um schema de criação (ex.: `ItemCreate`), converte para o modelo ORM, persiste com a sessão e devolve um schema de resposta (ex.: `Item`), construído a partir do objeto ORM.

## Pydantic e validação

O **Pydantic** valida dados usando type hints. Um modelo Pydantic declara os campos e tipos; ao receber um dicionário (ou JSON), ele valida e pode converter tipos (ex.: string numérica para int). Se algo for inválido, levanta um erro que o FastAPI traduz em resposta 422 (Unprocessable Entity).

No FastAPI, modelos Pydantic são usados para:

- **Body** de POST/PUT: validação da entrada.
- **response_model** nas rotas: formatação e documentação da saída (e remoção de campos que não estejam no schema).

## Padrão de schemas por operação

É comum ter vários schemas para a mesma entidade:

- **Base**: campos comuns (ex.: `ItemBase` com name, description, price). Não costuma ser usado diretamente na rota; serve para herança.
- **Create**: para criação (POST). Herda do Base; pode ter campos extras (ex.: usuário que criou). Não inclui `id` (gerado pelo banco).
- **Update**: para atualização (PUT/PATCH). Geralmente todos os campos opcionais, para atualização parcial.
- **Response** (ou o nome da entidade): para leitura (GET). Inclui `id` e qualquer campo que a API queira expor. Precisa de `model_config` com `from_attributes=True` (Pydantic v2) para ser construído a partir do objeto ORM.

Exemplo de nomenclatura: `ItemCreate`, `ItemUpdate`, `Item`.

## CRUD

**CRUD** (Create, Read, Update, Delete) são as operações básicas sobre um recurso:

- **Create**: POST em `/items/` com body → insere no banco e retorna o item criado.
- **Read**: GET em `/items/` (lista com paginação) e GET em `/items/{id}` (um item).
- **Update**: PUT (ou PATCH) em `/items/{id}` com body → atualiza e retorna o item.
- **Delete**: DELETE em `/items/{id}` → remove e retorna status (ex.: 204 ou mensagem).

No tutorial deste módulo você implementa esse fluxo completo: schemas Pydantic (v2), rotas que usam `Depends(get_db)` e as operações sobre a tabela `items` via SQLAlchemy.
