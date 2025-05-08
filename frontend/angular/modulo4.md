# 📦 Módulo 4 – Consumo de API REST (CRUD) no Angular

## 🎯 Objetivo do módulo

Neste módulo, o aluno aprenderá:

- Como usar o `HttpClient` do Angular
- Como configurar uma aplicação para consumir APIs REST
- Como criar um serviço para encapsular as chamadas HTTP
- Como realizar operações de CRUD em uma API
- Como estruturar componentes para exibir, criar, editar e remover dados

------

## 4.1 Importando o módulo `HttpClientModule`

Para utilizar o `HttpClient`, você deve importar o módulo no `AppModule`.

### `app.module.ts`

```ts
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    HttpClientModule,
    // outros módulos
  ]
})
export class AppModule { }
```

------

## 4.2 Criando um serviço para consumir a API

Vamos criar um serviço chamado `produtos.service.ts` que se conecta a uma API de produtos.

Use o Angular CLI:

```bash
ng generate service produtos
```

### `produtos.service.ts`

```ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Produto {
  id?: number;
  nome: string;
  preco: number;
  categoria: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProdutosService {
  private baseUrl = 'https://fakestoreapi.com/products';

  constructor(private http: HttpClient) {}

  listar(): Observable<Produto[]> {
    return this.http.get<Produto[]>(this.baseUrl);
  }

  buscarPorId(id: number): Observable<Produto> {
    return this.http.get<Produto>(`${this.baseUrl}/${id}`);
  }

  criar(produto: Produto): Observable<Produto> {
    return this.http.post<Produto>(this.baseUrl, produto);
  }

  atualizar(id: number, produto: Produto): Observable<Produto> {
    return this.http.put<Produto>(`${this.baseUrl}/${id}`, produto);
  }

  excluir(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
}
```

------

## 4.3 Criando um componente para listar os produtos

### Gerar componente:

```bash
ng generate component produtos
```

### `produtos.component.ts`

```ts
import { Component, OnInit } from '@angular/core';
import { ProdutosService, Produto } from '../produtos.service';

@Component({
  selector: 'app-produtos',
  templateUrl: './produtos.component.html',
  styleUrls: ['./produtos.component.css']
})
export class ProdutosComponent implements OnInit {
  produtos: Produto[] = [];

  constructor(private produtosService: ProdutosService) {}

  ngOnInit(): void {
    this.produtosService.listar().subscribe({
      next: (dados) => this.produtos = dados,
      error: (erro) => console.error('Erro ao carregar produtos:', erro)
    });
  }

  excluir(id: number): void {
    this.produtosService.excluir(id).subscribe({
      next: () => this.produtos = this.produtos.filter(p => p.id !== id),
      error: (erro) => console.error('Erro ao excluir produto:', erro)
    });
  }
}
```

### `produtos.component.html`

```html
<h2>Lista de Produtos</h2>

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Nome</th>
      <th>Preço</th>
      <th>Categoria</th>
      <th>Ações</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor="let produto of produtos">
      <td>{{ produto.id }}</td>
      <td>{{ produto.nome }}</td>
      <td>R$ {{ produto.preco }}</td>
      <td>{{ produto.categoria }}</td>
      <td>
        <button (click)="excluir(produto.id!)">Excluir</button>
      </td>
    </tr>
  </tbody>
</table>
```

------

## 4.4 Criando um formulário para adicionar um produto

### `produto-form.component.ts`

```ts
import { Component } from '@angular/core';
import { ProdutosService, Produto } from '../produtos.service';

@Component({
  selector: 'app-produto-form',
  templateUrl: './produto-form.component.html'
})
export class ProdutoFormComponent {
  novoProduto: Produto = {
    nome: '',
    preco: 0,
    categoria: ''
  };

  constructor(private produtosService: ProdutosService) {}

  salvar(): void {
    this.produtosService.criar(this.novoProduto).subscribe({
      next: (produtoCriado) => {
        alert('Produto cadastrado com sucesso!');
        this.novoProduto = { nome: '', preco: 0, categoria: '' };
      },
      error: (erro) => {
        console.error('Erro ao salvar produto:', erro);
        alert('Erro ao cadastrar produto.');
      }
    });
  }
}
```

### `produto-form.component.html`

```html
<h2>Cadastro de Produto</h2>

<form (ngSubmit)="salvar()" #form="ngForm">
  <label>Nome:</label>
  <input type="text" [(ngModel)]="novoProduto.nome" name="nome" required>

  <label>Preço:</label>
  <input type="number" [(ngModel)]="novoProduto.preco" name="preco" required>

  <label>Categoria:</label>
  <input type="text" [(ngModel)]="novoProduto.categoria" name="categoria" required>

  <button type="submit">Salvar</button>
</form>
```

------

## 4.5 Estrutura recomendada de rotas (opcional)

Para navegação entre telas de cadastro e listagem, crie rotas como:

### `app-routing.module.ts`

```ts
const routes: Routes = [
  { path: 'produtos', component: ProdutosComponent },
  { path: 'produtos/novo', component: ProdutoFormComponent },
  { path: '', redirectTo: '/produtos', pathMatch: 'full' }
];
```

------

## 🧪 Exercício prático

Crie uma aplicação Angular com os seguintes requisitos:

1. Conecte-se à API `https://fakestoreapi.com/products`
2. Crie um componente de listagem com botão de exclusão
3. Crie um formulário para cadastrar novos produtos
4. Após cadastrar, exiba o produto na lista

Desafio adicional: implemente a edição de um produto usando o método `PUT`.

------

## ✅ Conclusão do módulo

Você aprendeu:

- A configurar o `HttpClientModule`
- A criar um serviço para encapsular chamadas HTTP
- A fazer requisições GET, POST, PUT e DELETE
- A manipular dados da API em componentes
- A criar telas para operações CRUD

