# Upload de Imagens (FastAPI)

## Objetivos
- Permitir upload de imagem de perfil do restaurante
- Validar tipo/tamanho e salvar arquivo com nome seguro
- Atualizar `image_url` e servir URL pública

## Passo a passo
1. Endpoint `POST /items/{id}/image` recebendo `UploadFile`
2. Validar `content_type` (jpeg/png/webp) e tamanho (ler chunks, limitar ex.: 2MB)
3. Gerar nome seguro (slug + hash) e salvar em `UPLOAD_DIR`
4. Atualizar registro do item com `image_url`; remover arquivo antigo ao substituir
5. Montar `StaticFiles` em `/uploads` para servir imagens
6. Endpoint `DELETE /items/{id}/image` para remoção
7. Testes com `TestClient`: upload válido, tipo inválido, troca de imagem

## Checklist
- Variáveis `UPLOAD_DIR` e `BASE_URL` configuradas
- Limpeza em caso de erro no fluxo de upload
- Retorno inclui `imageUrl`
