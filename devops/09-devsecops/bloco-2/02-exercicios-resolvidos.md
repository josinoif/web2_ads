# Bloco 2 — Exercícios resolvidos

> Leia primeiro [02-codigo-dependencias.md](./02-codigo-dependencias.md).

---

## Exercício 1 — SAST na prática

**Enunciado.** O trecho abaixo está num endpoint da MedVault. Liste todos os problemas que Bandit/Semgrep devem apontar e proponha reescrita segura.

```python
import subprocess, yaml, pickle
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/import")
async def importar(req: Request):
    corpo = await req.body()
    dados = pickle.loads(corpo)
    cmd = dados.get("cmd")
    subprocess.run(cmd, shell=True)
    config = yaml.load(dados.get("yaml", b""))
    return {"ok": True, "config": config}
```

**Resposta.**

Problemas (múltiplos):

| # | Regra típica | Problema | Risco |
|---|-------------|---------|------|
| 1 | `B301 pickle_usage` | `pickle.loads` em input externo = RCE | CRÍTICO |
| 2 | `B602 subprocess_shell_true` | `shell=True` com string de input | RCE |
| 3 | `B506 yaml_load` | `yaml.load` sem SafeLoader | RCE via tag YAML |
| 4 | Pattern custom | Aceita payload sem validação | Injection em geral |
| 5 | Pattern custom | Sem autorização no endpoint | Broken access control |

Reescrita (mínimo viável seguro):

```python
import json, shlex, subprocess
import yaml
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PayloadImport(BaseModel):
    cmd: list[str]    # lista, nao string
    yaml_text: str

COMMAND_ALLOWLIST = {"ls", "whoami"}

@app.post("/import")
async def importar(payload: PayloadImport, user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403)
    if not payload.cmd or payload.cmd[0] not in COMMAND_ALLOWLIST:
        raise HTTPException(400, "comando nao permitido")
    subprocess.run(payload.cmd, check=True, timeout=5)  # sem shell
    config = yaml.safe_load(payload.yaml_text)
    return {"ok": True, "config": config}
```

Ponto central: **nunca** desserializar input não-confiável com pickle; **nunca** `shell=True` com input; **sempre** `yaml.safe_load`.

---

## Exercício 2 — Priorização de SCA

**Enunciado.** `pip-audit` retornou:

| Pacote | Versão | CVE | Severidade | Fix |
|--------|--------|-----|------------|-----|
| `urllib3` | 1.26.5 | GHSA-g4mx | HIGH | 1.26.18 |
| `jinja2` | 3.1.2 | CVE-2024-aaa | MEDIUM | 3.1.4 |
| `setuptools` | 60.10.0 | CVE-2024-bbb | LOW | 70.0.0 |
| `django` | 3.2.18 | CVE-2024-ccc | CRITICAL | 4.2.15 |

Seu produto é uma API (sem Django) que usa `django-auth-ldap` como dependência transitiva. Proponha plano de ação em **ordem** com justificativa de 1 linha cada.

**Resposta.**

1. **django CRITICAL — investigar primeiro.** Mesmo que você não use Django diretamente, `django-auth-ldap` arrasta Django. Preciso avaliar se o vetor afeta componentes que estão de fato em uso. Se afetar, **upgrade urgente** para série 4.2 (e avaliar compatibilidade com `django-auth-ldap`). Se não afetar, **documentar** exceção com referência à análise.
2. **urllib3 HIGH — upgrade direto.** Bump para 1.26.18 é trivial, sem quebra de API.
3. **jinja2 MEDIUM — agendar upgrade junto do próximo bump de rotina.** Já discutimos no Bloco 1 o caso de aceitação; aqui, com fix disponível, aceita, mas coloca data.
4. **setuptools LOW — avaliar.** LOW raramente bloqueia; upgrade quando houver janela (às vezes setuptools 70+ quebra builds antigas).

**Regra geral:** `CRITICAL` com fix → bloqueia PR até resolver; `HIGH` com fix → resolve este sprint; `MEDIUM/LOW` → backlog com data-limite; **sem fix** → aceite documentado.

---

## Exercício 3 — Escrever regra Semgrep

**Enunciado.** Para a MedVault, escreva uma regra Semgrep que **proíba** funções que recebem diretamente `request.query_params["id"]` e passam para query SQL como string.

**Resposta.**

`.semgrep/sql-concat.yaml`:

```yaml
rules:
  - id: medvault-no-sql-concat
    message: "Concatenacao de input em SQL = SQL injection. Use query parametrizada."
    severity: ERROR
    languages: [python]
    patterns:
      - pattern-either:
          - pattern: |
              $Q = f"SELECT ... {$REQ.query_params[$K]} ..."
          - pattern: |
              $Q = "SELECT ..." + $REQ.query_params[$K] + "..."
          - pattern: |
              $Q = "SELECT ..." + $X
              ...
              $X = $REQ.query_params[$K]
      - metavariable-regex:
          metavariable: $REQ
          regex: '(request|req)'
```

Teste com código-isca:

```python
# Deveria pegar:
q1 = f"SELECT * FROM paciente WHERE id = {request.query_params['id']}"
# Deveria pegar:
pid = request.query_params["id"]
q2 = "SELECT * FROM paciente WHERE id = " + pid
# Nao deveria pegar (parametrizado):
q3 = "SELECT * FROM paciente WHERE id = %s"
cur.execute(q3, (request.query_params["id"],))
```

Executar:

```bash
semgrep --config .semgrep/sql-concat.yaml src/
```

---

## Exercício 4 — Secret detection e resposta

**Enunciado.** Gitleaks encontrou:

```
src/config.py:12 aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
src/config.py:13 aws_secret_access_key = "wJalrXUt...EXAMPLE"
```

Descreva, passo a passo, sua resposta (**não** basta `git revert`).

**Resposta.**

1. **Tratar como comprometido imediatamente.** O commit pode ter sido público por segundos — basta um bot para coletar.
2. **Rotacionar no provedor.** Console AWS → IAM → Access Keys → *Make Inactive* + *Delete* a chave antiga; gerar nova; atualizar nos sistemas que consomem.
3. **Verificar uso da chave antiga.** CloudTrail: `LookupEvents` filtrado por `AccessKeyId=AKIAIOSFODNN7EXAMPLE` nas últimas N horas. Se houve uso não-autorizado, acionar plano de incidente.
4. **Remover do código vivo.** `git rm` credencial, mover para variável de ambiente/secret manager, commit de correção.
5. **(Opcional) Reescrever histórico** com `git filter-repo` ou BFG, `force-push`, pedir que colaboradores re-clonem. **Isso não substitui a rotação.**
6. **Adicionar pre-commit Gitleaks** para evitar recorrência; criar `.gitleaks.toml` com regra específica se aplicável.
7. **Postmortem blameless:** como o segredo foi parar ali? (Ex.: script de setup que escrevia `config.py` local foi commitado). Mudar processo para não produzir esse arquivo.
8. **Registrar incidente interno** para trilha de auditoria LGPD/ISO (mesmo que nenhum dado tenha vazado).

Observação chave: o custo de rotação hoje (minutos) é infinitamente menor que o de uso indevido depois.

---

## Exercício 5 — SBOM + Grype

**Enunciado.** Você gerou `sbom.cdx.json` com Syft na release v1.0.0 em janeiro. Em março, surge CVE crítica em `httpx<=0.27.0`. Descreva como descobrir se a v1.0.0 foi afetada **sem** rebuildar a imagem, e como comunicar clientes.

**Resposta.**

Passos técnicos:

1. **Reexecutar Grype sobre o SBOM antigo:**
   ```bash
   grype sbom:sbom.cdx.json --output json > scan-v1.0.0-2024-03.json
   ```
2. Filtrar por `httpx`:
   ```bash
   jq '.matches[] | select(.artifact.name == "httpx")' scan-v1.0.0-2024-03.json
   ```
3. Se achar, confirmar versão: se `0.27.0`, a v1.0.0 **está afetada**.

Ação produto:

4. **Emitir VEX (Vulnerability Exploitability eXchange)** — documento formal dizendo se o produto está afetado ou não, justificando:
   - Se **não afetado** (ex.: `httpx` só é usado em path dev): emitir VEX `not_affected` com justificativa `vulnerable_code_not_in_execute_path`.
   - Se **afetado**: emitir VEX `affected`, produzir patch v1.0.1, comunicar clientes.

Comunicação:

5. **Advisory público** no GitHub (`Security advisory`) com: descrição, versões afetadas, versão corrigida, workaround temporário.
6. **E-mail direto** para clientes empresariais com contato de segurança cadastrado.
7. **Atualizar postura no site**: página `/security/advisories` versionada.

**Valor do SBOM:** sem ele, você teria que rebuildar a imagem ou vasculhar commits para saber versão exata de `httpx` — inviável em escala. Com ele, resposta em minutos.

---

## Exercício 6 — Interpretar relatório consolidado

**Enunciado.** Rodando `python security_report.py bandit.sarif semgrep.sarif pip-audit.json --fail-on high`, a saída mostra:

```
ferramenta     severidade     id                   alvo               descricao
bandit         high           B602                 src/run.py         subprocess with shell=True
semgrep        error          python.requests...   src/http.py        TLS verify disabled
pip-audit      high           GHSA-v845-jxx5       urllib3==1.26.5    HTTP response splitting
bandit         medium         B104                 src/server.py      binding to all interfaces
pip-audit      medium         PYSEC-2024-XXX       jinja2==3.1.2      sandbox escape via template

Total: 5 | >= high: 3
```

Exit code: 1. Qual sua priorização e comunicação ao time?

**Resposta.**

**Priorização (agora):**

1. `semgrep python.requests - TLS verify disabled`: suspender verificação TLS é prática que habilita MITM silencioso. **Correção imediata no mesmo PR.**
2. `bandit B602 shell=True`: pode ser RCE. Revisar o fluxo que chega até ali; corrigir com subprocess sem shell.
3. `pip-audit urllib3 HIGH`: bump para 1.26.18 (fix direto).

**Para o backlog (não bloqueia, mas entra no próximo sprint):**

4. `bandit B104 all interfaces`: `0.0.0.0` pode ser intencional em container; validar com contexto. Se aceite, adicionar `# nosec` com comentário.
5. `pip-audit jinja2 MEDIUM`: já discutimos no Bloco 1; aceitação documentada com data.

**Comunicação ao time (no PR, não em DM):**

> A execução falhou porque 3 achados HIGH bloqueiam:
>
> 1. `src/http.py` tem `verify=False` — corrigir ou justificar em PR separado.
> 2. `src/run.py:L42` usa `shell=True` — refatorar para `subprocess.run([...])`.
> 3. `urllib3 1.26.5` → bump `1.26.18`.
>
> Os 2 MEDIUM entram em backlog. Link pro SARIF no Code scanning.

**Ponto pedagógico.** O relatório consolidado economiza cliques; ele **não substitui** interpretação humana — severidade é sinal, não decisão.

---

## Autoavaliação

- [ ] Reconheço padrões inseguros em Python (pickle, shell=True, yaml.load, verify=False).
- [ ] Priorizo CVE por severidade + exploitabilidade no produto.
- [ ] Escrevo regras Semgrep customizadas para o domínio.
- [ ] Sei a resposta correta para vazamento de credencial (rotacionar).
- [ ] Gero SBOM e o utilizo para reanalisar vulnerabilidades post-hoc.
- [ ] Uso `security_report.py` ou equivalente para visão unificada.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Segurança do código e das dependências](02-codigo-dependencias.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Bloco 3 — Imagens e supply chain: endurecendo o artefato](../bloco-3/03-imagens-supply-chain.md) |

<!-- nav:end -->
