# Glossário — Arquitetura

**Módulo:** [10 — Arquitetura](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **Estilo de arquitetura** | Organização recorrente de componentes e conectores (layered, MS, EDA…). |
| **Cliente–servidor** | Quem pede / quem atende (relação de papéis). |
| **N-tier** | Camadas em processos/máquinas distintos (ex.: UI · API · DB). |
| **Monólito** | Um deployável coeso; camadas costumam ser *internas*. |
| **Layered** | Organização em camadas com dependência tipicamente “para baixo”. |
| **SOA** | Estilo de integração/reuso de serviços; ESB é *uma* implementação possível. |
| **ESB** | Barramento de integração centralizado (pode virar SPOF). |
| **Anti-corruption layer (ACL)** | Adaptador que isola o modelo do portal do legado (ERP etc.). |
| **Microsserviços** | Serviços com deploy (e, idealmente, dados) independentes — não “N containers”. |
| **Pipeline de serviços** | Vários processos HTTP em cadeia (lab A) — *aproximação* didática de MS. |
| **Service-based** | Poucos serviços “grossos” — meio-termo monólito ↔ MS. |
| **EDA** | Arquitetura orientada a eventos (fila/tópico; reações assíncronas). |
| **Peer-to-peer (P2P)** | Nós clientes e servidores; pouco ou nenhum centro obrigatório. |
| **DHT** | Tabela hash distribuída — busca estruturada em P2P. |
| **Super-peer** | Nó com papel extra (índice/roteamento) em P2P híbrido. |
| **Granularidade** | Quão “fino” é o corte dos serviços. |
| **Bounded context** | Fronteira de modelo/linguagem (ajuda a cortar serviços). |
| **Ownership de dados** | Quem é responsável por escrever/validar um conjunto de dados. |
| **Orquestração** | Um componente central coordena o fluxo entre serviços. |
| **Coreografia** | Cada serviço reage a eventos; sem maestro único. |
| **Acoplamento temporal** | Produtor precisa que o consumidor esteja *agora* disponível (sync). |
| **Taxa distribuída** | Custo extra de rede, falha parcial, dados e ops ao distribuir (também chamado “imposto” distribuído na literatura). |
| **Híbrido** | Combinação consciente (ex.: monólito + fila; MS + eventos). |
| **SPOF** | Single Point of Failure — um nó cuja queda derruba o sistema. |
| **BFF** | Backend for Frontend — borda adaptada a um canal (web/mobile). |
| **SOA theater** | Adotar jargão/SOA sem fronteiras nem contratos reais. |

Ver também: [glossário 01](../01-comunicacao/glossario.md) · [05](../05-escalabilidade/glossario.md) · [09](../09-observabilidade/glossario.md).
