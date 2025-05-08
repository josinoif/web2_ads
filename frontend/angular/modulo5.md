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

## 5.2 Importando o módulo `ReactiveFormsModule`

### `app.module.ts`:

```ts
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
  imports: [
    ReactiveFormsModule
  ]
})
export class AppModule { }
```

------

## 5.3 Criando um formulário com `FormBuilder`

### Gerar componente:

```bash
ng generate component cadastro-produto
```

### `cadastro-produto.component.ts`:

```ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-cadastro-produto',
  templateUrl: './cadastro-produto.component.html'
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

Validador que bloqueia nomes com a palavra "teste":

```ts
import { AbstractControl, ValidationErrors } from '@angular/forms';

export function nomeInvalidoValidator(control: AbstractControl): ValidationErrors | null {
  const valor = control.value?.toLowerCase();
  if (valor && valor.includes('teste')) {
    return { nomeInvalido: true };
  }
  return null;
}
```

Uso no `FormBuilder`:

```ts
this.formulario = this.fb.group({
  nome: ['', [Validators.required, nomeInvalidoValidator]]
});
```

------

## 🧪 Exercício prático

Crie um componente `cadastro-cliente` com os seguintes campos:

- Nome (mínimo 2 letras)
- Email (obrigatório e válido)
- Idade (mínimo 18 anos)

Requisitos:

- Exiba mensagens de erro claras
- Valide os campos no envio
- Mostre um alerta com os dados do cliente se o formulário estiver válido

------

## ✅ Conclusão do módulo

Você aprendeu:

- A diferença entre formulários template-driven e reativos
- A criar e configurar formulários reativos com `FormBuilder`
- A aplicar validações integradas e customizadas
- A exibir mensagens de erro no template
- A garantir que o formulário só seja enviado quando válido

