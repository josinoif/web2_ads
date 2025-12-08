# Autenticação e Autorização (NestJS)

## Objetivos
- Implementar registro/login com JWT
- Proteger rotas de CRUD e upload
- Aplicar autorização simples (papéis ou dono do recurso)

## Passo a passo
1. `AuthModule`: service de usuários, hashing com bcrypt, rota `POST /auth/register` e `POST /auth/login`
2. `JwtModule` com secret/expiração; strategy + guard (`JwtAuthGuard`)
3. Decorator `@CurrentUser()` para acessar usuário na rota
4. Guards/filters para verificar dono em updates/deletes de reviews e itens
5. Tests de integração para login, rota protegida, token inválido

## Checklist
- `JWT_SECRET` e expiração configurados
- Password hashing e validação robusta
- Mensagens de erro consistentes
