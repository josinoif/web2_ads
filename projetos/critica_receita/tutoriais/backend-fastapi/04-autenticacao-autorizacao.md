# Autenticação e Autorização (FastAPI)

## Objetivos
- Implementar registro/login com JWT
- Proteger rotas de CRUD e upload
- Garantir autorização básica (dono do recurso ou papéis simples)

## Passo a passo
1. Modelo `User`, hashing de senha com passlib, rota `POST /auth/register`
2. Rota `POST /auth/login` emitindo JWT (HS256) com expiração
3. Dependência `get_current_user` para proteger rotas
4. Checagem de dono para editar/deletar avaliações e itens
5. Testes: token inválido/expirado, acesso negado, fluxo feliz

## Checklist
- `JWT_SECRET`, `JWT_EXPIRES_IN` em env
- Tokens renováveis ou expiração curta definida
- Mensagens de erro coerentes
