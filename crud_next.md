Aqui está um tutorial passo a passo para criar uma aplicação CRUD com NestJS.

### Passo 1: Instalar o NestJS

Primeiro, você precisa instalar o NestJS CLI globalmente se ainda não o fez:

```bash
npm install -g @nestjs/cli
```

### Passo 2: Criar um Novo Projeto

Crie um novo projeto NestJS com o comando:

```bash
nest new project-name
```

### Passo 3: Criar um Módulo

Crie um módulo para gerenciar a entidade (por exemplo, `users`):

```bash
nest g module users
```

### Passo 4: Criar um Service

O service é responsável pela lógica de negócios:

```bash
nest g service users
```

### Passo 5: Criar um Controller

O controller lida com as solicitações HTTP:

```bash
nest g controller users
```

### Passo 6: Definir a Entidade

Defina a entidade `User`:

Crie um arquivo `user.entity.ts` dentro da pasta `users`:

```typescript
export class User {
  id: number;
  name: string;
  age: number;
  email: string;
}
```

### Passo 7: Implementar o Service

Implemente o serviço para gerenciar os dados do usuário (`users.service.ts`):

```typescript
import { Injectable } from '@nestjs/common';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  private users: User[] = [];

  findAll(): User[] {
    return this.users;
  }

  findOne(id: number): User {
    return this.users.find(user => user.id === id);
  }

  create(user: User) {
    this.users.push(user);
  }

  update(id: number, updatedUser: User) {
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex > -1) {
      this.users[userIndex] = updatedUser;
    }
  }

  remove(id: number) {
    this.users = this.users.filter(user => user.id !== id);
  }
}
```

### Passo 8: Implementar o Controller

Implemente o controller para lidar com as requisições HTTP (`users.controller.ts`):

```typescript
import { Controller, Get, Post, Body, Param, Put, Delete } from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from './user.entity';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): User[] {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string): User {
    return this.usersService.findOne(Number(id));
  }

  @Post()
  create(@Body() user: User) {
    this.usersService.create(user);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updatedUser: User) {
    this.usersService.update(Number(id), updatedUser);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    this.usersService.remove(Number(id));
  }
}
```

### Passo 9: Configurar o AppModule

Certifique-se de que o módulo `UsersModule` está importado no `app.module.ts`:

```typescript
import { Module } from '@nestjs/common';
import { UsersModule } from './users/users.module';

@Module({
  imports: [UsersModule],
})
export class AppModule {}
```

### Passo 10: Iniciar a Aplicação

Inicie a aplicação com:

```bash
npm run start
```

### Conclusão

Você agora tem uma aplicação CRUD básica com NestJS. Para uma implementação mais completa, considere integrar um banco de dados como PostgreSQL ou MongoDB e usar o TypeORM ou Mongoose para gerenciar suas entidades.