# Tutorial: CRUD Completo com NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar entidades com TypeORM e decorators
- Implementar DTOs com validação automática
- Desenvolver services com injeção de dependência
- Criar controllers RESTful completos
- Implementar paginação e filtros
- Tratar erros de forma consistente

## 📖 Conteúdo

### 1. Criando as Entidades

**Arquivo `src/modules/restaurante/entities/restaurante.entity.ts`:**

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
} from 'typeorm';
import { Avaliacao } from '../../avaliacao/entities/avaliacao.entity';

@Entity('restaurantes')
export class Restaurante {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  nome: string;

  @Column({ length: 50 })
  categoria: string;

  @Column({ type: 'text', nullable: true })
  endereco: string;

  @Column({ length: 20, nullable: true })
  telefone: string;

  @Column({ type: 'text', nullable: true })
  descricao: string;

  @Column({ default: true })
  ativo: boolean;

  @Column({ type: 'decimal', precision: 3, scale: 2, default: 0 })
  avaliacao_media: number;

  @Column({ length: 500, nullable: true })
  image_url: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  @OneToMany(() => Avaliacao, (avaliacao) => avaliacao.restaurante)
  avaliacoes: Avaliacao[];
}
```

**Arquivo `src/modules/avaliacao/entities/avaliacao.entity.ts`:**

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Restaurante } from '../../restaurante/entities/restaurante.entity';

@Entity('avaliacoes')
export class Avaliacao {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'int' })
  nota: number;

  @Column({ type: 'text', nullable: true })
  comentario: string;

  @Column({ length: 100, nullable: true })
  nome_avaliador: string;

  @Column()
  restaurante_id: number;

  @ManyToOne(() => Restaurante, (restaurante) => restaurante.avaliacoes, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'restaurante_id' })
  restaurante: Restaurante;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}
```

### 2. Criando os DTOs

**Arquivo `src/modules/restaurante/dto/create-restaurante.dto.ts`:**

```typescript
import {
  IsString,
  IsNotEmpty,
  IsOptional,
  IsEnum,
  Length,
  Matches,
  IsUrl,
} from 'class-validator';

enum Categoria {
  Italiana = 'Italiana',
  Japonesa = 'Japonesa',
  Brasileira = 'Brasileira',
  Mexicana = 'Mexicana',
  Arabe = 'Árabe',
  Hamburgueria = 'Hamburgueria',
  Pizzaria = 'Pizzaria',
  Vegetariana = 'Vegetariana',
  Outra = 'Outra',
}

export class CreateRestauranteDto {
  @IsString()
  @IsNotEmpty({ message: 'Nome é obrigatório' })
  @Length(3, 100, { message: 'Nome deve ter entre 3 e 100 caracteres' })
  nome: string;

  @IsEnum(Categoria, { message: 'Categoria inválida' })
  @IsNotEmpty({ message: 'Categoria é obrigatória' })
  categoria: string;

  @IsString()
  @IsOptional()
  endereco?: string;

  @IsString()
  @IsOptional()
  @Matches(/^[\d\s\(\)\-\+]+$/, { message: 'Telefone inválido' })
  telefone?: string;

  @IsString()
  @IsOptional()
  @Length(0, 500, { message: 'Descrição muito longa' })
  descricao?: string;

  @IsUrl({}, { message: 'URL da imagem inválida' })
  @IsOptional()
  image_url?: string;
}
```

**Arquivo `src/modules/restaurante/dto/update-restaurante.dto.ts`:**

```typescript
import { PartialType } from '@nestjs/mapped-types';
import { CreateRestauranteDto } from './create-restaurante.dto';

export class UpdateRestauranteDto extends PartialType(CreateRestauranteDto) {}
```

**Arquivo `src/modules/restaurante/dto/query-restaurante.dto.ts`:**

```typescript
import { IsOptional, IsString, IsInt, Min, Max } from 'class-validator';
import { Type } from 'class-transformer';

export class QueryRestauranteDto {
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page?: number = 1;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 10;

  @IsOptional()
  @IsString()
  categoria?: string;

  @IsOptional()
  @IsString()
  busca?: string;

  @IsOptional()
  @IsString()
  ordenar?: string = 'avaliacao_media';

  @IsOptional()
  @IsString()
  direcao?: 'ASC' | 'DESC' = 'DESC';
}
```

**Arquivo `src/modules/avaliacao/dto/create-avaliacao.dto.ts`:**

```typescript
import { IsInt, IsString, IsOptional, Min, Max, Length } from 'class-validator';

export class CreateAvaliacaoDto {
  @IsInt({ message: 'Nota deve ser um número inteiro' })
  @Min(1, { message: 'Nota mínima é 1' })
  @Max(5, { message: 'Nota máxima é 5' })
  nota: number;

  @IsString()
  @IsOptional()
  @Length(0, 500, { message: 'Comentário muito longo' })
  comentario?: string;

  @IsString()
  @IsOptional()
  @Length(0, 100, { message: 'Nome muito longo' })
  nome_avaliador?: string;
}
```

### 3. Implementando o Service

**Arquivo `src/modules/restaurante/restaurante.service.ts`:**

```typescript
import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like } from 'typeorm';
import { Restaurante } from './entities/restaurante.entity';
import { CreateRestauranteDto } from './dto/create-restaurante.dto';
import { UpdateRestauranteDto } from './dto/update-restaurante.dto';
import { QueryRestauranteDto } from './dto/query-restaurante.dto';

@Injectable()
export class RestauranteService {
  constructor(
    @InjectRepository(Restaurante)
    private readonly restauranteRepository: Repository<Restaurante>,
  ) {}

  async create(createRestauranteDto: CreateRestauranteDto): Promise<Restaurante> {
    const restaurante = this.restauranteRepository.create(createRestauranteDto);
    return await this.restauranteRepository.save(restaurante);
  }

  async findAll(query: QueryRestauranteDto) {
    const { page, limit, categoria, busca, ordenar, direcao } = query;
    
    const skip = (page - 1) * limit;

    const where: any = { ativo: true };

    if (categoria) {
      where.categoria = categoria;
    }

    if (busca) {
      where.nome = Like(`%${busca}%`);
    }

    const [restaurantes, total] = await this.restauranteRepository.findAndCount({
      where,
      skip,
      take: limit,
      order: {
        [ordenar]: direcao,
      },
    });

    return {
      data: restaurantes,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: number): Promise<Restaurante> {
    const restaurante = await this.restauranteRepository.findOne({
      where: { id },
      relations: ['avaliacoes'],
    });

    if (!restaurante) {
      throw new NotFoundException(`Restaurante com ID ${id} não encontrado`);
    }

    return restaurante;
  }

  async update(
    id: number,
    updateRestauranteDto: UpdateRestauranteDto,
  ): Promise<Restaurante> {
    const restaurante = await this.findOne(id);

    Object.assign(restaurante, updateRestauranteDto);

    return await this.restauranteRepository.save(restaurante);
  }

  async remove(id: number): Promise<void> {
    const restaurante = await this.findOne(id);
    
    // Soft delete
    restaurante.ativo = false;
    await this.restauranteRepository.save(restaurante);
  }

  async calcularMedia(id: number): Promise<void> {
    const result = await this.restauranteRepository
      .createQueryBuilder('r')
      .leftJoin('r.avaliacoes', 'a')
      .select('AVG(a.nota)', 'media')
      .where('r.id = :id', { id })
      .getRawOne();

    const media = result.media ? parseFloat(result.media) : 0;

    await this.restauranteRepository.update(id, {
      avaliacao_media: media,
    });
  }
}
```

**Arquivo `src/modules/avaliacao/avaliacao.service.ts`:**

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Avaliacao } from './entities/avaliacao.entity';
import { CreateAvaliacaoDto } from './dto/create-avaliacao.dto';
import { RestauranteService } from '../restaurante/restaurante.service';

@Injectable()
export class AvaliacaoService {
  constructor(
    @InjectRepository(Avaliacao)
    private readonly avaliacaoRepository: Repository<Avaliacao>,
    private readonly restauranteService: RestauranteService,
  ) {}

  async create(
    restauranteId: number,
    createAvaliacaoDto: CreateAvaliacaoDto,
  ): Promise<Avaliacao> {
    // Verificar se restaurante existe
    await this.restauranteService.findOne(restauranteId);

    const avaliacao = this.avaliacaoRepository.create({
      ...createAvaliacaoDto,
      restaurante_id: restauranteId,
    });

    const saved = await this.avaliacaoRepository.save(avaliacao);

    // Recalcular média
    await this.restauranteService.calcularMedia(restauranteId);

    return saved;
  }

  async findByRestaurante(restauranteId: number): Promise<Avaliacao[]> {
    return await this.avaliacaoRepository.find({
      where: { restaurante_id: restauranteId },
      order: { created_at: 'DESC' },
    });
  }

  async findOne(id: number): Promise<Avaliacao> {
    const avaliacao = await this.avaliacaoRepository.findOne({
      where: { id },
    });

    if (!avaliacao) {
      throw new NotFoundException(`Avaliação com ID ${id} não encontrada`);
    }

    return avaliacao;
  }

  async remove(id: number): Promise<void> {
    const avaliacao = await this.findOne(id);
    await this.avaliacaoRepository.remove(avaliacao);
    
    // Recalcular média
    await this.restauranteService.calcularMedia(avaliacao.restaurante_id);
  }
}
```

### 4. Criando os Controllers

**Arquivo `src/modules/restaurante/restaurante.controller.ts`:**

```typescript
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  ParseIntPipe,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { RestauranteService } from './restaurante.service';
import { CreateRestauranteDto } from './dto/create-restaurante.dto';
import { UpdateRestauranteDto } from './dto/update-restaurante.dto';
import { QueryRestauranteDto } from './dto/query-restaurante.dto';

@Controller('restaurantes')
export class RestauranteController {
  constructor(private readonly restauranteService: RestauranteService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() createRestauranteDto: CreateRestauranteDto) {
    const restaurante = await this.restauranteService.create(createRestauranteDto);
    return {
      mensagem: 'Restaurante criado com sucesso',
      restaurante,
    };
  }

  @Get()
  async findAll(@Query() query: QueryRestauranteDto) {
    return await this.restauranteService.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number) {
    return await this.restauranteService.findOne(id);
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateRestauranteDto: UpdateRestauranteDto,
  ) {
    const restaurante = await this.restauranteService.update(id, updateRestauranteDto);
    return {
      mensagem: 'Restaurante atualizado com sucesso',
      restaurante,
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('id', ParseIntPipe) id: number) {
    await this.restauranteService.remove(id);
  }
}
```

**Arquivo `src/modules/avaliacao/avaliacao.controller.ts`:**

```typescript
import {
  Controller,
  Get,
  Post,
  Delete,
  Body,
  Param,
  ParseIntPipe,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { AvaliacaoService } from './avaliacao.service';
import { CreateAvaliacaoDto } from './dto/create-avaliacao.dto';

@Controller('restaurantes/:restauranteId/avaliacoes')
export class AvaliacaoController {
  constructor(private readonly avaliacaoService: AvaliacaoService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(
    @Param('restauranteId', ParseIntPipe) restauranteId: number,
    @Body() createAvaliacaoDto: CreateAvaliacaoDto,
  ) {
    const avaliacao = await this.avaliacaoService.create(
      restauranteId,
      createAvaliacaoDto,
    );
    return {
      mensagem: 'Avaliação criada com sucesso',
      avaliacao,
    };
  }

  @Get()
  async findAll(@Param('restauranteId', ParseIntPipe) restauranteId: number) {
    return await this.avaliacaoService.findByRestaurante(restauranteId);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('id', ParseIntPipe) id: number) {
    await this.avaliacaoService.remove(id);
  }
}
```

### 5. Criando os Módulos

**Arquivo `src/modules/restaurante/restaurante.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RestauranteController } from './restaurante.controller';
import { RestauranteService } from './restaurante.service';
import { Restaurante } from './entities/restaurante.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Restaurante])],
  controllers: [RestauranteController],
  providers: [RestauranteService],
  exports: [RestauranteService],
})
export class RestauranteModule {}
```

**Arquivo `src/modules/avaliacao/avaliacao.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AvaliacaoController } from './avaliacao.controller';
import { AvaliacaoService } from './avaliacao.service';
import { Avaliacao } from './entities/avaliacao.entity';
import { RestauranteModule } from '../restaurante/restaurante.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([Avaliacao]),
    RestauranteModule,
  ],
  controllers: [AvaliacaoController],
  providers: [AvaliacaoService],
})
export class AvaliacaoModule {}
```

### 6. Atualizar AppModule

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThrottlerModule } from '@nestjs/throttler';
import { getDatabaseConfig } from './config/database.config';
import { validate } from './config/env.validation';
import { HealthController } from './health/health.controller';
import { RestauranteModule } from './modules/restaurante/restaurante.module';
import { AvaliacaoModule } from './modules/avaliacao/avaliacao.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
    }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: getDatabaseConfig,
    }),
    ThrottlerModule.forRoot([
      {
        ttl: 60000,
        limit: 10,
      },
    ]),
    RestauranteModule,
    AvaliacaoModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
```

## 🔨 Atividade Prática

### Exercício 1: Testar Endpoints

```bash
# Iniciar servidor
npm run start:dev
```

**Crie o arquivo `tests/api-tests.http` no VS Code:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api

### Criar restaurante
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "endereco": "Rua X, 123"
}

### Listar restaurantes com filtros
GET {{baseUrl}}/restaurantes?categoria=Italiana&page=1&limit=10

### Obter restaurante por ID
GET {{baseUrl}}/restaurantes/1

### Atualizar restaurante
PUT {{baseUrl}}/restaurantes/1
Content-Type: application/json

{
  "telefone": "(11) 1234-5678",
  "descricao": "Melhor pizza da cidade!"
}

### Adicionar avaliação
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Excelente!",
  "nome_avaliador": "João"
}

### Listar avaliações do restaurante
GET {{baseUrl}}/restaurantes/1/avaliacoes

### Deletar restaurante (soft delete)
DELETE {{baseUrl}}/restaurantes/1
```

**💡 Instale a extensão:** REST Client no VS Code

### Exercício 2: Adicionar Busca Avançada

Implemente busca que considere nome E descrição.

### Exercício 3: Soft Delete Completo

Adicione campo `deleted_at` e implemente soft delete real.

## 💡 Conceitos-Chave

- **DTOs**: Data Transfer Objects para validação
- **Entities**: Mapeamento objeto-relacional
- **Decorators**: Metadados para validação e ORM
- **Dependency Injection**: Inversão de controle
- **Repository Pattern**: Abstração de acesso a dados

## ➡️ Próximos Passos

No próximo tutorial:
- Upload de imagens com validação
- Servir arquivos estáticos
- Integração com storage

## 📚 Recursos

- [TypeORM Relations](https://typeorm.io/relations)
- [Class Validator Decorators](https://github.com/typestack/class-validator#validation-decorators)
- [NestJS CRUD](https://docs.nestjs.com/techniques/database)
