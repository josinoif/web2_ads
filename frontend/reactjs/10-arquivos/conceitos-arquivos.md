# Envio e manipulação de arquivos no frontend

## Introdução

Muitas aplicações precisam que o usuário **envie arquivos** (upload) ou **baixe arquivos** (download). No frontend React, isso envolve o uso do **input type="file"**, da **File API** do navegador e do **FormData** para enviar arquivos via HTTP. Para download, o frontend pode abrir um link que aponta para a API ou usar a resposta blob de uma requisição para gerar um link temporário.

---

## Conceitos principais

- **Input file**: `<input type="file" />` permite que o usuário selecione um ou mais arquivos. O evento `onChange` fornece o arquivo (ou lista) em `e.target.files` (objeto **FileList**; cada item é um **File**).
- **File API**: o objeto **File** (herda de **Blob**) tem propriedades como `name`, `size`, `type`. Pode ser lido com **FileReader** (ex.: `readAsDataURL` para preview de imagem).
- **FormData**: objeto para montar o corpo de uma requisição multipart/form-data. Você adiciona campos com `formData.append('campo', valor)`. Para arquivo: `formData.append('arquivo', file)`. Axios e fetch aceitam FormData no body.
- **Upload**: geralmente POST (ou PUT) para uma URL da API com o body sendo um FormData contendo o arquivo. O backend responde com a URL ou o ID do arquivo salvo.
- **Download**: o usuário pode baixar clicando em um link `<a href={url} download>` (quando a URL é do mesmo origin ou tem CORS e o servidor retorna o header apropriado) ou o frontend faz uma requisição, recebe um blob e cria um Object URL com `URL.createObjectURL(blob)` e dispara o download via link ou programaticamente.

---

## Boas práticas

- Validar tipo e tamanho do arquivo no frontend (e sempre no backend) para evitar envio de arquivos inválidos ou muito grandes.
- Exibir progresso de upload quando possível (axios com `onUploadProgress`, ou fetch com ReadableStream).
- Para preview de imagens, use `FileReader.readAsDataURL(file)` e defina o resultado em um estado que será usado no `src` de uma `<img>`.
- **No React 19**, prefira `<form action={minhaAction}>` + `useActionState` para uploads: o `FormData` (incluindo o `File`) chega pronto na action, e `useFormStatus` dá `pending` no botão sem código extra.

## Diagrama do fluxo de upload

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Input as &lt;input type=file&gt;
    participant Form as &lt;form action={...}&gt;
    participant Act as Action (FormData)
    participant API as API

    User->>Input: seleciona arquivo
    Input-->>Form: File no FormData
    User->>Form: clica "Enviar"
    Form->>Act: chama action(prev, formData)
    Act->>API: POST multipart/form-data
    API-->>Act: ok / erro
    Act-->>Form: novo state
    Form-->>User: feedback (sucesso/erro)
```

---

## Conclusão

Envio e manipulação de arquivos no React usam o input file, a File API e o FormData para upload, e links ou blobs para download. No [tutorial-arquivos.md](tutorial-arquivos.md) você implementará um formulário de upload e uma listagem com opção de download.
