# Tutorial: Tratamento Avançado de Erros no NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar Exception Filters customizados
- Tratar erros específicos do TypeORM
- Implementar logging estruturado de erros
- Criar respostas de erro consistentes
- Implementar retry logic para operações críticas
- Diferenciar erros por ambiente (dev/prod)

## 📖 Conteúdo

### 1. Exception Filters do NestJS

**Exception Filters** capturam exceções e formatam respostas de erro.

**Hierarquia de exceções:**
```
HttpException
├── BadRequestException (400)
├── UnauthorizedException (401)
├── ForbiddenException (403)
├── NotFoundException (404)
├── ConflictException (409)
├── InternalServerErrorException (500)
└── ... outras
```

### 2. Exception Filter Global

**Arquivo `src/filters/http-exception.filter.ts`:**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = response<Response>();
    const request = ctx.getRequest<Request>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Erro interno do servidor';
    let errors: any = undefined;

    // Tratar HttpException do NestJS
    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (typeof exceptionResponse === 'object') {
        message = (exceptionResponse as any).message || message;
        errors = (exceptionResponse as any).errors;
      }
    }
    // Tratar outros erros
    else if (exception instanceof Error) {
      message = exception.message;
    }

    // Log do erro
    const errorLog = {
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
      status,
      message,
      stack: exception instanceof Error ? exception.stack : undefined,
    };

    if (status >= 500) {
      this.logger.error(JSON.stringify(errorLog));
    } else {
      this.logger.warn(JSON.stringify(errorLog));
    }

    // Resposta
    const errorResponse = {
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message,
      ...(errors && { errors }),
      ...(process.env.NODE_ENV === 'development' && {
        stack: exception instanceof Error ? exception.stack : undefined,
      }),
    };

    response.status(status).json(errorResponse);
  }
}
```

### 3. Filter para Erros do TypeORM

**Arquivo `src/filters/typeorm-exception.filter.ts`:**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Response } from 'express';
import {
  QueryFailedError,
  EntityNotFoundError,
  TypeORMError,
} from 'typeorm';

@Catch(QueryFailedError, EntityNotFoundError, TypeORMError)
export class TypeOrmExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(TypeOrmExceptionFilter.name);

  catch(exception: TypeORMError, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Erro no banco de dados';
    let details: any = undefined;

    // QueryFailedError - Erros de query SQL
    if (exception instanceof QueryFailedError) {
      const error = exception as any;

      // Violação de unicidade
      if (error.code === '23505') {
        status = HttpStatus.CONFLICT;
        message = 'Registro duplicado';
        details = this.extrairCampoUnico(error.detail);
      }
      // Violação de chave estrangeira
      else if (error.code === '23503') {
        status = HttpStatus.BAD_REQUEST;
        message = 'Referência inválida';
        details = 'O recurso referenciado não existe';
      }
      // Violação de not null
      else if (error.code === '23502') {
        status = HttpStatus.BAD_REQUEST;
        message = 'Campo obrigatório não informado';
        details = this.extrairCampoNotNull(error.column);
      }
      // Check constraint
      else if (error.code === '23514') {
        status = HttpStatus.BAD_REQUEST;
        message = 'Valor inválido para campo';
        details = error.detail;
      }
      // Erro de sintaxe SQL
      else if (error.code === '42601') {
        status = HttpStatus.INTERNAL_SERVER_ERROR;
        message = 'Erro de sintaxe na query';
      }
      // Timeout de conexão
      else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNREFUSED') {
        status = HttpStatus.SERVICE_UNAVAILABLE;
        message = 'Banco de dados indisponível';
      }
    }
    // EntityNotFoundError - Entidade não encontrada
    else if (exception instanceof EntityNotFoundError) {
      status = HttpStatus.NOT_FOUND;
      message = 'Recurso não encontrado';
    }

    // Log do erro
    this.logger.error({
      timestamp: new Date().toISOString(),
      path: request.url,
      status,
      message,
      error: exception.message,
      stack: exception.stack,
    });

    // Resposta
    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message,
      ...(details && { details }),
      ...(process.env.NODE_ENV === 'development' && {
        error: exception.message,
        query: (exception as any).query,
      }),
    });
  }

  private extrairCampoUnico(detail: string): string {
    const match = detail?.match(/Key \((.+?)\)=/);
    return match ? `O campo '${match[1]}' já está em uso` : 'Valor duplicado';
  }

  private extrairCampoNotNull(column: string): string {
    return `O campo '${column}' é obrigatório`;
  }
}
```

### 4. Filter para Erros de Validação

**Arquivo `src/filters/validation-exception.filter.ts`:**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  BadRequestException,
} from '@nestjs/common';
import { Response } from 'express';

@Catch(BadRequestException)
export class ValidationExceptionFilter implements ExceptionFilter {
  catch(exception: BadRequestException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest();
    const status = exception.getStatus();
    const exceptionResponse: any = exception.getResponse();

    // Formatar erros de validação
    let errors = exceptionResponse.message;
    if (Array.isArray(errors)) {
      errors = errors.map((error) => ({
        field: error.property,
        constraints: error.constraints,
        message: Object.values(error.constraints).join(', '),
      }));
    }

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message: 'Erro de validação',
      errors,
    });
  }
}
```

### 5. Registrar Filters Globalmente

**Atualizar `src/main.ts`:**

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './filters/http-exception.filter';
import { TypeOrmExceptionFilter } from './filters/typeorm-exception.filter';
import { ValidationExceptionFilter } from './filters/validation-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.setGlobalPrefix('api');

  // Exception Filters (ordem importa!)
  app.useGlobalFilters(
    new HttpExceptionFilter(),
    new TypeOrmExceptionFilter(),
    new ValidationExceptionFilter(),
  );

  // Validation Pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      exceptionFactory: (errors) => {
        return new BadRequestException(errors);
      },
    }),
  );

  await app.listen(3000);
}

bootstrap();
```

### 6. Criar Exceções Customizadas

**Arquivo `src/exceptions/business.exception.ts`:**

```typescript
import { HttpException, HttpStatus } from '@nestjs/common';

export class RestauranteNaoEncontradoException extends HttpException {
  constructor(id: number) {
    super(`Restaurante com ID ${id} não encontrado`, HttpStatus.NOT_FOUND);
  }
}

export class AvaliacaoDuplicadaException extends HttpException {
  constructor(userId: number, restauranteId: number) {
    super(
      `Usuário ${userId} já avaliou o restaurante ${restauranteId}`,
      HttpStatus.CONFLICT,
    );
  }
}

export class ImagemNaoEncontradaException extends HttpException {
  constructor() {
    super('Restaurante não possui imagem', HttpStatus.NOT_FOUND);
  }
}

export class LimiteAvaliacoesExcedidoException extends HttpException {
  constructor() {
    super(
      'Limite de avaliações por dia excedido',
      HttpStatus.TOO_MANY_REQUESTS,
    );
  }
}
```

### 7. Usar Exceções Customizadas nos Services

**Atualizar `src/modules/restaurante/restaurante.service.ts`:**

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Restaurante } from './entities/restaurante.entity';
import { RestauranteNaoEncontradoException } from '../../exceptions/business.exception';

@Injectable()
export class RestauranteService {
  constructor(
    @InjectRepository(Restaurante)
    private restauranteRepository: Repository<Restaurante>,
  ) {}

  async findOne(id: number): Promise<Restaurante> {
    const restaurante = await this.restauranteRepository.findOne({
      where: { id },
      relations: ['avaliacoes'],
    });

    if (!restaurante) {
      throw new RestauranteNaoEncontradoException(id);
    }

    return restaurante;
  }

  async remove(id: number): Promise<void> {
    const restaurante = await this.findOne(id); // Usa exceção customizada

    // Soft delete
    restaurante.ativo = false;
    await this.restauranteRepository.save(restaurante);
  }
}
```

### 8. Interceptor para Logging de Requisições

**Arquivo `src/interceptors/logging.interceptor.ts`:**

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { method, url, body } = request;
    const startTime = Date.now();

    this.logger.log(`➡️  ${method} ${url} - Iniciado`);

    return next.handle().pipe(
      tap(() => {
        const duration = Date.now() - startTime;
        this.logger.log(`✅ ${method} ${url} - ${duration}ms`);
      }),
      catchError((error) => {
        const duration = Date.now() - startTime;
        this.logger.error(`❌ ${method} ${url} - ${duration}ms - ${error.message}`);
        throw error;
      }),
    );
  }
}
```

**Aplicar globalmente em `main.ts`:**

```typescript
import { LoggingInterceptor } from './interceptors/logging.interceptor';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // ... outros configs ...
  
  app.useGlobalInterceptors(new LoggingInterceptor());
  
  await app.listen(3000);
}
```

## 🔨 Atividade Prática

### Exercício 1: Testar Erros de Validação

**Arquivo `tests/error-handling-tests.http`:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api

### 1. Criar restaurante sem nome (400 - validação)
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "categoria": "Italiana"
}

### 2. Buscar restaurante inexistente (404)
GET {{baseUrl}}/restaurantes/99999

### 3. Criar restaurante duplicado (409)
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Pizza Bella",
  "categoria": "Italiana"
}

### Executar novamente (deve dar erro de duplicação)
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Pizza Bella",
  "categoria": "Italiana"
}

### 4. Avaliação com nota inválida (400)
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 10,
  "comentario": "Nota inválida"
}
```

### Exercício 2: Observar Logs

Inicie o servidor e observe os logs coloridos:

```
➡️  POST /api/restaurantes - Iniciado
✅ POST /api/restaurantes - 45ms

➡️  GET /api/restaurantes/99999 - Iniciado
❌ GET /api/restaurantes/99999 - 12ms - Restaurante com ID 99999 não encontrado
```

### Exercício 3: Testar Ambientes

**Development** (`.env`):
```env
NODE_ENV=development
```
- Stack trace visível
- Query SQL mostrada
- Detalhes completos

**Production**:
```env
NODE_ENV=production
```
- Apenas mensagem de erro
- Sem stack trace
- Sem detalhes internos

## 💡 Conceitos-Chave

- **Exception Filters**: Captura e formata exceções
- **Custom Exceptions**: Exceções específicas do domínio
- **Interceptors**: Interceptam requisições/respostas
- **Logging**: Registro estruturado de eventos
- **Error Codes**: Códigos de erro do PostgreSQL
- **Stack Traces**: Apenas em desenvolvimento

## 🛡️ Boas Práticas

1. **Hierarquia de Filters**:
   - Filters mais específicos primeiro
   - Filter global por último

2. **Mensagens de Erro**:
   - Mensagens amigáveis para usuários
   - Detalhes técnicos apenas em dev
   - Nunca exponha senhas ou tokens

3. **Logging**:
   - Log todos os erros 500+
   - Warn para erros 400-499
   - Inclua contexto (URL, método, timestamp)

4. **Exceções Customizadas**:
   - Crie exceções específicas do domínio
   - Use códigos HTTP corretos
   - Mensagens descritivas

5. **Segurança**:
   - Não exponha stack traces em produção
   - Não mostre queries SQL
   - Sanitize mensagens de erro

## ➡️ Próximos Passos

Você completou todos os tutoriais de backend NestJS! Próximo:
- Explorar recursos avançados
- Implementar WebSockets
- Adicionar GraphQL

## 📚 Recursos

- [NestJS Exception Filters](https://docs.nestjs.com/exception-filters)
- [TypeORM Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html)
- [NestJS Interceptors](https://docs.nestjs.com/interceptors)
- [Logging Best Practices](https://www.loggly.com/ultimate-guide/node-logging-basics/)
