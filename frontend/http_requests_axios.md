# Requisições HTTP com JavaScript usando Axios

Axios é uma biblioteca baseada em Promises que facilita a realização de requisições HTTP. Ela oferece uma interface mais simples e recursos adicionais em comparação com a Fetch API.

## Comparação entre Axios e Fetch API

### Vantagens do Axios sobre Fetch API

1. **Suporte a Navegadores Antigos**:
   - Axios funciona em navegadores mais antigos sem a necessidade de polyfills.

2. **Intercepção de Requisições e Respostas**:
   - Axios permite interceptar requisições e respostas, facilitando a manipulação de dados antes de serem enviados ou recebidos.

3. **Cancelamento de Requisições**:
   - Axios suporta o cancelamento de requisições, o que pode ser útil em certas situações, como quando o usuário navega para outra página antes da conclusão da requisição.

4. **Transformação de Dados**:
   - Axios permite transformar dados de requisições e respostas de forma mais simples.

5. **Tratamento de Erros**:
   - Axios simplifica o tratamento de erros, retornando diretamente o status HTTP e a mensagem de erro.

### Desvantagens do Axios em relação à Fetch API

1. **Tamanho da Biblioteca**:
   - Axios é uma biblioteca externa, o que aumenta o tamanho do seu projeto, enquanto Fetch API é nativa do navegador.

2. **Dependência Externa**:
   - Usar Axios adiciona uma dependência externa ao seu projeto, enquanto Fetch API não requer dependências adicionais.

## Fazendo uma Requisição GET

Uma requisição GET é usada para buscar dados de um servidor.

### Exemplo:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - GET</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição GET</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.get('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource')
                .then(response => {
                    document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
                })
                .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Fazendo uma Requisição POST
Uma requisição POST é usada para enviar dados para um servidor.

## Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - POST</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição POST</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.post('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource', {
                title: 'foo',
                body: 'bar',
                userId: 1
            })
            .then(response => {
                document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
            })
            .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Fazendo uma Requisição PUT
Uma requisição PUT é usada para atualizar dados em um servidor.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - PUT</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição PUT</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.put('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource/RESOURCE_ID', {
                title: 'foo',
                body: 'bar',
                userId: 1
            })
            .then(response => {
                document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
            })
            .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Fazendo uma Requisição DELETE
Uma requisição DELETE é usada para remover dados de um servidor.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - DELETE</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição DELETE</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.delete('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource/RESOURCE_ID')
                .then(response => {
                    document.getElementById('resultado').innerText = 'Recurso deletado com sucesso!';
                })
                .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Tratamento de Erros
É importante tratar erros ao fazer requisições HTTP para lidar com falhas de rede ou respostas inesperadas do servidor.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - Tratamento de Erros</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.get('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/invalid-endpoint')
                .then(response => {
                    document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
                })
                .catch(error => {
                    document.getElementById('resultado').innerText = 'Erro: ' + error.message;
                    console.error('Erro:', error);
                });
        }
    </script>
</body>
</html>
```

## Manipulação de Headers com Axios

Os headers HTTP são usados para passar informações adicionais com uma requisição ou resposta HTTP. Com Axios, você pode facilmente configurar e manipular headers para suas requisições.

### Configurando Headers Globais

Você pode configurar headers globais que serão aplicados a todas as requisições feitas com Axios.

### Exemplo:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - Headers Globais</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição com Headers Globais</button>
    <pre id="resultado"></pre>

    <script>
        // Configurando headers globais
        axios.defaults.headers.common['Authorization'] = 'Bearer YOUR_ACCESS_TOKEN';
        axios.defaults.headers.post['Content-Type'] = 'application/json';

        function fazerRequisicao() {
            axios.get('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource')
                .then(response => {
                    document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
                })
                .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

### Configurando Headers para uma Requisição Específica
Você também pode configurar headers para uma requisição específica, passando um objeto de configuração como segundo argumento para os métodos de requisição.

### Exemplo:

```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - Headers Específicos</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição com Headers Específicos</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.get('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource', {
                headers: {
                    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
                    'Custom-Header': 'CustomValue'
                }
            })
            .then(response => {
                document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
            })
            .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>

```

### Manipulando Headers em Requisições POST
Ao fazer requisições POST, você pode definir headers como Content-Type para especificar o tipo de dados que está sendo enviado.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Axios - Headers em POST</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição POST com Headers</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            axios.post('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource', {
                title: 'foo',
                body: 'bar',
                userId: 1
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
                }
            })
            .then(response => {
                document.getElementById('resultado').innerText = JSON.stringify(response.data, null, 2);
            })
            .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Conclusão

Axios é uma biblioteca poderosa e flexível para fazer requisições HTTP em JavaScript. Com ela, você pode buscar, enviar, atualizar e deletar dados de servidores de forma assíncrona, proporcionando uma experiência de usuário mais dinâmica e responsiva.


Nota: Substitua YOUR_UNIQUE_ENDPOINT pelo seu ID único fornecido pelo crudcrud.com, e RESOURCE_ID pelo nome do recurso que você deseja manipular.