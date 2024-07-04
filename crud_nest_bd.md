Para adicionar persistência em banco de dados à nossa aplicação CRUD com NestJS, vamos usar o TypeORM com um banco de dados PostgreSQL. 

### Passo 1: Instalar Dependências

Primeiro, instale as dependências necessárias:

```bash
npm install @nestjs/typeorm typeorm pg
```

### Passo 2: Configurar o Banco de Dados

No arquivo `app.module.ts`, configure a conexão com o banco de dados:

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersModule } from './users/users.module';
import { User } from './users/user.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: 'localhost',
      port: 5432,
      username: 'your_username',
      password: 'your_password',
      database: 'your_database',
      entities: [User],
      synchronize: true,
    }),
    UsersModule,
  ],
})
export class AppModule {}
```

### Passo 3: Atualizar a Entidade

Atualize a entidade `User` para ser uma entidade TypeORM:

```typescript
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column()
  age: number;

  @Column()
  email: string;
}
```

### Passo 4: Atualizar o Módulo de Usuários

Atualize o módulo `UsersModule` para importar o `TypeOrmModule`:

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { User } from './user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  providers: [UsersService],
  controllers: [UsersController],
})
export class UsersModule {}
```

### Passo 5: Atualizar o Serviço de Usuários

Atualize o serviço `UsersService` para usar o repositório TypeORM:

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  findAll(): Promise<User[]> {
    return this.usersRepository.find();
  }

  findOne(id: number): Promise<User> {
    return this.usersRepository.findOne(id);
  }

  async create(user: User): Promise<void> {
    await this.usersRepository.save(user);
  }

  async update(id: number, updatedUser: User): Promise<void> {
    await this.usersRepository.update(id, updatedUser);
  }

  async remove(id: number): Promise<void> {
    await this.usersRepository.delete(id);
  }
}
```

### Passo 6: Iniciar a Aplicação

Certifique-se de que o PostgreSQL está em execução e que você tem o banco de dados configurado corretamente. Em seguida, inicie a aplicação:

```bash
npm run start
```

### Conclusão

Agora você tem uma aplicação NestJS CRUD com persistência de dados usando TypeORM e PostgreSQL. Isso adiciona uma camada de persistência ao seu aplicativo, permitindo que os dados sejam salvos e recuperados de um banco de dados real. Para uma aplicação em produção, considere desativar a sincronização automática (`synchronize: false`) e usar migrações para gerenciar alterações no esquema do banco de dados.