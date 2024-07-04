Vamos criar um frontend Angular para consumir a API CRUD criada com Express.js e MySQL.

### Passo 1: Configurar o Projeto Angular

1. Certifique-se de que o Angular CLI está instalado. Se não estiver, instale-o com:

```bash
npm install -g @angular/cli
```

2. Crie um novo projeto Angular:

```bash
ng new crud-frontend-angular
cd crud-frontend-angular
```

3. Instale o pacote `@angular/material` e `@angular/flex-layout` para estilizar a aplicação:

```bash
ng add @angular/material
npm install @angular/flex-layout
```

4. Instale o `HttpClient` para fazer requisições HTTP:

```bash
npm install @angular/common@latest
```

### Passo 2: Criar o Serviço para a API

1. Crie um serviço para interagir com a API. No terminal, execute:

```bash
ng generate service user
```

2. No arquivo `src/app/user.service.ts`, adicione o seguinte código:

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface User {
  id: number;
  name: string;
  age: number;
  email: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:3000/users';

  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  addUser(user: User): Observable<User> {
    return this.http.post<User>(this.apiUrl, user);
  }

  updateUser(id: number, user: User): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/${id}`, user);
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
```

### Passo 3: Criar Componentes

1. Crie um componente para listar e gerenciar usuários:

```bash
ng generate component user-list
```

2. Crie um componente para o formulário de usuários:

```bash
ng generate component user-form
```

### Passo 4: Implementar o Componente `UserForm`

1. No arquivo `src/app/user-form/user-form.component.html`, adicione o seguinte código:

```html
<form (ngSubmit)="onSubmit()" *ngIf="user">
  <h2>{{ user.id ? 'Edit User' : 'Add User' }}</h2>
  <mat-form-field>
    <mat-label>Name</mat-label>
    <input matInput [(ngModel)]="user.name" name="name" required>
  </mat-form-field>
  <mat-form-field>
    <mat-label>Age</mat-label>
    <input matInput type="number" [(ngModel)]="user.age" name="age" required>
  </mat-form-field>
  <mat-form-field>
    <mat-label>Email</mat-label>
    <input matInput type="email" [(ngModel)]="user.email" name="email" required>
  </mat-form-field>
  <button mat-raised-button color="primary" type="submit">{{ user.id ? 'Update' : 'Add' }}</button>
  <button mat-button type="button" (click)="clearForm()">Cancel</button>
</form>
```

2. No arquivo `src/app/user-form/user-form.component.ts`, adicione o seguinte código:

```typescript
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { NgForm } from '@angular/forms';
import { User, UserService } from '../user.service';

@Component({
  selector: 'app-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.css']
})
export class UserFormComponent implements OnChanges {
  @Input() user: User = { id: 0, name: '', age: 0, email: '' };

  constructor(private userService: UserService) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes.user && !changes.user.currentValue) {
      this.user = { id: 0, name: '', age: 0, email: '' };
    }
  }

  onSubmit() {
    if (this.user.id) {
      this.userService.updateUser(this.user.id, this.user).subscribe();
    } else {
      this.userService.addUser(this.user).subscribe();
    }
    this.clearForm();
  }

  clearForm() {
    this.user = { id: 0, name: '', age: 0, email: '' };
  }
}
```

### Passo 5: Implementar o Componente `UserList`

1. No arquivo `src/app/user-list/user-list.component.html`, adicione o seguinte código:

```html
<div>
  <h2>User List</h2>
  <button mat-raised-button color="primary" (click)="addUser()">Add User</button>
  <table mat-table [dataSource]="users" class="mat-elevation-z8">

    <!-- Name Column -->
    <ng-container matColumnDef="name">
      <th mat-header-cell *matHeaderCellDef> Name </th>
      <td mat-cell *matCellDef="let user"> {{user.name}} </td>
    </ng-container>

    <!-- Age Column -->
    <ng-container matColumnDef="age">
      <th mat-header-cell *matHeaderCellDef> Age </th>
      <td mat-cell *matCellDef="let user"> {{user.age}} </td>
    </ng-container>

    <!-- Email Column -->
    <ng-container matColumnDef="email">
      <th mat-header-cell *matHeaderCellDef> Email </th>
      <td mat-cell *matCellDef="let user"> {{user.email}} </td>
    </ng-container>

    <!-- Actions Column -->
    <ng-container matColumnDef="actions">
      <th mat-header-cell *matHeaderCellDef> Actions </th>
      <td mat-cell *matCellDef="let user">
        <button mat-button (click)="editUser(user)">Edit</button>
        <button mat-button (click)="deleteUser(user.id)">Delete</button>
      </td>
    </ng-container>

    <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
    <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
  </table>
</div>
<app-user-form [user]="selectedUser" (clearForm)="clearSelectedUser()"></app-user-form>
```

2. No arquivo `src/app/user-list/user-list.component.ts`, adicione o seguinte código:

```typescript
import { Component, OnInit } from '@angular/core';
import { User, UserService } from '../user.service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css']
})
export class UserListComponent implements OnInit {
  users: User[] = [];
  selectedUser: User = { id: 0, name: '', age: 0, email: '' };
  displayedColumns: string[] = ['name', 'age', 'email', 'actions'];

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.fetchUsers();
  }

  fetchUsers() {
    this.userService.getUsers().subscribe(users => this.users = users);
  }

  addUser() {
    this.selectedUser = { id: 0, name: '', age: 0, email: '' };
  }

  editUser(user: User) {
    this.selectedUser = { ...user };
  }

  deleteUser(id: number) {
    this.userService.deleteUser(id).subscribe(() => this.fetchUsers());
  }

  clearSelectedUser() {
    this.selectedUser = { id: 0, name: '', age: 0, email: '' };
  }
}
```

### Passo 6: Atualizar o Módulo Principal `AppModule`

No arquivo `src/app/app.module.ts`, adicione as seguintes importações e configure o módulo:

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';

import { AppComponent } from './app.component';
import { UserListComponent } from './user-list/user-list.component';
import { UserFormComponent } from './user-form/user-form.component';

@NgModule({
  declarations: [
    AppComponent,
    UserListComponent,
    UserFormComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatFormFieldModule,
    MatIconModule,
    MatToolbarModule
  ],
  providers: [],
  bootstrap: [AppComponent

]
})
export class AppModule { }
```

### Passo 7: Atualizar o Componente Principal `AppComponent`

No arquivo `src/app/app.component.html`, adicione:

```html
<mat-toolbar color="primary">
  <span>CRUD Application</span>
</mat-toolbar>
<app-user-list></app-user-list>
```

### Passo 8: Estilizar a Aplicação

No arquivo `src/styles.css`, adicione um pouco de estilo:

```css
body {
  margin: 0;
  font-family: Roboto, sans-serif;
}

mat-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
}

.app-container {
  padding: 80px 20px 20px 20px;
  max-width: 800px;
  margin: auto;
}

mat-form-field {
  display: block;
  margin: 10px 0;
}

table {
  width: 100%;
}
```

### Passo 9: Iniciar a Aplicação

1. Certifique-se de que o servidor Express.js está em execução.

2. Inicie a aplicação Angular:

```bash
ng serve
```

### Conclusão

Agora você tem um frontend Angular que consome a API CRUD criada com Express.js e MySQL. A tela inicial exibe a lista de usuários com opções de adicionar, editar e deletar usuários diretamente na mesma tela. Para uma aplicação mais completa, considere adicionar tratamento de erros, validação de formulários e autenticação.