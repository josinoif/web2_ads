# Upload de Imagem de Perfil (Next.js App Router)

## Objetivos
- Permitir que o usuário envie e visualize a imagem do restaurante
- Validar tipo/tamanho no client e exibir preview
- Integrar com endpoint de upload e atualizar UI

## Passo a passo
1. Criar componente de upload (client component) com `<input type="file">` + preview
2. Validar MIME/tamanho (ex.: 2MB) antes de enviar; mostrar erros no toast
3. Enviar multipart com Axios para `POST /items/:id/image` e usar `onUploadProgress`
4. Atualizar cache (SWR/React Query) do item após sucesso; exibir imagem ou placeholder
5. Permitir remover/substituir imagem chamando `DELETE /items/:id/image`
6. Estados de loading/disabled e mensagens de sucesso/erro

## Checklist
- `NEXT_PUBLIC_API_URL` configurada
- Fallback de imagem padrão
- Acessibilidade: rótulos, foco, mensagens descritivas
