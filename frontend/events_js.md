# Introdução a Eventos JavaScript

Eventos são ações ou ocorrências que acontecem no navegador que podem ser capturadas e tratadas pelo JavaScript. Exemplos de eventos incluem cliques do mouse, pressionamentos de teclas, carregamento de uma página, entre outros.

## Tipos Comuns de Eventos

Aqui está uma lista mais abrangente de eventos JavaScript:

1. `click`: Disparado quando um elemento é clicado.
2. `dblclick`: Disparado quando um elemento é clicado duas vezes.
3. `mouseover`: Disparado quando o ponteiro do mouse passa sobre um elemento.
4. `mouseout`: Disparado quando o ponteiro do mouse sai de um elemento.
5. `mousemove`: Disparado quando o ponteiro do mouse se move sobre um elemento.
6. `mousedown`: Disparado quando um botão do mouse é pressionado sobre um elemento.
7. `mouseup`: Disparado quando um botão do mouse é liberado sobre um elemento.
8. `keydown`: Disparado quando uma tecla é pressionada.
9. `keyup`: Disparado quando uma tecla é liberada.
10. `keypress`: Disparado quando uma tecla é pressionada e liberada.
11. `load`: Disparado quando uma página ou recurso é carregado.
12. `unload`: Disparado quando uma página está prestes a ser descarregada.
13. `resize`: Disparado quando a janela do navegador é redimensionada.
14. `scroll`: Disparado quando a barra de rolagem de um elemento é movida.
15. `focus`: Disparado quando um elemento recebe foco.
16. `blur`: Disparado quando um elemento perde foco.
17. `change`: Disparado quando o valor de um elemento `<input>`, `<select>` ou `<textarea>` é alterado.
18. `submit`: Disparado quando um formulário é enviado.
19. `reset`: Disparado quando um formulário é redefinido.
20. `contextmenu`: Disparado quando o menu de contexto é solicitado (geralmente com o botão direito do mouse).
21. `input`: Disparado quando o valor de um elemento `<input>` ou `<textarea>` é alterado.
22. `select`: Disparado quando o texto dentro de um elemento `<input>` ou `<textarea>` é selecionado.
23. `drag`: Disparado continuamente enquanto um elemento está sendo arrastado.
24. `dragstart`: Disparado no início de uma operação de arrastar.
25. `dragend`: Disparado no final de uma operação de arrastar.
26. `dragover`: Disparado quando um elemento arrastado é movido sobre um destino de soltar.
27. `drop`: Disparado quando um elemento arrastado é solto em um destino de soltar.
28. `copy`: Disparado quando o conteúdo é copiado.
29. `cut`: Disparado quando o conteúdo é cortado.
30. `paste`: Disparado quando o conteúdo é colado.

## Adicionando Eventos

Para adicionar eventos a elementos HTML, você pode usar o método `addEventListener`. Aqui está um exemplo de como adicionar um evento de clique a um botão:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Eventos</title>
</head>
<body>
    <button id="meuBotao">Clique em mim!</button>

    <script>
        const botao = document.getElementById('meuBotao');
        botao.addEventListener('click', function() {
            alert('Botão clicado!');
        });
    </script>
</body>
</html>
```

Neste exemplo, quando o botão com o id `meuBotao` é clicado, uma mensagem de alerta é exibida.

Removendo Eventos
Você também pode remover eventos usando o método `removeEventListener`. Para isso, a função de evento deve ser nomeada:

```html 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de Remoção de Eventos</title>
</head>
<body>
    <button id="meuBotao">Clique em mim!</button>
    <button id="removerEvento">Remover Evento</button>

    <script>
        const botao = document.getElementById('meuBotao');
        const removerBotao = document.getElementById('removerEvento');

        function mostrarAlerta() {
            alert('Botão clicado!');
        }

        botao.addEventListener('click', mostrarAlerta);

        removerBotao.addEventListener('click', function() {
            botao.removeEventListener('click', mostrarAlerta);
            alert('Evento removido!');
        });
    </script>
</body>
</html>

```

Neste exemplo, o evento de clique é removido do botão meuBotao quando o botão `removerEvento` é clicado.

## Conclusão

Eventos são uma parte fundamental do desenvolvimento web interativo. Compreender como adicionar e remover eventos permite que você crie experiências de usuário dinâmicas e responsivas. 


## Exercícios

### Nível Fácil

1. **Clique no Botão**
   - Crie um botão que exiba um alerta com a mensagem "Botão clicado!" quando for clicado.

2. **Mudança de Cor**
   - Crie um parágrafo que mude sua cor de fundo para amarelo quando o mouse passar sobre ele (`mouseover`) e volte à cor original quando o mouse sair (`mouseout`).

3. **Contador de Cliques**
   - Crie um botão que, ao ser clicado, incremente um contador exibido em um parágrafo.

4. **Exibir Texto**
   - Crie um campo de texto (`input`) e um botão. Quando o botão for clicado, exiba o texto digitado no campo de texto em um parágrafo.

### Nível Intermediário

5. **Formulário de Envio**
   - Crie um formulário com um campo de texto e um botão de envio. Quando o formulário for enviado, exiba uma mensagem de confirmação e previna o comportamento padrão de envio do formulário.

6. **Tecla Pressionada**
   - Crie um campo de texto que exiba uma mensagem em um parágrafo indicando qual tecla foi pressionada (`keydown`).

7. **Arrastar e Soltar**
   - Crie dois elementos div. Permita que um dos elementos seja arrastado e solto dentro do outro.

### Nível Difícil

8. **Jogo de Memória**
   - Crie um simples jogo de memória com cartas que podem ser viradas ao clicar. As cartas devem ser embaralhadas e o jogo deve detectar quando todas as cartas foram combinadas.

9. **Desenho com o Mouse**
   - Crie uma área de desenho onde o usuário pode desenhar com o mouse. Use eventos de `mousedown`, `mousemove` e `mouseup` para detectar e desenhar linhas.

10. **Validação de Formulário**
    - Crie um formulário com vários campos (nome, email, senha). Adicione validação em tempo real para garantir que os campos sejam preenchidos corretamente antes de permitir o envio do formulário. Exiba mensagens de erro apropriadas para cada campo.

Esses exercícios ajudarão a praticar a manipulação de eventos em JavaScript e a criar interações dinâmicas em páginas web.