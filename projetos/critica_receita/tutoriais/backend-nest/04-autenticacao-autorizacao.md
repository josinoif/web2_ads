# Tutorial: Autenticação e Autorização com NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar registro e login com JWT
- Criar estratégias de autenticação com Passport
- Proteger rotas com Guards
- Implementar autorização baseada em roles
- Gerenciar refresh tokens
- Criar decorators customizados

## 📖 Conteúdo

### 1. Instalando Dependências

```bash
npm install @nestjs/jwt @nestjs/passport passport passport-jwt
npm install bcrypt
npm install --save-dev @types/passport-jwt @types/bcrypt
```

### 2. Criando a Entidade User

**Arquivo `src/modules/user/entities/user.entity.ts`:**

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  nome: string;

  @Column({ unique: true, length: 255 })
  email: string;

  @Column()
  password: string;

  @Column({
    type: 'enum',
    enum: UserRole,
    default: UserRole.USER,
  })
  role: UserRole;

  @Column({ default: true })
  ativo: boolean;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}
```

### 3. Criando DTOs de Autenticação

**Arquivo `src/modules/auth/dto/register.dto.ts`:**

```typescript
import {
  IsEmail,
  IsString,
  MinLength,
  MaxLength,
  Matches,
} from 'class-validator';

export class RegisterDto {
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  nome: string;

  @IsEmail({}, { message: 'Email inválido' })
  email: string;

  @IsString()
  @MinLength(8, { message: 'Senha deve ter no mínimo 8 caracteres' })
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: 'Senha deve conter letra maiúscula, minúscula e número',
  })
  password: string;
}
```

**Arquivo `src/modules/auth/dto/login.dto.ts`:**

```typescript
import { IsEmail, IsString } from 'class-validator';

export class LoginDto {
  @IsEmail({}, { message: 'Email inválido' })
  email: string;

  @IsString()
  password: string;
}
```

### 4. Criando o User Service

**Arquivo `src/modules/user/user.service.ts`:**

```typescript
import {
  Injectable,
  ConflictException,
  NotFoundException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User } from './entities/user.entity';
import { RegisterDto } from '../auth/dto/register.dto';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async create(registerDto: RegisterDto): Promise<User> {
    const existing = await this.userRepository.findOne({
      where: { email: registerDto.email },
    });

    if (existing) {
      throw new ConflictException('Email já cadastrado');
    }

    const hashedPassword = await bcrypt.hash(registerDto.password, 12);

    const user = this.userRepository.create({
      ...registerDto,
      password: hashedPassword,
    });

    return await this.userRepository.save(user);
  }

  async findByEmail(email: string): Promise<User | null> {
    return await this.userRepository.findOne({ where: { email } });
  }

  async findById(id: number): Promise<User> {
    const user = await this.userRepository.findOne({ where: { id } });

    if (!user) {
      throw new NotFoundException('Usuário não encontrado');
    }

    return user;
  }

  async validatePassword(
    plainPassword: string,
    hashedPassword: string,
  ): Promise<boolean> {
    return await bcrypt.compare(plainPassword, hashedPassword);
  }
}
```

### 5. Criando o Auth Service

**Arquivo `src/modules/auth/auth.service.ts`:**

```typescript
import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UserService } from '../user/user.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';

export interface JwtPayload {
  sub: number;
  email: string;
  role: string;
}

@Injectable()
export class AuthService {
  constructor(
    private readonly userService: UserService,
    private readonly jwtService: JwtService,
  ) {}

  async register(registerDto: RegisterDto) {
    const user = await this.userService.create(registerDto);

    const token = this.generateToken({
      sub: user.id,
      email: user.email,
      role: user.role,
    });

    return {
      mensagem: 'Usuário registrado com sucesso',
      user: {
        id: user.id,
        nome: user.nome,
        email: user.email,
        role: user.role,
      },
      access_token: token,
    };
  }

  async login(loginDto: LoginDto) {
    const user = await this.userService.findByEmail(loginDto.email);

    if (!user || !user.ativo) {
      throw new UnauthorizedException('Credenciais inválidas');
    }

    const isPasswordValid = await this.userService.validatePassword(
      loginDto.password,
      user.password,
    );

    if (!isPasswordValid) {
      throw new UnauthorizedException('Credenciais inválidas');
    }

    const token = this.generateToken({
      sub: user.id,
      email: user.email,
      role: user.role,
    });

    return {
      user: {
        id: user.id,
        nome: user.nome,
        email: user.email,
        role: user.role,
      },
      access_token: token,
    };
  }

  async validateUser(payload: JwtPayload) {
    const user = await this.userService.findById(payload.sub);

    if (!user || !user.ativo) {
      throw new UnauthorizedException('Usuário inválido');
    }

    return user;
  }

  private generateToken(payload: JwtPayload): string {
    return this.jwtService.sign(payload);
  }
}
```

### 6. Criando a JWT Strategy

**Arquivo `src/modules/auth/strategies/jwt.strategy.ts`:**

```typescript
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { AuthService, JwtPayload } from '../auth.service';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    private readonly authService: AuthService,
    private readonly configService: ConfigService,
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: configService.get('JWT_SECRET'),
    });
  }

  async validate(payload: JwtPayload) {
    const user = await this.authService.validateUser(payload);
    return user;
  }
}
```

### 7. Criando Guards

**Arquivo `src/modules/auth/guards/jwt-auth.guard.ts`:**

```typescript
import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
```

**Arquivo `src/modules/auth/guards/roles.guard.ts`:**

```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { UserRole } from '../../user/entities/user.entity';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>('roles', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles) {
      return true;
    }

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user.role === role);
  }
}
```

### 8. Criando Decorators

**Arquivo `src/modules/auth/decorators/current-user.decorator.ts`:**

```typescript
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.user;
  },
);
```

**Arquivo `src/modules/auth/decorators/roles.decorator.ts`:**

```typescript
import { SetMetadata } from '@nestjs/common';
import { UserRole } from '../../user/entities/user.entity';

export const Roles = (...roles: UserRole[]) => SetMetadata('roles', roles);
```

**Arquivo `src/modules/auth/decorators/public.decorator.ts`:**

```typescript
import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

### 9. Criando o Auth Controller

**Arquivo `src/modules/auth/auth.controller.ts`:**

```typescript
import {
  Controller,
  Post,
  Body,
  Get,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { CurrentUser } from './decorators/current-user.decorator';
import { User } from '../user/entities/user.entity';
import { Public } from './decorators/public.decorator';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Public()
  @Post('register')
  async register(@Body() registerDto: RegisterDto) {
    return await this.authService.register(registerDto);
  }

  @Public()
  @Post('login')
  @HttpCode(HttpStatus.OK)
  async login(@Body() loginDto: LoginDto) {
    return await this.authService.login(loginDto);
  }

  @Get('me')
  @UseGuards(JwtAuthGuard)
  async getProfile(@CurrentUser() user: User) {
    return {
      id: user.id,
      nome: user.nome,
      email: user.email,
      role: user.role,
    };
  }
}
```

### 10. Configurando Módulos

**Arquivo `src/modules/auth/auth.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { JwtStrategy } from './strategies/jwt.strategy';
import { UserModule } from '../user/user.module';

@Module({
  imports: [
    UserModule,
    PassportModule,
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        secret: configService.get('JWT_SECRET'),
        signOptions: {
          expiresIn: '24h',
        },
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, JwtStrategy],
  exports: [AuthService],
})
export class AuthModule {}
```

**Arquivo `src/modules/user/user.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserService } from './user.service';
import { User } from './entities/user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  providers: [UserService],
  exports: [UserService],
})
export class UserModule {}
```

### 11. Protegendo Rotas

**Atualizar `src/modules/restaurante/restaurante.controller.ts`:**

```typescript
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  UseGuards,
} from '@nestjs/common';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import { UserRole, User } from '../user/entities/user.entity';
import { Public } from '../auth/decorators/public.decorator';

@Controller('restaurantes')
@UseGuards(JwtAuthGuard, RolesGuard)
export class RestauranteController {
  // GET - Público
  @Public()
  @Get()
  async findAll() {
    // ...
  }

  @Public()
  @Get(':id')
  async findOne() {
    // ...
  }

  // POST - Apenas autenticados
  @Post()
  async create(@CurrentUser() user: User, @Body() dto: any) {
    // ...
  }

  // PUT - Apenas admin ou dono
  @Put(':id')
  @Roles(UserRole.ADMIN)
  async update() {
    // ...
  }

  // DELETE - Apenas admin
  @Delete(':id')
  @Roles(UserRole.ADMIN)
  async remove() {
    // ...
  }

  // Upload - Autenticado
  @Post(':id/image')
  async uploadImage(@CurrentUser() user: User) {
    // ...
  }
}
```

### 12. Variáveis de Ambiente

Adicionar ao `.env`:

```env
JWT_SECRET=sua_chave_secreta_muito_segura_com_minimo_32_caracteres
JWT_EXPIRES_IN=24h
```

Atualizar validação:

```typescript
// src/config/env.validation.ts
class EnvironmentVariables {
  // ... outras variáveis ...

  @IsString()
  @MinLength(32)
  JWT_SECRET: string;

  @IsString()
  JWT_EXPIRES_IN: string;
}
```

## 🔨 Atividade Prática

### Exercício 1: Testar Autenticação

**Crie o arquivo `tests/auth-tests.http` no VS Code:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api
# Após login, copie o token aqui:
@token = seu_token_jwt_aqui

### Registrar usuário
POST {{baseUrl}}/auth/register
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "password": "Senha123"
}

### Login
POST {{baseUrl}}/auth/login
Content-Type: application/json

{
  "email": "joao@email.com",
  "password": "Senha123"
}

### Obter perfil (copie o token da resposta de login)
GET {{baseUrl}}/auth/me
Authorization: Bearer {{token}}

### Criar restaurante (com autenticação)
POST {{baseUrl}}/restaurantes
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "nome": "Restaurante Teste",
  "categoria": "Brasileira"
}

### Tentar acessar sem token (deve retornar 401)
GET {{baseUrl}}/auth/me
```

### Exercício 2: Implementar Refresh Token

Adicione refresh token com expiração maior.

### Exercício 3: Rate Limiting em Login

Limite tentativas de login por IP.

## 💡 Conceitos-Chave

- **JWT**: JSON Web Token para autenticação stateless
- **Passport**: Middleware de autenticação
- **Guards**: Proteção de rotas
- **Decorators**: Metadados e injeção customizada
- **Roles**: Autorização baseada em papéis

## ➡️ Próximos Passos

- Implementar recuperação de senha
- OAuth2 com Google/Facebook
- Two-factor authentication

## 📚 Recursos

- [NestJS Authentication](https://docs.nestjs.com/security/authentication)
- [Passport JWT](http://www.passportjs.org/packages/passport-jwt/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
