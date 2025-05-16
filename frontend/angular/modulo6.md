# 📦 Módulo 6 – Tratamento de Erros e Feedback ao Usuário no Angular

## 🎯 Objetivo do módulo

Neste módulo, você aprenderá:

- A capturar erros de chamadas HTTP usando `catchError`
- A criar um **interceptor global de erros**
- A exibir **mensagens de erro na interface** com um componente de alerta
- A centralizar o tratamento e exibição de mensagens para o usuário

------

## 6.1 Por que tratar erros?

Sem tratamento de erros, falhas inesperadas derrubam a aplicação ou deixam o usuário confuso. O tratamento adequado:

- Evita que erros quebrem o fluxo
- Permite exibir mensagens úteis ao usuário
- Facilita a manutenção e depuração

------

## 6.2 Tratando erros diretamente com `catchError`

### Exemplo prático:

Esse código normalmente fica no arquivo do componente responsável pela chamada HTTP, por exemplo, em `produtos.component.ts`:

```ts
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

this.http.get('/api/produtos').pipe(
  catchError((error) => {
    this.alertaService.exibir('Erro ao buscar produtos.');
    return throwError(() => error);
  })
).subscribe();
```

> Esse padrão é útil para lidar com erros **específicos** de uma requisição.

------

## 6.3 Tratamento global com interceptor

Vamos agora tratar **todos os erros da aplicação** com um interceptor centralizado.

### Passo 1 – Criar o interceptor:

```bash
ng generate interceptor interceptores/erro
```

### `erro.interceptor.ts`:

```ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AlertaService } from '../servicos/alerta.service';

@Injectable()
export class ErroInterceptor implements HttpInterceptor {
  constructor(private alerta: AlertaService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((erro: HttpErrorResponse) => {
        let mensagem = 'Erro desconhecido.';

        switch (erro.status) {
          case 0:
            mensagem = 'Não foi possível conectar ao servidor.';
            break;
          case 400:
            mensagem = 'Requisição inválida.';
            break;
          case 401:
            mensagem = 'Você precisa estar autenticado.';
            break;
          case 403:
            mensagem = 'Você não tem permissão para acessar este recurso.';
            break;
          case 404:
            mensagem = 'Recurso não encontrado.';
            break;
          case 500:
            mensagem = 'Erro interno no servidor.';
            break;
        }

        this.alerta.exibir(mensagem);
        return throwError(() => erro);
      })
    );
  }
}
```

------
### Passo 2 – Registrar o interceptor em um projeto:

No arquivo principal de bootstrap (por exemplo, `main.ts`):

```ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { ErroInterceptor } from './interceptores/erro.interceptor';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(
      withInterceptors([ErroInterceptor])
    )
  ]
});
```

> Certifique-se de que o `ErroInterceptor` está anotado com `@Injectable()` e disponível para injeção.

------

## 6.4 Criando um serviço e componente de alerta reutilizável

### `alerta.service.ts`:

```ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AlertaService {
  private mensagemSubject = new BehaviorSubject<string | null>(null);
  mensagem$ = this.mensagemSubject.asObservable();

  exibir(mensagem: string) {
    this.mensagemSubject.next(mensagem);

    // Oculta automaticamente após 5 segundos
    setTimeout(() => this.mensagemSubject.next(null), 5000);
  }
}
```

### `alerta.component.ts`:

```ts
import { Component } from '@angular/core';
import { AlertaService } from './alerta.service';

@Component({
  selector: 'app-alerta',
  template: `
    <div *ngIf="mensagem" class="alerta">
      {{ mensagem }}
    </div>
  `,
  styles: [`
    .alerta {
      background-color: #f44336;
      color: white;
      padding: 12px;
      margin: 12px;
      border-radius: 4px;
    }
  `]
})
export class AlertaComponent {
  mensagem: string | null = null;

  constructor(private alertaService: AlertaService) {
    this.alertaService.mensagem$.subscribe(msg => this.mensagem = msg);
  }
}
```

### Passo 3 – Inserir o componente no layout

No `app.component.html` ou em outro componente de layout:

```html
<app-alerta></app-alerta>
<router-outlet></router-outlet>
```

------

## 6.5 Fluxo completo do tratamento de erro

1. Uma chamada HTTP falha
2. O interceptor captura o erro
3. O interceptor chama `alertaService.exibir(...)`
4. O `alertaService` publica a mensagem
5. O `alerta.component` exibe a mensagem no topo da tela

------

## 🧪 Exercício prático

1. Crie o interceptor `ErroInterceptor` e registre no app
2. Crie o `AlertaService` e o `AlertaComponent`
3. Use `alertaService.exibir(...)` para mostrar mensagens de erro
4. Teste com endpoints inválidos para ver a mensagem exibida dinamicamente

------

## ✅ Conclusão

Você aprendeu:

- A capturar erros com `catchError` e `throwError`
- A tratar erros de forma global com interceptores
- A criar um serviço para exibição de mensagens de erro
- A criar um componente de alerta reutilizável
- A fornecer feedback visual claro e útil ao usuário

