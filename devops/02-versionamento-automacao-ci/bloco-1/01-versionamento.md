# Bloco 1 — Versionamento como Controle de Complexidade

O versionamento não é apenas “guardar versões do código”. É um **mecanismo de controle de complexidade** e de **redução de risco** quando várias pessoas alteram o mesmo sistema. Neste bloco você verá conceitos fundamentais, estratégias de branching e o papel do Git e dos Pull Requests nesse contexto.

---

## 1. Controle de versão distribuído

Em um **controle de versão distribuído** (como o Git), cada desenvolvedor tem uma **cópia completa** do repositório. Não existe um “servidor central” obrigatório para trabalhar: você pode fazer commits, branches e merges localmente e só depois sincronizar (por exemplo, com o GitHub ou GitLab).

### Por que isso importa para DevOps?

- **Trabalho offline** e integração depois.
- **Múltiplos remotos** (origin, upstream, forks).
- **Histórico rico** (quem, quando, por quê) — base para auditoria e debugging.

### Comandos essenciais

```bash
# Clonar repositório (cópia local completa)
git clone https://github.com/org/repo.git
cd repo

# Ver estado e histórico
git status
git log --oneline -5

# Configurar identidade (uma vez por máquina)
git config user.name "Seu Nome"
git config user.email "seu@email.com"
```

---

## 2. Git como ferramenta sociotécnica

O Git não é só tecnologia: ele **molda o fluxo de trabalho** do time. Decisões como “usamos muitas branches longas ou integramos direto na main?” têm impacto em:

- **Risco de integração** — branches longas acumulam divergência e conflitos.
- **Visibilidade** — o que está “em progresso” fica explícito nas branches e nos PRs.
- **Revisão de código** — Pull/Merge Requests tornam a integração um ato consciente e revisado.

Humble & Farley, em *Entrega Contínua*, enfatizam que **integrar com frequência reduz o risco de integração tardia**. Ou seja:

- **Branch longa** → risco acumulado, merge difícil, bugs descobertos tarde.
- **Merge frequente** → risco controlado, conflitos menores, feedback rápido.

> **Referência:** Humble, J.; Farley, D. *Entrega Contínua: como entregar software de forma confiável e rápida*. Rio de Janeiro: Alta Books. (Capítulos sobre integração contínua e gestão de configuração.)

No SRE, **simplicidade** e **automação** são princípios fundamentais. Estratégias de branching muito complexas (dezenas de branches longas) aumentam a complexidade operacional e o toil. Ver *Site Reliability Engineering* (O'Reilly), sobre eliminação de toil e simplicidade.

---

## 3. Estratégias de branching

Escolher uma estratégia é **modelar o fluxo de trabalho** do time. Não existe “a melhor” em absoluto; existe a que melhor se adequa ao contexto (tamanho do time, ritmo de release, regulamentação).

### 3.1 Git Flow

O **Git Flow** foi popularizado por Vincent Driessen e define duas branches de longa duração e três tipos de branches de apoio, com papéis bem delimitados.

#### Branches principais

| Branch | Papel | Regra prática |
|--------|--------|----------------|
| **`main`** (ou `master`) | Reflete o que está **em produção**. Cada commit aqui corresponde a uma versão liberada (ou a um hotfix). | Só recebe merge de `release/*` ou `hotfix/*`; não se commita direto. |
| **`develop`** | Linha de **integração** do time. Acumula todas as funcionalidades prontas que ainda não foram liberadas em uma release. | Recebe merge de `feature/*`; daqui saem as branches `release/*`. |

#### Branches de apoio

| Tipo | Origem | Destino | Uso |
|------|--------|---------|-----|
| **`feature/*`** | `develop` | `develop` | Nova funcionalidade ou melhoria; vida típica de dias a algumas semanas. |
| **`release/*`** | `develop` | `main` e `develop` | Preparar uma versão para produção: ajustes de versão, changelog, correções de último momento; não se adiciona feature nova aqui. |
| **`hotfix/*`** | `main` | `main` e `develop` | Correção urgente em produção (bug crítico, vulnerabilidade); depois do merge em `main`, deve ser levado de volta para `develop`. |

Diagrama do fluxo:

```text
main     ----*--------*--------*--------*  (releases / hotfixes)
              \      /  \      /  \   /
release/1.2    *----*    \    /    *
              \          \  /
develop        -*--*----*--*--*--*--------
                    \    /  \    /
feature/login        *--*    *--*  (merge em develop)
feature/pagamento         *------*
```

#### Comandos típicos (resumo)

```bash
# Nova feature (a partir de develop atualizada)
git checkout develop && git pull origin develop
git checkout -b feature/nome-da-feature
# ... commits ...
git checkout develop && git merge --no-ff feature/nome-da-feature
git push origin develop

# Abrir release (quando develop está pronta para virar versão X.Y)
git checkout develop && git pull origin develop
git checkout -b release/1.2.0
# Ajustes de versão, changelog; correções leves permitidas
git checkout main && git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release 1.2.0"
git checkout develop && git merge --no-ff release/1.2.0
git push origin main develop --tags

# Hotfix (bug crítico em produção)
git checkout main && git pull origin main
git checkout -b hotfix/1.2.1
# ... correção ...
git checkout main && git merge --no-ff hotfix/1.2.1
git tag -a v1.2.1 -m "Hotfix 1.2.1"
git checkout develop && git merge --no-ff hotfix/1.2.1
git push origin main develop --tags
```

#### Casos de uso próximos da vida real

**Caso 1 — Sistema bancário ou de pagamentos com releases trimestrais**

- A instituição exige **versão estável em produção** e **releases planejadas** (ex.: a cada trimestre), com testes de regressão e aprovação de compliance antes de ir ao ar.
- **`main`** = exatamente o que está em produção; **`develop`** = próxima versão em construção. Features entram em **`feature/*`** e só vão para **`develop`** após revisão e testes. Quando a data da release se aproxima, abre-se **`release/2.1.0`**: congelam-se funcionalidades novas, fazem-se apenas ajustes de versão e correções pequenas; após homologação e aprovação, o merge em **`main`** e a tag **v2.1.0** marcam a release oficial.
- **Por que Git Flow faz sentido:** separação clara entre “em produção” e “próxima release”; hotfix em produção não mistura com desenvolvimento da próxima versão.

**Caso 2 — Produto SaaS com versão “enterprise” e outra “cloud”**

- Existem **dois “sabores” de release** (enterprise instalado no cliente vs cloud), mas o código é um só. O time usa **`main`** como linha de produção estável; **`develop`** integra tudo; **`release/enterprise-2025.1`** e **`release/cloud-2025.1`** podem ser abertas a partir de **`develop`** em momentos diferentes, cada uma com seus ajustes de configuração e documentação antes do merge em **`main`** e da tag correspondente.
- **Por que Git Flow ajuda:** várias release branches em paralelo sem poluir **`main`**; **`main`** continua sendo o histórico “o que já foi liberado”.

**Caso 3 — Bug crítico em produção (ex.: cálculo de juros errado)**

- Foi para o ar a versão **1.3.0**; em **`develop`** já há código da **1.4.0**. Descobre-se um erro grave no cálculo de juros em produção.
- Abre-se **`hotfix/1.3.1`** a partir de **`main`** (não de **`develop`**). A correção é feita só nessa branch; depois merge em **`main`**, tag **v1.3.1**, deploy da correção. Em seguida, merge de **`hotfix/1.3.1`** em **`develop`** para que a correção não se perca na próxima release.
- **Por que esse fluxo:** evita misturar as novas features da 1.4.0 com a correção urgente; produção recebe apenas o hotfix; **`develop`** fica alinhada ao que foi corrigido.

**Caso 4 — Quando o Git Flow começa a pesar**

- Time pequeno, deploy contínuo (várias vezes por semana), **`main`** sempre estável. Manter **`develop`** + **`release/*`** + **`feature/*`** gera **toil**: dois merges por feature (feature → develop, depois release → main), conflitos entre **release** e **develop**, e a pergunta “em qual branch eu trabalho?” vira constante.
- Nesse cenário, **GitHub Flow** ou **Trunk-Based** costumam reduzir complexidade e atraso; o Git Flow continua fazendo sentido quando há **releases planejadas**, **ciclos longos** e necessidade explícita de uma “versão de produção” estável e auditável.

#### Quando faz sentido e quando pesa

| Faz sentido | Pesa |
|-------------|------|
| Releases planejadas (mensais, trimestrais); necessidade de “versão de produção” estável e rastreável. | Deploy contínuo; time pequeno; poucas releases por ano mas muitas entregas por semana. |
| Múltiplas versões em produção (ex.: cliente A na 1.2, cliente B na 1.3) ou compliance/auditoria por versão. | Muitos merges (feature→develop, release→main, hotfix→main e develop); risco de **develop** ficar muito à frente de **main**. |
| Hotfixes que não podem misturar com funcionalidades ainda não validadas. | Dúvida sobre onde abrir branch (develop vs main); **release** longa vira “mini-develop” e conflitos aumentam. |

---

### 3.2 GitHub Flow

O **GitHub Flow** foi criado pelo GitHub para seu próprio desenvolvimento: uma única branch principal sempre implantável e branches de curta duração para cada mudança. Não há `develop` nem `release/*`; a história é simples e o deploy costuma ser por commit (ou por tag quando se precisa marcar uma versão).

#### Ideia central

| Conceito | Descrição |
|----------|-----------|
| **`main` sempre implantável** | Qualquer commit em `main` está pronto para ir a produção (ou para staging). Não se faz merge sem que o código esteja testado e revisado. |
| **Branches descritivas e curtas** | Cada feature, correção ou experimento vive em uma branch (ex.: `feature/login-oauth`, `fix/DEVPAY-42-juros`); vida típica de horas a poucos dias. |
| **Deploy por commit ou tag** | Não existe “branch de release”; deploys são disparados a partir de `main` (ou de tags como `v1.2.3` se o processo exigir versão numérica). |

#### Regras práticas

- **Nunca commitar direto em `main`** (exceto em repositórios muito pequenos ou correções triviais, conforme política do time). Toda mudança entra via Pull Request.
- **Branch sempre a partir de `main` atualizada** — `git checkout main && git pull && git checkout -b feature/nome` — para reduzir divergência e conflitos no merge.
- **Merge em `main`** só após revisão aprovada e pipeline de CI verde; depois do merge, a branch pode ser apagada.

Diagrama:

```text
main     ----*----*----*----*----*----*----*
              \  /  \  /  \  /
feature/a      *      *    *   (curtas, merge rápido)
feature/b           *------*
fix/issue-1                  *
```

#### Comandos típicos

```bash
# Nova feature ou correção (sempre a partir de main atualizada)
git checkout main
git pull origin main
git checkout -b feature/nome-da-feature
# ... commits ...
git push -u origin feature/nome-da-feature
# Abrir Pull Request: feature/nome-da-feature → main
# Após aprovação e CI verde: merge no GitHub/GitLab
# Localmente, após o merge:
git checkout main
git pull origin main
git branch -d feature/nome-da-feature

# Marcar versão para deploy (opcional)
git tag -a v1.2.3 -m "Release 1.2.3"
git push origin v1.2.3
```

#### Casos de uso próximos da vida real

**Caso 1 — Startup com deploy diário (ex.: DevPay)**

- Time de 5–8 pessoas; deploy para produção várias vezes por semana (ou diário). Não há “data de release” fixa; cada feature ou correção entra quando está pronta.
- **Fluxo:** desenvolvedor abre `feature/calculo-juros-compostos` a partir de `main`, trabalha 1–2 dias, abre PR; CI roda (build, testes, lint); após 1 aprovação e CI verde, merge em `main`; pipeline de deploy sobe para produção (ou staging primeiro). Não existe branch `develop` nem `release/1.2.0` — a “versão” é o estado atual de `main`.
- **Por que GitHub Flow:** poucos conceitos; todo mundo sabe que `main` é a verdade; integração frequente reduz conflitos e alinha com a ideia “branch longa = risco”.

**Caso 2 — API interna consumida por outros times**

- Um time mantém uma API (ex.: serviço de pagamentos); outros times dependem dela. As mudanças precisam ser estáveis e retrocompatíveis; deploys são frequentes mas controlados por CI e revisão.
- **Fluxo:** mudanças em branches `feature/*` ou `fix/*`; PR obrigatório com revisão; CI garante testes e compatibilidade; merge em `main` dispara deploy em staging e, após checagem, em produção. Tags como `v2.1.0` podem ser criadas em `main` para documentar “versões” sem manter branch de release.
- **Por que GitHub Flow:** uma única linha de verdade (`main`); mudanças pequenas e frequentes; rollback simples (reverter commit ou redeploy da tag anterior).

**Caso 3 — Correção urgente (hotfix) no GitHub Flow**

- Em produção há um bug crítico (ex.: endpoint retornando 500). Em Git Flow abriríamos `hotfix/*` a partir de `main`; no GitHub Flow o fluxo é o mesmo conceito, mas com outro nome: branch de correção a partir de `main`, PR, merge em `main`, deploy.
- **Fluxo:** `git checkout main && git pull && git checkout -b fix/correcao-endpoint-500`; correção mínima; PR com prioridade; merge em `main`; deploy. Não há branch `develop` para onde “levar” o fix — tudo já está em `main`.
- **Vantagem:** um único fluxo para feature e correção; menos regras (“é feature ou hotfix?”); o que importa é branch curta e merge rápido em `main`.

**Caso 4 — Quando o GitHub Flow não basta**

- A empresa exige **releases planejadas** com ciclo de homologação longo (compliance, testes de regressão manuais, aprovação de mudança). O que está em `main` não pode ir direto para produção; precisa de uma “versão candidata” congelada por um tempo.
- Nesse cenário, **Git Flow** (com `release/*`) ou um **GitHub Flow estendido** (branch `release/X.Y` criada a partir de `main` em datas específicas, só essa branch indo para homologação e depois produção) podem ser mais adequados. O GitHub Flow puro funciona melhor quando **main** pode ser implantado com frequência sem um estágio extra de “release congelada”.

#### Quando faz sentido e quando pesa

| Faz sentido | Pesa ou não encaixa |
|-------------|----------------------|
| Deploy contínuo ou muito frequente; time pequeno ou médio; uma única “versão” em produção. | Necessidade de várias versões em produção ao mesmo tempo (ex.: cliente A na 1.2, B na 1.3) sem múltiplas branches de release. |
| Integração frequente com `main`; menos conceitos para o time; CI e PR como únicos gates. | Ciclo de release longo com “congelamento” e homologação separada; compliance que exige branch de release auditável. |
| Hotfix = mesmo fluxo de feature (branch a partir de `main`, PR, merge); rollback por revert ou redeploy de tag. | Time muito grande com muitas features em paralelo sem disciplina de branch curta — `main` pode ficar instável se merges forem grandes ou mal testados. |

---

### 3.3 Trunk-Based Development

**Trunk-Based Development (TBD)** é uma estratégia em que há **uma única branch principal** (o “trunk”, em geral `main` ou `master`) e **todas as mudanças** são integradas nela com **muita frequência** — várias vezes ao dia por desenvolvedor. Branches de feature existem, mas são **muito curtas** (horas ou um dois dias no máximo) e o objetivo é **nunca** deixar o trunk muito à frente da branch nem a branch muito à frente do trunk.

#### Trunk-Based vs GitHub Flow

Ambas usam **uma branch principal** (`main`) e branches de curta duração; a diferença está no **ritmo e na disciplina**:

| Aspecto | GitHub Flow | Trunk-Based Development |
|---------|-------------|--------------------------|
| **Vida da branch** | Curta (dias); uma feature pode levar 1–3 dias na branch. | **Muito curta** (horas a 1–2 dias); integração no trunk **várias vezes ao dia**. |
| **Frequência de merge** | Um merge por feature/correção quando está pronto. | **Vários merges por dia**; o mesmo desenvolvedor pode integrar mais de uma vez no mesmo dia (ex.: em pedaços pequenos). |
| **Funcionalidade incompleta** | Pode ficar na branch até a feature estar “pronta” para o usuário. | Código incompleto pode ir para o trunk **desligado por feature flag**; a integração não espera a feature estar 100% visível. |
| **Ênfase** | “Main sempre implantável”; branches descritivas; PR e CI. | “**Nunca** divergir do trunk”; branch é um detalhe de implementação, não um lugar para “morar” por dias. |
| **Risco de conflito** | Baixo se branches forem curtas. | **Mínimo**: ninguém fica muito tempo fora do trunk; conflitos são pequenos e frequentes. |

Em resumo: **GitHub Flow** já é simples e integra com frequência; **Trunk-Based** leva isso ao extremo — branches são quase efêmeras e o trunk é a única linha de verdade, com integração contínua no sentido estrito (várias vezes ao dia). Humble & Farley tratam a integração contínua como prática de integrar ao mainline várias vezes ao dia; o TBD é a estratégia de branching que mais se alinha a isso.

#### Ideia central

- **Trunk = única fonte da verdade.** Tudo que está “em desenvolvimento” relevante está no trunk (mesmo que desligado por flag).
- **Branches de vida muito curta.** Servem para isolar um conjunto pequeno de commits (ex.: um refactor, uma função nova); assim que passam no CI e na revisão, viram merge no trunk.
- **Feature flags.** Permitem commitar e fazer merge de código “incompleto” no trunk: a funcionalidade fica desativada até estar pronta; assim evita-se branch longa “até a feature estar 100%”.
- **Main sempre verde.** O trunk deve passar no CI a todo momento; quem quebra corrige na hora (ou o merge é bloqueado).

Diagrama (vários merges no mesmo dia):

```text
main     *-*-*-*-*-*-*-*-*-*-*-*-*-*
          \/ \/ \/ \/ \/ \/
           merges muito frequentes (mesmo dev, mesmo dia)
```

#### Feature flags em poucas palavras

Em vez de manter uma branch `feature/nova-tela` por duas semanas até a tela estar pronta, o time:

1. Cria a branch, implementa em **pedaços pequenos**, faz merge no trunk **várias vezes** (código atrás de uma flag `nova_tela_habilitada = false`).
2. O trunk continua estável; a nova tela não aparece para o usuário.
3. Quando tudo está pronto, muda-se a flag (por config, deploy ou outro mecanismo) e a funcionalidade é ativada. A branch já foi apagada há tempo.

Isso exige disciplina (não commitar código quebrado mesmo “desligado”) e uma forma de ligar/desligar features (arquivo de config, variável de ambiente, serviço de feature flags).

#### Comandos típicos (ritmo trunk-based)

```bash
# Começar trabalho (trunk sempre atualizado)
git checkout main
git pull origin main
git checkout -b feature/refactor-calculo-juros

# Trabalhar em pedaço pequeno; integrar em seguida
# ... commits (ex.: 1–3 commits) ...
git fetch origin main
git rebase origin/main   # ou merge; manter branch alinhada ao trunk
git push origin feature/refactor-calculo-juros
# Abrir PR; revisão e CI; merge em main
# Repetir: novo branch para o próximo pedaço, ou continuar na mesma branch por mais algumas horas

# Não ficar mais de 1–2 dias na mesma branch sem integrar no trunk
```

#### Casos de uso próximos da vida real

**Caso 1 — Time de produto com deploy várias vezes ao dia**

- Equipe de 10 pessoas; cada um integra no `main` várias vezes por dia. Branches existem só para isolar 2–4 horas de trabalho; ao final da manhã ou do dia a branch já foi mergeada.
- **Fluxo:** branch `feature/ajuste-validacao-cpf` às 9h; 3 commits; PR às 12h; merge. À tarde, nova branch `feature/log-erro`; 2 commits; PR e merge no mesmo dia. O trunk avança dezenas de commits por dia; conflitos são raros porque ninguém fica muito tempo fora.
- **Por que TBD:** máxima frequência de integração; alinhado ao que Humble & Farley descrevem como integração contínua “várias vezes ao dia”.

**Caso 2 — Refatoração grande sem branch longa**

- Precisam refatorar um módulo de pagamentos (centenas de linhas). Em vez de uma branch `refactor/pagamentos` por duas semanas, o time quebra em **etapas pequenas**: cada etapa é uma branch de 1–2 dias, merge no trunk, próximo passo em outra branch. O trunk sempre compila e os testes passam; a refatoração avança em “fatias”.
- **Por que TBD:** evita “branch de refactor gigante” que um dia vira um merge impossível; integração contínua da própria refatoração.

**Caso 3 — Feature grande com feature flag**

- Nova jornada “assinatura recorrente” vai levar três semanas. Em vez de uma branch de três semanas, o time usa **feature flag**: cada pedaço da jornada é desenvolvido em branch curta, merge no trunk com a feature **desligada** (flag `assinatura_recorrente = false`). No trunk o código existe mas não é acessível ao usuário. No final, ativam a flag em produção.
- **Por que TBD:** a “feature longa” não vira “branch longa”; o trunk recebe o código em pedaços e continua deployável.

**Caso 4 — Quando Trunk-Based não encaixa**

- Time distribuído em fusos diferentes; revisão de PR leva 24h. “Integrar várias vezes ao dia” esbarra na disponibilidade de revisor e no tamanho mínimo de um PR que faça sentido revisar. Nesse contexto, **GitHub Flow** (branch de 1–2 dias, um merge por feature) pode ser mais realista.
- Ou: código legado com poucos testes; integrar no trunk com frequência pode deixar o trunk quebrado com frequência. Primeiro é preciso melhorar testes e disciplina; depois considerar TBD.

#### Quando faz sentido e quando pesa

| Faz sentido | Pesa ou não encaixa |
|-------------|----------------------|
| Time que consegue integrar no trunk várias vezes ao dia (revisão e CI rápidos). | Revisão lenta ou time distribuído; PRs demoram horas/dias para ser aprovados. |
| Disciplina de branches muito curtas e de não quebrar o trunk (testes, CI forte). | Código legado com pouca cobertura; trunk quebra fácil e o time não consegue corrigir na hora. |
| Uso de feature flags para funcionalidades grandes; aceitação de “código no trunk mas desligado”. | Cultura de “só merge quando a feature está 100% visível”; resistência a feature flags. |
| Objetivo explícito: mínimo risco de merge, máximo de integração (Humble & Farley). | Necessidade de branches de release longas ou múltiplas versões em produção (aí Git Flow ou variantes fazem mais sentido). |

> **Referência:** Humble & Farley discutem integração contínua e o perigo de branches longas; trunk-based é a estratégia que mais se aproxima do ideal “integrar várias vezes ao dia”.

---

## 4. Semantic Versioning (SemVer)

O **Semantic Versioning** padroniza o significado dos números de versão: `MAJOR.MINOR.PATCH` (ex.: `2.1.3`).

| Parte | Quando incrementar | Exemplo |
|-------|--------------------|---------|
| **MAJOR** | Mudanças incompatíveis com a API anterior | 1.0.0 → 2.0.0 |
| **MINOR** | Nova funcionalidade compatível com versões anteriores | 1.2.0 → 1.3.0 |
| **PATCH** | Correções de bugs compatíveis | 1.2.3 → 1.2.4 |

Exemplo de tags no Git:

```bash
# Marcar versão no repositório
git tag -a v1.2.3 -m "Release 1.2.3: correção no cálculo de juros"
git push origin v1.2.3

# Listar tags
git tag -l
```

Isso ajuda na **rastreabilidade** (qual versão está em produção?) e na **comunicação** com outros times ou consumidores da API.

---

## 5. Pull Requests como mecanismo de qualidade

Pull Requests (GitHub) ou Merge Requests (GitLab) são o momento em que o código **sai da máquina do desenvolvedor** e **entra na linha compartilhada**. Não são apenas “pedido de merge”: são o **gate** em que revisão, discussão e automação (CI) garantem que a integração não degrade a qualidade do repositório.

### Três funções do PR

| Função | Descrição |
|--------|-----------|
| **Revisão de código** | Outra pessoa (ou várias) lê o diff, sugere melhorias, aponta bugs ou riscos. Reduz erros e espalha conhecimento sobre o código. |
| **Discussão** | Comentários no PR alinham decisões (design, nomenclatura, trade-offs) antes do merge; o histórico fica registrado. |
| **Gates de qualidade** | O pipeline de CI roda no PR (build, testes, lint). Se falhar, o merge pode ser bloqueado até a correção — ninguém integra código quebrado. |

### O que faz um bom PR

- **Título e descrição claros** — o que mudou e por quê; link para issue/ticket se houver. Quem revisa entende o contexto sem adivinhar.
- **Tamanho razoável** — PRs pequenos (ex.: até 300–400 linhas de diff) são revisados mais rápido e com mais cuidado; PRs gigantes tendem a “aprovação por cansaço”.
- **Atomicidade** — um PR = uma ideia (uma feature, um fix, um refactor). Misturar várias coisas num PR dificulta revisão e rollback.
- **Branch atualizada com o alvo** — antes de pedir revisão, atualizar a branch com `main` (rebase ou merge) para evitar conflitos no merge final e garantir que o CI rode sobre o estado mais recente.

### Fluxo típico com PR

```bash
# Criar branch a partir da main atualizada
git checkout main
git pull origin main
git checkout -b feature/DEVPAY-42-calculo-juros

# Trabalhar, commitar (commits pequenos e descritivos)
git add .
git commit -m "feat(calculo): implementa juros compostos"

# Manter branch atualizada com main (reduz conflitos)
git fetch origin main
git rebase origin/main   # ou: git merge origin/main

# Enviar e abrir PR
git push -u origin feature/DEVPAY-42-calculo-juros
# No GitHub/GitLab: abrir Pull/Merge Request para main;
# preencher título e descrição; solicitar revisores.

# Após aprovação e CI verde: merge (no GitHub/GitLab).
# Localmente, após o merge:
git checkout main
git pull origin main
git branch -d feature/DEVPAY-42-calculo-juros
```

### Políticas comuns

| Política | Descrição |
|----------|------------|
| **Revisão obrigatória** | Exigir um ou mais aprovadores antes de permitir merge. Em áreas críticas (ex.: pagamentos), às vezes 2 aprovações ou aprovação de alguém específico (code owner). |
| **CI verde** | Merge só permitido se o pipeline (build, testes, lint) tiver passado no PR. Branch protection no GitHub/GitLab bloqueia merge com CI falho. |
| **Branch atualizada** | Regra “a branch deve estar atualizada com main” evita merge de código desatualizado e reduz conflitos. |
| **PRs pequenos** | Convenção ou limite informal de tamanho (ex.: “evitar PRs com mais de 500 linhas”) para manter revisão eficaz. |
| **Code owners** | Arquivos/pastas têm “donos”; PRs que os alteram exigem aprovação de pelo menos um deles (GitHub: CODEOWNERS; GitLab: approval rules). |

### Casos de uso próximos da vida real

**Caso 1 — Onboarding e espalhar conhecimento**

- Novo desenvolvedor entra no time; nos primeiros PRs, alguém mais experiente revisa e comenta não só bugs, mas convenções (como nomear funções, onde colocar testes, como tratar erros). O PR vira **canal de aprendizado**; o histórico de comentários serve para quem vier depois.
- **Por que PR:** revisão obrigatória garante que ninguém mergeia sozinho sem que pelo menos uma outra pessoa tenha visto o código e o contexto.

**Caso 2 — Área crítica (pagamentos, segurança)**

- Na DevPay, mudanças no módulo de cobrança exigem **2 aprovações** e **CI verde**; um dos aprovadores deve ser o “code owner” da pasta `payments/`. O PR descreve o que mudou e qual impacto em valores/transações; em caso de dúvida, a discussão fica registrada no PR.
- **Por que PR:** gate explícito antes do código entrar na linha principal; rastreabilidade de quem aprovou e do que foi discutido (útil para auditoria e pós-incidente).

**Caso 3 — Evitar regressão antes do merge**

- Antes de ter CI no PR, um desenvolvedor alterou um utilitário usado em vários lugares e fez merge; os testes não rodavam no PR. Em produção, outra parte do sistema quebrou. Depois disso, o time passou a exigir **CI verde no PR**: build e testes rodam na branch do PR; se falhar, o merge é bloqueado.
- **Por que PR:** o PR é o lugar onde a automação (CI) atua como gate; “não mergear com CI vermelho” vira política e reduz bugs que só apareceriam em produção.

**Caso 4 — Time distribuído e revisão assíncrona**

- Time em fusos diferentes; não dá para fazer pair programming o tempo todo. O desenvolvedor abre o PR ao final do dia; o revisor vê na manhã seguinte, deixa comentários; o autor responde e corrige no seu horário. O PR é o **ponto de encontro** para revisão assíncrona.
- **Por que PR:** discussão e aprovação não dependem de reunião; o histórico do PR documenta decisões e sugestões.

**Caso 5 — Quando o PR vira burocracia**

- PRs com **milhares de linhas**, **5 aprovadores** obrigatórios e **revisão que demora dias** viram gargalo: o time evita abrir PR ou faz merge sem revisão de verdade. Ou: todo PR exige aprovação de uma única pessoa sobrecarregada, e o trabalho fica na fila.
- **Ajustes:** limitar tamanho dos PRs (quebrar em vários); reduzir número de aprovadores ou usar code owners só onde importa; definir SLA de revisão (ex.: “revisar em até 1 dia útil”); garantir que o CI seja rápido para não segurar o merge por motivo evitável.

### Resumo da seção

- PR = **revisão** + **discussão** + **gate de qualidade (CI)** antes do código entrar na linha compartilhada.
- Bom PR: título/descrição claros, tamanho razoável, uma ideia por PR, branch atualizada com o alvo.
- Políticas típicas: revisão obrigatória, CI verde, branch atualizada, code owners em áreas críticas.
- Casos reais: onboarding, área crítica (pagamentos), evitar regressão com CI, time distribuído; cuidado para o PR não virar gargalo (PRs gigantes, muitos aprovadores, revisão lenta).

---

## 6. Conexão importante: branch longa vs merge frequente

| Prática | Efeito |
|---------|--------|
| **Branch longa** | Risco acumulado, conflitos grandes, bugs descobertos tarde, integração dolorosa. |
| **Merge frequente** | Risco controlado, conflitos pequenos, feedback rápido, alinhado a CI. |

Para a DevPay (e para qualquer time que queira reduzir risco e aumentar previsibilidade), a recomendação conceitual é: **preferir branches curtas e integração frequente**, alinhada a uma estratégia (GitHub Flow ou Trunk-Based) que faça sentido para o contexto.

---

## Resumo do bloco

- **Controle distribuído** (Git) permite trabalho local e histórico completo.
- **Git** é sociotécnico: influencia como o time integra e revisa código.
- **Estratégias:** Git Flow (mais estrutura), GitHub Flow (main sempre deployável), Trunk-Based (máxima integração).
- **SemVer** padroniza versões (MAJOR.MINOR.PATCH).
- **Pull Requests** são o mecanismo de qualidade e integração consciente; CI no PR reduz risco antes do merge.

---

## Referências bibliográficas para aprofundamento

O tema deste bloco (versionamento, branching, PRs) é abordado em livros e materiais de referência do módulo. A lista completa está em [referencias.md](../referencias.md); abaixo, referências direcionadas ao **aprofundamento do versionamento**.

### Livros e material da disciplina

| Obra / Material | Capítulos relacionados ao tema | Onde encontrar | Aproveitamento para este bloco |
|-----------------|-------------------------------|----------------|---------------------------------|
| **Humble & Farley — *Entrega Contínua*** | **Cap. 3 — Integração contínua** (risco de integração tardia, integrar frequentemente, build e testes no mainline). **Cap. 5 — Gestão de configuração** (versionamento de código, branching, ambientes). **Cap. 14 — Controle de versão e gestão de branches** (estratégias de branch, trunk-based, release branches). *Nota: números podem variar na edição em português.* | Alta Books (pt) / Addison-Wesley (en). Ver [referencias.md](../referencias.md). | Fundamentação de “integrar frequentemente”, risco de branches longas, pipeline como linha de produção. |
| **Google — *Site Reliability Engineering* (O'Reilly)** | **Cap. 5 — Eliminating Toil** (automação, trabalho repetitivo, quando não automatizar). **Part I — Introduction** (princípios de SRE, simplicidade). **Cap. 2 — O ciclo de vida de um incidente** (contexto de mudança e confiabilidade). *Índice: procure por "Toil", "Automation", "Simplicity".* | O'Reilly. Ver [referencias.md](../referencias.md). | Conexão entre automação, simplicidade operacional e fluxo de trabalho (branching); evite complexidade desnecessária. |
| **AWS Certified DevOps Engineer** | **Domínio: Continuous Integration and Continuous Delivery** — seções sobre CodeCommit (repositório Git na AWS), CodeBuild (build em nuvem), estratégias de branch e pipeline. *Consulte o blueprint oficial da certificação para números exatos de domínio/capítulo.* | Material de certificação AWS. Ver [referencias.md](../referencias.md). | Visão de repositório e pipeline em nuvem (CodeCommit, CodeBuild); complementa o uso de Git e estratégias de branch em ambiente enterprise. |

### Referências na web (versionamento e branching)

| Tema | Referência | Uso |
|------|------------|-----|
| **Git Flow** | Vincent Driessen — *A successful Git branching model* (blog/post clássico) | Origem do Git Flow; diagramas e convenções de `feature`, `release`, `hotfix`. |
| **GitHub Flow** | Documentação GitHub — *GitHub Flow* | Definição oficial: uma branch principal, branches curtas, deploy por commit. |
| **Trunk-Based Development** | trunkbaseddevelopment.com e artigos em *Continuous Delivery* | Prática de integração muito frequente; feature flags; comparação com outras estratégias. |
| **Semantic Versioning** | [semver.org](https://semver.org/) | Especificação MAJOR.MINOR.PATCH e boas práticas de versionamento. |
| **Git (documentação)** | [git-scm.com/doc](https://git-scm.com/doc) | Referência oficial de comandos e conceitos (branch, merge, rebase). |


No próximo bloco você verá **Integração Contínua (CI)** em detalhe: pipeline, build reprodutível, testes automatizados e feedback rápido.

**Próximo:** [Bloco 2 — Integração Contínua](../bloco-2/02-integracao-continua.md)  
**Exercícios deste bloco:** [01-exercicios-resolvidos.md](01-exercicios-resolvidos.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Cenário PBL — Problema Norteador do Módulo](../00-cenario-pbl.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 1 — Exercícios Resolvidos (Versionamento)](01-exercicios-resolvidos.md) |

<!-- nav:end -->
