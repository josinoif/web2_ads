# Gabarito enxuto — Decisões (10)

**Abra só depois** de tentar [decisoes.md](decisoes.md). Não é a única resposta certa — é um espelho.

| Cenário | Direção razoável | Risco se errar |
|---------|------------------|----------------|
| **1** MVP 1 time | Monólito layered **modular**. Fila só se o pico do prazo já doer. Lab A: 3 processos cedo = taxa distribuída sem ganho de time. | Travado em rede/ops; ou monólito sem fronteiras (“bola de lama”) |
| **2** 4 times | Preferir **service-based** (poucos serviços grossos) se o time ainda é pequeno; MS fino só com **dados por contexto** e deploys realmente independentes. Escala seletiva do boletim ([05](../05-escalabilidade/)). Lab A = isolamento de *processo*; ainda falta DB/deploy por time. | DB único = monólito distribuído; 12 MS no dia 1 = taxa sem ganho |
| **3** Pico + análise | EDA / fila na borda (lab B: sync ~2s vs eventos ms; worker down ainda aceita). Pode ser **monólito + fila**. | Sync na borda derruba UX no prazo; ou EDA sem status/`trace_id` ([09](../09-observabilidade/)) |
| **4** Legados | SOA / integração explícita + **ACL** no ERP; orquestração se fluxo longo/auditável; coreografia se fatos estáveis. ESB é opção, não obrigação. | ESB SPOF / SOA theater; ou N integrações ad hoc |
| **5** P2P materiais | P2P raro como *núcleo*; notas/matrícula querem autoridade central. Arquivos: object storage ([08](../08-armazenamento-arquivos/)). | UX/segurança/churn; descentralizar o que precisa de auditoria |
| **6** MS por moda | Não. Escada (§1): monólito → (+ fila) → service-based → MS quando time/deploy/dados pedirem. | Taxa distribuída sem benefício; produto para |
| **Síntese** | Um estilo + 2 mecanismos da trilha + 1 custo validável | Desenho só de caixas sem evidência |

---

## Rubrica (espelho rápido)

- Cita **pipeline ≠ MS** no lab A → rumo a Bom/Ótimo.  
- Só “usar microsserviços” sem taxa/dados/time → Insuficiente.
