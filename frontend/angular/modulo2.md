# 📦 Módulo 2 – Componentes e Templates (Angular)

## 🎯 Objetivo do Módulo

Neste módulo, você aprenderá:

- O que é um componente em Angular
- Como criar e organizar componentes
- Como trabalhar com dados no template usando bindings
- Como controlar o DOM com diretivas (`*ngIf`, `*ngFor`, `[ngClass]`, `[ngStyle]`)
- Como aplicar estilos e eventos

------

## 2.1 O que é um Componente?

Um **componente** é uma das partes mais fundamentais em Angular. Ele representa uma seção visual da interface (UI) da aplicação. Cada componente possui:

- Um **template HTML**: o que será renderizado na tela
- Uma **classe TypeScript**: onde está a lógica do componente
- Um **arquivo de estilo**: define o visual daquele componente

------

## 2.2 Criando um componente com o Angular CLI

No terminal, dentro do projeto Angular:

```bash
ng generate component saudacao
```

O Angular criará automaticamente os arquivos:

```
src/app/saudacao/
├── saudacao.component.ts
├── saudacao.component.html
├── saudacao.component.css
└── saudacao.component.spec.ts
```

------

## 2.3 Interpolação: exibindo dados no template

Vamos mostrar o nome de um usuário no HTML usando a sintaxe `{{ }}`.

### `saudacao.component.ts`:

```ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-saudacao',
  templateUrl: './saudacao.component.html',
  styleUrls: ['./saudacao.component.css']
})
export class SaudacaoComponent {
  nomeUsuario: string = 'Maria';
}
```

### `saudacao.component.html`:

```html
<h1>Olá, {{ nomeUsuario }}!</h1>
```

> A interpolação permite exibir diretamente o valor da variável `nomeUsuario` no HTML.

------

## 2.4 Property Binding: ligando propriedades HTML

Você pode definir atributos de elementos HTML com dados do componente.

### `saudacao.component.ts`:

```ts
imagemUrl: string = 'https://angular.io/assets/images/logos/angular/angular.png';
```

### `saudacao.component.html`:

```html
<img [src]="imagemUrl" alt="Logo do Angular" width="120">
```

> O `[src]` vincula o valor de `imagemUrl` ao atributo `src` do elemento `<img>`.

------

## 2.5 Event Binding: reagindo a eventos do usuário

Vamos adicionar um botão que, ao ser clicado, conta o número de cliques.

### `saudacao.component.ts`:

```ts
contador: number = 0;

incrementar(): void {
  this.contador++;
}
```

### `saudacao.component.html`:

```html
<button (click)="incrementar()">Clique aqui</button>
<p>Você clicou {{ contador }} vezes.</p>
```

> O evento `(click)` chama o método `incrementar()` sempre que o botão é clicado.

------

## 2.6 Diretivas estruturais: `*ngIf` e `*ngFor`

No Angular 19, para usar diretivas como `*ngIf` e `*ngFor`, é necessário importar explicitamente o módulo `CommonModule` no contexto do componente standalone. Isso ocorre porque o Angular agora adota uma abordagem modular mais explícita.

### Como adaptar o componente `saudacao`

Certifique-se de que o componente `SaudacaoComponent` seja configurado como standalone e importe o `CommonModule`. Por exemplo:

### `saudacao.component.ts`:

```ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-saudacao',
  standalone: true, // Configuração standalone
  imports: [CommonModule], // Importação necessária
  templateUrl: './saudacao.component.html',
  styleUrls: ['./saudacao.component.css']
})
export class SaudacaoComponent {
  nomeUsuario: string = 'Maria';
  contador: number = 0;
  frutas: string[] = ['Maçã', 'Banana', 'Uva'];

  incrementar(): void {
    this.contador++;
  }
}
```

### `*ngIf`: exibe um elemento condicionalmente

```html
<p *ngIf="contador > 0">Você já clicou pelo menos uma vez!</p>
```

### `*ngFor`: repete elementos com base em uma lista

```html
<ul>
  <li *ngFor="let fruta of frutas">{{ fruta }}</li>
</ul>
```

> Certifique-se de que o `CommonModule` está importado diretamente no componente standalone para que as diretivas `*ngIf` e `*ngFor` funcionem corretamente.

## 2.7 Diretivas de atributo: `[ngClass]` e `[ngStyle]`

### Exemplo com `ngClass`:

### `saudacao.component.ts`:

```ts
estaAtivo: boolean = true;
```

### `saudacao.component.html`:

```html
<p [ngClass]="{ 'ativo': estaAtivo, 'inativo': !estaAtivo }">
  Este texto muda de classe com base no estado.
</p>
```

### `saudacao.component.css`:

```css
.ativo {
  color: green;
  font-weight: bold;
}

.inativo {
  color: gray;
  text-decoration: line-through;
}
```

------

### Exemplo com `ngStyle`:

### `saudacao.component.ts`:

```ts
corTexto: string = 'blue';
```

### `saudacao.component.html`:

```html
<p [ngStyle]="{ 'color': corTexto, 'font-size': '18px' }">
  Texto com estilo dinâmico
</p>
```

> `ngStyle` aplica estilos inline com base nas variáveis da classe.

------

## 2.8 Exercício prático (atividade individual)

Crie um componente chamado `lista-tarefas` com a seguinte funcionalidade:

### Requisitos:

1. Exiba uma lista de tarefas com `*ngFor`.
2. Use `*ngIf` para exibir uma mensagem “Lista vazia” caso não haja tarefas.
3. Adicione um botão para marcar cada tarefa como concluída.
4. Use `ngClass` para aplicar uma classe nas tarefas concluídas.
5. Mostre quantas tarefas foram concluídas no total.

### Exemplo sugerido:

#### `lista-tarefas.component.ts`:

```ts
export class ListaTarefasComponent {
  tarefas = [
    { descricao: 'Estudar Angular', concluida: false },
    { descricao: 'Praticar exercícios', concluida: false },
    { descricao: 'Ler documentação', concluida: false }
  ];

  concluirTarefa(tarefa: any) {
    tarefa.concluida = true;
  }

  get totalConcluidas() {
    return this.tarefas.filter(t => t.concluida).length;
  }
}
```

#### `lista-tarefas.component.html`:

```html
<h2>Lista de Tarefas</h2>

<p *ngIf="tarefas.length === 0">Lista vazia.</p>

<ul>
  <li *ngFor="let tarefa of tarefas" [ngClass]="{ 'concluida': tarefa.concluida }">
    {{ tarefa.descricao }}
    <button (click)="concluirTarefa(tarefa)" [disabled]="tarefa.concluida">Concluir</button>
  </li>
</ul>

<p>Total de tarefas concluídas: {{ totalConcluidas }}</p>
```

#### `lista-tarefas.component.css`:

```css
.concluida {
  text-decoration: line-through;
  color: green;
}
```

------

## 🧠 Dicas para o aluno

- Toda lógica da aplicação deve ficar no `.ts`. O HTML deve apenas exibir os dados e capturar eventos.
- Evite usar `any` quando possível. Tipos fortes ajudam a prevenir erros.
- Sempre use interpolação e bindings ao invés de manipular diretamente o DOM.

------

## ✅ Conclusão do Módulo

Você aprendeu:

- O que é e como criar um componente
- Como usar interpolação para mostrar dados
- Como reagir a eventos do usuário
- Como renderizar listas e aplicar lógica condicional
- Como aplicar estilos dinamicamente com diretivas

