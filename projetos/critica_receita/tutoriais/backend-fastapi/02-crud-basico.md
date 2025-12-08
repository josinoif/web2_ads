# CRUD Básico (FastAPI)

## Objetivos
- Implementar CRUD de restaurantes/receitas e avaliações
- Usar Pydantic para schemas e SQLAlchemy para modelos

## Passo a passo
1. Modelos `Item` e `Review` com relacionamentos
2. Schemas de entrada/saída (create/update) com validação
3. Routers `items` e `reviews` com prefixo `/api`
4. Operações: listar (com filtros/paginação), criar, obter, atualizar, deletar
5. Tratamento de erros com `HTTPException`; dependência `get_db` nas rotas
6. Testes com `TestClient` cobrindo happy path e erros comuns

## Checklist
- Respostas consistentes; status codes corretos
- Filtros e paginação funcionando
- Validação rejeita dados inválidos
