Para adicionar persistência em banco de dados à nossa aplicação CRUD com NestJS, vamos usar o TypeORM com um banco de dados PostgreSQL. 


### Passo 1: Configurar o MySQL usando Docker

1. Certifique-se de que o Docker está instalado e em execução na sua máquina.

2. Execute o seguinte comando para baixar a imagem do MySQL e iniciar um contêiner:

```bash
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=aula_web2 -p 3306:3306 -d mysql:latest
```

3. Acesse o container do MySQL:

```bash
docker exec -it mysql-container mysql -u root -p
```
Isso abrirá o terminal MySQL dentro do container e pedirá a senha de root que você definiu (neste caso, `root`).

### Passo 2: Instalar Dependências

## 1. Instalar o Node.js

Certifique-se de ter o Node.js instalado na sua máquina. Você pode baixar a última versão do [site oficial do Node.js](https://nodejs.org/).

## 2. Instalar o Nest CLI

O Nest CLI facilita a criação e o gerenciamento de projetos NestJS. Para instalá-lo, execute o seguinte comando no seu terminal:

```bash
npm install -g @nestjs/cli
```

## 3. Criar um novo projeto
Use o Nest CLI para criar um novo projeto. No terminal, execute:

```bash
nest new projeto-nest
```

## 4. Navegar até o diretório do projeto
Após a criação do projeto, navegue até o diretório do projeto:

```bash
cd projeto-nest
```

## 5. Iniciar o servidor de desenvolvimento
Para iniciar o servidor de desenvolvimento, execute:

```bash 
npm run start:dev
```

## 6. Estrutura do projeto

A estrutura básica do projeto NestJS inclui:
- `src/` - Diretório principal do código-fonte.
- `main.ts` - O ponto de entrada da aplicação.
- `app.module.ts` - O módulo raiz da aplicação.
- `app.controller.ts` e `app.service.ts` - Exemplos de controlador e serviço.

## 7. Estrutura de Components no NestJS

### Services

Os `services` em NestJS são responsáveis por implementar a lógica de negócio da aplicação. Eles são usados para abstrair e encapsular a lógica de processamento de dados e interações com bancos de dados ou APIs externas.

### Controllers

Os `controllers` são responsáveis por lidar com as requisições HTTP e retornar respostas ao cliente. Eles recebem as requisições, delegam a lógica de negócio aos `services` e retornam as respostas apropriadas.

### Modules

Os `modules` são usados para organizar o código da aplicação em partes coesas e reutilizáveis. Cada `module` pode conter `controllers`, `services` e outros `modules`. Eles são a estrutura básica de organização e encapsulamento no NestJS.


## 8. Exemplo Básico

Criando um módulo de usuários
```bash
nest generate module users
```

Criando um controlador de usuários
```bash
nest generate controller users
```

Criando um serviço de usuários
```bash
nest generate service users
```

Exemplo do código do UserService

```typescript
// src/users/users.service.ts
import { Injectable } from '@nestjs/common';

@Injectable()
export class UsersService {
  private readonly users = ['user1', 'user2'];

  findAll(): string[] {
    return this.users;
  }
}
```

Exemplo de código do UserController

```typescript
// src/users/users.controller.ts
import { Controller, Get } from '@nestjs/common';
import { UsersService } from './users.service';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll() {
    return this.usersService.findAll();
  }
}
```

## Adicionando um Modelo de Dados com TypeORM no NestJS usando MySQL

### 1. Instalar as Dependências

Primeiro, você precisa instalar o TypeORM e o driver do MySQL:

```bash
npm install @nestjs/typeorm typeorm mysql2
```

### 2. Configurar o TypeORM
No arquivo `app.module.ts`, configure o TypeORM para se conectar ao banco de dados MySQL. Adicione o módulo TypeOrmModule e defina a configuração de conexão com o MySQL.

    
```typescript
// src/app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersModule } from './users/users.module';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'database',
      entities: [__dirname + '/**/*.entity{.ts,.js}'],
      synchronize: true, // Atenção: Use apenas em desenvolvimento
    }),
    UsersModule,
  ],
})
export class AppModule {}

```

### 3. Criar uma Entidade User
Crie uma nova entidade para o modelo `User`. Primeiro, crie um arquivo para a entidade dentro do diretório  `users`.

```typescript 
// src/users/user.entity.ts
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 100 })
  name: string;

  @Column({ type: 'varchar', length: 150, unique: true })
  email: string;

  @Column({ type: 'varchar', length: 255 })
  password: string;

  @Column({ type: 'date', nullable: true })
  birthDate?: Date;
}
```

### 4. Atualizar o Módulo Users

Certifique-se de que o módulo `UsersModule esteja configurado para usar o TypeORM e a nova entidade.

```typescript
// src/users/users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { User } from './user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
})
export class UsersModule {}

```

### 5. Atualizar o Serviço Users
O serviço `UsersService` deve ser atualizado para utilizar o repositório do TypeORM para manipular a entidade `User`.

```typescript
// src/users/users.service.ts
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

  async findAll(): Promise<User[]> {
    return this.usersRepository.find();
  }

  async findOne(id: number): Promise<User> {
    return this.usersRepository.findOneBy({ id });
  }

  async create(user: Partial<User>): Promise<User> {
    const newUser = this.usersRepository.create(user);
    return this.usersRepository.save(newUser);
  }

  async update(id: number, user: Partial<User>): Promise<User> {
    await this.usersRepository.update(id, user);
    return this.usersRepository.findOneBy({ id });
  }

  async remove(id: number): Promise<void> {
    await this.usersRepository.delete(id);
  }
}

```

### 6. Atualizar o Controlador Users

Atualize o controlador `UsersController` para usar o `UsersService` e manipular as requisições HTTP.

```typescript
// src/users/users.controller.ts
import { Controller, Get, Post, Body, Param, Delete } from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from './user.entity';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Post()
  create(@Body() user: Partial<User>): Promise<User> {
    return this.usersService.create(user);
  }

  @Get(':id')
  findOne(@Param('id') id: number): Promise<User> {
    return this.usersService.findOne(id);
  }

  @Delete(':id')
  remove(@Param('id') id: number): Promise<void> {
    return this.usersService.remove(id);
  }
}
```

### 7. Estrutura do Projeto
A estrutura básica de um projeto NestJS com `services`, `controllers`, `modules` e TypeORM para MySQL pode ser a seguinte:

```text
src/
├── app.controller.ts
├── app.module.ts
├── app.service.ts
├── main.ts
└── users/
    ├── users.controller.ts
    ├── users.module.ts
    ├── users.service.ts
    └── user.entity.ts

```

Com essas etapas, você configurou o TypeORM para usar MySQL e criou uma entidade User para seu projeto NestJS.

### 8. Exercicio

Tente implementar a funcionalidade de atualização de dados. Realize pesquisas na documentação do NestJS (https://docs.nestjs.com).