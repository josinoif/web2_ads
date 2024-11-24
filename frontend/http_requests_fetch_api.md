# Requisições HTTP com JavaScript usando Fetch API

A Fetch API é uma interface moderna que permite fazer requisições HTTP de forma simples e intuitiva. Ela é baseada em Promises, o que facilita o tratamento de operações assíncronas.

## Fazendo uma Requisição GET

Uma requisição GET é usada para buscar dados de um servidor.

### Exemplo:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Fetch API - GET</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição GET</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://jsonplaceholder.typicode.com/posts/1')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
                })
                .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Fazendo uma Requisição POST
Uma requisição POST é usada para enviar dados para um servidor.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Fetch API - POST</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição POST</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://jsonplaceholder.typicode.com/posts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: 'foo',
                    body: 'bar',
                    userId: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
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
    <title>Exemplo de Fetch API - PUT</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição PUT</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://jsonplaceholder.typicode.com/posts/1', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: 1,
                    title: 'foo',
                    body: 'bar',
                    userId: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
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
    <title>Exemplo de Fetch API - DELETE</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição DELETE</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://jsonplaceholder.typicode.com/posts/1', {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    document.getElementById('resultado').innerText = 'Recurso deletado com sucesso!';
                } else {
                    document.getElementById('resultado').innerText = 'Erro ao deletar o recurso.';
                }
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
    <title>Exemplo de Fetch API - Tratamento de Erros</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://jsonplaceholder.typicode.com/invalid-endpoint')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro na requisição: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
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

## Manipulação de Headers com Fetch API

Os headers HTTP são usados para passar informações adicionais com uma requisição ou resposta HTTP. Com a Fetch API, você pode configurar e manipular headers para suas requisições de forma simples.

### Configurando Headers para uma Requisição Específica

Você pode configurar headers para uma requisição específica passando um objeto de configuração como segundo argumento para o método `fetch`.

### Exemplo:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Fetch API - Headers Específicos</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição com Headers Específicos</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource', {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
                    'Custom-Header': 'CustomValue'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
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
    <title>Exemplo de Fetch API - Headers em POST</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição POST com Headers</button>
    <pre id="resultado"></pre>

    <script>
        function fazerRequisicao() {
            fetch('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
                },
                body: JSON.stringify({
                    title: 'foo',
                    body: 'bar',
                    userId: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
            })
            .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

### Configurando Headers Globais
Diferente do Axios, a Fetch API não possui uma maneira direta de configurar headers globais. No entanto, você pode criar uma função personalizada para fazer isso.

### Exemplo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Fetch API - Headers Globais</title>
</head>
<body>
    <button onclick="fazerRequisicao()">Fazer Requisição com Headers Globais</button>
    <pre id="resultado"></pre>

    <script>
        function fetchWithHeaders(url, options = {}) {
            const headers = {
                'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
                'Custom-Header': 'CustomValue',
                ...options.headers
            };

            return fetch(url, {
                ...options,
                headers
            });
        }

        function fazerRequisicao() {
            fetchWithHeaders('https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/resource')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
                })
                .catch(error => console.error('Erro:', error));
        }
    </script>
</body>
</html>
```

## Conclusão
A Fetch API é uma ferramenta poderosa e flexível para fazer requisições HTTP em JavaScript. Com ela, você pode buscar, enviar, atualizar e deletar dados de servidores de forma assíncrona, proporcionando uma experiência de usuário mais dinâmica e responsiva. 