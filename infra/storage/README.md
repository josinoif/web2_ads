# Mini-curso: Armazenamento de Arquivos em Aplicações Web

Mini-curso sobre onde e como persistir arquivos em aplicações web: fundamentação teórica e tutoriais práticos. Você vai avaliar **armazenamento em disco (filesystem)**, **MinIO** (S3-compatível) e **AWS S3** (ou LocalStack para estudo local), e aprender a implementar upload e download em cada abordagem.

## Pré-requisitos

- Conhecimentos básicos de **HTTP** e **API REST**
- **Node.js** e **npm** instalados
- **Docker** instalado (para os módulos 03 e 04 — MinIO e LocalStack)
- Editor de código (recomendado: VS Code ou Cursor)

## Como usar os materiais

- Cada módulo tem arquivos de **conceitos** (teoria) e **tutoriais** (passo a passo).
- Estude a teoria antes de fazer o tutorial correspondente.
- Nos tutoriais, siga os passos na ordem e leia a seção "Explicação dos principais elementos".
- Para o frontend que envia arquivos, você pode usar o material do curso [React — Arquivos](../frontend/reactjs/10-arquivos/).

## Estrutura do curso

| Módulo | Conteúdo |
|--------|----------|
| [01 - Fundamentação](01-fundamentacao/) | Conceitos de armazenamento; quando usar cada abordagem |
| [02 - Armazenamento local](02-armazenamento-local/) | Filesystem: salvar no disco do servidor |
| [03 - MinIO](03-minio/) | Object storage S3-compatível com Docker |
| [04 - S3 e nuvem](04-s3-cloud/) | AWS S3 e LocalStack para estudo local |
| [05 - Comparação e prática](05-comparacao-pratica/) | Tabela comparativa, decisão e boas práticas |
| [Recursos](recursos/) | Glossário e referências |

## Objetivos de aprendizagem

- Entender a diferença entre filesystem e object storage
- Saber quando usar disco local, MinIO ou S3
- Implementar upload e download com Express (disco, MinIO, S3/LocalStack)
- Aplicar boas práticas de segurança e validação
