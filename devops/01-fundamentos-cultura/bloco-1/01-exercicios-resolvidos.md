# Exercícios Resolvidos — Bloco 1

**Tempo estimado:** 20 a 30 minutos.

Estes exercícios testam sua compreensão conceitual do Bloco 1. Tente responder **antes** de ler a resolução.

---

## Exercício 1 — A origem dos silos

**Enunciado:**

Em muitas empresas, as áreas de Desenvolvimento e Operação foram historicamente organizadas como times separados, cada um reportando a um gestor diferente e com bônus atrelados a métricas distintas. Explique, com suas palavras, por que essa estrutura **inevitavelmente** gera conflito entre os dois times, mesmo quando todos agem com a melhor das intenções.

### Resolução

O conflito é **estrutural**, não comportamental. Ele surge porque as duas áreas recebem **incentivos opostos para a mesma ação** — a mudança em produção.

- **Dev é recompensado por entregar funcionalidades.** Para Dev, mais mudança = melhor desempenho.
- **Ops é recompensado por manter o sistema estável.** Para Ops, menos mudança = menor chance de incidente = melhor desempenho.

Quando Dev tenta entregar uma mudança, Ops vê uma **ameaça à sua métrica**. Quando Ops trava ou posterga uma mudança, Dev vê uma **barreira à sua métrica**. Nenhum dos dois lados está sendo "mau" — os dois estão respondendo **racionalmente** aos incentivos que receberam.

É por isso que DevOps insiste que a mudança **não é um problema cultural pessoal** ("essas pessoas são difíceis de lidar") e sim um **problema de design organizacional**: enquanto os incentivos estiverem assim, o conflito se reproduz sozinho, independentemente de quem está nos cargos.

> **Conexão com a CloudStore:** esse é exatamente o motivo pelo qual, no cenário, Dev "joga por cima do muro" e Ops "reinicia e espera o próximo incêndio". Ninguém está agindo errado dentro do sistema que foi construído para eles.

---

## Exercício 2 — Identificando a Parede da Confusão

**Enunciado:**

Classifique cada uma das seguintes frases como **(A) sintoma típico da Parede da Confusão**, **(B) prática DevOps saudável**, ou **(C) neutro/depende do contexto**:

1. "O deploy só pode ser feito às sextas-feiras às 22h pela equipe de infra."
2. "Dev e Ops participam juntos do desenho da arquitetura do novo serviço."
3. "Usamos Kubernetes para rodar tudo."
4. "Se algo quebra em produção, eu abro um chamado no Jira e espero."
5. "Todo engenheiro do time tem acesso ao Grafana de produção em modo leitura."
6. "A equipe de Dev entra na escala de on-call uma semana por rodízio."
7. "Temos um 'DevOps Engineer' que cuida do Jenkins."
8. "Documentamos incidentes em postmortem, focando em quem falhou."

### Resolução

| # | Frase | Classificação | Justificativa |
|---|-------|---------------|---------------|
| 1 | Deploy só sexta 22h pela infra | **A** — Parede | Janela rígida + equipe exclusiva = separação Dev/Ops institucionalizada. |
| 2 | Dev e Ops juntos no desenho | **B** — Saudável | Colaboração desde o início; Ops influencia decisões arquiteturais. |
| 3 | Usamos Kubernetes | **C** — Depende | K8s é ferramenta; pode coexistir com cultura ruim. |
| 4 | Abre chamado e espera | **A** — Parede | Comunicação assíncrona por ticket é sintoma clássico de silo. |
| 5 | Todos têm Grafana de prod (leitura) | **B** — Saudável | Visibilidade compartilhada; Dev consegue diagnosticar sem pedir a Ops. |
| 6 | Dev no on-call rotativo | **B** — Saudável | "You build it, you run it" (mantra DevOps); incentivo compartilhado. |
| 7 | "DevOps Engineer" cuida do Jenkins | **A** — Parede (disfarçada) | É apenas Ops rebatizado. Criou-se um cargo para "fazer DevOps" em vez de transformar a organização. |
| 8 | Postmortem focado em quem falhou | **A** — Parede | Cultura de culpa; aprendizado fica comprometido. O correto é **blameless postmortem** (veja Bloco 4). |

---

## Exercício 3 — DevOps ≠ ferramenta

**Enunciado:**

Um colega afirma: *"Nossa empresa já adotou DevOps. Compramos GitLab, Docker e subimos Kubernetes."* Avalie criticamente essa afirmação em até 5 linhas.

### Resolução (exemplo)

A afirmação confunde **habilitadores técnicos** com **transformação DevOps**. GitLab, Docker e Kubernetes são ferramentas poderosas, mas **não alteram sozinhas** a forma como Dev e Ops colaboram, compartilham responsabilidade ou aprendem com falhas. É possível ter toda essa stack e manter silos, on-call apenas para Ops, deploy manual em janela e postmortem de culpa. DevOps é primariamente **cultura e processo**; ferramenta é **consequência**, não causa.

> Conforme Kim et al. (2016), no *The DevOps Handbook*, os Três Caminhos exigem mudanças em fluxo, feedback e aprendizado — nenhuma dessas dimensões é resolvida automaticamente por trocar de ferramenta.

---

## Exercício 4 — Aplicação à CloudStore

**Enunciado:**

Revise os 10 sintomas do [cenário da CloudStore](../00-cenario-pbl.md). Identifique **três sintomas** que são **manifestações diretas da Parede da Confusão** e justifique.

### Resolução (exemplo de resposta correta)

Qualquer combinação coerente de três entre: 1, 2, 4, 7, 9. Exemplo:

- **Sintoma 2 — "Jogar por cima do muro":** literal. Dev entrega um `.jar` sem documentação executável; Ops precisa "adivinhar". É a metáfora original da Parede da Confusão tornada prática diária.
- **Sintoma 4 — "Funciona na minha máquina":** clássico da Parede. A separação de ambientes Dev/Ops e a falta de ferramental compartilhado (containers, IaC) fazem com que a responsabilidade pelo problema seja sempre "do outro".
- **Sintoma 9 — "On-call só de Ops":** incentivo desalinhado institucionalizado. Dev não sofre a consequência do que constrói; a dor é toda de Ops. Sem essa realimentação, Dev não tem pressão para escrever código operável.

---

## Exercício 5 — Por que o "Time DevOps" é um anti-padrão?

**Enunciado:**

Um gestor sugere: *"Vamos resolver nossos problemas criando um Time DevOps entre Dev e Ops."* Explique por que essa solução, na prática, tende a **piorar** o problema em vez de resolvê-lo.

### Resolução

A sugestão parte da intenção correta (derrubar barreiras), mas aplica a solução errada: ela cria **um terceiro silo**. O que acontece:

1. **Dev continua separado** — agora "joga por cima do muro" para o Time DevOps em vez de para Ops.
2. **Ops continua separado** — recebe coisas já "DevOps-ificadas" pelo novo time.
3. **O Time DevOps vira gargalo** — toda mudança passa por ele.
4. **Responsabilidade pelo produto continua difusa** — na verdade, fica pior, porque agora são três partes debatendo de quem é a culpa.

A solução correta é **estrutural**: Dev e Ops compartilham objetivos, rituais, ferramentas, métricas e responsabilidade pelo sistema em produção. Em vez de criar um time entre eles, **funde-se a responsabilidade** — mantendo especializações (Dev ainda é Dev, Ops ainda é Ops), mas alinhando os incentivos.

Modelos organizacionais conhecidos que tentam implementar isso:

- **"You build it, you run it"** (Amazon): o time que constrói opera.
- **Platform Team / Enabling Team** (*Team Topologies*, Skelton & Pais): um time fornece **plataforma** (self-service) para que os times de produto rodem suas próprias cargas. Este modelo é útil para a CloudStore — os 8 Ops viram uma *Platform Team* e os 40 Devs passam a rodar o que constroem com apoio dessa plataforma.

> **Leitura complementar recomendada:** *Team Topologies* (Matthew Skelton & Manuel Pais, IT Revolution 2019) — não está na pasta `books/`, mas é o livro contemporâneo mais influente sobre como estruturar times em organizações DevOps.

---

## Exercício 6 — Desafiador (opcional)

**Enunciado:**

Em qual contexto/situação DevOps **não** deveria ser a prioridade de uma organização? Dê um exemplo.

### Resolução (exemplo de resposta)

DevOps **não é bala de prata**. Há contextos em que investir em transformação DevOps antes de outros problemas seria desperdício:

- **Produto sem product-market fit:** se a empresa ainda não sabe *o que* está construindo, entregar *mais rápido* algo errado piora as coisas. Validação de produto vem antes.
- **Arquitetura fundamentalmente quebrada:** um monolito com acoplamento extremo não se resolve com pipeline. Pode ser necessário refatorar partes antes.
- **Liderança tóxica:** se a alta liderança pratica cultura de culpa e microgestão, qualquer prática DevOps será sabotada. O problema é anterior.
- **Regulação externa pesada** (ex.: aviação, equipamento médico certificado): ciclos curtos podem literalmente ser proibidos por regulação — aqui o foco é **DevOps compatível com certificação** (gates formais automatizados).

DevOps funciona bem quando o problema é de **fluxo, colaboração e confiabilidade**. Quando o problema é **outro**, DevOps ajuda pouco — e pode até distrair.

---

## Próximo passo

Quando se sentir confortável com estes conceitos, siga para o **[Bloco 2 — Modelo CALMS](../bloco-2/02-modelo-calms.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — O que é DevOps e a Parede da Confusão](01-o-que-e-devops.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Bloco 2 — Modelo CALMS](../bloco-2/02-modelo-calms.md) |

<!-- nav:end -->
