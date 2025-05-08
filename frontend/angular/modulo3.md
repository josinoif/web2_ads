# 🧩 Módulo 3 – Serviços e Injeção de Dependência (Angular)

## 🎯 Objetivo do módulo

Neste módulo, você aprenderá:

- O que são serviços em Angular e por que usá-los
- Como criar serviços com Angular CLI
- O que é Injeção de Dependência (DI) e como o Angular a utiliza
- Como compartilhar dados entre componentes usando serviços
- Como encapsular a lógica de negócio fora dos componentes

------

## 3.1 O que é um Serviço?

Um **serviço** em Angular é uma **classe que encapsula uma funcionalidade reutilizável**, como:

- Requisições HTTP
- Lógica de autenticação
- Gerenciamento de estado
- Compartilhamento de dados entre componentes

> Serviços promovem a **separação de responsabilidades**, mantendo os componentes focados apenas na apresentação.

------

## 3.2 Injeção de Dependência no Angular

**Injeção de Dependência (DI)** é um padrão que permite **"injetar" dependências (objetos, serviços, etc.) em outras classes**, em vez de criá-las manualmente.

O Angular possui um **mecanismo de DI embutido**, que automaticamente fornece instâncias dos serviços quando você os declara no construtor de um componente ou outro serviço.

------

## 3.3 Criando um Serviço com Angular CLI

Para criar um serviço:

```bash
ng generate service tarefas
```

O Angular criará:

```
src/app/tarefas.service.ts
```

------

## 3.4 Exemplo prático: serviço de tarefas

### `tarefas.service.ts`:

```ts
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TarefasService {
  private tarefas = [
    { descricao: 'Estudar Angular', concluida: false },
    { descricao: 'Praticar exercícios', concluida: false }
  ];

  obterTarefas() {
    return this.tarefas;
  }

  concluirTarefa(tarefa: any) {
    tarefa.concluida = true;
  }

  adicionarTarefa(descricao: string) {
    this.tarefas.push({ descricao, concluida: false });
  }
}
```

> A anotação `@Injectable({ providedIn: 'root' })` faz com que o serviço seja singleton e esteja disponível em toda a aplicação.

------

## 3.5 Usando o Serviço em um Componente

Agora vamos usar esse serviço dentro de um componente (`lista-tarefas`) para exibir e manipular as tarefas.

### `lista-tarefas.component.ts`:

```ts
import { Component, OnInit } from '@angular/core';
import { TarefasService } from '../tarefas.service';

@Component({
  selector: 'app-lista-tarefas',
  templateUrl: './lista-tarefas.component.html',
  styleUrls: ['./lista-tarefas.component.css']
})
export class ListaTarefasComponent implements OnInit {
  tarefas: any[] = [];

  constructor(private tarefasService: TarefasService) {}

  ngOnInit(): void {
    this.tarefas = this.tarefasService.obterTarefas();
  }

  concluir(tarefa: any): void {
    this.tarefasService.concluirTarefa(tarefa);
  }

  adicionarNovaTarefa(): void {
    this.tarefasService.adicionarTarefa('Nova tarefa adicionada!');
  }

  get totalConcluidas(): number {
    return this.tarefas.filter(t => t.concluida).length;
  }
}
```

### `lista-tarefas.component.html`:

```html
<h2>Lista de Tarefas</h2>

<ul>
  <li *ngFor="let tarefa of tarefas" [ngClass]="{ 'concluida': tarefa.concluida }">
    {{ tarefa.descricao }}
    <button (click)="concluir(tarefa)" [disabled]="tarefa.concluida">Concluir</button>
  </li>
</ul>

<p>Total de tarefas concluídas: {{ totalConcluidas }}</p>

<button (click)="adicionarNovaTarefa()">Adicionar Tarefa</button>
```

------

## 3.6 Compartilhando dados entre componentes com serviços

Se você tiver dois componentes distintos (ex: `cadastro-tarefa` e `lista-tarefas`), o serviço pode servir como **ponte para compartilhar dados entre eles**, pois mantém o estado centralizado.

------

## 3.7 Boas práticas

- Coloque lógica de negócio e acesso a dados em serviços, nunca nos componentes.
- Use `providedIn: 'root'` para a maioria dos casos – isso cria um singleton reutilizável.
- Prefira usar interfaces ou `types` para modelar os dados dos serviços (ex: `Tarefa` ao invés de `any`).

------

## 🧪 Exercício prático

Crie um serviço chamado `ContadorService` com os seguintes métodos:

- `incrementar()`: incrementa uma variável `contador`
- `obterValor()`: retorna o valor atual
- `resetar()`: zera o contador

Depois, crie um componente chamado `contador` que:

- Exibe o valor atual do contador
- Tem botões para incrementar e resetar
- Usa o serviço para manipular os dados

------

## ✅ Conclusão

Você aprendeu:

- O que são serviços e por que usá-los
- Como a injeção de dependência funciona no Angular
- Como separar responsabilidades entre componentes e serviços
- Como compartilhar dados de forma reativa e centralizada

