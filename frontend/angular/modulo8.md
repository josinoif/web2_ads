# 🧭 Módulo 8 – Rotas e Navegação no Angular

## 🎯 Objetivo do Módulo

Neste módulo, você aprenderá:

- A configurar rotas com `RouterModule`
- A criar navegação entre páginas
- A passar parâmetros entre componentes via URL
- A usar `routerLink` e navegação programática
- A proteger rotas com guards (`AuthGuard`)
- A aplicar boas práticas de organização de rotas

------

## 8.1 Importando e configurando o `RouterModule`

### `app-routing.module.ts`

Se o projeto não tiver um arquivo de rotas, crie com o CLI:

```bash
ng generate module app-routing --flat --module=app
```

E defina as rotas:

```ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LoginComponent } from './login/login.component';
import { ProdutosComponent } from './produtos/produtos.component';
import { CadastroProdutoComponent } from './cadastro-produto/cadastro-produto.component';
import { AuthGuard } from './auth.guard';

const routes: Routes = [
  { path: '', redirectTo: 'produtos', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'produtos', component: ProdutosComponent, canActivate: [AuthGuard] },
  { path: 'produtos/novo', component: CadastroProdutoComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: 'produtos' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
```

### `app.module.ts`

Certifique-se de importar o módulo de rotas:

```ts
import { AppRoutingModule } from './app-routing.module';

@NgModule({
  imports: [
    AppRoutingModule
  ]
})
```

------

## 8.2 Navegação com `routerLink`

No template HTML, use `[routerLink]` para navegar entre páginas:

### Exemplo:

```html
<nav>
  <a routerLink="/produtos">Produtos</a>
  <a routerLink="/produtos/novo">Cadastrar Produto</a>
  <a routerLink="/login">Login</a>
</nav>
```

> O Angular atualiza a URL sem recarregar a página (Single Page Application – SPA).

------

## 8.3 Navegação programática

Você também pode navegar usando o código TypeScript:

```ts
import { Router } from '@angular/router';

constructor(private router: Router) {}

this.router.navigate(['/produtos']);
```

> Isso é útil após login, salvar formulários ou em botões com lógica.

------

## 8.4 Parâmetros de rota

Use parâmetros na URL para carregar dados específicos, como editar um produto:

### Definindo a rota com parâmetro:

```ts
{ path: 'produtos/:id', component: CadastroProdutoComponent }
```

### Navegando até a rota com parâmetro:

```html
<a [routerLink]="['/produtos', produto.id]">Editar</a>
```

### Recebendo o parâmetro no componente:

```ts
import { ActivatedRoute } from '@angular/router';

constructor(private route: ActivatedRoute) {}

ngOnInit(): void {
  const id = this.route.snapshot.paramMap.get('id');
  console.log('ID do produto:', id);
}
```

> Também é possível usar `route.paramMap.subscribe(...)` para escutar mudanças dinâmicas.

------

## 8.5 Protegendo rotas com `AuthGuard`

Você já aprendeu a usar `AuthGuard` no módulo 7. Aqui relembramos como proteger uma rota:

```ts
{ path: 'produtos', component: ProdutosComponent, canActivate: [AuthGuard] }
```

Isso impede o acesso à rota se o usuário não estiver autenticado.

------

## 8.6 Redirecionamentos e rotas coringa

- Redirecionamento padrão (home):

```ts
{ path: '', redirectTo: 'produtos', pathMatch: 'full' }
```

- Rota coringa (página não encontrada):

```ts
{ path: '**', redirectTo: 'produtos' }
```

------

## 8.7 Exibindo o conteúdo das rotas

No `app.component.html`, deve haver o `router-outlet`, que representa o local onde o conteúdo das rotas será carregado:

```html
<app-alerta></app-alerta>
<nav>
  <a routerLink="/produtos">Produtos</a>
  <a routerLink="/produtos/novo">Novo</a>
</nav>

<router-outlet></router-outlet>
```

------

## 🧪 Exercício prático

1. Crie a rota `/produtos/:id` para editar um produto.
2. Crie links com `[routerLink]` para navegar entre lista e cadastro.
3. No `CadastroProdutoComponent`, recupere o `id` da URL e exiba-o.
4. Crie uma navegação programática para redirecionar após salvar.
5. Configure uma rota coringa `**` para redirecionar o usuário em caso de erro.

------

## ✅ Conclusão do módulo

Você aprendeu:

- A criar rotas no Angular e usar `RouterModule`
- A navegar usando `[routerLink]` e `router.navigate(...)`
- A usar parâmetros de rota
- A proteger rotas com guards
- A estruturar a navegação de forma clara, segura e escalável

