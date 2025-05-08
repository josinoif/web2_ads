
## Módulo 1 – Introdução ao Angular

### Objetivo do Módulo:

Ao final deste módulo, o aluno será capaz de:

- Entender o que é o Angular e onde ele se encaixa no desenvolvimento web.
- Instalar o Angular CLI e criar um novo projeto.
- Compreender a estrutura de um projeto Angular.
- Executar o projeto localmente e visualizar a aplicação no navegador.

------

### 1.1 O que é Angular?

- Framework frontend baseado em TypeScript criado pelo Google.
- Utilizado para criar aplicações web do tipo SPA (Single Page Applications).
- Vantagens:
  - Modularidade (componentes e serviços)
  - Tipagem estática com TypeScript
  - Ferramentas integradas (roteamento, HTTP, formulários)
  - Comunidade e suporte corporativo

📘 *Explicação teórica:*
 Angular != AngularJS (AngularJS é a versão 1.x; Angular atual é reescrito em TypeScript)

------

### 1.2 Instalando o Angular CLI

📦 Pré-requisitos:

- Node.js e npm instalados
- Terminal com permissões administrativas

📘 *Comando para instalar o CLI:*

```bash
npm install -g @angular/cli
```

📘 *Verificar instalação:*

```bash
ng version
```

------

### 1.3 Criando um novo projeto Angular

📘 *Comando:*

```bash
ng new minha-aplicacao
```

📝 Durante o processo:

- Escolher usar roteamento (`Yes`)
- Selecionar estilo (recomenda-se `CSS` ou `SCSS`)

📘 *Rodar o servidor de desenvolvimento:*

```bash
cd minha-aplicacao
ng serve
```

🌐 Acesse a aplicação:
 `http://localhost:4200`

------

### 1.4 Estrutura de Diretórios

```text
minha-aplicacao/
├── src/
│   ├── app/
│   │   ├── app.component.ts     <- Componente principal
│   │   ├── app.module.ts        <- Módulo raiz
│   ├── assets/                  <- Recursos estáticos
│   ├── environments/            <- Configurações por ambiente
├── angular.json                 <- Configuração do Angular
├── package.json                 <- Dependências e scripts
```

🔎 **Explicação:**

- `app.module.ts`: ponto de entrada da aplicação (declara os módulos e componentes usados)
- `app.component.ts/html/css`: primeiro componente renderizado

------

### 1.5 Executando e Modificando o Primeiro Componente

📘 *Abrir o arquivo `src/app/app.component.html`*
 Substituir o conteúdo por:

```html
<h1>Olá, Angular!</h1>
<p>Essa é minha primeira aplicação em Angular.</p>
```

🔄 Salvar e ver o navegador atualizar automaticamente!

------

### 1.6 Arquitetura de um Frontend em Angular

A arquitetura de um frontend em Angular é baseada em conceitos fundamentais que promovem modularidade, reutilização e escalabilidade. Abaixo estão os principais elementos que compõem essa arquitetura:

#### **Componentes**
- São as unidades básicas de construção da interface do usuário.
- Cada componente é composto por:
  - **HTML**: define a estrutura visual.
  - **CSS/SCSS**: define o estilo.
  - **TypeScript**: define a lógica e o comportamento.
- Exemplo de um componente:
  ```typescript
  @Component({
    selector: 'app-exemplo',
    templateUrl: './exemplo.component.html',
    styleUrls: ['./exemplo.component.css']
  })
  export class ExemploComponent {
    titulo = 'Meu Componente Angular';
  }
  ```

#### **Módulos**
- Agrupam componentes, serviços e outros módulos relacionados.
- O módulo raiz (`AppModule`) é o ponto de entrada da aplicação.
- Outros módulos podem ser criados para organizar funcionalidades específicas (ex.: `UserModule`, `AdminModule`).

#### **Serviços e Injeção de Dependência**
- Serviços são usados para lógica de negócios e compartilhamento de dados entre componentes.
- A injeção de dependência permite que serviços sejam facilmente reutilizados e testados.

#### **Roteamento**
- Gerencia a navegação entre diferentes páginas ou estados da aplicação.
- Configurado no arquivo `app-routing.module.ts`.
- Exemplo de configuração:
  ```typescript
  const routes: Routes = [
    { path: '', component: HomeComponent },
    { path: 'sobre', component: SobreComponent }
  ];
  ```

#### **Diretivas**
- Permitem manipular o DOM de forma declarativa.
- Exemplos:
  - **Estruturais**: `*ngIf`, `*ngFor`.
  - **Atributos**: `[ngClass]`, `[ngStyle]`.

#### **Pipes**
- Transformam dados para exibição.
- Exemplo: `{{ preco | currency:'BRL' }}`.

#### **Comunicação entre Componentes**
- **Input/Output**: permite que componentes pais e filhos troquem dados.
- **EventEmitter**: usado para emitir eventos de um componente filho para o pai.

#### **State Management (Gerenciamento de Estado)**
- Para aplicações maiores, bibliotecas como `NgRx` ou `Akita` podem ser usadas para gerenciar o estado global.

🔎 **Resumo:**
A arquitetura Angular é projetada para ser modular e escalável, permitindo que equipes trabalhem de forma eficiente em projetos de qualquer tamanho.

------

### 🧪 Exercício Prático 1

> ✅ Crie um novo projeto chamado `hello-angular`, rode localmente e altere o conteúdo do `app.component.html` para exibir seu nome e uma mensagem de boas-vindas.

