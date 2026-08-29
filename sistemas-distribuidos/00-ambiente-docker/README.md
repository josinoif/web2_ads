# 00 — Ambiente de experimentação com Docker

**Papel neste curso:** ponto de partida. Antes dos mini-projetos de sistemas distribuídos, você precisa conseguir **subir vários “nós”**, **ligar/desligar** serviços, **inspecionar rede/logs** e **simular falhas** sem instalar tudo na máquina.

**Status:** pronto para uso (referência + lab mínimo)

---

## Por que Docker nesta disciplina?

Em sistemas distribuídos o objeto de estudo **não** é um processo sozinho — é o comportamento de **vários processos** que se comunicam, falham e compartilham (ou não) estado.

Com Docker você consegue, no notebook:

| Necessidade da disciplina | Como o Docker ajuda |
|---------------------------|---------------------|
| Vários nós com o mesmo código | Vários containers a partir da mesma imagem |
| Serviços de apoio (Redis, MinIO, Jaeger) | `docker run` / Compose sem instalar no host |
| Isolar redes / simular “máquinas” | Redes bridge; nomes DNS entre containers |
| Simular queda de nó | `docker stop` / `docker kill` |
| Ver o que cada nó “pensa” | `docker logs`, `docker exec` |
| Repetir o experimento | Mesmo `docker-compose.yml` para toda a turma |

> Este material é uma **folha de referência orientada a lab**. Para aprofundar Dockerfile/Compose em geral, veja também [`infra/docker/`](../../infra/docker/) e [`devops/05-containers/`](../../devops/05-containers/).

---

## 1. Verificar instalação

```text
docker --version
docker compose version
docker info
docker run --rm hello-world
```

Se `hello-world` imprimir a mensagem de sucesso, o runtime está ok.

**Windows:** instale o [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) e use o **PowerShell** ou o Windows Terminal. Os blocos `docker compose` abaixo são **os mesmos** no Linux. Scripts `.sh` e `curl` no host: [linux-e-windows.md](../ferramentas/linux-e-windows.md).

**Alternativa:** Podman — a maior parte dos exemplos funciona com `alias docker=podman` (Compose: `podman compose` ou `docker-compose` compatível).

---

## 2. Modelo mental (o suficiente para o lab)

```
Imagem  = receita imutável (camadas + metadados)
Container = processo em execução a partir de uma imagem
Rede    = como containers se enxergam (DNS pelo nome do serviço)
Volume  = disco que sobrevive ao stop/rm do container
Compose = declara N serviços + rede + volumes num YAML
```

No lab de SD, pense assim:

- **1 container ≈ 1 nó** (processo isolado com IP/porta próprios na rede Docker)
- **Compose ≈ o “cluster” local** do experimento
- **stop/kill ≈ falha** de um nó
- **rede + nomes ≈ descoberta** entre serviços

---

## 3. Folha de comandos (o que mais se usa em aula)

### Ciclo de vida

```bash
# subir em primeiro plano (logs na tela)
docker run --rm -p 8080:80 nginx:alpine

# subir em background, com nome
docker run -d --name web -p 8080:80 nginx:alpine

docker ps                 # só rodando
docker ps -a              # incluindo parados
docker stop web           # SIGTERM (parada “educada”)
docker kill web           # SIGKILL (queda brusca — útil em lab de falhas)
docker start web
docker rm web             # remove container parado
docker rm -f web          # force (stop + rm)
```

Flags que aparecem o tempo todo:

| Flag | Para quê no lab |
|------|-----------------|
| `--rm` | some ao sair (não acumula lixo) |
| `-d` | background |
| `--name` | nome estável para logs/exec/stop |
| `-p host:container` | expor porta no notebook |
| `-e VAR=valor` | config sem rebuild |
| `--network` | colocar o nó na rede do experimento |
| `--memory` / `--cpus` | limitar recurso (simular nó “fraco”) |

### Imagens

```bash
docker pull redis:7-alpine
docker images
docker build -t sd-node:lab .
docker rmi sd-node:lab
```

### Logs e inspeção (depuração do experimento)

```bash
docker logs web
docker logs -f --tail 50 web          # acompanhar ao vivo
docker exec -it web sh                # entrar no container (alpine: sh)
docker inspect web                    # JSON completo (IP, env, mounts…)
docker stats                          # CPU/memória ao vivo
```

Descobrir IP na rede Docker:

```bash
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web
```

### Redes (vários nós se falando)

```bash
docker network create sd-lab
docker run -d --name a --network sd-lab nginx:alpine
docker run -d --name b --network sd-lab nginx:alpine

# de dentro de b, o hostname "a" resolve para o container a
docker exec -it b sh -c "wget -qO- http://a:80 | head"
```

| Rede | Uso típico no lab |
|------|-------------------|
| `bridge` (default) | containers isolados; comunicação via IP ou rede nomeada |
| rede user-defined | **DNS pelo nome** — padrão do Compose |
| `host` | sem isolamento de rede (raro no lab; útil só em demos pontuais) |

**Ideia de experimento (partição):** dois containers em redes diferentes não se enxergam — dá para “partir” o cluster sem mexer em iptables.

### Volumes e bind mounts

```bash
docker volume create dados
docker run -d --name db -v dados:/data redis:7-alpine

# bind mount: pasta do host ↔ pasta do container (ótimo em desenvolvimento)
docker run --rm -v "$PWD":/app -w /app python:3.12-alpine python script.py
```

| Tipo | Quando usar no lab |
|------|--------------------|
| Volume nomeado | estado que deve sobreviver (Redis, MinIO) |
| Bind mount | editar código no host e rodar no container |
| Sem volume | nó efêmero (reiniciar = estado zera) — ótimo para demo de falha |

### Limpeza (quando o disco enche de experimento antigo)

```bash
docker container prune -f
docker image prune -f
docker volume prune -f
docker network prune -f
# cuidado: remove muita coisa não usada
docker system prune -af
```

---

## 4. Docker Compose — o “cluster” do experimento

Em vez de dez `docker run`, declare o lab num arquivo.

Comandos essenciais:

```bash
docker compose up -d          # sobe tudo em background
docker compose ps
docker compose logs -f
docker compose logs -f node-a # só um serviço
docker compose stop
docker compose down           # para e remove containers da stack
docker compose down -v        # também apaga volumes (reset total)
docker compose exec node-a sh # interativo; no Windows use Windows Terminal
docker compose exec -T node-a wget -qO- http://node-b:8000/  # um comando, sem TTY
docker compose scale worker=3 # se o serviço permitir réplicas (ver Compose)
```

Padrões úteis em SD:

```yaml
services:
  node-a:
    build: ./node
    environment:
      NODE_NAME: a
    ports:
      - "8001:8000"   # host:container — cada nó numa porta do notebook

  node-b:
    build: ./node
    environment:
      NODE_NAME: b
    ports:
      - "8002:8000"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Entre containers, use o **nome do serviço** (`http://node-a:8000`, `redis:6379`), não `localhost` — `localhost` dentro do container é o próprio container.

---

## 5. Receitas de experimentação (checklist da disciplina)

### Subir N nós iguais

```bash
docker compose up -d --scale worker=3
```

(Exige serviço sem `container_name` fixo e, de preferência, sem porta publicada conflitante — ou use portas distintas por serviço, como no lab desta pasta.)

### Simular falha de um nó

```bash
docker compose stop node-b          # saída “limpa”
docker kill $(docker compose ps -q node-b)  # queda brusca
docker compose start node-b         # recuperação
```

Observe o que os outros nós fazem (timeout, retry, eleição, leitura stale…).

### Ver latência / carga por nó

```bash
docker stats
docker compose logs -f
```

### Limitar recurso (nó “fraco”)

```bash
docker run -d --name fraco --memory=64m --cpus=0.2 ...
```

No Compose:

```yaml
deploy:
  resources:
    limits:
      cpus: "0.2"
      memory: 64M
```

> Em Compose “clássico” fora de Swarm, `deploy.resources` pode ser ignorado conforme a versão/engine — se não pegar, use `mem_limit` / `cpus` no serviço ou `docker update`.

### Isolar grupos de nós (intuição de partição)

```bash
docker network create lado-esq
docker network create lado-dir
# coloque node-a e node-b em lado-esq; node-c só em lado-dir
# node-c não resolve node-a → “partição”
```

---

## 6. Lab mínimo desta pasta

Na subpasta [`lab/`](lab/) há um Compose com:

- **3 nós** HTTP idênticos (`node-a`, `node-b`, `node-c`) — cada um responde com o próprio nome
- **1 Redis** — serviço de apoio típico dos próximos tutoriais

### Como rodar

```text
cd sistemas-distribuidos/00-ambiente-docker/lab
docker compose up -d --build
docker compose ps
```

Teste no host:

```text
# Linux / macOS / Git Bash
curl -s http://localhost:8001/

# Windows PowerShell
curl.exe -s http://localhost:8001/
```

Repita para `8002` e `8003`.

Teste **entre nós** (DNS do Compose) — `-T` evita erro de TTY no Windows:

```text
docker compose exec -T node-a wget -qO- http://node-b:8000/
docker compose exec -T node-a wget -qO- http://redis:6379 || true
```

Simule falha:

```text
docker compose stop node-b

# Linux / macOS / Git Bash
curl -s http://localhost:8002/ || echo "node-b fora"
curl -s http://localhost:8001/

# Windows PowerShell
curl.exe -s http://localhost:8002/ || echo "node-b fora"
curl.exe -s http://localhost:8001/

docker compose start node-b
```

Encerrar e limpar:

```bash
docker compose down -v
```

### O que você deve conseguir fazer ao final deste 00

- [ ] Explicar imagem vs container vs rede vs volume
- [ ] Subir e derrubar um “cluster” local com Compose
- [ ] Acessar um serviço pela porta do host e pelo nome DNS interno
- [ ] Usar `logs`, `exec`, `stop`/`kill` num experimento
- [ ] Resetar o lab com `down -v` sem deixar lixo

---

## 7. Mapa rápido: comando → intenção no lab

| Quero… | Comando |
|--------|---------|
| Subir o experimento | `docker compose up -d --build` |
| Ver se os nós estão vivos | `docker compose ps` / `docker ps` |
| Ler o que um nó imprimiu | `docker compose logs -f node-a` |
| Entrar no nó | `docker compose exec node-a sh` (Windows: Windows Terminal) |
| Derrubar um nó | `docker compose stop node-a` |
| Matar um nó de forma brusca | `docker kill $(docker compose ps -q node-a)` |
| Ver CPU/memória | `docker stats` |
| Zerar o lab | `docker compose down -v` |
| Rodar um Redis avulso | `docker run -d --name redis -p 6379:6379 redis:7-alpine` |
| Rodar MinIO avulso | `docker run -d --name minio -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"` |

---

## 8. Boas práticas no lab da disciplina

1. **Um Compose por tutorial** — facilita `down -v` sem derrubar o resto.
2. **Nomes explícitos de serviço** (`node-a`, `redis`) — aparecem em logs e DNS.
3. **Portas no host sequenciais** (`8001`, `8002`, `8003`) — fácil de lembrar em sala.
4. **Não dependa de `localhost` entre containers** — use o nome do serviço.
5. **Trate stop/kill como parte do roteiro** — falha é feature do experimento, não acidente.
6. **Documente no README do tutorial** a stack Compose esperada (o aluno só copia o caminho).

---

## 9. Serviços que vão aparecer nos próximos módulos

| Tutorial | Uso típico do Docker |
|----------|----------------------|
| Comunicação / locks / cache | Redis |
| Escalabilidade | vários workers + gateway |
| Armazenamento de arquivos | MinIO |
| Observabilidade | Jaeger / Loki / Prometheus (stack mínima) |
| Qualquer um | N containers como nós + `stop` para falha |

---

## Perguntas-guia

- Por que `curl localhost:8001` no host funciona, mas `curl localhost:8000` **dentro** de `node-b` não fala com `node-a`?
- Qual a diferença, para o experimento, entre `compose stop` e `docker kill`?
- Quando faz sentido volume nomeado vs container sem volume?
- O que o Compose resolve que uma sequência de `docker run` deixa fácil de errar em sala?
