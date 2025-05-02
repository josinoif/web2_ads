# Introdução ao Docker  

O Docker é uma plataforma de código aberto que revolucionou a maneira como desenvolvedores e equipes de operações criam, distribuem e executam aplicações. Ele foi criado em 2013 pela empresa Docker Inc., com o objetivo de resolver problemas comuns enfrentados no desenvolvimento de software, como inconsistências entre ambientes de desenvolvimento, teste e produção.  

## Motivação para a Criação  

Antes do Docker, era comum que aplicações funcionassem em um ambiente, mas falhassem em outro devido a diferenças de configuração. A necessidade de uma solução que garantisse portabilidade, consistência e isolamento levou ao desenvolvimento do Docker. Ele utiliza a tecnologia de containers, que permite empacotar uma aplicação e todas as suas dependências em um único ambiente isolado.  

## Principais Recursos  

- **Portabilidade**: Containers podem ser executados em qualquer ambiente que suporte Docker, seja no seu laptop, em servidores locais ou na nuvem.  
- **Isolamento**: Cada container é isolado, garantindo que uma aplicação não interfira em outra.  
- **Eficiência**: Containers compartilham o kernel do sistema operacional, tornando-os mais leves e rápidos que máquinas virtuais.  
- **Escalabilidade**: Facilita a criação de arquiteturas baseadas em microsserviços, permitindo escalar partes específicas de uma aplicação.  

## Usos do Docker  

O Docker é amplamente utilizado em diversas etapas do ciclo de vida do software:  

- **Desenvolvimento**: Criação de ambientes consistentes para desenvolvedores.  
- **Testes**: Execução de testes em ambientes idênticos ao de produção.  
- **Implantação**: Automação e simplificação do processo de deploy.  
- **CI/CD**: Integração contínua e entrega contínua com pipelines otimizados.  

## Casos de Uso em Empresas  

- **Spotify**: Utiliza Docker para gerenciar microsserviços, permitindo escalar rapidamente suas aplicações.  
- **PayPal**: Adotou Docker para acelerar o tempo de deploy e melhorar a eficiência operacional.  
- **Netflix**: Usa containers para criar ambientes de teste consistentes e para gerenciar sua infraestrutura de streaming.  
- **Airbnb**: Implementou Docker para simplificar o gerenciamento de ambientes e melhorar a colaboração entre equipes.  

O Docker continua sendo uma ferramenta essencial para empresas que buscam agilidade, eficiência e confiabilidade em seus processos de desenvolvimento e operações.  


## Funcionamento do Docker  

O Docker funciona utilizando a tecnologia de containers, que são ambientes isolados que compartilham o kernel do sistema operacional do host. Isso permite que aplicações sejam executadas de forma consistente, independentemente do ambiente subjacente. A seguir, detalhamos como o Docker gerencia processamento, memória, armazenamento e rede.

### Processamento e Limitação de Recursos  

O Docker permite limitar o uso de CPU e memória para cada container, garantindo que eles não consumam mais recursos do que o necessário. Isso é feito utilizando as funcionalidades de cgroups (control groups) do kernel Linux.  

- **Limitação de CPU**:  
  É possível definir a quantidade de CPU que um container pode usar. Por exemplo, para limitar um container a usar apenas metade de um núcleo de CPU, você pode usar a flag `--cpus`:  
  ```bash
  docker run --cpus="0.5" my-container
  ```  

- **Limitação de Memória**:  
  O Docker também permite limitar a quantidade de memória disponível para um container. Por exemplo, para limitar um container a 512 MB de memória:  
  ```bash
  docker run --memory="512m" my-container
  ```  

Essas configurações são úteis para evitar que um único container monopolize os recursos do sistema, especialmente em ambientes de produção.

### Gerenciamento de Memória  

O Docker utiliza a memória de forma eficiente, compartilhando bibliotecas e outros recursos entre containers sempre que possível. Além disso, ele permite configurar limites de memória swap para containers, garantindo que eles não utilizem mais memória do que o permitido.  

- **Exemplo de Limitação de Swap**:  
  ```bash
  docker run --memory="512m" --memory-swap="1g" my-container
  ```  
  Nesse exemplo, o container pode usar até 512 MB de memória física e 512 MB adicionais de swap.

### Gerenciamento de Armazenamento  

O Docker oferece várias opções para gerenciar o armazenamento de dados, dependendo das necessidades da aplicação.  

- **Volumes**:  
  Volumes são a forma recomendada de persistir dados em Docker. Eles são gerenciados pelo Docker e podem ser compartilhados entre containers.  
  ```bash
  docker volume create my-volume
  docker run -v my-volume:/data my-container
  ```  

- **Bind Mounts**:  
  Permitem mapear um diretório do host para dentro do container. Isso é útil para desenvolvimento, mas menos seguro em produção.  
  ```bash
  docker run -v /path/on/host:/path/in/container my-container
  ```  

- **Storage Drivers**:  
  O Docker utiliza drivers de armazenamento para gerenciar como os dados são armazenados no sistema de arquivos do host. Exemplos incluem `overlay2`, `aufs` e `btrfs`.  

### Gerenciamento de Rede  

O Docker oferece várias opções para configurar redes, permitindo que containers se comuniquem entre si e com o mundo externo.  

- **Bridge Network**:  
  É a configuração padrão. Containers conectados a uma rede bridge podem se comunicar entre si usando seus nomes.  
  ```bash
  docker network create my-bridge-network
  docker run --network=my-bridge-network my-container
  ```  

- **Host Network**:  
  O container compartilha a pilha de rede do host, eliminando o isolamento de rede.  
  ```bash
  docker run --network="host" my-container
  ```  

- **Overlay Network**:  
  Usada em clusters Docker Swarm para conectar containers em diferentes hosts.  
  ```bash
  docker network create --driver overlay my-overlay-network
  ```  

- **Port Mapping**:  
  Permite expor portas do container para o host. Por exemplo, para expor a porta 80 do container na porta 8080 do host:  
  ```bash
  docker run -p 8080:80 my-container
  ```  

### Exemplo Prático  

Imagine que você está criando uma aplicação web com um banco de dados. Você pode configurar os containers da seguinte forma:  

1. Criar uma rede bridge para comunicação entre os containers:  
   ```bash
   docker network create app-network
   ```  

2. Executar o banco de dados com um volume para persistência de dados:  
   ```bash
   docker run --name db --network app-network -v db-data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root mysql
   ```  

3. Executar a aplicação web conectada à mesma rede:  
   ```bash
   docker run --name web --network app-network -p 8080:80 my-web-app
   ```  

Com essa configuração, a aplicação web pode se comunicar com o banco de dados usando o nome do container `db`, e a aplicação estará acessível na porta 8080 do host.

O Docker oferece flexibilidade e controle sobre os recursos, tornando-o uma ferramenta poderosa para desenvolvimento e produção.  