# 🔐 Módulo 7 – Autenticação com JWT: Login, Logout e Proteção de Rotas

## 🎯 Objetivo do Módulo

Neste módulo, você aprenderá:

- Como funciona a autenticação baseada em JWT
- Como implementar login e logout no Angular
- Como armazenar o token JWT de forma segura
- Como interceptar requisições para enviar o token
- Como proteger rotas com `AuthGuard`
- Como exibir mensagens de erro de autenticação para o usuário

------

## 7.1 Como funciona a autenticação com JWT

O fluxo básico:

1. O usuário envia credenciais para a API.
2. A API valida e retorna um token JWT.
3. O frontend armazena o token (geralmente em `localStorage`).
4. O frontend envia o token no cabeçalho `Authorization` em cada requisição.
5. A API valida o token antes de processar a requisição.

------

## 7.2 Criando um serviço de autenticação

### `auth.service.ts`

```ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'https://fakestoreapi.com/auth/login';

  constructor(private http: HttpClient) {}

  login(usuario: { username: string; password: string }) {
    return this.http.post<{ token: string }>(this.apiUrl, usuario).pipe(
      tap((resposta) => {
        localStorage.setItem('token', resposta.token);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
  }

  isAutenticado(): boolean {
    return !!localStorage.getItem('token');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}
```

------

## 7.3 Criando o componente de login

### `login.component.ts`

```ts
import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  username = '';
  password = '';
  erro = '';

  constructor(private auth: AuthService, private router: Router) {}

  logar(): void {
    this.erro = '';
    this.auth.login({ username: this.username, password: this.password })
      .subscribe({
        next: () => this.router.navigate(['/produtos']),
        error: () => this.erro = 'Usuário ou senha inválidos.'
      });
  }
}
```

### `login.component.html`

```html
<h2>Login</h2>

<form (ngSubmit)="logar()">
  <label>Usuário:</label>
  <input [(ngModel)]="username" name="username" required>

  <label>Senha:</label>
  <input type="password" [(ngModel)]="password" name="password" required>

  <div *ngIf="erro" class="erro">{{ erro }}</div>

  <button type="submit">Entrar</button>
</form>
```

### `login.component.css`

```css
.erro {
  color: red;
  margin-top: 10px;
}
```

------

## 7.4 Criando o botão de logout

Você pode colocar isso em um `app.component.html` ou menu:

```html
<button *ngIf="auth.isAutenticado()" (click)="auth.logout()">Sair</button>
```

------

## 7.5 Enviando o token automaticamente com interceptor

### `token.interceptor.ts`

```ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../auth.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.auth.getToken();
    if (token) {
      const reqClone = req.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
      return next.handle(reqClone);
    }
    return next.handle(req);
  }
}
```

### Registrar no módulo:

```ts
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { TokenInterceptor } from './interceptores/token.interceptor';

@NgModule({
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true }
  ]
})
export class AppModule {}
```

------

## 7.6 Protegendo rotas com AuthGuard

### `auth.guard.ts`

```ts
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (this.auth.isAutenticado()) {
      return true;
    } else {
      this.router.navigate(['/login']);
      return false;
    }
  }
}
```

### Uso no roteamento:

```ts
const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'produtos', component: ProdutosComponent, canActivate: [AuthGuard] }
];
```

------

## 7.7 Exibindo mensagens de erro na tela

Já fizemos isso em `login.component.ts` com a variável `erro`, mas você pode usar um `AlertaService` ou `MatSnackBar` (do Angular Material) para mensagens amigáveis, como visto no módulo anterior.

------

## 🧪 Exercício prático

1. Crie o serviço `AuthService` com métodos `login`, `logout`, `getToken` e `isAutenticado`
2. Crie o componente `LoginComponent` com formulário e mensagem de erro
3. Crie o `TokenInterceptor` e registre no `AppModule`
4. Crie o `AuthGuard` para proteger a rota `/produtos`
5. Teste login, redirecionamento, logout e persistência do token

------

## ✅ Conclusão do Módulo

Você aprendeu:

- A implementar login e logout com JWT
- A armazenar e enviar o token JWT em requisições
- A proteger rotas com `AuthGuard`
- A exibir feedbacks amigáveis para o usuário
- A estruturar a autenticação de forma profissional e reutilizável

