# Tutorial: Upload de Imagens com NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Configurar MulterModule para upload
- Validar tipo MIME e tamanho de arquivos
- Implementar interceptors customizados
- Servir arquivos estáticos com ServeStaticModule
- Gerenciar ciclo de vida de arquivos
- Tratar erros de upload adequadamente

## 📖 Conteúdo

### 1. Instalando Dependências

```bash
npm install @nestjs/platform-express
npm install --save-dev @types/multer
npm install @nestjs/serve-static
npm install file-type
```

### 2. Configurando o Upload Module

**Arquivo `src/modules/upload/upload.config.ts`:**

```typescript
import { diskStorage } from 'multer';
import { extname } from 'path';
import { v4 as uuid } from 'uuid';
import { BadRequestException } from '@nestjs/common';
import { MulterOptions } from '@nestjs/platform-express/multer/interfaces/multer-options.interface';

export const multerConfig: MulterOptions = {
  storage: diskStorage({
    destination: process.env.UPLOAD_DIR || './uploads',
    filename: (req, file, callback) => {
      const uniqueName = `${uuid()}${extname(file.originalname)}`;
      callback(null, uniqueName);
    },
  }),
  fileFilter: (req, file, callback) => {
    const allowedMimes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    
    if (!allowedMimes.includes(file.mimetype)) {
      return callback(
        new BadRequestException(
          'Tipo de arquivo não permitido. Use JPEG, PNG ou WebP.',
        ),
        false,
      );
    }

    callback(null, true);
  },
  limits: {
    fileSize: 2 * 1024 * 1024, // 2MB
  },
};
```

### 3. Criando o Upload Service

**Arquivo `src/modules/upload/upload.service.ts`:**

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { unlink } from 'fs/promises';
import { join } from 'path';

@Injectable()
export class UploadService {
  constructor(private readonly configService: ConfigService) {}

  getFileUrl(filename: string): string {
    const baseUrl = this.configService.get('BASE_URL');
    return `${baseUrl}/uploads/${filename}`;
  }

  async deleteFile(filename: string): Promise<void> {
    if (!filename) return;

    const uploadDir = this.configService.get('UPLOAD_DIR') || './uploads';
    const filePath = join(uploadDir, filename);

    try {
      await unlink(filePath);
    } catch (error) {
      console.warn(`Arquivo não encontrado para remoção: ${filename}`);
    }
  }

  extractFilename(url: string): string {
    if (!url) return null;
    const parts = url.split('/');
    return parts[parts.length - 1];
  }
}
```

### 4. Integrando Upload ao Restaurante

**Atualizar `src/modules/restaurante/restaurante.service.ts`:**

```typescript
import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like } from 'typeorm';
import { Restaurante } from './entities/restaurante.entity';
import { CreateRestauranteDto } from './dto/create-restaurante.dto';
import { UpdateRestauranteDto } from './dto/update-restaurante.dto';
import { QueryRestauranteDto } from './dto/query-restaurante.dto';
import { UploadService } from '../upload/upload.service';

@Injectable()
export class RestauranteService {
  constructor(
    @InjectRepository(Restaurante)
    private readonly restauranteRepository: Repository<Restaurante>,
    private readonly uploadService: UploadService,
  ) {}

  // ... métodos anteriores ...

  async uploadImage(id: number, file: Express.Multer.File): Promise<string> {
    if (!file) {
      throw new BadRequestException('Nenhuma imagem foi enviada');
    }

    const restaurante = await this.findOne(id);

    // Remover imagem antiga se existir
    if (restaurante.image_url) {
      const oldFilename = this.uploadService.extractFilename(restaurante.image_url);
      await this.uploadService.deleteFile(oldFilename);
    }

    // Gerar URL da nova imagem
    const imageUrl = this.uploadService.getFileUrl(file.filename);

    // Atualizar restaurante
    restaurante.image_url = imageUrl;
    await this.restauranteRepository.save(restaurante);

    return imageUrl;
  }

  async deleteImage(id: number): Promise<void> {
    const restaurante = await this.findOne(id);

    if (!restaurante.image_url) {
      throw new BadRequestException('Restaurante não possui imagem');
    }

    // Remover arquivo
    const filename = this.uploadService.extractFilename(restaurante.image_url);
    await this.uploadService.deleteFile(filename);

    // Limpar URL
    restaurante.image_url = null;
    await this.restauranteRepository.save(restaurante);
  }
}
```

### 5. Criando o Controller de Upload

**Atualizar `src/modules/restaurante/restaurante.controller.ts`:**

```typescript
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  ParseIntPipe,
  HttpCode,
  HttpStatus,
  UseInterceptors,
  UploadedFile,
  BadRequestException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { RestauranteService } from './restaurante.service';
import { CreateRestauranteDto } from './dto/create-restaurante.dto';
import { UpdateRestauranteDto } from './dto/update-restaurante.dto';
import { QueryRestauranteDto } from './dto/query-restaurante.dto';
import { multerConfig } from '../upload/upload.config';

@Controller('restaurantes')
export class RestauranteController {
  constructor(private readonly restauranteService: RestauranteService) {}

  // ... métodos anteriores ...

  @Post(':id/image')
  @UseInterceptors(FileInterceptor('image', multerConfig))
  async uploadImage(
    @Param('id', ParseIntPipe) id: number,
    @UploadedFile() file: Express.Multer.File,
  ) {
    const imageUrl = await this.restauranteService.uploadImage(id, file);
    return {
      mensagem: 'Imagem enviada com sucesso',
      imageUrl,
    };
  }

  @Delete(':id/image')
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteImage(@Param('id', ParseIntPipe) id: number) {
    await this.restauranteService.deleteImage(id);
  }
}
```

### 6. Criando o Upload Module

**Arquivo `src/modules/upload/upload.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { MulterModule } from '@nestjs/platform-express';
import { UploadService } from './upload.service';
import { multerConfig } from './upload.config';

@Module({
  imports: [MulterModule.register(multerConfig)],
  providers: [UploadService],
  exports: [UploadService],
})
export class UploadModule {}
```

### 7. Configurar Arquivos Estáticos

**Atualizar `src/app.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ServeStaticModule } from '@nestjs/serve-static';
import { join } from 'path';
import { getDatabaseConfig } from './config/database.config';
import { validate } from './config/env.validation';
import { RestauranteModule } from './modules/restaurante/restaurante.module';
import { AvaliacaoModule } from './modules/avaliacao/avaliacao.module';
import { UploadModule } from './modules/upload/upload.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
    }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: getDatabaseConfig,
    }),
    ServeStaticModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => [
        {
          rootPath: join(__dirname, '..', configService.get('UPLOAD_DIR', 'uploads')),
          serveRoot: '/uploads',
        },
      ],
    }),
    RestauranteModule,
    AvaliacaoModule,
    UploadModule,
  ],
})
export class AppModule {}
```

### 8. Atualizar Restaurante Module

**Arquivo `src/modules/restaurante/restaurante.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RestauranteController } from './restaurante.controller';
import { RestauranteService } from './restaurante.service';
import { Restaurante } from './entities/restaurante.entity';
import { UploadModule } from '../upload/upload.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([Restaurante]),
    UploadModule,
  ],
  controllers: [RestauranteController],
  providers: [RestauranteService],
  exports: [RestauranteService],
})
export class RestauranteModule {}
```

### 9. Interceptor para Validação Avançada

**Arquivo `src/modules/upload/interceptors/file-validation.interceptor.ts`:**

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  BadRequestException,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { readFile } from 'fs/promises';
import { fileTypeFromBuffer } from 'file-type';

@Injectable()
export class FileValidationInterceptor implements NestInterceptor {
  async intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Promise<Observable<any>> {
    const request = context.switchToHttp().getRequest();
    const file = request.file;

    if (!file) {
      return next.handle();
    }

    // Validar MIME type real (não apenas extensão)
    const buffer = await readFile(file.path);
    const fileType = await fileTypeFromBuffer(buffer);

    if (!fileType) {
      throw new BadRequestException('Não foi possível determinar o tipo de arquivo');
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(fileType.mime)) {
      throw new BadRequestException(
        `Tipo de arquivo não permitido: ${fileType.mime}`,
      );
    }

    return next.handle();
  }
}
```

### 10. Tratamento de Erros do Multer

**Arquivo `src/common/filters/multer-exception.filter.ts`:**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpStatus,
} from '@nestjs/common';
import { Response } from 'express';

@Catch()
export class MulterExceptionFilter implements ExceptionFilter {
  catch(exception: any, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Erro ao fazer upload do arquivo';

    if (exception.code === 'LIMIT_FILE_SIZE') {
      status = HttpStatus.BAD_REQUEST;
      message = 'Arquivo muito grande. Tamanho máximo: 2MB';
    } else if (exception.code === 'LIMIT_UNEXPECTED_FILE') {
      status = HttpStatus.BAD_REQUEST;
      message = 'Campo de arquivo inesperado';
    }

    response.status(status).json({
      statusCode: status,
      message,
      timestamp: new Date().toISOString(),
    });
  }
}
```

**Registrar no main.ts:**

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';
import { MulterExceptionFilter } from './common/filters/multer-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));

  app.useGlobalFilters(new MulterExceptionFilter());

  await app.listen(3000);
}
bootstrap();
```

## 🔨 Atividade Prática

### Exercício 1: Testar Upload

```bash
# Upload de imagem
curl -X POST http://localhost:3000/api/restaurantes/1/image \
  -F "image=@/caminho/para/imagem.jpg"

# Resposta esperada:
# {
#   "mensagem": "Imagem enviada com sucesso",
#   "imageUrl": "http://localhost:3000/uploads/uuid-123.jpg"
# }

# Acessar imagem
curl http://localhost:3000/uploads/uuid-123.jpg
```

### Exercício 2: Validações

Teste os cenários:
- ✅ Upload de imagem válida (JPEG, PNG, WebP)
- ❌ Arquivo maior que 2MB
- ❌ Tipo de arquivo inválido (PDF, TXT)
- ✅ Substituir imagem existente
- ✅ Remover imagem

### Exercício 3: Adicionar Compressão

Instale `sharp` e adicione compressão automática:

```bash
npm install sharp
```

```typescript
import * as sharp from 'sharp';

async uploadImage(id: number, file: Express.Multer.File): Promise<string> {
  // Comprimir imagem
  const compressedPath = file.path.replace(extname(file.path), '-compressed.jpg');
  
  await sharp(file.path)
    .resize(1200, 1200, { fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 80 })
    .toFile(compressedPath);

  // Remover original
  await unlink(file.path);

  // Continuar com arquivo comprimido...
}
```

## 💡 Conceitos-Chave

- **Multer**: Middleware para multipart/form-data
- **Interceptors**: Executam lógica antes/depois do handler
- **FileInterceptor**: Captura arquivo do request
- **ServeStaticModule**: Serve arquivos estáticos
- **File Validation**: Validação além da extensão

## ➡️ Próximos Passos

No próximo tutorial:
- Autenticação com JWT
- Autorização baseada em roles
- Proteger rotas de upload

## 📚 Recursos

- [NestJS File Upload](https://docs.nestjs.com/techniques/file-upload)
- [Multer Documentation](https://github.com/expressjs/multer)
- [Sharp - Image Processing](https://sharp.pixelplumbing.com/)
- [ServeStaticModule](https://docs.nestjs.com/recipes/serve-static)
