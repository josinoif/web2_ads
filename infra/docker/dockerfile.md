# Introdução ao Dockerfile: Fundamentos, Tipos e Exemplos para Desenvolvimento de Software

## 1. Fundamentação Teórica

Um **Dockerfile** é um arquivo de texto que serve como receita para criar uma **imagem Docker personalizada**. Ele define instruções passo a passo que o Docker segue para construir um ambiente com todas as dependências e configurações necessárias para executar uma aplicação.

Dockerfiles são parte essencial da **virtualização de aplicações em nível de sistema operacional**, conhecida como conteinerização. Isso permite criar ambientes padronizados, replicáveis e portáteis para desenvolvimento e produção.

## 2. Por que esse recurso existe?

Antes do Docker, era comum enfrentarmos problemas como:

- "Funciona na minha máquina, mas não no servidor"
- Conflitos de versões de dependências
- Ambientes de desenvolvimento inconsistentes
- Processos de deploy complexos e manuais

O Docker resolve isso criando **contêners isolados**, e o Dockerfile automatiza a criação dessas imagens. Assim, todos os desenvolvedores, ambientes de teste e produção podem usar a **mesma imagem base**, garantindo previsibilidade e consistência.

## 3. Comandos e recursos do Dockerfile

### `FROM`

Define a imagem base a ser usada.

```Dockerfile
FROM node:22-alpine
```

### `WORKDIR`

Define o diretório de trabalho dentro do contêiner.

```Dockerfile
WORKDIR /app
```

### `COPY` ou `ADD`

Copia arquivos do host para o contêiner.

```Dockerfile
COPY . .
```

### `RUN`

Executa comandos durante a construção da imagem.

```Dockerfile
RUN npm install
```

### `CMD`

Define o comando padrão que o contêiner executará ao iniciar.

```Dockerfile
CMD ["node", "server.js"]
```

### `EXPOSE`

Indica que a aplicação escuta uma porta.

```Dockerfile
EXPOSE 3000
```

### `ENV`

Define variáveis de ambiente.

```Dockerfile
ENV NODE_ENV=production
```

### `ENTRYPOINT`

Semelhante ao CMD, mas não pode ser sobrescrito facilmente.

------

## 4. Como o Dockerfile ajuda no desenvolvimento de software

- **Ambientes consistentes:** Todo o time desenvolve e testa no mesmo ambiente
- **Facilidade de onboarding:** Um novo dev só precisa do Docker para começar
- **Testes isolados:** Pode testar múltiplas versões de uma dependência sem impactar seu sistema
- **CI/CD integrado:** Usado em pipelines de integração e entrega contínua
- **Portabilidade:** Leve seu ambiente para qualquer lugar que suporte Docker

------

## 5. Tipos de imagem Docker e suas diferenças

### `alpine`

- Base: Alpine Linux
- Tamanho: ~5MB
- Prós: Leve, rápida de baixar
- Contras: Nem sempre possui ferramentas (ex: bash, curl)

### `slim`

- Base: Debian enxuto
- Tamanho: ~20-50MB
- Prós: Boa compatibilidade e menor tamanho
- Contras: Menos ferramentas que a imagem completa

### `bookworm`, `bullseye`, `buster`

- Base: Debian
- Tamanho: 50-100MB ou mais
- Prós: Compatibilidade alta com dependências
- Contras: Imagem maior

------

## 6. Dockerfile para interação via bash (especialmente útil para Windows)

```Dockerfile
FROM debian:bookworm
RUN apt update && apt install -y bash curl git vim
CMD ["bash"]
```

### Como usar:

```bash
docker build -t my-dev-shell .
docker run -it my-dev-shell
```

### Útil para:

- Desenvolvedores Windows que querem terminal Linux completo
- Testar comandos em ambiente Unix-like

------

## 7. Dockerfile para desenvolvimento Angular

```Dockerfile
FROM node:22-bookworm
WORKDIR /app
RUN npm install -g @angular/cli
EXPOSE 4200
CMD ["bash"]
```

### Como usar:

```bash
docker build -t angular-dev .
docker run -it -p 4200:4200 -v ${PWD}:/app angular-dev
```

### Explicação:

- Usa imagem do Node.js
- Instala Angular CLI
- Permite servir a aplicação com `ng serve`
- Porta 4200 exposta para acessar via navegador

------

## 8. Dockerfile para desenvolvimento Python

```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash"]
```

### Como usar:

```bash
docker build -t python-dev .
docker run -it -v ${PWD}:/app python-dev
```

### Explicação:

- Usa imagem oficial do Python
- Instala dependências via `requirements.txt`
- Executa `bash` para ambiente interativo

------

## 9. Dockerfile para desenvolvimento Node.js

```Dockerfile
FROM node:22-bookworm
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Como usar:

```bash
docker build -t node-dev .
docker run -it -p 3000:3000 -v ${PWD}:/app node-dev
```

### Explicação:

- Usa imagem do Node.js
- Instala dependências
- Executa `npm start`
- Porta 3000 exposta para acesso

------

## 💡 Principais comandos de Docker para usar com Dockerfiles

| Comando                               | O que faz                                |
| ------------------------------------- | ---------------------------------------- |
| `docker build -t nome .`              | Constrói a imagem com base no Dockerfile |
| `docker run -it nome`                 | Roda um contêiner interativo             |
| `docker run -d -p 4200:4200 nome`     | Roda em background com porta exposta     |
| `docker exec -it <container_id> bash` | Entra no contêiner já em execução        |
| `docker ps`                           | Lista os contêineres ativos              |
| `docker stop <container_id>`          | Para um contêiner                        |



## Conclusão

O Dockerfile é uma ferramenta essencial para quem desenvolve software moderno. Ele permite criar ambientes isolados, reprodutíveis e eficientes. Ao entender bem os tipos de imagens, comandos e aplicações práticas, você estará apto a construir ambientes para qualquer stack: Node.js, Python, Angular, ou mesmo um simples shell Linux para exploração e testes.