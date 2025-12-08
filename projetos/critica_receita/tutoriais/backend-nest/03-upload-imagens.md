# Upload de Imagens (NestJS)

## Objetivos
- Permitir upload de imagem de perfil do restaurante
- Validar MIME/tamanho e armazenar com nome seguro
- Expor URL pública e substituir/remover imagem anterior

## Passo a passo
1. Configurar `MulterModule` e `FileInterceptor('file')` com storage em disco (hash + extensão)
2. Limitar tipos (jpeg/png/webp) e tamanho (ex.: 2MB) via `limits` e checagem de MIME real
3. Rota `POST /items/:id/image` protegida; atualizar service para salvar `imageUrl` e remover antiga
4. Rota `DELETE /items/:id/image` para remoção
5. Servir estáticos com `ServeStaticModule` apontando para `UPLOAD_DIR`
6. Testes e2e: upload válido, tipo inválido, tamanho excedido, troca de imagem

## Checklist
- Variáveis `UPLOAD_DIR` e `BASE_URL` definidas
- Fallback para ausência de imagem
- Limpeza de arquivo em caso de erro no fluxo
