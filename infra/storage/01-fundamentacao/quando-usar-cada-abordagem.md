# Quando usar cada abordagem de armazenamento

## Introdução

Não existe uma única “melhor” opção para todos os projetos. A escolha depende do **cenário** (desenvolvimento, produção pequena ou escalável), **orçamento**, **complexidade** que a equipe aceita e necessidade de **multi-região** ou **alta disponibilidade**. Este texto resume cenários típicos e uma comparação entre filesystem, MinIO e S3 (ou outros provedores de object storage).

---

## Cenários de uso

### Desenvolvimento e testes locais

- **Filesystem**: salvar em uma pasta `uploads/` no projeto (ou fora do código). Simples e rápido para prototipar.
- **MinIO em Docker**: aproxima o ambiente da produção se você já usa (ou planeja usar) API S3. Útil para testar upload/download e presigned URLs sem custo de nuvem.

### Produção pequena ou média

- **MinIO self-hosted**: um único servidor ou um pequeno cluster MinIO pode atender bem. Você mantém a infraestrutura e não paga por uso de objeto em nuvem.
- **S3 (ou equivalente)**: mesmo em projetos médios, muitos times preferem S3 para não gerenciar disco e backup; o custo inicial costuma ser baixo com volumes moderados.

### Produção escalável ou multi-região

- **Object storage em nuvem** (AWS S3, Google Cloud Storage, Azure Blob): durabilidade, replicação, CDN e integração com o ecossistema do provedor. O filesystem no servidor de aplicação não é recomendado quando há várias instâncias ou quando o volume de arquivos cresce muito.

---

## Tabela comparativa

| Critério        | Filesystem   | MinIO (self-hosted) | S3 / cloud      |
|-----------------|-------------|----------------------|------------------|
| **Custo**       | Só o disco  | Infra + manutenção   | Pago por uso     |
| **Escalabilidade** | Limitada (1 servidor) | Boa (cluster) | Muito alta       |
| **Complexidade**   | Baixa      | Média                 | Média (APIs, IAM) |
| **Backup/DR**   | Seu cuidado | Seu cuidado           | Oferecido        |
| **Lock-in**     | Nenhum      | API S3 (portável)     | Provedor         |
| **Uso típico**  | Dev, MVP    | Produção pequena/média | Qualquer escala  |

---

## Critérios de decisão

1. **Tamanho e crescimento**: se o volume de arquivos e o número de usuários podem crescer bastante, object storage tende a ser mais adequado.
2. **Orçamento**: sem orçamento para nuvem e com capacidade de operar servidor, MinIO ou filesystem podem ser suficientes no início.
3. **Múltiplas instâncias**: se a aplicação roda em mais de uma instância (load balancer), arquivos no disco de uma máquina não são visíveis nas outras; object storage (MinIO ou S3) resolve isso.
4. **Compatibilidade**: MinIO expõe API S3; código escrito para MinIO pode ser reutilizado contra S3 (com ajuste de endpoint e credenciais).

---

## Conclusão

Use **filesystem** para desenvolvimento ou MVPs com um único servidor. Considere **MinIO** para produção pequena/média ou para desenvolver já com API S3. Adote **S3** (ou outro object storage em nuvem) quando precisar de escala, multi-região ou quer delegar durabilidade e backup ao provedor. Nos módulos seguintes você implementará cada abordagem na prática.
