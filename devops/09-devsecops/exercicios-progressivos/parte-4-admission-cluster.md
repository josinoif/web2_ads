# Parte 4 — Admission control e cluster endurecido

**Entrega desta parte:**

- k3d com Calico (NetworkPolicy) + audit log.
- Namespaces `medvault-dev` e `medvault-prod` com PSS.
- Kyverno com políticas `verify-images`, `disallow-latest`, `require-nonroot`, `registry-allowlist`, `resources-limits`.
- RBAC mínimo por app.
- Prova de rejeição e prova de sucesso com manifestos de teste.

---

## 1. Cluster k3d com segurança

```bash
mkdir -p ~/k8s/medvault/audit
cat > ~/k8s/medvault/audit-policy.yaml <<'YAML'
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages: ["RequestReceived"]
rules:
  - level: RequestResponse
    resources:
      - { group: "", resources: ["secrets","configmaps"] }
      - { group: "rbac.authorization.k8s.io", resources: ["*"] }
      - { group: "", resources: ["pods/exec","pods/attach","pods/portforward"] }
  - level: Metadata
YAML

k3d cluster create medvault \
  --agents 1 \
  --volume ~/k8s/medvault/audit:/var/log/k8s-audit \
  --volume ~/k8s/medvault/audit-policy.yaml:/etc/kubernetes/audit-policy.yaml \
  --k3s-arg="--disable=traefik@server:0" \
  --k3s-arg="--flannel-backend=none@server:0" \
  --k3s-arg="--disable-network-policy@server:0" \
  --k3s-arg="--kube-apiserver-arg=audit-policy-file=/etc/kubernetes/audit-policy.yaml@server:0" \
  --k3s-arg="--kube-apiserver-arg=audit-log-path=/var/log/k8s-audit/audit.log@server:0" \
  --k3s-arg="--kube-apiserver-arg=audit-log-maxage=7@server:0"
```

Instalar Calico como CNI:

```bash
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.2/manifests/tigera-operator.yaml
cat <<EOF | kubectl apply -f -
apiVersion: operator.tigera.io/v1
kind: Installation
metadata: { name: default }
spec:
  calicoNetwork:
    ipPools:
      - blockSize: 26
        cidr: 10.42.0.0/16
        encapsulation: VXLANCrossSubnet
EOF
```

Aguardar `kubectl get pods -n calico-system` pronto.

---

## 2. Namespaces com PSS

```yaml
# k8s/namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: medvault-dev
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/warn: restricted
---
apiVersion: v1
kind: Namespace
metadata:
  name: medvault-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

```bash
kubectl apply -f k8s/namespaces.yaml
```

---

## 3. NetworkPolicy

```yaml
# k8s/netpol/default-deny.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: medvault-prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: medvault-prod }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
          podSelector:
            matchLabels: { k8s-app: kube-dns }
      ports: [{ protocol: UDP, port: 53 }]
```

Aplique e teste rejeição (Pod curl a google):

```bash
kubectl -n medvault-prod run test --rm -it --image=curlimages/curl \
  --labels=app=test --command -- sh -c "curl -m 3 https://google.com"
# Esperado: timeout
```

---

## 4. Kyverno

Instalar:

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

Políticas em `policies/`:

`policies/disallow-latest.yaml`:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: disallow-latest }
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-tag
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["medvault-prod","medvault-dev"] }
      validate:
        message: "Imagem :latest nao permitida."
        pattern:
          spec:
            containers:
              - image: "!*:latest"
```

`policies/require-nonroot.yaml`:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-nonroot }
spec:
  validationFailureAction: Enforce
  rules:
    - name: runAsNonRoot
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["medvault-prod"] }
      validate:
        message: "Pods devem definir runAsNonRoot=true."
        pattern:
          spec:
            =(securityContext):
              runAsNonRoot: true
            containers:
              - =(securityContext):
                  runAsNonRoot: true
```

`policies/registry-allowlist.yaml`:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: registry-allowlist }
spec:
  validationFailureAction: Enforce
  rules:
    - name: allowed-registries
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["medvault-prod","medvault-dev"] }
      validate:
        message: "Imagens so podem vir de ghcr.io/medvault* ou registry.medvault.local/*."
        pattern:
          spec:
            containers:
              - image: "ghcr.io/SEU-USER/* | registry.medvault.local/*"
```

`policies/verify-images.yaml`:

```yaml
apiVersion: kyverno.io/v2beta1
kind: ClusterPolicy
metadata: { name: verify-images }
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: cosign-keyless
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["medvault-prod"] }
      verifyImages:
        - imageReferences: ["ghcr.io/SEU-USER/medvault-api*"]
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/SEU-USER/medvault-api/.github/workflows/release.yml@refs/tags/v*"
                    issuer: "https://token.actions.githubusercontent.com"
```

`policies/resources-limits.yaml`:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: resources-limits }
spec:
  validationFailureAction: Enforce
  rules:
    - name: limits-obrigatorios
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ["medvault-prod"] }
      validate:
        message: "Containers devem ter resources.limits de cpu e memoria."
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    cpu: "?*"
                    memory: "?*"
```

---

## 5. RBAC mínimo

`k8s/rbac/prontuario.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: prontuario, namespace: medvault-prod }
automountServiceAccountToken: false
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: prontuario-ro, namespace: medvault-prod }
rules:
  - apiGroups: [""]
    resources: [configmaps]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: prontuario-ro, namespace: medvault-prod }
subjects:
  - kind: ServiceAccount
    name: prontuario
    namespace: medvault-prod
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: prontuario-ro
```

---

## 6. Testes de rejeição

`manifests/tests/pod-inseguro.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata: { name: teste-inseguro, namespace: medvault-prod }
spec:
  containers:
    - name: bad
      image: nginx:latest     # :latest nao permitido
      securityContext:
        runAsUser: 0           # root
```

```bash
kubectl apply -f manifests/tests/pod-inseguro.yaml
# Esperado: Error do admission. Captura saida para docs/aceitacao.md.
```

`manifests/tests/pod-bom.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: teste-bom
  namespace: medvault-prod
spec:
  serviceAccountName: prontuario
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      image: ghcr.io/SEU-USER/medvault-api:v1.0.0
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: ["ALL"] }
      resources:
        requests: { cpu: 50m, memory: 64Mi }
        limits:   { cpu: 200m, memory: 256Mi }
```

---

## 7. Auditoria RBAC

```bash
python ../devops/09-devsecops/bloco-4/rbac_audit.py --namespace medvault-prod
```

Esperado: 0 achados HIGH (nenhum cluster-admin; nenhum default SA em deployments).

---

## 8. Makefile

```makefile
apply:
	kubectl apply -f k8s/namespaces.yaml
	kubectl apply -f k8s/netpol/
	kubectl apply -f policies/
	kubectl apply -f k8s/rbac/

policy-test:
	-kubectl apply -f manifests/tests/pod-inseguro.yaml
	kubectl apply -f manifests/tests/pod-bom.yaml
	kubectl -n medvault-prod get pods

rbac-audit:
	python ../devops/09-devsecops/bloco-4/rbac_audit.py --namespace medvault-prod
```

---

## Critérios de aceitação

- [ ] `kubectl get netpol -n medvault-prod` lista `default-deny` + allows.
- [ ] `kubectl apply -f pod-inseguro.yaml` **falha** com mensagens de ao menos 2 políticas Kyverno.
- [ ] `kubectl apply -f pod-bom.yaml` **passa**.
- [ ] Nenhum Deployment usa `default` ServiceAccount.
- [ ] `rbac_audit.py` retorna sem achados HIGH.
- [ ] Audit log existe em `/var/log/k8s-audit/audit.log` dentro do container server.

Próxima: [Parte 5 — secrets, incidente e postmortem](./parte-5-secrets-incidente.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — SBOM, assinatura e proveniência](parte-3-sbom-assinatura.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Parte 5 — Secrets management, incidente simulado e postmortem](parte-5-secrets-incidente.md) |

<!-- nav:end -->
