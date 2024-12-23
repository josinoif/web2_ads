# Docker mysql



Aqui está um exemplo de um arquivo `docker-compose.yml` que levanta um banco de dados MySQL e um cliente web para gerenciar o banco, como o Adminer:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydatabase
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  adminer:
    image: adminer:latest
    container_name: adminer
    restart: always
    ports:
      - "8080:8080"

volumes:
  mysql_data:
```

### Como usar

1. Salve o arquivo acima como `docker-compose.yml` no seu ambiente.

2. Certifique-se de ter o Docker e Docker Compose instalados.

3. Execute o comando:

   ```bash
   docker-compose up -d
   ```

### Acessar os serviços

- MySQL: Está disponível na porta `3306`. Você pode conectar-se com as credenciais:
  - Usuário: `root`
  - Senha: `rootpassword`
  - Banco de Dados: `mydatabase`
- **Adminer**: Acesse `http://localhost:8080` em seu navegador para gerenciar o banco de dados via interface web.
