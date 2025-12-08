# CRUD Básico (NestJS)

## Objetivos
- Implementar CRUD de restaurantes/receitas e avaliações
- Usar DTOs com `class-validator` e services com injeção de dependência

## Passo a passo
1. Entidades `Item` e `Review` com relações; repositórios via TypeORM
2. DTOs `CreateItemDto`, `UpdateItemDto`, `CreateReviewDto`, `UpdateReviewDto` com validação
3. Services contendo regras de negócio e tratamento de erros (not found, conflito)
4. Controllers com rotas REST: listar, filtrar, paginação, CRUD completo
5. Filtro global para transformar exceções em respostas consistentes
6. Testes unitários dos services com repositório em memória/mock

## Checklist
- Rotas CRUD respondem com status e payload consistentes
- Validação rejeita entradas inválidas
- Paginação e filtros simples funcionando
