# 📦 Módulo 5 – Formulários Reativos e Validações no Angular
## 🎯 Objetivo do módulo

Neste módulo, o aluno aprenderá:

- A diferença entre formulários template-driven e reativos
- A configurar e usar formulários reativos com `FormGroup`, `FormControl` e `FormBuilder`
- A aplicar validações integradas e customizadas
- A exibir mensagens de erro amigáveis no template
- A submeter dados apenas quando o formulário for válido

------

## 5.1 Tipos de Formulários em Angular

Angular suporta dois tipos de formulários:

| Tipo                     | Controle no Template     | Recomendado para                                             |
| ------------------------ | ------------------------ | ------------------------------------------------------------ |
| Template-driven          | Alto (usa ngModel)       | Formulários simples                                          |
| Reativo (Reactive Forms) | Totalmente no TypeScript | Formulários complexos, dinâmicos ou com validação customizada |

Neste módulo, focaremos **exclusivamente em formulários reativos**, que são padrão em projetos empresariais.

------

## 5.2 Importando o módulo `ReactiveFormsModule` em componentes standalone

Em projetos standalone, você importa módulos diretamente no decorator do componente.

### Exemplo:

```ts
import { Component } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  standalone: true,
  selector: 'app-cadastro-produto',
  templateUrl: './cadastro-produto.component.html',
  imports: [ReactiveFormsModule]
})
export class CadastroProdutoComponent { /* ... */ }
```

------

## 5.3 Criando um formulário com `FormBuilder` (Standalone)

### Gerar componente standalone:

```bash
ng generate component cadastro-produto --standalone
```

### `cadastro-produto.component.ts`:

```ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({
  standalone: true,
  selector: 'app-cadastro-produto',
  templateUrl: './cadastro-produto.component.html',
  imports: [ReactiveFormsModule]
})
export class CadastroProdutoComponent implements OnInit {
  formulario!: FormGroup;

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.formulario = this.fb.group({
      nome: ['', [Validators.required, Validators.minLength(3)]],
      preco: [null, [Validators.required, Validators.min(0.01)]],
      categoria: ['', Validators.required]
    });
  }

  salvar(): void {
    if (this.formulario.valid) {
      console.log('Produto salvo:', this.formulario.value);
      alert('Produto salvo com sucesso!');
      this.formulario.reset();
    } else {
      alert('Formulário inválido. Verifique os campos.');
    }
  }
}
```

------

## 5.4 Template do formulário

### `cadastro-produto.component.html`:

```html
<h2>Cadastro de Produto</h2>

<form [formGroup]="formulario" (ngSubmit)="salvar()">
  <label>Nome:</label>
  <input type="text" formControlName="nome">
  <div *ngIf="formulario.get('nome')?.invalid && formulario.get('nome')?.touched">
    <small *ngIf="formulario.get('nome')?.errors?.['required']">Nome é obrigatório.</small>
    <small *ngIf="formulario.get('nome')?.errors?.['minlength']">Mínimo de 3 caracteres.</small>
  </div>

  <label>Preço:</label>
  <input type="number" formControlName="preco">
  <div *ngIf="formulario.get('preco')?.invalid && formulario.get('preco')?.touched">
    <small *ngIf="formulario.get('preco')?.errors?.['required']">Preço é obrigatório.</small>
    <small *ngIf="formulario.get('preco')?.errors?.['min']">Preço deve ser maior que zero.</small>
  </div>

  <label>Categoria:</label>
  <input type="text" formControlName="categoria">
  <div *ngIf="formulario.get('categoria')?.invalid && formulario.get('categoria')?.touched">
    <small>Categoria é obrigatória.</small>
  </div>

  <button type="submit" [disabled]="formulario.invalid">Salvar</button>
</form>
```

------

## 5.5 Explicando o uso de validações

### Validadores integrados usados:

- `Validators.required`: campo obrigatório
- `Validators.minLength(n)`: número mínimo de caracteres
- `Validators.min(n)`: valor mínimo permitido

### Checando validade no template:

- `formulario.get('campo')?.invalid` — o campo é inválido
- `formulario.get('campo')?.touched` — o campo foi tocado (focado ao menos uma vez)

------

## 5.6 Criando validações customizadas

Às vezes, as validações integradas do Angular não são suficientes para as regras de negócio da sua aplicação. Nesses casos, você pode criar seus próprios validadores customizados.

### Exemplo: Bloquear nomes que contenham a palavra "teste"

Vamos criar uma função validadora que impede que o campo "nome" contenha a palavra "teste" (ignorando maiúsculas/minúsculas).

#### 1. Criando o validador customizado

Crie um arquivo chamado `nome-invalido.validator.ts` na mesma pasta do seu componente ou em uma pasta dedicada a validadores, por exemplo:  
`src/app/cadastro-produto/nome-invalido.validator.ts`

```ts
import { AbstractControl, ValidationErrors } from '@angular/forms';

/**
 * Validador customizado que retorna erro se o valor do campo contiver "teste".
 * @param control O controle do formulário a ser validado.
 * @returns Um objeto de erro se inválido, ou null se válido.
 */
export function nomeInvalidoValidator(control: AbstractControl): ValidationErrors | null {
  const valor = control.value;
  if (typeof valor === 'string' && valor.toLowerCase().includes('teste')) {
    // Retorna um objeto indicando o erro
    return { nomeInvalido: true };
  }
  // Retorna null se não houver erro
  return null;
}
```

#### 2. Usando o validador no FormBuilder

No arquivo do componente onde você define o formulário, por exemplo, em `cadastro-produto.component.ts`, adicione o validador customizado ao array de validações do campo desejado:

```ts
import { FormBuilder, Validators } from '@angular/forms';
import { nomeInvalidoValidator } from './nome-invalido.validator';

this.formulario = this.fb.group({
  nome: [
    '',
    [
      Validators.required, // campo obrigatório
      nomeInvalidoValidator // nosso validador customizado
    ]
  ]
});
```

#### 3. Exibindo a mensagem de erro no template

No template, você pode exibir uma mensagem específica quando o erro `nomeInvalido` estiver presente:

```html
<input type="text" formControlName="nome">
<div *ngIf="formulario.get('nome')?.errors?.['nomeInvalido'] && formulario.get('nome')?.touched">
  <small>O nome não pode conter a palavra "teste".</small>
</div>
```

Dessa forma, você pode criar qualquer lógica de validação personalizada para atender às necessidades do seu formulário.

------

## 🧪 Exercício prático

Crie um componente standalone `cadastro-cliente` com os seguintes campos:

- Nome (mínimo 2 letras)
- Email (obrigatório e válido)
- Idade (mínimo 18 anos)

Requisitos:

- Exiba mensagens de erro claras
- Valide os campos no envio
- Mostre um alerta com os dados do cliente se o formulário estiver válido

**Dica:** Use `ReactiveFormsModule` no array `imports` do decorator do componente.

------

## ✅ Conclusão do módulo

Você aprendeu:

- A diferença entre formulários template-driven e reativos
- A criar e configurar formulários reativos com `FormBuilder`
- A aplicar validações integradas e customizadas
- A exibir mensagens de erro no template
- A garantir que o formulário só seja enviado quando válido

