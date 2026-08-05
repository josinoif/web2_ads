# Exercícios Resolvidos — Bloco 1

Exercícios do Bloco 1 ([Fundamentos de Containers](01-fundamentos-containers.md)). Tente **resolver antes de ler a resposta**.

---

## Exercício 1 — VM, container ou processo?

Para cada cenário, diga qual forma de isolação é mais adequada e por quê.

a) Script Python que roda em um laptop para analisar um CSV local.
b) 3000 instâncias de um microsserviço idêntico, com pico sazonal forte.
c) Executar um binário Windows legado num servidor Linux.
d) Plataforma educacional que executa **código não-confiável** de qualquer aluno (CodeLab).
e) Pipeline de testes que sobe Postgres/Redis a cada PR, destrói ao final.

### Solução

| # | Forma | Justificativa |
|---|-------|---------------|
| a | **Processo** | Não precisa isolamento; laptop é o dev. Container adicionaria complexidade sem ganho. |
| b | **Container** | Densidade alta, start rápido, imagem idêntica → escalabilidade horizontal eficiente. VM teria overhead proibitivo em 3000 instâncias. |
| c | **VM** | Precisa kernel Windows. Container Linux não roda binário Windows real (sem Wine etc.). |
| d | **Container + camada adicional** (gVisor/Kata) ou VM leve (Firecracker) | Container **sozinho** tem risco de escape. Código não-confiável exige mais rigor. O bloco discute isso; este módulo mostra como containers **ajudam**, não como resolvem 100%. |
| e | **Container** | Testcontainers/Compose: efêmero, isolado, rápido. Caso de uso ideal. |

**Insight:** "tudo é container" é moda; há casos onde VM ou processo comum continuam certos.

---

## Exercício 2 — Mapeando namespaces

Você precisa isolar um processo de forma que ele:

1. **Não veja** outros processos do host.
2. **Tenha** seu próprio IP.
3. **Monte** seu próprio `/home`.
4. **Compartilhe** memória IPC com outro processo do host.

Quais namespaces criar, quais reusar do host?

### Solução

| Requisito | Namespace | Ação |
|-----------|-----------|------|
| 1 — não ver processos | **PID** | criar novo |
| 2 — IP próprio | **NET** | criar novo |
| 3 — montagem própria de /home | **MNT** | criar novo |
| 4 — IPC compartilhado com host | **IPC** | **reusar** o do host (não criar) |

Demais (UTS, USER, CGROUP): geralmente criar novo para isolar hostname, privilégios e cgroups, mas **não obrigatórios** pelo enunciado.

Comando Docker equivalente (esboço):

```bash
docker run \
  --ipc=host \            # reusa IPC do host
  --hostname meuhost \    # implica UTS novo
  alpine sleep 9999
```

(Os namespaces PID, NET, MNT são **sempre** novos por padrão no `docker run`.)

**Isto é diferente em `--privileged`?** Sim — `--privileged` mantém namespaces mas **concede todas as capabilities**, devolvendo quase todo acesso do host ao processo.

---

## Exercício 3 — Rodando o inspector

Você rodou `inspect_namespaces.py` no seu shell e dentro de um `alpine:3.20` e observou:

| Namespace | Shell (PID 1000) | Container (PID 30000) |
|-----------|-------------------|------------------------|
| pid | 4026531836 | 4026532100 |
| net | 4026531993 | 4026532200 |
| user | 4026531837 | 4026531837 |

Duas observações e duas perguntas:

a) O namespace `user` é **o mesmo**. O que isso implica em termos de segurança?
b) Como você modificaria o `docker run` para **separar** o user namespace?

### Solução

**a)** Se o namespace `user` é igual ao do host, o UID 0 (root) dentro do container é **exatamente** o UID 0 do host. Em caso de escape (bug no runtime, `docker.sock` montado, `--privileged`), o atacante já é root no host.

Mitigações:

- **`USER` não-root** no Dockerfile — **primeira linha de defesa** (Bloco 2).
- **userns remap** no Docker — mapeia UID 0 do container para (por exemplo) UID 100000 do host. Configura-se no `/etc/docker/daemon.json`:
  ```json
  { "userns-remap": "default" }
  ```
- **Rootless Docker / Podman** — inverte o default: containers não-root por padrão, com userns automático.

**b)** Duas formas:

1. Configurar o daemon em `/etc/docker/daemon.json` com `"userns-remap": "default"` e reiniciar. **Todos** containers passam a usar namespace de user mapeado.
2. Usar **Podman** (rootless por default).

Em máquinas de desenvolvimento Linux, `podman` é um atalho instantâneo para isso.

---

## Exercício 4 — Cgroups vs ulimit

Volte ao Sintoma 4 da CodeLab: "Submissão infinita fura `ulimit -t` quando o programa faz fork".

a) Por que `ulimit -t` (CPU time) não funciona após fork?
b) Qual controller de cgroup v2 atende melhor?
c) Escreva o trecho em `docker run` que aplica limite de 1 CPU, 256 MB de RAM, 30 PIDs e tempo máximo.

### Solução

**a)** `ulimit` aplica limite **por processo**. Quando o processo-filho é criado com `fork()`, ele herda o limite mas o **contador é reiniciado** (cada processo tem seu próprio quantum de CPU time). Um programa malicioso que forka em loop continua consumindo CPU indefinidamente — o limite é respeitado por cada filho individualmente, mas o **grupo** consome tudo.

**b)**

- **`cpu`** controller (cgroup v2) com `cpu.max` limita CPU para o **grupo inteiro**, não por processo.
- **`pids`** controller limita fork bombs (número máximo de PIDs no grupo).
- **`memory`** controller limita RSS do grupo (OOM kill quando ultrapassa).

**c)**

```bash
docker run --rm \
  --cpus=1 \
  --memory=256m \
  --memory-swap=256m \
  --pids-limit=30 \
  --stop-timeout=30 \
  runner-python:0.1 \
  python /submissao/main.py
```

`--stop-timeout` só limita `docker stop`, não tempo de execução. Para tempo de execução real, envolver com `timeout 30s` dentro do container ou usar o orquestrador (K8s Jobs têm `activeDeadlineSeconds`).

---

## Exercício 5 — OCI na prática

Indique se cada afirmação é VERDADEIRA ou FALSA. Corrija as falsas.

a) Uma imagem OCI sempre tem `latest` como tag default implícita quando salva no registry.
b) O mesmo digest `sha256:...` sempre aponta para o mesmo conteúdo em qualquer registry.
c) Posso construir uma imagem com `docker build` e rodar com `podman run` sem conversão.
d) A ordem das layers na imagem **não importa** para caching.
e) `FROM scratch` resulta numa imagem **sem kernel**.

### Solução

| Item | V/F | Correção |
|------|-----|----------|
| a | **F** | `latest` é uma **tag opcional** aplicada apenas se nenhuma outra for especificada no `docker tag` / `docker push`. Não há "default implícito" universal; é convenção. |
| b | **V** | Conteúdo é endereçado por hash. Se o digest é idêntico, o conteúdo é idêntico — garantia criptográfica. |
| c | **V** | Ambos produzem/consomem OCI. Podman é drop-in. |
| d | **F** | Ordem **importa muito**. Camadas mais voláteis (código-fonte) ficam **por cima** para não invalidar o cache das mais estáveis (dependências). Bloco 2 entra em detalhe. |
| e | **F** | **Imagem nunca tem kernel** — kernel é do host. `FROM scratch` significa **sem sistema de arquivos base** (nem mesmo `libc`). Usado com binários estaticamente linkados (Go) para imagens mínimas. |

---

## Exercício 6 — Quando container NÃO basta

Um cenário: você precisa oferecer a **alunos** um ambiente de **root** para fazerem experimentos de **configuração de rede** (ex.: `iptables`, montar interfaces, usar `tcpdump`). Obviamente não pode ser o servidor de produção.

Uma engenheira propõe: "vamos rodar cada aluno num container com `--privileged`, e está resolvido".

Critique em 5 a 6 linhas.

### Solução

Crítica ponto a ponto:

1. **`--privileged` desabilita quase todas as proteções**: concede todas as capabilities, desativa AppArmor/SELinux, permite montar qualquer dispositivo. O aluno, dentro do container, tem acesso equivalente a root no host. CVE-2019-5736 no runc foi um escape **sem** privileged — com `--privileged`, é trivial.

2. **`--privileged` compartilha `/dev`**: o aluno pode manipular dispositivos do host (disco, GPU), não só "redes".

3. **O caso de uso pede isolação forte, não container apenas**: a solução adequada é **VM por aluno** (lightweight — Firecracker / Kata Containers — ou via hypervisor tradicional). A VM isola o kernel; container, não.

4. **Alternativa com menos proteção perdida**: `--cap-add=NET_ADMIN --cap-add=NET_RAW` dá acesso a ajustes de rede **sem** abrir todas as outras capabilities. Se o laboratório **apenas** precisa de iptables/tcpdump, isso já é suficiente e muito mais seguro.

5. **Se for usar container**, adicionar `gVisor` ou `Kata` como runtime dá isolação de syscalls e resolve grande parte do risco — mas `--privileged` mesmo assim deveria estar **proibido**.

**Resposta curta:** `--privileged` é quase sinônimo de "não estou rodando em container" do ponto de vista de segurança. A engenheira resolveu o sintoma (funciona) e criou um vetor de escape sério. Prefira capabilities específicas + runtime reforçado, ou VM quando o isolamento precisa ser robusto.

---

## Próximo passo

- Retome o **[Bloco 1](01-fundamentos-containers.md)** se algum exercício foi difícil.
- Siga para o **[Bloco 2 — Dockerfile e boas práticas](../bloco-2/02-dockerfile-boas-praticas.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Fundamentos de Containers](01-fundamentos-containers.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Bloco 2 — Dockerfile e Boas Práticas](../bloco-2/02-dockerfile-boas-praticas.md) |

<!-- nav:end -->
