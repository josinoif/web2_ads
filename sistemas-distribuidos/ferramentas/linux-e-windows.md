# Como rodar labs no Linux e no Windows

Os labs usam **Docker Compose** (igual nos dois sistemas) e, na maioria, scripts `.sh` (bash + `curl` + `python3`).

No **Linux e macOS** isso roda nativo. No **Windows PowerShell**, `curl` não é o curl, `python3` muitas vezes não existe e `./scripts/foo.sh` não abre.

## Comandos iguais nos dois sistemas

Estes valem no PowerShell, cmd, bash e zsh — **copie do tutorial sem traduzir**:

```text
docker compose up -d --build
docker compose ps
docker compose logs -f
docker compose exec -T SERVICO sh -c "comando"
docker compose stop SERVICO
docker compose start SERVICO
docker compose down -v
```

Use **`-T`** no `exec` (evita `the input device is not a TTY` no Windows). Só use `-it` quando for **entrar** num shell interativo (`docker compose exec -it node-a sh`).

Tutoriais RabbitMQ e Kafka (pedido-pago) já usam só isso + `docker compose exec -T api python lab.py …`.

## Scripts `.sh` dos labs

Na pasta do lab (onde está o `docker-compose.yml`):

| Sistema | Como chamar `scripts/enviar-lote.sh 10` |
|---------|------------------------------------------|
| Linux / macOS | `./scripts/enviar-lote.sh 10` ou `./lab.sh enviar-lote 10` |
| Windows PowerShell | `.\lab.ps1 enviar-lote 10` |
| Windows cmd | `lab.cmd enviar-lote 10` |
| Git Bash / WSL | `./scripts/enviar-lote.sh 10` **ou** `./lab.sh enviar-lote 10` |

O nome do script é o arquivo **sem** `scripts/` e **sem** `.sh`. Exemplos:

```text
.\lab.ps1 enviar-lote 10
.\lab.ps1 gravar-nota aluno-01 SD 8.0
.\lab.ps1 cliente sincrono
```

Variáveis que o tutorial exporta (`N=40`, `WC=w1`, `AVISO_ID=...`) no PowerShell:

```text
$env:N = "40"
.\lab.ps1 publicar-lote hot
```

O `lab.ps1` / `lab.sh` (no Windows) constrói a imagem `aulas-ads-lab-tools` na primeira vez e executa o mesmo `.sh` dentro de um container Linux, com acesso ao Docker do host.

## HTTP no host (`curl`)

| Sistema | Comando |
|---------|---------|
| Linux / macOS / Git Bash / WSL | `curl -s http://localhost:PORTA/` |
| Windows PowerShell | `curl.exe -s http://localhost:PORTA/` |

No PowerShell, `curl` sem `.exe` é o `Invoke-WebRequest` — não serve para os exemplos da disciplina.

JSON no PowerShell:

```text
curl.exe -s -X POST http://localhost:8080/provas -H "Content-Type: application/json" -d "{\"aluno\":\"maria\"}"
```

No bash pode usar aspas simples: `-d '{"aluno":"maria"}'`.

Pretty-print JSON: no Linux, `| python3 -m json.tool`. No Windows, o `.\lab.ps1` já usa Python da imagem; no host, `| curl.exe` sem o pipe do python, ou WSL.

## Python 3 no host

Não é obrigatório no Windows: os scripts `.sh` via `lab.ps1` já usam Python de dentro da imagem. No Linux, `python3 -m json.tool` continua válido.

## Pré-requisito

Docker Desktop (Windows/macOS) ou Docker Engine + Compose (Linux), com o daemon **no ar**.
