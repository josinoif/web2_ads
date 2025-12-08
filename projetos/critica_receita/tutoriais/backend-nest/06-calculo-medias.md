# Tutorial: Cálculo Automático de Médias no NestJS

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar subscribers do TypeORM para atualização automática
- Calcular médias de avaliações em tempo real
- Usar hooks de entidades
- Otimizar queries com agregações
- Implementar desnormalização controlada

## 📖 Conteúdo

### 1. Entendendo Subscribers do TypeORM

**Subscribers** são classes que escutam eventos específicos de entidades e executam lógica customizada.

**Eventos disponíveis:**
- `afterInsert` - Após inserir registro
- `afterUpdate` - Após atualizar registro
- `afterRemove` - Após remover registro
- `beforeInsert`, `beforeUpdate`, `beforeRemove`

### 2. Criar Subscriber para Avaliações

**Arquivo `src/modules/avaliacao/subscribers/avaliacao.subscriber.ts`:**

```typescript
import {
  EntitySubscriberInterface,
  EventSubscriber,
  InsertEvent,
  RemoveEvent,
  UpdateEvent,
  DataSource,
} from 'typeorm';
import { Injectable } from '@nestjs/common';
import { Avaliacao } from '../entities/avaliacao.entity';
import { Restaurante } from '../../restaurante/entities/restaurante.entity';

@Injectable()
@EventSubscriber()
export class AvaliacaoSubscriber implements EntitySubscriberInterface<Avaliacao> {
  constructor(private dataSource: DataSource) {
    dataSource.subscribers.push(this);
  }

  /**
   * Indica que este subscriber é para a entidade Avaliacao
   */
  listenTo() {
    return Avaliacao;
  }

  /**
   * Após inserir uma avaliação, atualizar média do restaurante
   */
  async afterInsert(event: InsertEvent<Avaliacao>) {
    await this.atualizarMediaRestaurante(
      event.entity.restaurante_id,
      event.manager,
    );
  }

  /**
   * Após atualizar uma avaliação, recalcular média se a nota mudou
   */
  async afterUpdate(event: UpdateEvent<Avaliacao>) {
    if (event.entity && event.entity.restaurante_id) {
      await this.atualizarMediaRestaurante(
        event.entity.restaurante_id,
        event.manager,
      );
    }
  }

  /**
   * Após remover uma avaliação, atualizar média do restaurante
   */
  async afterRemove(event: RemoveEvent<Avaliacao>) {
    if (event.entity && event.entity.restaurante_id) {
      await this.atualizarMediaRestaurante(
        event.entity.restaurante_id,
        event.manager,
      );
    }
  }

  /**
   * Método auxiliar para calcular e atualizar a média
   */
  private async atualizarMediaRestaurante(
    restauranteId: number,
    manager: any,
  ) {
    // Calcular nova média
    const result = await manager
      .createQueryBuilder(Avaliacao, 'avaliacao')
      .select('AVG(avaliacao.nota)', 'media')
      .where('avaliacao.restaurante_id = :restauranteId', { restauranteId })
      .getRawOne();

    const media = result?.media ? parseFloat(result.media).toFixed(2) : 0;

    // Atualizar restaurante
    await manager
      .createQueryBuilder()
      .update(Restaurante)
      .set({ avaliacao_media: media })
      .where('id = :id', { id: restauranteId })
      .execute();

    console.log(`✅ Média do restaurante ${restauranteId} atualizada: ${media}`);
  }
}
```

### 3. Registrar Subscriber no Module

**Atualizar `src/modules/avaliacao/avaliacao.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AvaliacaoController } from './avaliacao.controller';
import { AvaliacaoService } from './avaliacao.service';
import { Avaliacao } from './entities/avaliacao.entity';
import { AvaliacaoSubscriber } from './subscribers/avaliacao.subscriber';
import { RestauranteModule } from '../restaurante/restaurante.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([Avaliacao]),
    RestauranteModule,
  ],
  controllers: [AvaliacaoController],
  providers: [
    AvaliacaoService,
    AvaliacaoSubscriber, // Registrar subscriber
  ],
  exports: [AvaliacaoService],
})
export class AvaliacaoModule {}
```

### 4. Método Alternativo: Hooks na Entidade

**Atualizar `src/modules/avaliacao/entities/avaliacao.entity.ts`:**

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  AfterInsert,
  AfterUpdate,
  AfterRemove,
  getManager,
} from 'typeorm';
import { Restaurante } from '../../restaurante/entities/restaurante.entity';

@Entity('avaliacoes')
export class Avaliacao {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'int' })
  nota: number;

  @Column({ type: 'text', nullable: true })
  comentario: string;

  @Column({ length: 100, nullable: true })
  nome_avaliador: string;

  @Column()
  restaurante_id: number;

  @ManyToOne(() => Restaurante, (restaurante) => restaurante.avaliacoes, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'restaurante_id' })
  restaurante: Restaurante;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  /**
   * Hook: Após inserir, atualizar média
   */
  @AfterInsert()
  async atualizarMediaAposInserir() {
    await this.calcularMedia();
  }

  /**
   * Hook: Após atualizar, recalcular média
   */
  @AfterUpdate()
  async atualizarMediaAposAtualizar() {
    await this.calcularMedia();
  }

  /**
   * Hook: Após remover, recalcular média
   */
  @AfterRemove()
  async atualizarMediaAposRemover() {
    await this.calcularMedia();
  }

  /**
   * Método privado para calcular média
   */
  private async calcularMedia() {
    const manager = getManager();

    const result = await manager
      .createQueryBuilder(Avaliacao, 'avaliacao')
      .select('AVG(avaliacao.nota)', 'media')
      .where('avaliacao.restaurante_id = :restauranteId', {
        restauranteId: this.restaurante_id,
      })
      .getRawOne();

    const media = result?.media ? parseFloat(result.media).toFixed(2) : 0;

    await manager
      .createQueryBuilder()
      .update(Restaurante)
      .set({ avaliacao_media: media })
      .where('id = :id', { id: this.restaurante_id })
      .execute();
  }
}
```

### 5. Service com Método Manual de Recálculo

**Atualizar `src/modules/restaurante/restaurante.service.ts`:**

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Restaurante } from './entities/restaurante.entity';
import { Avaliacao } from '../avaliacao/entities/avaliacao.entity';
import { CreateRestauranteDto } from './dto/create-restaurante.dto';
import { UpdateRestauranteDto } from './dto/update-restaurante.dto';

@Injectable()
export class RestauranteService {
  constructor(
    @InjectRepository(Restaurante)
    private restauranteRepository: Repository<Restaurante>,

    @InjectRepository(Avaliacao)
    private avaliacaoRepository: Repository<Avaliacao>,
  ) {}

  // ... métodos existentes ...

  /**
   * Recalcular média de um restaurante manualmente
   */
  async recalcularMedia(id: number): Promise<Restaurante> {
    const restaurante = await this.restauranteRepository.findOne({
      where: { id },
    });

    if (!restaurante) {
      throw new NotFoundException(`Restaurante com ID ${id} não encontrado`);
    }

    // Calcular média
    const result = await this.avaliacaoRepository
      .createQueryBuilder('avaliacao')
      .select('AVG(avaliacao.nota)', 'media')
      .where('avaliacao.restaurante_id = :id', { id })
      .getRawOne();

    const media = result?.media ? parseFloat(result.media) : 0;

    // Atualizar restaurante
    restaurante.avaliacao_media = media;
    await this.restauranteRepository.save(restaurante);

    return restaurante;
  }

  /**
   * Recalcular médias de todos os restaurantes (útil para manutenção)
   */
  async recalcularTodasMedias(): Promise<{ atualizado: number }> {
    const restaurantes = await this.restauranteRepository.find();

    for (const restaurante of restaurantes) {
      await this.recalcularMedia(restaurante.id);
    }

    return { atualizado: restaurantes.length };
  }

  /**
   * Obter estatísticas gerais
   */
  async getEstatisticas() {
    const totalRestaurantes = await this.restauranteRepository.count({
      where: { ativo: true },
    });

    const totalAvaliacoes = await this.avaliacaoRepository.count();

    const mediaGeral = await this.avaliacaoRepository
      .createQueryBuilder('avaliacao')
      .select('AVG(avaliacao.nota)', 'media')
      .getRawOne();

    const topRestaurantes = await this.restauranteRepository.find({
      where: { ativo: true },
      order: { avaliacao_media: 'DESC' },
      take: 10,
    });

    return {
      total_restaurantes: totalRestaurantes,
      total_avaliacoes: totalAvaliacoes,
      media_geral: mediaGeral?.media
        ? parseFloat(mediaGeral.media).toFixed(2)
        : 0,
      top_restaurantes: topRestaurantes.map((r) => ({
        id: r.id,
        nome: r.nome,
        categoria: r.categoria,
        avaliacao_media: r.avaliacao_media,
      })),
    };
  }
}
```

### 6. Adicionar Endpoints de Estatísticas

**Atualizar `src/modules/restaurante/restaurante.controller.ts`:**

```typescript
import { Controller, Get, Post, Param, ParseIntPipe } from '@nestjs/common';
import { RestauranteService } from './restaurante.service';

@Controller('restaurantes')
export class RestauranteController {
  constructor(private readonly restauranteService: RestauranteService) {}

  // ... endpoints existentes ...

  /**
   * Recalcular média de um restaurante específico
   */
  @Post(':id/recalcular-media')
  async recalcularMedia(@Param('id', ParseIntPipe) id: number) {
    return this.restauranteService.recalcularMedia(id);
  }

  /**
   * Recalcular todas as médias (admin only - adicionar guard depois)
   */
  @Post('recalcular-todas-medias')
  async recalcularTodasMedias() {
    return this.restauranteService.recalcularTodasMedias();
  }

  /**
   * Obter estatísticas gerais
   */
  @Get('estatisticas')
  async getEstatisticas() {
    return this.restauranteService.getEstatisticas();
  }
}
```

### 7. Atualizar Module com Dependências

**Atualizar `src/modules/restaurante/restaurante.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RestauranteController } from './restaurante.controller';
import { RestauranteService } from './restaurante.service';
import { Restaurante } from './entities/restaurante.entity';
import { Avaliacao } from '../avaliacao/entities/avaliacao.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([Restaurante, Avaliacao]),
  ],
  controllers: [RestauranteController],
  providers: [RestauranteService],
  exports: [RestauranteService, TypeOrmModule],
})
export class RestauranteModule {}
```

## 🔨 Atividade Prática

### Exercício 1: Testar Atualização Automática

**Arquivo `tests/media-tests.http`:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api

### 1. Criar restaurante
POST {{baseUrl}}/restaurantes
Content-Type: application/json

{
  "nome": "Teste Médias",
  "categoria": "Italiana"
}

### 2. Adicionar primeira avaliação (nota 5)
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Excelente!"
}

### 3. Ver média (deve ser 5.00)
GET {{baseUrl}}/restaurantes/1

### 4. Adicionar segunda avaliação (nota 3)
POST {{baseUrl}}/restaurantes/1/avaliacoes
Content-Type: application/json

{
  "nota": 3,
  "comentario": "Razoável"
}

### 5. Ver média atualizada (deve ser 4.00)
GET {{baseUrl}}/restaurantes/1

### 6. Recalcular média manualmente
POST {{baseUrl}}/restaurantes/1/recalcular-media

### 7. Ver estatísticas gerais
GET {{baseUrl}}/restaurantes/estatisticas
```

### Exercício 2: Verificar Logs

Observe os logs do servidor ao criar/atualizar/deletar avaliações:

```
✅ Média do restaurante 1 atualizada: 5.00
✅ Média do restaurante 1 atualizada: 4.00
```

### Exercício 3: Testar Recálculo em Massa

```bash
# Criar script para popular dados
npm run seed

# Recalcular todas as médias
curl -X POST http://localhost:3000/api/restaurantes/recalcular-todas-medias
```

## 💡 Conceitos-Chave

- **Subscribers**: Listeners globais para eventos de entidades
- **Entity Hooks**: Métodos executados em eventos específicos
- **Agregação**: Cálculos sobre conjunto de dados (AVG, SUM, COUNT)
- **Desnormalização**: Armazenar dados calculados para performance
- **QueryBuilder**: Construtor de queries complexas do TypeORM

## 🎯 Comparação: Subscribers vs Hooks

| Aspecto | Subscribers | Entity Hooks |
|---------|------------|--------------|
| **Escopo** | Global, uma instância | Por entidade |
| **Flexibilidade** | Mais flexível | Mais simples |
| **Testabilidade** | Mais fácil de mockar | Acoplado à entidade |
| **Performance** | Mesma | Mesma |
| **Recomendado** | Lógica complexa | Lógica simples |

## 🛡️ Boas Práticas

1. **Escolha a abordagem certa**:
   - Subscribers para lógica complexa e reutilizável
   - Hooks para lógica simples e específica da entidade

2. **Performance**:
   - Evite queries N+1
   - Use transações para operações em lote
   - Cache estatísticas se necessário

3. **Consistência**:
   - Sempre use arredondamento consistente
   - Trate casos de 0 avaliações
   - Valide dados antes de calcular

4. **Manutenção**:
   - Crie endpoint para recálculo manual
   - Log operações de atualização
   - Monitore performance

## ➡️ Próximos Passos

No próximo tutorial:
- Tratamento avançado de erros
- Exception filters customizados
- Logging estruturado

## 📚 Recursos

- [TypeORM Subscribers](https://typeorm.io/listeners-and-subscribers)
- [TypeORM Entity Listeners](https://typeorm.io/listeners-and-subscribers#what-is-an-entity-listener)
- [NestJS Database](https://docs.nestjs.com/techniques/database)
- [SQL Aggregation Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
