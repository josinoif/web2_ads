# Tutorial: CORS e Segurança no NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Configurar CORS corretamente no NestJS
- Implementar rate limiting com Throttler
- Adicionar headers de segurança com Helmet
- Implementar validação global de pipes
- Proteger contra ataques comuns (XSS, CSRF, etc)
- Configurar diferentes ambientes (dev/prod)

## 📖 Conteúdo

### 1. Instalação de Dependências

```bash
npm install @nestjs/throttler helmet
npm install --save-dev @types/express
```

**Atualizar `package.json`:**

```json
{
  "dependencies": {
    "@nestjs/throttler": "^5.0.1",
    "helmet": "^7.1.0"
  }
}
```

### 2. Configuração de CORS

**Atualizar `src/main.ts`:**

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import helmet from 'helmet';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);

  // Prefixo global para todas as rotas
  app.setGlobalPrefix('api');

  // CORS - Configuração por ambiente
  const corsOptions = {
    origin: configService.get('NODE_ENV') === 'production'
      ? [
          'https://tasterank.com',
          'https://www.tasterank.com',
        ]
      : [
          'http://localhost:3000',
          'http://localhost:5173',
          'http://localhost:4200',
        ],
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept',
    ],
    exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
    credentials: true,
    maxAge: 3600, // 1 hora de cache para preflight
  };

  app.enableCors(corsOptions);

  // Headers de segurança com Helmet
  app.use(helmet({
    contentSecurityPolicy: configService.get('NODE_ENV') === 'production' ? undefined : false,
    crossOriginEmbedderPolicy: false,
  }));

  // Validação global
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // Remove propriedades não definidas no DTO
      forbidNonWhitelisted: true, // Lança erro se propriedade extra for enviada
      transform: true, // Transforma tipos automaticamente
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  const port = configService.get('PORT') || 3000;
  await app.listen(port);
  
  console.log(`🚀 Application is running on: http://localhost:${port}/api`);
}

bootstrap();
```

### 3. Implementar Rate Limiting (Throttler)

**Atualizar `src/app.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import { getDatabaseConfig } from './config/database.config';
import { RestauranteModule } from './modules/restaurante/restaurante.module';
import { AvaliacaoModule } from './modules/avaliacao/avaliacao.module';
import { AuthModule } from './modules/auth/auth.module';

@Module({
  imports: [
    // Config
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),

    // Database
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: getDatabaseConfig,
      inject: [ConfigService],
    }),

    // Rate Limiting
    ThrottlerModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        throttlers: [
          {
            ttl: config.get('THROTTLE_TTL') || 60000, // 1 minuto
            limit: config.get('THROTTLE_LIMIT') || 100, // 100 requisições
          },
        ],
      }),
    }),

    // Modules
    RestauranteModule,
    AvaliacaoModule,
    AuthModule,
  ],
  providers: [
    // Aplicar rate limiting globalmente
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
```

### 4. Configurar Rate Limits Customizados

**Arquivo `src/decorators/throttle-custom.decorator.ts`:**

```typescript
import { SetMetadata } from '@nestjs/common';

export const THROTTLE_SKIP = 'throttle_skip';
export const SkipThrottle = () => SetMetadata(THROTTLE_SKIP, true);

export const CUSTOM_THROTTLE = 'custom_throttle';
export const CustomThrottle = (ttl: number, limit: number) =>
  SetMetadata(CUSTOM_THROTTLE, { ttl, limit });
```

**Aplicar em rotas específicas:**

```typescript
import { Controller, Post, UseGuards } from '@nestjs/common';
import { ThrottlerGuard } from '@nestjs/throttler';
import { Throttle } from '@nestjs/throttler';
import { SkipThrottle } from '../../decorators/throttle-custom.decorator';

@Controller('auth')
export class AuthController {
  // Login: limite mais rigoroso
  @Post('login')
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 tentativas por minuto
  async login() {
    // ...
  }

  // Register: limite moderado
  @Post('register')
  @Throttle({ default: { limit: 3, ttl: 3600000 } }) // 3 por hora
  async register() {
    // ...
  }

  // Public endpoint: sem limite
  @Get('public')
  @SkipThrottle()
  async getPublicData() {
    // ...
  }
}
```

### 5. Headers de Segurança Customizados

**Arquivo `src/middleware/security-headers.middleware.ts`:**

```typescript
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class SecurityHeadersMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    // Prevenir clickjacking
    res.setHeader('X-Frame-Options', 'DENY');
    
    // Prevenir MIME type sniffing
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // XSS Protection
    res.setHeader('X-XSS-Protection', '1; mode=block');
    
    // Strict Transport Security (apenas em HTTPS)
    if (req.secure) {
      res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    }
    
    // Referrer Policy
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    // Permissions Policy
    res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

    next();
  }
}
```

**Registrar middleware em `app.module.ts`:**

```typescript
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { SecurityHeadersMiddleware } from './middleware/security-headers.middleware';

@Module({
  // ... imports e providers
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(SecurityHeadersMiddleware)
      .forRoutes('*'); // Aplicar em todas as rotas
  }
}
```

### 6. Variáveis de Ambiente para Segurança

**Atualizar `.env`:**

```env
# Server
NODE_ENV=development
PORT=3000

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=senha
DATABASE_NAME=critica_receita

# JWT
JWT_SECRET=sua-chave-secreta-muito-forte-min-32-caracteres
JWT_EXPIRES_IN=1d

# Rate Limiting
THROTTLE_TTL=60000
THROTTLE_LIMIT=100

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 7. Validação de Ambiente

**Arquivo `src/config/env.validation.ts`:**

```typescript
import { plainToInstance } from 'class-transformer';
import {
  IsEnum,
  IsNumber,
  IsString,
  MinLength,
  validateSync,
  Min,
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
  @Min(1)
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
  @MinLength(32)
  JWT_SECRET: string;

  @IsString()
  JWT_EXPIRES_IN: string;

  @IsNumber()
  THROTTLE_TTL: number;

  @IsNumber()
  THROTTLE_LIMIT: number;
}

export function validate(config: Record<string, unknown>) {
  const validatedConfig = plainToInstance(EnvironmentVariables, config, {
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

**Aplicar validação em `app.module.ts`:**

```typescript
import { validate } from './config/env.validation';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
      validate, // Validar variáveis ao iniciar
    }),
    // ...
  ],
})
```

## 🔨 Atividade Prática

### Exercício 1: Testar CORS

**Crie `tests/cors-test.html`:**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Teste CORS</title>
</head>
<body>
  <h1>Teste de CORS</h1>
  <button onclick="testCors()">Testar Requisição</button>
  <pre id="result"></pre>

  <script>
    async function testCors() {
      try {
        const response = await fetch('http://localhost:3000/api/restaurantes');
        const data = await response.json();
        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
      } catch (error) {
        document.getElementById('result').textContent = 'Erro: ' + error.message;
      }
    }
  </script>
</body>
</html>
```

Abra o arquivo no navegador e teste.

### Exercício 2: Testar Rate Limiting

**Arquivo `tests/rate-limit-test.http`:**

```http
### Teste rate limiting - Execute várias vezes rapidamente

### Requisição 1
GET http://localhost:3000/api/restaurantes

### Requisição 2
GET http://localhost:3000/api/restaurantes

### Requisição 3
GET http://localhost:3000/api/restaurantes

### Requisição 4
GET http://localhost:3000/api/restaurantes

### Requisição 5
GET http://localhost:3000/api/restaurantes

# Continue até receber 429 Too Many Requests
```

### Exercício 3: Verificar Headers de Segurança

```bash
# Verificar headers com curl
curl -I http://localhost:3000/api/restaurantes

# Deve retornar:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
```

## 💡 Conceitos-Chave

- **CORS**: Cross-Origin Resource Sharing para permitir requisições entre domínios
- **Rate Limiting**: Limitar número de requisições por período
- **Helmet**: Middleware para headers de segurança
- **Throttler**: Sistema de rate limiting do NestJS
- **ValidationPipe**: Validação automática de entrada
- **Environment Variables**: Configuração por ambiente

## 🛡️ Boas Práticas

1. **CORS**:
   - Liste domínios permitidos explicitamente em produção
   - Nunca use `origin: '*'` em produção
   - Configure credenciais corretamente

2. **Rate Limiting**:
   - Limites mais rigorosos para auth (login/register)
   - Limites moderados para escrita (POST/PUT/DELETE)
   - Limites flexíveis para leitura (GET)

3. **Headers de Segurança**:
   - Use HTTPS em produção
   - Configure CSP (Content Security Policy)
   - Implemente HSTS

4. **Validação**:
   - Valide todas as entradas
   - Use whitelist para DTOs
   - Sanitize dados antes de usar

5. **Secrets**:
   - Nunca commite .env
   - Use secrets managers em produção
   - Rotacione chaves periodicamente

## ➡️ Próximos Passos

No próximo tutorial:
- Cálculo automático de médias
- Hooks do TypeORM
- Agregações e estatísticas

## 📚 Recursos

- [NestJS CORS](https://docs.nestjs.com/security/cors)
- [NestJS Rate Limiting](https://docs.nestjs.com/security/rate-limiting)
- [Helmet.js](https://helmetjs.github.io/)
- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/)
