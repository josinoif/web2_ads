# Tutorial: Setup do Projeto NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar projeto NestJS com CLI
- Configurar variáveis de ambiente com validação
- Conectar ao PostgreSQL usando TypeORM
- Estruturar projeto com módulos
- Habilitar CORS e segurança básica
- Implementar logging estruturado

## 📖 Conteúdo

### 1. Instalando o NestJS CLI

```bash
# Instalar CLI globalmente
npm install -g @nestjs/cli

# Verificar instalação
nest --version

# Criar novo projeto
nest new tasterank-api

# Escolher gerenciador de pacotes (npm)
# Entrar no diretório
cd tasterank-api
```

### 2. Instalando Dependências

```bash
# TypeORM e PostgreSQL
npm install @nestjs/typeorm typeorm pg

# Configuração
npm install @nestjs/config

# Validação
npm install class-validator class-transformer

# Segurança
npm install helmet
npm install @nestjs/throttler

# Utilitários
npm install bcrypt
npm install @types/bcrypt --save-dev
```

### 3. Estrutura do Projeto

```
tasterank-api/
├── src/
│   ├── app.module.ts          # Módulo raiz
│   ├── main.ts                # Entry point
│   ├── config/                # Configurações
│   │   ├── database.config.ts
│   │   └── env.validation.ts
│   ├── common/                # Código compartilhado
│   │   ├── filters/
│   │   │   └── http-exception.filter.ts
│   │   ├── interceptors/
│   │   │   └── logging.interceptor.ts
│   │   └── pipes/
│   │       └── validation.pipe.ts
│   ├── modules/
│   │   ├── restaurante/
│   │   │   ├── restaurante.module.ts
│   │   │   ├── restaurante.controller.ts
│   │   │   ├── restaurante.service.ts
│   │   │   ├── entities/
│   │   │   │   └── restaurante.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-restaurante.dto.ts
│   │   │       └── update-restaurante.dto.ts
│   │   ├── avaliacao/
│   │   │   └── ...
│   │   └── upload/
│   │       └── ...
│   └── health/
│       └── health.controller.ts
├── uploads/                    # Arquivos de upload
├── .env
├── .env.example
├── nest-cli.json
├── tsconfig.json
└── package.json
```

### 4. Configuração de Variáveis de Ambiente

**Arquivo `src/config/env.validation.ts`:**

```typescript
import { plainToClass } from 'class-transformer';
import {
  IsEnum,
  IsNumber,
  IsString,
  validateSync,
} from 'class-validator';

enum Environment {
  Development = 'development',
  Production = 'production',
  Test = 'test',
}

class EnvironmentVariables {
  @IsEnum(Environment)
  NODE_ENV: Environment;

  @IsNumber()
  PORT: number;

  @IsString()
  DATABASE_HOST: string;

  @IsNumber()
  DATABASE_PORT: number;

  @IsString()
  DATABASE_USER: string;

  @IsString()
  DATABASE_PASSWORD: string;

  @IsString()
  DATABASE_NAME: string;

  @IsString()
  UPLOAD_DIR: string;

  @IsString()
  BASE_URL: string;
}

export function validate(config: Record<string, unknown>) {
  const validatedConfig = plainToClass(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });

  const errors = validateSync(validatedConfig, {
    skipMissingProperties: false,
  });

  if (errors.length > 0) {
    throw new Error(errors.toString());
  }

  return validatedConfig;
}
```

**Arquivo `.env.example`:**

```env
NODE_ENV=development
PORT=3000

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=senha123
DATABASE_NAME=tasterank_db

UPLOAD_DIR=./uploads
BASE_URL=http://localhost:3000
```

### 5. Configuração do TypeORM

**Arquivo `src/config/database.config.ts`:**

```typescript
import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import { ConfigService } from '@nestjs/config';

export const getDatabaseConfig = (
  configService: ConfigService,
): TypeOrmModuleOptions => ({
  type: 'postgres',
  host: configService.get('DATABASE_HOST'),
  port: configService.get('DATABASE_PORT'),
  username: configService.get('DATABASE_USER'),
  password: configService.get('DATABASE_PASSWORD'),
  database: configService.get('DATABASE_NAME'),
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  synchronize: configService.get('NODE_ENV') === 'development',
  logging: configService.get('NODE_ENV') === 'development',
  ssl:
    configService.get('NODE_ENV') === 'production'
      ? { rejectUnauthorized: false }
      : false,
});
```

### 6. Módulo Principal

**Arquivo `src/app.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThrottlerModule } from '@nestjs/throttler';
import { getDatabaseConfig } from './config/database.config';
import { validate } from './config/env.validation';
import { HealthController } from './health/health.controller';

@Module({
  imports: [
    // Configuração global
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
    }),

    // Banco de dados
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: getDatabaseConfig,
    }),

    // Rate limiting
    ThrottlerModule.forRoot([
      {
        ttl: 60000, // 1 minuto
        limit: 10,  // 10 requisições
      },
    ]),

    // Módulos da aplicação
    // RestauranteModule,
    // AvaliacaoModule,
    // UploadModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
```

### 7. Entry Point

**Arquivo `src/main.ts`:**

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import helmet from 'helmet';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const configService = app.get(ConfigService);
  const port = configService.get('PORT') || 3000;

  // Segurança
  app.use(helmet());

  // CORS
  app.enableCors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  });

  // Prefixo global
  app.setGlobalPrefix('api');

  // Pipes de validação
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,        // Remove propriedades não definidas no DTO
      forbidNonWhitelisted: true, // Retorna erro se propriedade extra
      transform: true,        // Transforma payload em instância do DTO
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // Filtros de exceção
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(port);
  console.log(`🚀 Servidor rodando em http://localhost:${port}`);
  console.log(`📚 API disponível em http://localhost:${port}/api`);
}
bootstrap();
```

### 8. Health Check

**Arquivo `src/health/health.controller.ts`:**

```typescript
import { Controller, Get } from '@nestjs/common';

@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    };
  }
}
```

### 9. Filtro de Exceções

**Arquivo `src/common/filters/http-exception.filter.ts`:**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Response } from 'express';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message: string | object = 'Erro interno do servidor';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      message =
        typeof exceptionResponse === 'object'
          ? exceptionResponse
          : { message: exceptionResponse };
    } else if (exception instanceof Error) {
      message = exception.message;
    }

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      ...(typeof message === 'object' ? message : { message }),
    });
  }
}
```

## 🔨 Atividade Prática

### Exercício 1: Iniciar o Projeto

1. Crie o arquivo `.env` baseado no `.env.example`
2. Ajuste as credenciais do PostgreSQL
3. Execute:
```bash
npm run start:dev
```

4. Acesse:
   - `http://localhost:3000/health`

Resposta esperada:
```json
{
  "status": "ok",
  "timestamp": "2025-12-07T10:30:00.000Z",
  "uptime": 5.123
}
```

### Exercício 2: Testar Validação de Env

1. Remova uma variável obrigatória do `.env`
2. Tente iniciar o servidor
3. Observe o erro de validação

## 💡 Conceitos-Chave

- **Módulos**: Organizam a aplicação em unidades coesas
- **Providers**: Injeção de dependências (services, repositories)
- **Controllers**: Roteamento e handlers de requisições
- **Pipes**: Validação e transformação de dados
- **Filters**: Tratamento de exceções
- **Guards**: Autenticação e autorização
- **Interceptors**: Logging, cache, transformação de resposta

## ➡️ Próximos Passos

No próximo tutorial:
- Criar entidades com TypeORM
- Implementar CRUD completo
- Usar DTOs com validação

## 📚 Recursos

- [NestJS Docs](https://docs.nestjs.com/)
- [TypeORM Docs](https://typeorm.io/)
- [Class Validator](https://github.com/typestack/class-validator)
