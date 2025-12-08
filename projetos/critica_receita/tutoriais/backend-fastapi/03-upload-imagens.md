# Tutorial: Upload de Imagens com FastAPI

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar upload de arquivos com FastAPI
- Validar tipos e tamanhos de arquivo
- Salvar imagens no sistema de arquivos
- Servir arquivos estáticos
- Atualizar registros com URLs de imagem

## 📖 Conteúdo

### 1. Instalação de Dependências

```bash
pip install python-multipart pillow
```

**Atualizar `requirements.txt`:**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic-settings==2.1.0
alembic==1.13.1
python-multipart==0.0.6
pillow==10.2.0
```

### 2. Configurar Diretórios de Upload

**Atualizar `app/config.py`:**

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 2 * 1024 * 1024  # 2MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

settings = Settings()

# Criar diretório de uploads se não existir
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

### 3. Service de Upload

**Arquivo `app/services/upload.py`:**

```python
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
from PIL import Image
import uuid
import os
from app.config import settings

class UploadService:
    @staticmethod
    def validate_file(file: UploadFile):
        """Validar tipo e tamanho do arquivo"""
        # Validar extensão
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não permitido. Use: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )

        # Validar tipo MIME
        allowed_mimes = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de arquivo inválido. Apenas imagens são permitidas.",
            )

    @staticmethod
    async def save_upload_file(file: UploadFile) -> str:
        """Salvar arquivo e retornar URL"""
        try:
            # Validar arquivo
            UploadService.validate_file(file)

            # Gerar nome único
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = settings.UPLOAD_DIR / unique_filename

            # Ler conteúdo
            content = await file.read()

            # Validar tamanho
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE / (1024 * 1024)}MB",
                )

            # Validar se é imagem válida
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Arquivo não é uma imagem válida",
                )

            # Salvar arquivo
            with open(file_path, "wb") as f:
                f.write(content)

            # Retornar URL relativa
            return f"/uploads/{unique_filename}"

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar arquivo: {str(e)}",
            )

    @staticmethod
    def delete_file(file_url: str):
        """Deletar arquivo do sistema"""
        if not file_url:
            return

        # Extrair nome do arquivo da URL
        filename = Path(file_url).name
        file_path = settings.UPLOAD_DIR / filename

        # Deletar se existir
        if file_path.exists():
            os.remove(file_path)
```

### 4. Router de Upload

**Arquivo `app/routers/upload.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.upload import UploadService
from app.services.restaurante import RestauranteService

router = APIRouter()

@router.post("/restaurantes/{id}/imagem")
async def upload_imagem_restaurante(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload de imagem para restaurante"""
    # Verificar se restaurante existe
    restaurante = RestauranteService.get_by_id(db, id)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {id} não encontrado",
        )

    # Deletar imagem antiga se existir
    if restaurante.image_url:
        UploadService.delete_file(restaurante.image_url)

    # Salvar nova imagem
    image_url = await UploadService.save_upload_file(file)

    # Atualizar URL no banco
    restaurante.image_url = image_url
    db.commit()
    db.refresh(restaurante)

    return {
        "message": "Imagem enviada com sucesso",
        "image_url": image_url,
    }

@router.delete("/restaurantes/{id}/imagem", status_code=status.HTTP_204_NO_CONTENT)
async def delete_imagem_restaurante(
    id: int,
    db: Session = Depends(get_db),
):
    """Remover imagem do restaurante"""
    # Verificar se restaurante existe
    restaurante = RestauranteService.get_by_id(db, id)
    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante com ID {id} não encontrado",
        )

    if not restaurante.image_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não possui imagem",
        )

    # Deletar arquivo
    UploadService.delete_file(restaurante.image_url)

    # Remover URL do banco
    restaurante.image_url = None
    db.commit()
```

### 5. Servir Arquivos Estáticos

**Atualizar `app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import restaurante, avaliacao, upload

app = FastAPI(
    title="Crítica Receita API",
    version="1.0.0",
    description="API para avaliação de restaurantes",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Registrar routers
app.include_router(restaurante.router, prefix="/api/restaurantes", tags=["restaurantes"])
app.include_router(avaliacao.router, prefix="/api", tags=["avaliacoes"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

@app.get("/")
async def root():
    return {"message": "Crítica Receita API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 6. Adicionar Import Faltante

**Atualizar `app/services/upload.py` (topo do arquivo):**

```python
import io
```

## 🔨 Atividade Prática

### Exercício 1: Testar Upload

**Crie o arquivo `tests/upload-tests.http` no VS Code:**

```http
### Variáveis
@baseUrl = http://localhost:8000/api

### Upload de imagem (coloque uma imagem.jpg na pasta tests/)
POST {{baseUrl}}/restaurantes/1/imagem
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="imagem.jpg"
Content-Type: image/jpeg

< ./tests/imagem.jpg
------WebKitFormBoundary7MA4YWxkTrZu0gW--

### Verificar restaurante após upload
GET {{baseUrl}}/restaurantes/1

### Deletar imagem
DELETE {{baseUrl}}/restaurantes/1/imagem

### Acessar imagem diretamente (abrir no navegador)
# GET http://localhost:8000/uploads/nome-arquivo.jpg
```

**💡 Dica:** Para upload de arquivos, você também pode usar:
- **Thunder Client** (extensão do VS Code mais visual)
- **Postman** para testes mais complexos

### Exercício 2: Testar Validações

Teste enviar arquivos inválidos pelo arquivo `.http` e observe os erros:
- Arquivo > 2MB
- Tipo não permitido (PDF, TXT)
- Arquivo corrompido

### Exercício 3: Upload via Python

```python
import requests

url = "http://localhost:8000/api/restaurantes/1/imagem"
files = {"file": open("imagem.jpg", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

## 💡 Conceitos-Chave

- **UploadFile**: Classe do FastAPI para uploads
- **File(...)**: Parâmetro de dependência para arquivos
- **StaticFiles**: Servir arquivos estáticos
- **UUID**: Gerar nomes únicos
- **PIL/Pillow**: Validação de imagens
- **Content-Type**: Validação de MIME types

## 🛡️ Boas Práticas

1. **Sempre validar**:
   - Tipo de arquivo (extensão e MIME)
   - Tamanho do arquivo
   - Conteúdo (imagem válida)

2. **Nomes únicos**:
   - Use UUID para evitar colisões
   - Preserve a extensão original

3. **Segurança**:
   - Nunca confie no nome do arquivo enviado
   - Valide o conteúdo, não apenas a extensão
   - Configure limites de tamanho

4. **Organização**:
   - Separe uploads em diretórios por tipo
   - Considere subdiretorios por data: `uploads/2024/01/`

5. **Limpeza**:
   - Delete arquivos antigos ao atualizar
   - Implemente rotina de limpeza de arquivos órfãos

## ➡️ Próximos Passos

No próximo tutorial:
- Autenticação JWT
- Autorização por roles
- Proteção de rotas

## 📚 Recursos

- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Python Multipart](https://andrew-d.github.io/python-multipart/)
- [UUID Module](https://docs.python.org/3/library/uuid.html)
