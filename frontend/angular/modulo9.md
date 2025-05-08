# ✅ Módulo 9 – Boas Práticas e Estrutura de Projeto Angular

## 🎯 Objetivo do módulo

Neste módulo, você aprenderá:

- Como organizar os arquivos e módulos do seu projeto Angular
- Como estruturar componentes, serviços, interceptadores e guards de forma reutilizável
- A aplicar o padrão **Core & Shared Modules**
- A seguir convenções de nomes e separação de responsabilidades
- A preparar sua aplicação para crescer com qualidade e manutenibilidade

------

## 9.1 Estrutura básica recomendada

Uma estrutura limpa, modular e escalável:

```
src/
├── app/
│   ├── core/            → Serviços de uso geral, interceptores, guards, etc.
│   ├── shared/          → Componentes, pipes, diretivas e módulos reutilizáveis
│   ├── auth/            → Login, AuthService, AuthGuard
│   ├── produtos/        → CRUD de produtos
│   ├── app-routing.module.ts
│   └── app.module.ts
```

------

## 9.2 Padrão Core e Shared

### 🧠 CoreModule

Contém recursos **usados uma única vez**, como:

- `AuthService`
- `AuthGuard`
- `HttpInterceptor`
- `NavbarComponent` (se fixo)
- `AppInitializer`

```bash
ng generate module core
```

### 🧠 SharedModule

Contém **recursos reutilizáveis em vários lugares**, como:

- Botões, inputs personalizados
- Pipes
- Diretivas
- Componentes de alerta, loading, etc.

```bash
ng generate module shared
```

Exemplo de exportação no `shared.module.ts`:

```ts
@NgModule({
  declarations: [AlertaComponent],
  imports: [],
  exports: [AlertaComponent]
})
export class SharedModule {}
```

------

## 9.3 Organização por domínios/funcionalidades

Cada funcionalidade da aplicação (como `produtos`, `clientes`, `pedidos`) deve ter seu próprio módulo:

```
app/
├── produtos/
│   ├── produtos.component.ts
│   ├── produto-form.component.ts
│   ├── produtos.service.ts
│   └── produtos-routing.module.ts
ng generate module produtos --routing
```

> Isso permite **lazy loading** e separação clara por contexto.

------

## 9.4 Boas práticas de nomeação

| Elemento    | Padrão de nome                    |
| ----------- | --------------------------------- |
| Componentes | `nome-feature.component.ts`       |
| Serviços    | `nome-feature.service.ts`         |
| Guards      | `auth.guard.ts`, `admin.guard.ts` |
| Pipes       | `capitalizar.pipe.ts`             |
| Diretivas   | `destacar.directive.ts`           |

------

## 9.5 Boas práticas de código

- **SRP (Single Responsibility Principle)**: cada componente/serviço deve ter uma única responsabilidade
- **Não misture lógica de negócio no template**
- **Use tipos e interfaces com TypeScript** – evite `any`
- **Evite lógica duplicada** – extraia para serviços
- **Use `async` pipes sempre que possível** com `Observables`
- **Evite acessar diretamente o `localStorage`** – crie um wrapper (como `AuthService`)
- **Centralize tratamento de erros e exibição de mensagens**

------

## 9.6 Organizando ambientes

No Angular, você pode usar `environment.ts` para configurar URLs e chaves da aplicação:

```ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};
```

No código:

```ts
import { environment } from 'src/environments/environment';

this.http.get(`${environment.apiUrl}/produtos`);
```

> Em produção, `environment.prod.ts` será usado automaticamente pelo build.

------

## 9.7 Separando responsabilidades com clareza

| Camada          | Responsabilidade                          |
| --------------- | ----------------------------------------- |
| Componentes     | Interface do usuário                      |
| Serviços        | Lógica de negócios e acesso a dados       |
| Interceptors    | Manipulação de requisições/respostas HTTP |
| Guards          | Controle de acesso às rotas               |
| Pipes/Diretivas | Apresentação e comportamento no template  |

------

## 9.8 Configuração de lint e formatação

Recomenda-se:

- **ESLint** ou **TSLint** (Angular CLI já inclui)
- **Prettier** para padronização de estilo
- **EditorConfig** para consistência entre editores

------

## 🧪 Exercício prático

1. Refatore sua aplicação criando os módulos:
   - `core`
   - `shared`
   - `auth`
   - `produtos`
2. Mova `AuthService`, `AuthGuard` e `TokenInterceptor` para `core`
3. Mova `AlertaComponent` para `shared`
4. Agrupe componentes de produtos no módulo `produtos`
5. Use `environment.ts` para configurar a URL da API

------

## ✅ Conclusão do módulo

Você aprendeu:

- A estruturar projetos Angular com foco em escalabilidade
- A usar `CoreModule` e `SharedModule` para modularizar melhor
- A aplicar boas práticas de nomeação, separação de responsabilidades e organização por funcionalidade
- A preparar sua aplicação para ambientes reais e times de desenvolvimento

