# Tutorial NestJS – Backend

Material de estudo para desenvolvimento backend com **NestJS 10**, pensado para que o aluno consiga seguir e reproduzir os exemplos em casa.

## Pré-requisitos

- **Node.js** 18 ou superior (recomendado: LTS 20)
- **TypeScript** 4.8+
- **npm** ou **yarn**
- Conhecimento básico de HTTP e REST

## Ordem sugerida dos capítulos

| Ordem | Arquivo | Conteúdo |
|-------|---------|----------|
| 1 | `1.introducao_nestjs.md` | O que é NestJS, vantagens, quando usar |
| 2 | `2.controllers.md` | Controllers, decorators, rotas HTTP |
| 3 | `3.services.md` | Services e injeção de dependência |
| 4 | `4.introducao_nestjs_persistencia.md` | Persistência com TypeORM (conceitos) |
| 5 | `5.crud_nest_bd.md` | CRUD completo com MySQL e TypeORM |
| 6 | `6.upload_arquivos.md` | Upload e download de arquivos (Multer) |
| 7 | `7.autenticacao.md` | Autenticação JWT (evolui o projeto do cap. 5) |
| 8 | `8.autorizacao.md` | Autorização por papéis (roles) |
| 9 | `9.documentacao_api.md` | Documentação da API com Swagger |
| 10 | `10.testes_software.md` | Testes no NestJS: unidade, integração, e2e, cobertura e TDD |
| — | `exercicio-1.md` | Exercício: e-commerce (entidades, CRUD, pagamento) |

## Dicas para estudo em casa

1. **Siga a ordem**: os tutoriais 5–8 partem de um mesmo projeto (CRUD de contatos + auth). Comece pelo 5 e vá evoluindo.
2. **Ambiente**: use MySQL em Docker (passo a passo no cap. 5) ou ajuste para outro banco suportado pelo TypeORM.
3. **Testes**: para validações manuais, use Postman/Insomnia/`curl` (cap. 9 ajuda no Swagger) e, para automação, siga o cap. 10.
4. **Referência**: em caso de dúvida, consulte a [documentação oficial do NestJS](https://docs.nestjs.com/).

## Compatibilidade

O material foi revisado para **NestJS 10**. Os exemplos de código e comandos foram checados para essa versão. Para atualizar para NestJS 11 ou versões futuras, use o [Migration Guide](https://docs.nestjs.com/migration-guide) oficial.
