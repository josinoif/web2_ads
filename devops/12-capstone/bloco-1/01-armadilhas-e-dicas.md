# Fase 1 — Armadilhas, dicas e orientações de banca

> Complemento à [Fase 1 — Design e fundação](./01-fase-design.md). Aqui você encontra um anexo pragmático: o que avaliadores costumam buscar, dúvidas recorrentes, critérios não-escritos.

---

## 1. Como a banca lê a Fase 1

Nenhuma banca lê 15 ADRs ao vivo. **Ela escolhe 2-3** e te pergunta:

1. *"Por que essa decisão e não a alternativa?"*
2. *"O que mudaria se o contexto fosse outro?"*
3. *"Qual risco você aceitou ao escolher assim?"*

Seu ADR precisa **responder as três** sozinho — sem que você precise "completar de cabeça". Se o ADR omite alternativas, você perde pontos sem abrir a boca.

---

## 2. Anti-padrões que o professor reconhece de longe

- **ADR "ChatGPT boilerplate"**. Começa com "No contexto moderno de DevOps...". Nenhum contexto, nenhuma escolha local.
- **Datas todas no mesmo dia**. Todas as 8 ADRs criadas em um único commit — sem registro de **evolução**.
- **RFC sem RFC**. Documento chamado "RFC" mas que apenas descreve a escolha já feita, sem alternativas discutidas.
- **Charter genérico copiado**. "Valorizamos colaboração, excelência e inovação." Inútil.
- **Diagrama Mermaid copiado de tutorial**. Se o diagrama não sobrevive à pergunta "explique esse nó aqui", não é seu.

---

## 3. Dicas operacionais

### 3.1 Escrevendo ADR em 30 minutos

1. Título curto (≤ 12 palavras).
2. Uma **pergunta** em "Contexto" (ex.: *"Como armazenar localização com busca eficiente por raio?"*).
3. Duas alternativas **reais** (não palha).
4. A decisão com **3 razões** (técnicas, não estilo pessoal).
5. Duas consequências **negativas** (ser honesto sobre o custo).
6. Campo "Revisão" com condição: *"Revisitar quando tivermos > 100k reports/mês"*.

### 3.2 Escrevendo RFC em 90 minutos

1. "Problema" em 1 parágrafo.
2. "Alternativas consideradas" em lista com 3 opções.
3. "Proposta" em 2 parágrafos — sem UML desnecessário.
4. "Rollout faseado" — vincula com este capstone (Fases 1-4).
5. "Métricas de sucesso" — 2 números, datas.
6. "Riscos principais" — 3 itens.
7. "O que não está sendo decidido agora" — importante para honestidade.

### 3.3 Revisando ADR sozinho (proxy de code review)

Na sequência, em papel ou numa issue:

- **Challenge 1**: existe uma alternativa C que você não listou?
- **Challenge 2**: essa decisão se justifica daqui a 6 meses se o escopo triplicar?
- **Challenge 3**: se você for trocado por outro engenheiro amanhã, ele entende em 5 minutos?

Se nota falhou em alguma, reescreva antes de aceitar.

---

## 4. Perguntas que a banca faz e você precisa conseguir responder

1. *"Por que não microsserviços desde o dia 1?"*  
   → Resposta boa: *"Custo de operação e de observação multiplica; MVP em monolito modular até a dor aparecer. ADR-XXX registra quando reconsidero."*

2. *"Por que Postgres e não Mongo para dados com foto e localização?"*  
   → *"Relacional cobre multitenancy, LGPD, integridade referencial; PostGIS resolve lat/long sem custo; foto vai para blob-storage separado."*

3. *"E se o cidadão apaga a conta? LGPD exige eliminação."*  
   → Resposta boa cita: (a) inventário de dados; (b) processo de anonimização retroativa em logs; (c) prazo máximo (15 dias LGPD).

4. *"Qual é o cenário em que você rollba um ADR?"*  
   → Resposta boa: *"Quando uma premissa do 'Contexto' muda; registro via ADR novo que supersedes o antigo."*

5. *"Quem revisou sua RFC já que você é o único autor?"*  
   → Aceita-se *"eu mesmo, em dois momentos separados (escrita + crítica em 48h); registrei o segundo na seção de histórico"*. **Não aceita** *"ninguém"*.

---

## 5. Ferramentas úteis nesta fase

- **adr-tools** (shell script) para numerar ADRs. Opcional, mas organiza.
- **Mermaid Live** (mermaid.live) para prototipar diagramas.
- **Structurizr** / **C4 model** para projetos maiores (fora do capstone, mas vale conhecer).
- **`pre-commit`**: ative já na Fase 1 para lint/format automáticos.
- **`commitlint`** + **`Conventional Commits`**: define padrão de mensagem de commit e permite changelog automático (Fase 4 agradece).

---

## 6. Sinais de que você está pronto para a Fase 2

- Você consegue explicar em 60 segundos o produto inteiro sem pausar.
- Você escolhe 3 ADRs e aponta onde cada um pode "quebrar" se o contexto mudar.
- Seu colega (ou orientador) consegue ler o README e **entender** para que serve o sistema **sem perguntar**.
- CI verde; commit pattern consistente.
- Você dorme a noite sem sentir que "preciso voltar para arrumar aquilo".

Se tudo acima se aplica, rode `git tag v0.1.0-design-ready` e siga para a Fase 2.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 1 — Design e fundação](01-fase-design.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Fase 2 — Entrega contínua end-to-end](../bloco-2/02-fase-entrega.md) |

<!-- nav:end -->
