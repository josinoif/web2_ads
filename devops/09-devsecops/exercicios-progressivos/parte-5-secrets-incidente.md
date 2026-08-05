# Parte 5 — Secrets management, incidente simulado e postmortem

**Entrega desta parte:**

- Sealed Secrets **ou** External Secrets + Vault (modo dev) funcionando.
- Documento `docs/secrets.md` com procedimento de criar, consumir e rotacionar segredos.
- Simulação de incidente (`scripts/incidente.sh` + `scripts/recuperacao.sh`).
- Postmortem blameless (`docs/postmortem-incident-01.md`).
- 3 ADRs (`docs/adrs/`).

---

## 1. Sealed Secrets

Instalar:

```bash
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system
kubectl -n kube-system wait --for=condition=Available deploy sealed-secrets -t 120s
```

Instalar `kubeseal`:

```bash
curl -sL https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/kubeseal-linux-amd64 \
  -o /usr/local/bin/kubeseal
chmod +x /usr/local/bin/kubeseal
```

Criar segredo:

```bash
kubectl create secret generic db-creds \
  --from-literal=DATABASE_URL='postgres://medvault:SENHA@postgres.medvault-prod:5432/medvault' \
  --dry-run=client -o yaml > /tmp/db-creds.yaml

kubeseal --format yaml --namespace medvault-prod \
  < /tmp/db-creds.yaml > k8s/secrets/db-creds.sealed.yaml

rm /tmp/db-creds.yaml
```

Commit apenas `k8s/secrets/db-creds.sealed.yaml`. Aplicar:

```bash
kubectl apply -f k8s/secrets/db-creds.sealed.yaml
kubectl -n medvault-prod get secret db-creds
```

O Deployment consome via `envFrom`:

```yaml
envFrom:
  - secretRef: { name: db-creds }
```

---

## 2. Alternativa: External Secrets + Vault (dev)

Se optou por ESO:

```bash
helm install vault hashicorp/vault \
  --set "server.dev.enabled=true" \
  --set "server.dev.devRootToken=root" \
  -n vault --create-namespace

helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace

kubectl exec -n vault vault-0 -- vault kv put secret/medvault/db \
  DATABASE_URL="postgres://medvault:SENHA@postgres.medvault-prod:5432/medvault"
```

Com SecretStore + ExternalSecret (ver Bloco 4). O resultado é um `Secret` populado automaticamente.

---

## 3. `docs/secrets.md`

```markdown
# Secrets management — MedVault

## Principios
1. Nenhum segredo em ConfigMap.
2. Nenhum segredo em claro no git.
3. Rotacao e possivel sem downtime.

## Criar segredo (Sealed Secrets)
1. Produzir Secret local: `kubectl create secret generic ... --dry-run=client -o yaml > /tmp/sec.yaml`
2. Selar: `kubeseal --format yaml -n NS < /tmp/sec.yaml > k8s/secrets/NAME.sealed.yaml`
3. Deletar `/tmp/sec.yaml`.
4. Commit apenas o `*.sealed.yaml`.
5. `kubectl apply -f ...`

## Rotacionar
1. Gerar novo valor no provedor (DB, API externa).
2. Repetir criar segredo com o novo valor.
3. `kubectl rollout restart deploy/NAME` para releitura.
4. Invalidar valor antigo no provedor.

## Incidente
Ver `docs/runbooks/security-incident.md` — tratar como comprometido, rotacionar imediatamente.
```

---

## 4. Incidente simulado

`scripts/incidente.sh`:

```bash
#!/usr/bin/env bash
# Simula: atacante conseguiu token de ServiceAccount e tenta listar secrets.
set -e

kubectl -n medvault-prod run atacante --image=curlimages/curl --restart=Never \
  --overrides='{
    "spec": {
      "serviceAccountName": "prontuario",
      "containers": [{
        "name": "atacante",
        "image": "curlimages/curl",
        "command": ["sh","-c","sleep 3600"]
      }]
    }
  }'

echo "Aguardando pod ficar Running..."
kubectl -n medvault-prod wait --for=condition=Ready pod/atacante

echo ""
echo "Tentando listar secrets (deveria falhar por RBAC):"
kubectl -n medvault-prod exec atacante -- sh -c '
  TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>/dev/null || echo "sem-token")
  curl -sk -H "Authorization: Bearer $TOKEN" \
    https://kubernetes.default.svc/api/v1/namespaces/medvault-prod/secrets
'
```

Observar:

- Se `automountServiceAccountToken: false` (Parte 4): não há token dentro do pod.
- Se `Role` não inclui `secrets`: 403 Forbidden.

`scripts/recuperacao.sh`:

```bash
#!/usr/bin/env bash
set -e
echo "1) Contencao: isolar pod"
kubectl -n medvault-prod label pod atacante sec.quarantine=true
kubectl apply -f - <<YAML
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: quarantine, namespace: medvault-prod }
spec:
  podSelector: { matchLabels: { sec.quarantine: "true" } }
  policyTypes: [Ingress, Egress]
YAML

echo "2) Evidencia: copiar logs"
mkdir -p ./evidencia
kubectl -n medvault-prod logs atacante > ./evidencia/atacante.log 2>&1 || true
kubectl -n medvault-prod describe pod atacante > ./evidencia/atacante.describe

echo "3) Erradicar: deletar pod"
kubectl -n medvault-prod delete pod atacante --grace-period=0 --force

echo "4) Recuperar: confirmar estado"
kubectl -n medvault-prod get pods
```

Adicionar ao Makefile:

```makefile
incident:
	bash scripts/incidente.sh

recover:
	bash scripts/recuperacao.sh
```

---

## 5. Runbook

`docs/runbooks/security-incident.md`:

```markdown
# Runbook — Incidente de seguranca

## Severidade
- S1: vazamento confirmado de dados pessoais, acesso indevido a producao.
- S2: tentativa com evidencia de impacto potencial.
- S3: suspeita sem evidencia.

## Papeis
- **IR lead**: on-call de seguranca, decide; autoridade para parar producao.
- **Scribe**: registra timeline em tempo real.
- **Comunicacoes**: fala com clientes, juridico/DPO, imprensa se S1.
- **DPO/LGPD**: avalia se ha notificacao a ANPD (art. 48).

## Fluxo
1. **Detectar** (origem do sinal: Falco, Alertmanager, cliente, achado manual).
2. **Avaliar** gravidade em ate 15 min; promover ou encerrar.
3. **Conter**:
   - Isolar recursos comprometidos via NetworkPolicy de quarentena.
   - Desativar credencial/chave suspeita.
   - Nao apagar pods: preservar para analise.
4. **Preservar evidencia**: logs, dump de memoria se aplicavel, snapshots.
5. **Erradicar**: corrigir raiz (rebuild imagem com patch, rotacionar secrets).
6. **Recuperar**: redeploy; monitorar proximas 24h.
7. **Comunicar** (S1/S2): cliente em <24h; ANPD em <72h se aplicavel.
8. **Postmortem blameless** em <7 dias apos resolucao.

## Comunicacao LGPD (template)
### Para titular
"Identificamos em [DATA] um incidente que pode ter afetado dados pessoais seus: [lista minima]. Apurou-se ate o momento: [fatos]. As medidas tomadas: [lista]. Caso tenha duvidas: dpo@medvault.example."

### Para ANPD
Formulario oficial; incluir: natureza do dado, titulares afetados (aproximado), consequencias potenciais, medidas adotadas.
```

---

## 6. Postmortem

`docs/postmortem-incident-01.md` — após rodar `make incident && make recover`:

```markdown
# Postmortem — Tentativa de listagem de Secrets via SA comprometida

**Data:** 2026-04-21
**Severidade:** S2 (tentativa contida; sem vazamento).
**Autor:** [seu nome] (IR lead)

## Resumo em 1 paragrafo
Um pod de atacante foi criado simulando obtencao de acesso a ServiceAccount `prontuario` no ns `medvault-prod`. Tentativa de enumerar secrets falhou pelo RBAC minimo. Pod quarentenado e destruido em <3 min. Detalhes em timeline.

## Timeline (UTC-3)
- 14:02 `scripts/incidente.sh` executado.
- 14:03 Pod `atacante` Running.
- 14:03 `curl` contra kube-api retornou 403 (sem permissao em secrets).
- 14:04 Quarentena aplicada; evidencia salva.
- 14:05 Pod deletado.

## Root cause
Nao aplicavel (simulacao). A "causa" do cenario simulado seria `automountServiceAccountToken=true` + Role com acesso a Secrets.

## 3 whys
1. Por que a tentativa falhou? Porque o RBAC nao concede `secrets` a SA.
2. Por que o RBAC esta restrito? Porque fizemos RBAC mimimo na Parte 4.
3. Por que focamos em RBAC minimo? Porque auditoria revelou `cluster-admin` ligado em 4 SAs.

## Actions
| # | Acao | Dono | Prazo |
|---|------|------|-------|
| 1 | Monitorar alerta Falco para tentativas de exec em pods de prod | @devsec | 1 sem |
| 2 | Testes automatizados de RBAC em CI | @infra | 2 sem |
| 3 | Incluir cenario similar em proxima tabletop | @irlead | 1 mes |
```

---

## 7. ADRs

`docs/adrs/001-estrategia-secrets.md`:

```markdown
# ADR-001 — Estrategia de Secrets

## Contexto
Auditoria encontrou segredos em ConfigMap. Precisamos mudar sem bloquear entregas.

## Decisao
Adotar **Sealed Secrets** como padrao. ExternalSecrets/Vault avaliados para 6 meses.

## Consequencias
+ Simples, integra com GitOps.
+ Sem depender de Vault central.
- Rotacao requer re-selar + commit (nao automatica).
- Necessidade de backup da chave do controller.
```

`docs/adrs/002-admission-kyverno.md`, `docs/adrs/003-slsa-l2.md`: análogos.

---

## Critérios de aceitação

- [ ] `kubectl -n medvault-prod get secret db-creds` mostra o segredo, criado via Sealed Secrets (ou ESO).
- [ ] `git log -p k8s/secrets/ | grep -Ei "password|postgres://.*:.*@"` não mostra valor em claro.
- [ ] `make incident` cria pod atacante; `curl` falha com 403.
- [ ] `make recover` aplica quarentena, preserva evidência e remove pod.
- [ ] `docs/postmortem-incident-01.md` preenchido com timeline, root cause, 3 whys e actions datadas.
- [ ] 3 ADRs em `docs/adrs/` documentando escolhas.
- [ ] Runbook em `docs/runbooks/security-incident.md` cobre papéis, fluxo e comunicação LGPD.

## Fechamento

Com essas 5 partes você tem:

- **Pipeline** que falha em SAST, SCA, Secrets, IaC e Image.
- **Artefato** assinado com cosign + SBOM + proveniência SLSA.
- **Cluster** com PSS restricted, NetworkPolicy default-deny, RBAC mínimo, audit log.
- **Secrets** fora do git.
- **Respostas** a incidente testadas e documentadas.

Isso é o que o mercado chama de "DevSecOps pragmático" — não é perfeição, é **maturidade operacional verificável**.

Referências consolidadas estão em [referencias.md](../referencias.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Admission control e cluster endurecido](parte-4-admission-cluster.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Entrega avaliativa — Módulo 9 (DevSecOps)](../entrega-avaliativa.md) |

<!-- nav:end -->
