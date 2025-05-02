# Introdução ao Docker Compose  

## 🔹 Módulo 1 – Introdução ao Docker e Docker Compose  

### O que é Docker?  
Docker é uma plataforma que permite criar, implantar e executar aplicações em containers. Containers são ambientes isolados que incluem tudo o que uma aplicação precisa para funcionar, como bibliotecas, dependências e o próprio código.  

### Containers vs. Máquinas Virtuais  
- **Containers**: Leves, compartilham o kernel do sistema operacional, iniciam rapidamente.  
- **Máquinas Virtuais**: Mais pesadas, incluem um sistema operacional completo, consomem mais recursos.  

### Problemas que o Docker Compose resolve  
- Gerenciar múltiplos containers como uma única aplicação.  
- Definir configurações em um único arquivo (`docker-compose.yml`).  
- Facilitar a comunicação entre containers.  

### Visão geral do `docker-compose.yml`  
O arquivo `docker-compose.yml` é usado para configurar os serviços, volumes, redes e outras dependências de uma aplicação. Exemplo básico:  

```yaml  
version: '3.8'  
services:  
  app:  
    build: .  
    ports:  
      - "3000:3000"  
  db:  
    image: postgres:latest  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  

## 🔹 Módulo 2 – Estrutura e Sintaxe do `docker-compose.yml`  

### O que é o arquivo `docker-compose.yml`?  
O arquivo `docker-compose.yml` é o coração do Docker Compose. Ele define como os serviços de uma aplicação devem ser configurados, conectados e executados. É um arquivo no formato YAML que descreve os serviços, volumes, redes e outras configurações necessárias para a aplicação.

### Estrutura básica do `docker-compose.yml`  
A estrutura básica do arquivo inclui:  
1. **Versão**: Define a versão do Docker Compose a ser usada.  
2. **Serviços**: Representam os containers que serão executados.  
3. **Volumes**: Configuram a persistência de dados.  
4. **Redes**: Conectam os serviços entre si.  

Exemplo básico:  
```yaml  
version: '3.8'  
services:  
  app:  
    build: .  
    ports:  
      - "3000:3000"  
  db:  
    image: postgres:latest  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  

### Detalhando cada seção  

#### 1. **Versão (`version`)**  
A versão do Compose define os recursos disponíveis no arquivo.  
- Exemplo:  
  ```yaml  
  version: '3.8'  
  ```  
  A versão `3.8` é amplamente utilizada e compatível com a maioria dos recursos modernos do Docker Compose.

#### 2. **Serviços (`services`)**  
Os serviços representam os containers que compõem a aplicação. Cada serviço é configurado com instruções específicas, como imagem, portas, volumes e variáveis de ambiente.  
- Exemplo:  
  ```yaml  
  services:  
    web:  
      build: ./web  
      ports:  
        - "8080:80"  
      depends_on:  
        - db  
    db:  
      image: mysql:5.7  
      environment:  
        MYSQL_ROOT_PASSWORD: example  
  ```  
  Neste exemplo:  
  - O serviço `web` é construído a partir do diretório `./web`.  
  - O serviço `db` utiliza a imagem oficial do MySQL.  
  - A variável de ambiente `MYSQL_ROOT_PASSWORD` é configurada para o banco de dados.  

#### 3. **Volumes (`volumes`)**  
Os volumes são usados para persistir dados gerados pelos containers.  
- Exemplo:  
  ```yaml  
  volumes:  
    db_data:  
  services:  
    database:  
      image: postgres:latest  
      volumes:  
        - db_data:/var/lib/postgresql/data  
  ```  
  Neste exemplo, o volume `db_data` armazena os dados do PostgreSQL, garantindo que eles não sejam perdidos ao reiniciar o container.

#### 4. **Redes (`networks`)**  
As redes conectam os serviços entre si, permitindo que eles se comuniquem.  
- Exemplo:  
  ```yaml  
  networks:  
    app_network:  
  services:  
    web:  
      build: ./web  
      networks:  
        - app_network  
    db:  
      image: mysql:5.7  
      networks:  
        - app_network  
  ```  
  Aqui, os serviços `web` e `db` estão conectados à mesma rede `app_network`, permitindo que se comuniquem diretamente.

### Principais instruções do `docker-compose.yml`  

#### `build`  
Define o contexto de build para criar a imagem do serviço.  
- Exemplo:  
  ```yaml  
  build: ./app  
  ```  
  O Docker usará o Dockerfile localizado no diretório `./app` para construir a imagem.

#### `image`  
Especifica uma imagem Docker existente para o serviço.  
- Exemplo:  
  ```yaml  
  image: nginx:latest  
  ```  
  O Docker usará a imagem oficial do Nginx na versão mais recente.

#### `ports`  
Mapeia portas do container para o host.  
- Exemplo:  
  ```yaml  
  ports:  
    - "8080:80"  
  ```  
  O tráfego na porta `8080` do host será redirecionado para a porta `80` do container.

#### `volumes`  
Define volumes para persistência de dados ou compartilhamento de arquivos.  
- Exemplo:  
  ```yaml  
  volumes:  
    - ./data:/app/data  
  ```  
  O diretório local `./data` será montado no container no caminho `/app/data`.

#### `environment`  
Configura variáveis de ambiente para o serviço.  
- Exemplo:  
  ```yaml  
  environment:  
    - NODE_ENV=production  
    - API_KEY=12345  
  ```  
  As variáveis `NODE_ENV` e `API_KEY` serão acessíveis dentro do container.

#### `depends_on`  
Define dependências entre serviços, garantindo que um serviço seja iniciado antes de outro.  
- Exemplo:  
  ```yaml  
  depends_on:  
    - db  
  ```  
  O serviço atual só será iniciado após o serviço `db`.

### Exemplo completo e detalhado  
```yaml  
version: '3.8'  
services:  
  frontend:  
    build: ./frontend  
    ports:  
      - "3000:3000"  
    depends_on:  
      - backend  
  backend:  
    build: ./backend  
    ports:  
      - "5000:5000"  
    environment:  
      DATABASE_URL: postgres://user:password@db:5432/mydatabase  
    depends_on:  
      - db  
  db:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: user  
      POSTGRES_PASSWORD: password  
      POSTGRES_DB: mydatabase  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
networks:  
  default:  
    driver: bridge  
```  

Neste exemplo:  
- O serviço `frontend` depende do `backend`, que por sua vez depende do `db`.  
- O banco de dados PostgreSQL utiliza um volume nomeado para persistir os dados.  
- A rede padrão conecta todos os serviços.

### Boas práticas ao criar o `docker-compose.yml`  
1. **Use nomes descritivos para serviços, volumes e redes**: Facilita a leitura e manutenção.  
2. **Separe configurações sensíveis**: Utilize arquivos `.env` para armazenar variáveis de ambiente.  
3. **Teste individualmente cada serviço**: Certifique-se de que cada serviço funciona antes de integrá-los.  
4. **Documente o arquivo**: Adicione comentários para explicar configurações complexas.  
5. **Evite hardcoding de valores**: Use variáveis de ambiente para maior flexibilidade.  

### Testando o arquivo `docker-compose.yml`  
Após criar o arquivo, você pode testá-lo com os seguintes comandos:  
- `docker compose config`: Valida a sintaxe do arquivo.  
- `docker compose up`: Inicia os serviços definidos no arquivo.  
- `docker compose ps`: Lista os serviços em execução.  

Essas práticas e exemplos ajudarão você a dominar o uso do `docker-compose.yml` e a criar configurações robustas para suas aplicações.

## 🔹 Módulo 3 – Subindo Múltiplos Containers  

### Exemplo com backend + banco de dados  
```yaml  
services:  
  backend:  
    build: ./backend  
    ports:  
      - "5000:5000"  
    environment:  
      API_KEY: "my-secret-key"  
    depends_on:  
      - database  
  database:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: user  
      POSTGRES_PASSWORD: password  
      POSTGRES_DB: mydatabase  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  
Neste exemplo:  
- O serviço `backend` depende do serviço `database` e só será iniciado após o banco de dados.  
- O volume `db_data` é usado para persistir os dados do PostgreSQL.  
- Variáveis de ambiente configuram o banco de dados e o backend.

### Exemplo com frontend, backend e banco de dados  
```yaml  
services:  
  frontend:  
    build: ./frontend  
    ports:  
      - "3000:3000"  
    depends_on:  
      - backend  
  backend:  
    build: ./backend  
    ports:  
      - "5000:5000"  
    depends_on:  
      - database  
  database:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: user  
      POSTGRES_PASSWORD: password  
      POSTGRES_DB: mydatabase  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  
Neste exemplo:  
- O serviço `frontend` depende do `backend`, que por sua vez depende do `database`.  
- A comunicação entre os serviços é feita automaticamente via rede interna do Docker Compose.  

### Comando `docker compose up`  
- `docker compose up`: Inicia os containers definidos no arquivo `docker-compose.yml`.  
- `docker compose up -d`: Inicia os containers em segundo plano (modo "detached").  
- `docker compose up --build`: Reconstrói as imagens antes de iniciar os containers.  

### Logs e status dos containers  
- `docker compose logs`: Exibe os logs de todos os containers.  
  - Para logs de um serviço específico: `docker compose logs <nome_do_serviço>`.  
- `docker compose ps`: Lista os containers em execução e seus status.  

### Exemplo prático com logs  
```bash  
docker compose up -d  
docker compose logs -f backend  
```  
Neste exemplo:  
- Os containers são iniciados em segundo plano.  
- Os logs do serviço `backend` são exibidos em tempo real com o comando `-f`.

### Testando a comunicação entre serviços  
Após iniciar os containers, você pode testar a comunicação entre eles. Por exemplo:  
- Acesse o serviço `backend` e verifique se ele consegue se conectar ao banco de dados.  
- Use ferramentas como `curl` ou `Postman` para testar endpoints do `backend` e verificar se o `frontend` está funcionando corretamente.

### Boas práticas ao subir múltiplos containers  
1. **Defina dependências claras**: Use `depends_on` para garantir a ordem de inicialização.  
2. **Configure variáveis de ambiente**: Utilize arquivos `.env` para separar configurações sensíveis.  
3. **Teste individualmente cada serviço**: Certifique-se de que cada serviço funciona corretamente antes de integrá-los.  
4. **Use volumes para persistência**: Evite perder dados ao reiniciar containers.  
5. **Monitore os logs**: Acompanhe os logs para identificar problemas rapidamente.  

### Exemplo avançado com healthcheck  
```yaml  
services:  
  backend:  
    build: ./backend  
    ports:  
      - "5000:5000"  
    depends_on:  
      database:  
        condition: service_healthy  
  database:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: user  
      POSTGRES_PASSWORD: password  
      POSTGRES_DB: mydatabase  
    healthcheck:  
      test: ["CMD-SHELL", "pg_isready -U user"]  
      interval: 10s  
      timeout: 5s  
      retries: 3  
    volumes:  
      - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  
Neste exemplo:  
- O `healthcheck` garante que o banco de dados está pronto antes de iniciar o `backend`.  
- Isso evita erros de conexão durante a inicialização.  
- O comando `pg_isready` verifica a disponibilidade do PostgreSQL.  
- A configuração de `interval`, `timeout` e `retries` define como o Docker verifica a saúde do serviço.


## 🔹 Módulo 4 – Volumes e Persistência de Dados  

### O que são volumes no Docker?  
Volumes são a forma recomendada de persistir dados gerados e utilizados pelos containers. Eles permitem que os dados sobrevivam a reinicializações ou recriações dos containers, garantindo que informações importantes não sejam perdidas.

### Tipos de volumes  
1. **Volumes Nomeados**:  
  Criados explicitamente e podem ser reutilizados por diferentes containers.  
  Exemplo:  
  ```yaml  
  volumes:  
    db_data:  
  services:  
    database:  
     image: mysql:latest  
     volumes:  
      - db_data:/var/lib/mysql  
  ```  
  Neste exemplo, o volume `db_data` é nomeado e armazena os dados do MySQL.

2. **Volumes Anônimos**:  
  Criados automaticamente pelo Docker e não possuem um nome específico.  
  Exemplo:  
  ```yaml  
  services:  
    app:  
     image: nginx:latest  
     volumes:  
      - /var/lib/nginx  
  ```  
  Aqui, o Docker cria um volume anônimo para `/var/lib/nginx`.

3. **Bind Mounts**:  
  Mapeiam um diretório local diretamente para o container.  
  Exemplo:  
  ```yaml  
  services:  
    app:  
     image: nginx:latest  
     volumes:  
      - ./html:/usr/share/nginx/html  
  ```  
  Neste caso, o diretório local `./html` é montado no container, permitindo edição direta dos arquivos.

### Mapeamento de volumes locais  
O mapeamento de volumes locais é útil para persistir dados em diretórios específicos do host.  
Exemplo:  
```yaml  
services:  
  database:  
   image: mysql:latest  
   volumes:  
    - ./data:/var/lib/mysql  
```  
Neste exemplo:  
- O diretório local `./data` armazena os dados do MySQL.  
- Mesmo que o container seja removido, os dados permanecerão no diretório local.

### Boas práticas de persistência  
1. **Use volumes nomeados para dados importantes**:  
  Volumes nomeados são gerenciados pelo Docker, garantindo maior controle e reutilização.  
  Exemplo:  
  ```yaml  
  volumes:  
    db_data:  
  services:  
    database:  
     image: postgres:latest  
     volumes:  
      - db_data:/var/lib/postgresql/data  
  ```  

2. **Evite armazenar dados críticos diretamente em containers**:  
  Dados armazenados diretamente no sistema de arquivos do container serão perdidos se o container for removido.

3. **Configure permissões adequadas**:  
  Certifique-se de que o usuário do container tenha as permissões corretas para acessar os volumes.  
  Exemplo:  
  ```yaml  
  services:  
    app:  
     image: myapp:latest  
     volumes:  
      - ./config:/app/config  
     user: "1000:1000"  
  ```  

4. **Separe dados sensíveis**:  
  Utilize volumes diferentes para separar dados sensíveis de outros arquivos.  

5. **Evite volumes anônimos para dados persistentes**:  
  Volumes anônimos são úteis para testes ou dados temporários, mas não devem ser usados para persistência de longo prazo.

### Exemplo prático completo  
```yaml  
version: '3.8'  
services:  
  app:  
   image: myapp:latest  
   volumes:  
    - ./app-data:/usr/src/app/data  
   ports:  
    - "8080:8080"  
  database:  
   image: postgres:latest  
   environment:  
    POSTGRES_USER: admin  
    POSTGRES_PASSWORD: secret  
   volumes:  
    - db_data:/var/lib/postgresql/data  
volumes:  
  db_data:  
```  
Neste exemplo:  
- O serviço `app` utiliza um bind mount para persistir dados localmente.  
- O serviço `database` utiliza um volume nomeado para armazenar os dados do PostgreSQL.  
- Ambos os serviços têm seus dados persistidos de forma segura e reutilizável.

### Testando volumes  
Para verificar os volumes criados, use o comando:  
```bash  
docker volume ls  
```  
Para inspecionar um volume específico:  
```bash  
docker volume inspect <nome_do_volume>  
```  
Para remover volumes não utilizados:  
```bash  
docker volume prune  
```  
Esses comandos ajudam a gerenciar e monitorar os volumes no Docker.

## 🔹 Módulo 5 – Redes e Comunicação entre Serviços  

### Comunicação entre containers via Compose  
No Docker Compose, os containers de serviços definidos no mesmo arquivo `docker-compose.yml` podem se comunicar diretamente pelo nome do serviço. Isso ocorre porque o Docker cria automaticamente uma rede padrão para os serviços, permitindo que eles se conectem sem a necessidade de configurações adicionais.

Exemplo básico:  
```yaml  
services:  
  web:  
    build: ./web  
    depends_on:  
      - db  
  db:  
    image: postgres:latest  
```  
Neste exemplo:  
- O serviço `web` pode se conectar ao banco de dados `db` usando o nome `db` como hostname.  
- Por exemplo, no código do backend, a URL de conexão ao banco de dados seria algo como `postgres://user:password@db:5432/mydatabase`.

### Tipos de redes no Docker Compose  
O Docker oferece diferentes tipos de redes para atender a cenários variados. A escolha da rede depende do caso de uso e das necessidades específicas da aplicação.

#### 1. **Bridge (Ponte)**  
- **Descrição**: É o tipo de rede padrão para containers em um único host. Cada container conectado à rede bridge pode se comunicar com outros containers na mesma rede.  
- **Quando usar**:  
  - Para aplicações locais ou em desenvolvimento.  
  - Quando os serviços estão no mesmo host.  
- **Exemplo**:  
  ```yaml  
  networks:  
    my_bridge_network:  
      driver: bridge  
  services:  
    app:  
      image: myapp:latest  
      networks:  
        - my_bridge_network  
    db:  
      image: postgres:latest  
      networks:  
        - my_bridge_network  
  ```  
  Neste exemplo, os serviços `app` e `db` estão conectados à rede `my_bridge_network` e podem se comunicar diretamente.

#### 2. **Host**  
- **Descrição**: Compartilha a pilha de rede do host com o container. O container usa a mesma interface de rede do host, sem isolamento.  
- **Quando usar**:  
  - Para aplicações que precisam de alto desempenho em acesso à rede.  
  - Quando o isolamento de rede não é necessário.  
- **Exemplo**:  
  ```yaml  
  services:  
    app:  
      image: myapp:latest  
      network_mode: host  
  ```  
  Neste exemplo, o serviço `app` usa a rede do host diretamente. Isso significa que ele pode acessar os serviços do host sem restrições.

#### 3. **Overlay**  
- **Descrição**: Permite a comunicação entre containers em diferentes hosts. É usada principalmente em clusters Docker Swarm ou Kubernetes.  
- **Quando usar**:  
  - Para aplicações distribuídas em múltiplos hosts.  
  - Quando é necessário orquestrar serviços em um cluster.  
- **Exemplo**:  
  ```yaml  
  networks:  
    my_overlay_network:  
      driver: overlay  
  services:  
    app:  
      image: myapp:latest  
      networks:  
        - my_overlay_network  
    db:  
      image: postgres:latest  
      networks:  
        - my_overlay_network  
  ```  
  Neste exemplo, os serviços `app` e `db` podem estar em hosts diferentes, mas ainda assim se comunicarão pela rede `my_overlay_network`.

### Como escolher entre Bridge, Host e Overlay  
- **Bridge**:  
  - Use para desenvolvimento local ou quando todos os containers estão no mesmo host.  
  - É a escolha padrão para a maioria dos casos simples.  
- **Host**:  
  - Use para aplicações que precisam de desempenho máximo em acesso à rede.  
  - Evite em cenários onde o isolamento de rede é importante.  
- **Overlay**:  
  - Use para aplicações distribuídas em clusters.  
  - Requer configuração adicional e é mais adequada para produção em larga escala.

### Boas práticas para redes no Docker Compose  
1. **Use redes nomeadas**:  
   - Evite usar a rede padrão criada automaticamente pelo Docker. Redes nomeadas tornam a configuração mais clara e fácil de gerenciar.  
   - Exemplo:  
     ```yaml  
     networks:  
       app_network:  
         driver: bridge  
     services:  
       web:  
         image: nginx:latest  
         networks:  
           - app_network  
     ```  

2. **Separe redes por contexto**:  
   - Use redes diferentes para separar serviços que não precisam se comunicar diretamente.  
   - Exemplo:  
     ```yaml  
     networks:  
       frontend_network:  
         driver: bridge  
       backend_network:  
         driver: bridge  
     services:  
       frontend:  
         image: react-app:latest  
         networks:  
           - frontend_network  
       backend:  
         image: node-api:latest  
         networks:  
           - backend_network  
     ```  

3. **Configure sub-redes personalizadas**:  
   - Para maior controle, defina sub-redes específicas para suas redes.  
   - Exemplo:  
     ```yaml  
     networks:  
       custom_network:  
         driver: bridge  
         ipam:  
           config:  
             - subnet: 192.168.1.0/24  
     ```  

4. **Evite expor portas desnecessárias**:  
   - Use redes internas para comunicação entre serviços e exponha apenas o necessário para o host.  
   - Exemplo:  
     ```yaml  
     services:  
       web:  
         image: nginx:latest  
         ports:  
           - "8080:80"  
         networks:  
           - public_network  
       db:  
         image: postgres:latest  
         networks:  
           - private_network  
     networks:  
       public_network:  
         driver: bridge  
       private_network:  
         driver: bridge  
     ```  

5. **Documente as redes**:  
   - Adicione comentários no arquivo `docker-compose.yml` explicando o propósito de cada rede.  

### Casos de uso alinhados com práticas de mercado  
1. **Aplicações Web com Backend e Banco de Dados**:  
   - Use uma rede bridge para conectar o backend ao banco de dados.  
   - Exponha apenas o backend para o frontend e o frontend para o host.  

2. **Microserviços em Clusters**:  
   - Use redes overlay para conectar serviços distribuídos em diferentes hosts.  
   - Combine com ferramentas de orquestração como Docker Swarm ou Kubernetes.  

3. **Ambientes de Desenvolvimento**:  
   - Use redes bridge para isolar os serviços localmente.  
   - Configure sub-redes personalizadas para simular ambientes de produção.  

4. **Ambientes de Produção**:  
   - Use redes overlay para alta disponibilidade e escalabilidade.  
   - Combine com balanceadores de carga para gerenciar o tráfego entre serviços.  

### Testando redes no Docker Compose  
- Liste as redes criadas:  
  ```bash  
  docker network ls  
  ```  
- Inspecione uma rede específica:  
  ```bash  
  docker network inspect <nome_da_rede>  
  ```  
- Verifique a conectividade entre containers:  
  ```bash  
  docker exec -it <container_name> ping <nome_do_serviço>  
  ```  

Essas práticas e exemplos ajudam a configurar redes robustas e seguras, alinhadas com as necessidades de desenvolvimento e produção.

## 🔹 Módulo 6 – Variáveis de Ambiente e `.env`  

### Separando configuração do código  
Manter configurações sensíveis, como credenciais e chaves de API, fora do código é uma prática essencial para segurança e flexibilidade. O uso de arquivos `.env` permite que essas configurações sejam facilmente alteradas sem modificar o código-fonte ou o arquivo `docker-compose.yml`.

### Criando um arquivo `.env`  
Um arquivo `.env` é um arquivo de texto simples que armazena pares de chave-valor. Exemplo:  
```env  
DB_USER=admin  
DB_PASS=supersecret  
API_KEY=12345  
NODE_ENV=production  
```  

### Uso de `.env` no `docker-compose.yml`  
No arquivo `docker-compose.yml`, você pode referenciar variáveis definidas no `.env` usando a sintaxe `${VARIAVEL}`. Exemplo:  
```yaml  
version: '3.8'  
services:  
  database:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: ${DB_USER}  
      POSTGRES_PASSWORD: ${DB_PASS}  
  app:  
    build: ./app  
    environment:  
      API_KEY: ${API_KEY}  
      NODE_ENV: ${NODE_ENV}  
```  

### Carregando o arquivo `.env`  
Por padrão, o Docker Compose carrega automaticamente o arquivo `.env` localizado no mesmo diretório do arquivo `docker-compose.yml`. Caso o arquivo `.env` esteja em outro local ou tenha outro nome, você pode especificá-lo com a flag `--env-file`:  
```bash  
docker compose --env-file ./config/.env up  
```  

### Exemplo prático com múltiplos serviços  
```yaml  
version: '3.8'  
services:  
  backend:  
    build: ./backend  
    environment:  
      DATABASE_URL: postgres://${DB_USER}:${DB_PASS}@database:5432/${DB_NAME}  
      API_KEY: ${API_KEY}  
  database:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: ${DB_USER}  
      POSTGRES_PASSWORD: ${DB_PASS}  
      POSTGRES_DB: ${DB_NAME}  
```  
Arquivo `.env`:  
```env  
DB_USER=admin  
DB_PASS=supersecret  
DB_NAME=mydatabase  
API_KEY=abcdef123456  
```  

### Boas práticas ao usar `.env`  
1. **Nunca versionar o arquivo `.env` no controle de versão**:  
   Adicione o arquivo `.env` ao `.gitignore` para evitar que informações sensíveis sejam expostas.  
   ```gitignore  
   .env  
   ```  

2. **Use arquivos `.env` diferentes para cada ambiente**:  
   Crie arquivos como `.env.dev`, `.env.staging` e `.env.prod` para separar configurações de desenvolvimento, homologação e produção.  

3. **Valide as variáveis de ambiente**:  
   Certifique-se de que todas as variáveis necessárias estão definidas antes de iniciar os serviços. Você pode usar ferramentas como `dotenv-linter` para verificar inconsistências.  

4. **Evite hardcoding de valores no `docker-compose.yml`**:  
   Sempre que possível, use variáveis de ambiente para valores configuráveis.  

5. **Proteja o arquivo `.env`**:  
   Restrinja permissões de leitura/escrita para evitar acessos não autorizados.  
   ```bash  
   chmod 600 .env  
   ```  

6. **Documente as variáveis de ambiente**:  
   Crie um arquivo `.env.example` com exemplos de valores para facilitar a configuração por outros desenvolvedores.  
   ```env  
   DB_USER=example_user  
   DB_PASS=example_password  
   DB_NAME=example_database  
   API_KEY=example_key  
   ```  

### Lidando com segredos em produção  
Para produção, evite armazenar segredos diretamente no arquivo `.env`. Considere as seguintes alternativas:  
- **Gerenciadores de segredos**: Use ferramentas como AWS Secrets Manager, HashiCorp Vault ou Azure Key Vault.  
- **Variáveis de ambiente do sistema**: Configure variáveis diretamente no ambiente do servidor.  
- **Docker Secrets**: Para maior segurança, utilize o recurso de segredos do Docker Swarm.  

Exemplo com Docker Secrets:  
1. Crie o segredo:  
   ```bash  
   echo "supersecret" | docker secret create db_password -  
   ```  
2. Atualize o `docker-compose.yml`:  
   ```yaml  
   services:  
     database:  
       image: postgres:latest  
       secrets:  
         - db_password  
   secrets:  
     db_password:  
       external: true  
   ```  

### Debugging de variáveis de ambiente  
Para verificar se as variáveis estão sendo carregadas corretamente, você pode inspecionar o ambiente do container:  
```bash  
docker compose exec <serviço> env  
```  

### Testando configurações  
Antes de iniciar os serviços, valide o arquivo `docker-compose.yml` e as variáveis de ambiente:  
```bash  
docker compose config  
```  

Essas práticas ajudam a manter suas configurações seguras, organizadas e fáceis de gerenciar em diferentes ambientes.

## 🔹 Módulo 7 – Dependências entre Serviços  

### `depends_on` vs. `healthcheck`  

No Docker Compose, a dependência entre serviços pode ser gerenciada de duas formas principais:  

1. **`depends_on`**:  
  - Define a ordem de inicialização dos serviços.  
  - Garante que um serviço seja iniciado antes de outro, mas **não verifica se o serviço está pronto para uso**.  
  - Útil para cenários simples onde a ordem de inicialização é suficiente.  

  Exemplo:  
  ```yaml  
  version: '3.8'  
  services:  
    app:  
     build: ./app  
     depends_on:  
      - db  
    db:  
     image: postgres:latest  
  ```  
  Neste exemplo, o serviço `db` será iniciado antes do serviço `app`. No entanto, o `app` pode tentar se conectar ao banco de dados antes que ele esteja pronto para aceitar conexões.

2. **`healthcheck`**:  
  - Verifica se o serviço está pronto para uso antes de permitir que outros serviços dependam dele.  
  - Útil para cenários onde a simples inicialização do container não garante que o serviço esteja funcional.  

  Exemplo com `healthcheck`:  
  ```yaml  
  version: '3.8'  
  services:  
    app:  
     build: ./app  
     depends_on:  
      db:  
        condition: service_healthy  
    db:  
     image: postgres:latest  
     healthcheck:  
      test: ["CMD-SHELL", "pg_isready -U postgres"]  
      interval: 10s  
      timeout: 5s  
      retries: 3  
  ```  
  Neste exemplo:  
  - O `healthcheck` usa o comando `pg_isready` para verificar se o banco de dados PostgreSQL está pronto.  
  - O serviço `app` só será iniciado após o banco de dados passar no teste de saúde.  

### Estratégias de Retry  

Em cenários mais complexos, onde a inicialização de serviços depende de condições específicas, é comum usar scripts externos ou ferramentas para gerenciar retries.  

#### Usando o script `wait-for-it`  
O `wait-for-it` é um script popular que aguarda a disponibilidade de um serviço antes de prosseguir.  

Exemplo:  
1. Adicione o script ao seu projeto:  
  ```bash  
  curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh  
  chmod +x wait-for-it.sh  
  ```  

2. Atualize o `docker-compose.yml`:  
  ```yaml  
  version: '3.8'  
  services:  
    app:  
     build: ./app  
     command: ["./wait-for-it.sh", "db:5432", "--", "npm", "start"]  
     depends_on:  
      - db  
    db:  
     image: postgres:latest  
  ```  
  Neste exemplo:  
  - O script `wait-for-it.sh` aguarda a disponibilidade do banco de dados na porta `5432` antes de iniciar o comando `npm start` no serviço `app`.  

#### Usando `retry` em scripts personalizados  
Outra abordagem é criar scripts personalizados com lógica de retry.  

Exemplo de script Bash:  
```bash  
#!/bin/bash  
RETRIES=5  
until psql -h db -U postgres -c '\q'; do  
  echo "Aguardando o banco de dados..."  
  sleep 5  
  RETRIES=$((RETRIES-1))  
  if [ $RETRIES -le 0 ]; then  
   echo "Banco de dados não está disponível. Abortando."  
   exit 1  
  fi  
done  
echo "Banco de dados está pronto!"  
exec "$@"  
```  

Atualize o `docker-compose.yml` para usar o script:  
```yaml  
version: '3.8'  
services:  
  app:  
   build: ./app  
   entrypoint: ["./wait-for-db.sh"]  
   depends_on:  
    - db  
  db:  
   image: postgres:latest  
```  

### Casos de Uso no Mercado  

1. **Aplicações Web com Backend e Banco de Dados**:  
  - Cenário: Um backend que depende de um banco de dados para inicializar corretamente.  
  - Solução: Use `healthcheck` para garantir que o banco de dados esteja pronto antes de iniciar o backend.  

2. **Microserviços com Dependências Complexas**:  
  - Cenário: Um serviço de autenticação que depende de um banco de dados e de um serviço de cache.  
  - Solução: Combine `depends_on` com scripts de retry para gerenciar dependências de forma robusta.  

3. **Ambientes de Desenvolvimento**:  
  - Cenário: Desenvolvedores precisam de um ambiente local onde todos os serviços estejam prontos para uso.  
  - Solução: Use `wait-for-it` ou scripts personalizados para garantir que os serviços estejam disponíveis antes de iniciar o desenvolvimento.  

4. **Ambientes de Produção**:  
  - Cenário: Garantir que serviços críticos estejam prontos antes de expor endpoints ao tráfego de produção.  
  - Solução: Configure `healthcheck` com condições rigorosas e monitore logs para identificar problemas.  

### Boas Práticas  

1. **Combine `depends_on` e `healthcheck`**:  
  Use `depends_on` para gerenciar a ordem de inicialização e `healthcheck` para garantir que os serviços estejam prontos.  

2. **Teste os `healthchecks` regularmente**:  
  Certifique-se de que os comandos usados nos `healthchecks` são confiáveis e refletem o estado real do serviço.  

3. **Evite dependências circulares**:  
  Estruture seus serviços para evitar que um dependa de outro que, por sua vez, dependa do primeiro.  

4. **Documente as dependências**:  
  Inclua comentários no `docker-compose.yml` explicando as dependências entre os serviços.  

5. **Monitore os tempos de inicialização**:  
  Ajuste os intervalos e tempos limite dos `healthchecks` para refletir os tempos reais de inicialização dos serviços.  

Essas estratégias e práticas ajudam a criar ambientes robustos e confiáveis, alinhados com as necessidades do mercado moderno de desenvolvimento e operação de software.

## 🔹 Módulo 8 – Docker Compose para Desenvolvimento  

O Docker Compose é uma ferramenta poderosa para criar ambientes de desenvolvimento consistentes e eficientes. Ele permite que desenvolvedores configurem rapidamente múltiplos serviços, como bancos de dados, APIs e frontends, em um único arquivo. Este módulo detalha como usar o Docker Compose para otimizar o fluxo de trabalho de desenvolvimento, com foco em hot-reload, rebuilds automáticos e configurações específicas para desenvolvimento.

### Hot-reload com Bind Mounts  

O hot-reload é uma funcionalidade essencial para desenvolvimento, pois permite que alterações no código sejam refletidas imediatamente no ambiente de execução, sem a necessidade de reiniciar os containers. Para habilitar o hot-reload, utilizamos bind mounts, que mapeiam um diretório local para o container.

#### Exemplo de configuração com hot-reload:  
```yaml
version: '3.8'
services:
  app:
    build: .
    volumes:
      - ./src:/app/src
    ports:
      - "3000:3000"
    command: npm run dev
```

Neste exemplo:  
- O diretório local `./src` é mapeado para o diretório `/app/src` dentro do container.  
- Alterações feitas no código local são refletidas imediatamente no container.  
- O comando `npm run dev` inicia o servidor de desenvolvimento com suporte a hot-reload.

#### Casos de uso:  
- **Aplicações Node.js**: Use ferramentas como `nodemon` para reiniciar automaticamente o servidor ao detectar alterações no código.  
- **Aplicações React/Vue/Angular**: Configure o servidor de desenvolvimento para monitorar alterações nos arquivos do projeto.  

#### Boas práticas:  
1. **Evite mapear diretórios desnecessários**: Mapeie apenas os diretórios relevantes para o desenvolvimento, como `src` ou `config`.  
2. **Configure permissões adequadas**: Certifique-se de que o usuário do container tenha permissões para acessar os arquivos mapeados.  

---

### Rebuilds Automáticos  

Durante o desenvolvimento, é comum alterar dependências ou configurações que exigem a reconstrução da imagem Docker. O comando `docker compose up --build` facilita esse processo, garantindo que as alterações sejam aplicadas.

#### Exemplo de rebuild automático:  
```bash
docker compose up --build
```

#### Fluxo de trabalho típico:  
1. Faça alterações no `Dockerfile` ou em arquivos de configuração.  
2. Execute `docker compose up --build` para reconstruir as imagens.  
3. Verifique se as alterações foram aplicadas corretamente.  

#### Dica: Use o `watch` para rebuilds automáticos  
Em sistemas Unix, você pode usar o comando `watch` para monitorar alterações e executar rebuilds automaticamente:  
```bash
watch -n 5 "docker compose up --build"
```

---

### Configurações Específicas para Desenvolvimento  

Ambientes de desenvolvimento geralmente têm requisitos diferentes de ambientes de produção. Por exemplo, você pode querer habilitar logs detalhados, usar bancos de dados em memória ou configurar variáveis de ambiente específicas. Para isso, é recomendável criar um arquivo `docker-compose.dev.yml`.

#### Exemplo de arquivo `docker-compose.dev.yml`:  
```yaml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./src:/app/src
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
    command: npm run dev
  database:
    image: postgres:latest
    environment:
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: dev_db
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

#### Explicação:  
- **Arquivo separado para desenvolvimento**: O `docker-compose.dev.yml` contém configurações específicas para o ambiente de desenvolvimento, como variáveis de ambiente e volumes.  
- **Dockerfile customizado**: O `Dockerfile.dev` pode incluir ferramentas adicionais, como depuradores ou servidores de desenvolvimento.  
- **Banco de dados configurado para desenvolvimento**: O banco de dados usa credenciais e nomes de banco específicos para o ambiente de desenvolvimento.  

#### Executando o ambiente de desenvolvimento:  
```bash
docker compose -f docker-compose.dev.yml up
```

---

### Comparação: Desenvolvimento vs. Produção  

| Aspecto                | Desenvolvimento                          | Produção                              |
|------------------------|------------------------------------------|---------------------------------------|
| **Volumes**            | Bind mounts para hot-reload             | Volumes nomeados para persistência    |
| **Variáveis de ambiente** | Configurações locais (`.env.dev`)       | Configurações seguras (`.env.prod`)   |
| **Logs**               | Verbose para debugging                  | Compactos para monitoramento          |
| **Build**              | Imagens leves com ferramentas extras    | Imagens otimizadas e mínimas          |

---

### Boas Práticas para Desenvolvimento  

1. **Separe arquivos de configuração**: Use arquivos como `docker-compose.dev.yml` e `docker-compose.prod.yml` para isolar configurações de desenvolvimento e produção.  
2. **Use variáveis de ambiente**: Configure variáveis específicas para cada ambiente em arquivos `.env`.  
3. **Teste individualmente cada serviço**: Certifique-se de que cada serviço funciona corretamente antes de integrá-los.  
4. **Documente o ambiente**: Inclua instruções claras para configurar e executar o ambiente de desenvolvimento.  
5. **Evite hardcoding**: Use variáveis de ambiente para valores configuráveis, como URLs de APIs e credenciais.  

---

### Exemplo Prático Completo  

#### Estrutura do projeto:  
```
project/
├── backend/
│   ├── Dockerfile.dev
│   ├── src/
├── frontend/
│   ├── Dockerfile.dev
│   ├── src/
├── docker-compose.dev.yml
├── .env.dev
```

#### Arquivo `docker-compose.dev.yml`:  
```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend/src:/app/src
    ports:
      - "5000:5000"
    environment:
      NODE_ENV: development
    command: npm run dev
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend/src:/app/src
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
    command: npm start
  database:
    image: postgres:latest
    environment:
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: dev_db
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

#### Arquivo `.env.dev`:  
```env
NODE_ENV=development
DB_USER=dev_user
DB_PASS=dev_password
DB_NAME=dev_db
```

#### Comandos para iniciar o ambiente:  
1. Inicie os serviços:  
   ```bash
   docker compose -f docker-compose.dev.yml up
   ```  
2. Acesse os logs:  
   ```bash
   docker compose logs -f
   ```  
3. Teste os serviços:  
   - Acesse o frontend em `http://localhost:3000`.  
   - Verifique o backend em `http://localhost:5000`.  

---

Com essas práticas e exemplos, você pode configurar um ambiente de desenvolvimento eficiente e alinhado com as necessidades da indústria de software, garantindo maior produtividade e consistência no trabalho em equipe.

## 🔹 Módulo 9 – Docker Compose em Produção  

### Docker Compose em Produção: Visão Geral  
O Docker Compose é amplamente utilizado em ambientes de desenvolvimento, mas também pode ser usado em produção para gerenciar aplicações de pequeno a médio porte. No entanto, para cenários mais complexos, ferramentas como Docker Swarm ou Kubernetes são mais adequadas. Este módulo explora como usar o Docker Compose em produção, destacando boas práticas, exemplos reais e comparações com outras ferramentas de orquestração.

---

### Compose x Swarm x Kubernetes  

| Ferramenta       | Descrição                                                                 | Casos de Uso                                                                 |
|-------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------------|
| **Docker Compose** | Gerencia múltiplos containers em um único host.                          | Pequenas aplicações ou ambientes de desenvolvimento.                        |
| **Docker Swarm**   | Orquestração nativa do Docker para múltiplos hosts.                      | Aplicações distribuídas de médio porte com requisitos moderados de escalabilidade. |
| **Kubernetes**     | Plataforma avançada de orquestração para aplicações em contêineres.      | Grandes aplicações distribuídas com alta disponibilidade e escalabilidade.  |

#### Comparação:  

| Aspecto                  | Docker Compose                     | Docker Swarm                      | Kubernetes                          |
|--------------------------|-------------------------------------|------------------------------------|-------------------------------------|
| **Complexidade**         | Baixa                              | Moderada                          | Alta                                |
| **Escalabilidade**       | Limitada a um único host           | Multi-host                        | Multi-host com suporte avançado     |
| **Curva de aprendizado** | Rápida                             | Moderada                          | Íngreme                             |
| **Comunidade**           | Ampla                              | Moderada                          | Muito ampla                         |
| **Casos de uso**         | Desenvolvimento e produção simples | Produção de médio porte           | Produção de grande escala           |

---

### Ferramentas e Configurações para Produção  

#### Arquivo `docker-compose.prod.yml`  
Para produção, é recomendável criar um arquivo separado com configurações específicas, como imagens otimizadas, variáveis de ambiente seguras e volumes persistentes.

Exemplo:  
```yaml
version: '3.8'
services:
  app:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      NODE_ENV: production
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
    volumes:
      - app_data:/usr/src/app/data
  database:
    image: postgres:14
    environment:
      POSTGRES_USER: prod_user
      POSTGRES_PASSWORD: prod_password
      POSTGRES_DB: prod_db
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  app_data:
  db_data:
```

#### Explicação:  
- **Imagens otimizadas**: Use imagens pré-construídas e otimizadas para produção.  
- **Replicas**: Configuração de múltiplas réplicas para alta disponibilidade.  
- **Restart Policy**: Garante que os serviços sejam reiniciados automaticamente em caso de falhas.  
- **Volumes persistentes**: Evitam perda de dados ao reiniciar containers.  

---

### Exemplo Real: Airbnb  
A Airbnb utilizou Docker Compose em seus primeiros estágios de desenvolvimento para gerenciar múltiplos serviços localmente. À medida que a aplicação cresceu, eles migraram para Kubernetes para atender às demandas de escalabilidade e alta disponibilidade.  

#### Lições aprendidas:  
- **Compose é ideal para prototipagem e desenvolvimento inicial.**  
- **Migração para ferramentas de orquestração avançadas é necessária para grandes aplicações.**  

---

### Boas Práticas para Produção  

1. **Use imagens otimizadas**:  
   - Minimize o tamanho das imagens Docker para reduzir o tempo de inicialização e o consumo de recursos.  
   - Exemplo:  
     ```dockerfile
     FROM node:16-alpine
     WORKDIR /app
     COPY package.json .
     RUN npm install --production
     COPY . .
     CMD ["node", "server.js"]
     ```

2. **Configure variáveis de ambiente seguras**:  
   - Use gerenciadores de segredos como AWS Secrets Manager ou Docker Secrets.  
   - Exemplo com Docker Secrets:  
     ```yaml
     services:
       database:
         image: postgres:14
         secrets:
           - db_password
     secrets:
       db_password:
         file: ./secrets/db_password.txt
     ```

3. **Implemente políticas de reinício**:  
   - Garante que os serviços sejam reiniciados automaticamente em caso de falhas.  
   - Exemplo:  
     ```yaml
     restart_policy:
       condition: on-failure
     ```

4. **Monitore os serviços**:  
   - Use ferramentas como Prometheus, Grafana ou ELK Stack para monitorar logs e métricas.  

5. **Teste antes de implantar**:  
   - Valide o arquivo `docker-compose.prod.yml` com:  
     ```bash
     docker compose config
     ```

---

### Prós e Contras do Docker Compose em Produção  

| Prós                                      | Contras                                   |
|------------------------------------------|------------------------------------------|
| Simplicidade na configuração             | Limitado a um único host                 |
| Fácil de aprender e usar                 | Não possui balanceamento de carga nativo |
| Ideal para aplicações pequenas e médias | Escalabilidade limitada                  |
| Integração com ferramentas de CI/CD     | Menos robusto que Kubernetes             |

---

### Caso de Uso: Startup de E-commerce  

#### Cenário:  
Uma startup de e-commerce precisa gerenciar uma aplicação com backend, frontend e banco de dados. Eles optaram por usar Docker Compose em produção devido à simplicidade e ao custo reduzido.

#### Configuração:  
```yaml
version: '3.8'
services:
  frontend:
    image: ecommerce-frontend:latest
    ports:
      - "80:80"
  backend:
    image: ecommerce-backend:latest
    environment:
      DATABASE_URL: postgres://prod_user:prod_password@database:5432/prod_db
    ports:
      - "8080:8080"
  database:
    image: postgres:14
    environment:
      POSTGRES_USER: prod_user
      POSTGRES_PASSWORD: prod_password
      POSTGRES_DB: prod_db
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

#### Resultados:  
- **Tempo de implantação reduzido**: A startup conseguiu colocar a aplicação em produção rapidamente.  
- **Custo reduzido**: Não foi necessário investir em ferramentas de orquestração mais complexas.  
- **Limitações**: À medida que a aplicação cresceu, eles enfrentaram desafios de escalabilidade e migraram para Kubernetes.  

---

### Conclusão  

O Docker Compose é uma ferramenta poderosa para gerenciar aplicações em produção, especialmente em cenários de pequeno a médio porte. No entanto, é importante avaliar as necessidades de escalabilidade e alta disponibilidade antes de decidir usá-lo em produção. Para aplicações maiores, considere migrar para ferramentas como Docker Swarm ou Kubernetes.
  
  ### Exemplo de aplicação completa com boas práticas para diferentes linguagens  

  #### Exemplo para Java (Spring Boot)  
  ```yaml
  version: '3.8'
  services:
    app:
      image: openjdk:17-jdk-slim
      build:
        context: ./backend
        dockerfile: Dockerfile
      ports:
        - "8080:8080"
      environment:
        SPRING_PROFILES_ACTIVE: dev
      volumes:
        - ./backend:/app
      command: ["java", "-jar", "/app/target/app.jar"]
    database:
      image: postgres:latest
      environment:
        POSTGRES_USER: dev_user
        POSTGRES_PASSWORD: dev_password
        POSTGRES_DB: dev_db
      ports:
        - "5432:5432"
      volumes:
        - db_data:/var/lib/postgresql/data
  volumes:
    db_data:
  ```

  #### Exemplo para Python (Django)  
  ```yaml
  version: '3.8'
  services:
    web:
      build:
        context: ./backend
        dockerfile: Dockerfile
      command: python manage.py runserver 0.0.0.0:8000
      volumes:
        - ./backend:/app
      ports:
        - "8000:8000"
      environment:
        DJANGO_SETTINGS_MODULE: myproject.settings.dev
    database:
      image: postgres:latest
      environment:
        POSTGRES_USER: dev_user
        POSTGRES_PASSWORD: dev_password
        POSTGRES_DB: dev_db
      ports:
        - "5432:5432"
      volumes:
        - db_data:/var/lib/postgresql/data
  volumes:
    db_data:
  ```

  #### Exemplo para JavaScript (Node.js + Express)  
  ```yaml
  version: '3.8'
  services:
    app:
      build:
        context: ./backend
        dockerfile: Dockerfile
      command: npm run dev
      volumes:
        - ./backend:/app
        - /app/node_modules
      ports:
        - "3000:3000"
      environment:
        NODE_ENV: development
    database:
      image: mongo:latest
      ports:
        - "27017:27017"
      volumes:
        - mongo_data:/data/db
  volumes:
    mongo_data:
  ```

  Esses exemplos seguem boas práticas como:  
  - Uso de volumes para hot-reload durante o desenvolvimento.  
  - Configuração de variáveis de ambiente para separar ambientes de desenvolvimento e produção.  
  - Persistência de dados com volumes nomeados para bancos de dados.  
  - Uso de imagens leves e otimizadas para cada linguagem.  
  - Separação clara entre código-fonte e dependências no container.  
  - Configuração de portas para facilitar o acesso local durante o desenvolvimento.  
  - Uso de comandos específicos para iniciar os serviços no modo de desenvolvimento.  
