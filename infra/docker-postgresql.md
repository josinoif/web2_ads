# Banco de dados PostgreSQL no Docker



Aqui está um exemplo de arquivo `docker-compose.yml` para levantar um banco de dados PostgreSQL e um cliente web, como o pgAdmin:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: postgres-db
    restart: always
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: adminpassword
    ports:
      - "8080:80"

volumes:
  postgres_data:
```

### Como usar

1. Salve o conteúdo acima como `docker-compose.yml`.

2. Certifique-se de ter o Docker e Docker Compose instalados.

3. Execute o comando:

   ```bash
   docker-compose up -d
   ```

### Acessar os serviços

- PostgreSQL: Disponível na porta `5432`.
  - Usuário: `myuser`
  - Senha: `mypassword`
  - Banco de Dados: `mydatabase`
- pgAdmin: Acesse `http://localhost:8080` no navegador.
  - Login: `admin@example.com`
  - Senha: `adminpassword`

### Configuração no pgAdmin

1. Após acessar o pgAdmin, clique em "Add New Server".
2. Preencha os campos:
   - **General -> Name**: Escolha um nome para identificar o servidor, como `PostgresLocal`.
   - **Connection -> Hostname/Address**: `postgres`
   - **Connection -> Username**: `myuser`
   - **Connection -> Password**: `mypassword`
3. Salve e conecte-se ao servidor.