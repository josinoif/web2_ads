# Tutorial 7: CRUD - Update e Delete

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar operações UPDATE (PUT/PATCH)
- Implementar operação DELETE
- Diferenciar entre PUT e PATCH
- Implementar soft delete
- Validar existência de recursos antes de atualizar/deletar
- Tratar casos de atualização parcial

## 📖 Conteúdo

### 1. UPDATE - Atualização Completa (PUT)

**Adicionar no `restauranteController.js`:**

```javascript
/**
 * UPDATE - Atualizar restaurante completo
 * PUT /api/restaurantes/:id
 */
exports.update = async (req, res) => {
  const { id } = req.params;
  const { nome, categoria, endereco, telefone, descricao } = req.body;
  
  // Buscar restaurante
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  // Atualizar todos os campos
  await restaurante.update({
    nome,
    categoria,
    endereco,
    telefone,
    descricao
  });
  
  res.json({
    mensagem: 'Restaurante atualizado com sucesso',
    restaurante
  });
};

/**
 * PATCH - Atualização parcial
 * PATCH /api/restaurantes/:id
 */
exports.partialUpdate = async (req, res) => {
  const { id } = req.params;
  const camposPermitidos = ['nome', 'categoria', 'endereco', 'telefone', 'descricao'];
  
  // Buscar restaurante
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  // Filtrar apenas campos permitidos e presentes no body
  const updates = {};
  camposPermitidos.forEach(campo => {
    if (req.body[campo] !== undefined) {
      updates[campo] = req.body[campo];
    }
  });
  
  // Verificar se há algo para atualizar
  if (Object.keys(updates).length === 0) {
    throw new ApiError(400, 'Nenhum campo válido para atualizar');
  }
  
  // Atualizar
  await restaurante.update(updates);
  
  res.json({
    mensagem: 'Restaurante atualizado parcialmente',
    camposAtualizados: Object.keys(updates),
    restaurante
  });
};
```

### 2. DELETE - Exclusão

**Adicionar no `restauranteController.js`:**

```javascript
/**
 * DELETE - Soft delete (marca como inativo)
 * DELETE /api/restaurantes/:id
 */
exports.softDelete = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  if (!restaurante.ativo) {
    throw new ApiError(400, 'Restaurante já está inativo');
  }
  
  // Marcar como inativo ao invés de deletar
  await restaurante.update({ ativo: false });
  
  res.json({
    mensagem: 'Restaurante desativado com sucesso'
  });
};

/**
 * DELETE - Hard delete (remove permanentemente)
 * DELETE /api/restaurantes/:id/permanente
 */
exports.hardDelete = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  // Verificar se há avaliações associadas
  const avaliacoesCount = await Avaliacao.count({
    where: { restaurante_id: id }
  });
  
  if (avaliacoesCount > 0) {
    throw new ApiError(400, 
      `Não é possível deletar. Existem ${avaliacoesCount} avaliações associadas. ` +
      'Delete as avaliações primeiro ou use soft delete.'
    );
  }
  
  // Deletar permanentemente
  await restaurante.destroy();
  
  res.json({
    mensagem: 'Restaurante deletado permanentemente'
  });
};

/**
 * RESTORE - Reativar restaurante inativo
 * POST /api/restaurantes/:id/restaurar
 */
exports.restore = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError(404, 'Restaurante não encontrado');
  }
  
  if (restaurante.ativo) {
    throw new ApiError(400, 'Restaurante já está ativo');
  }
  
  await restaurante.update({ ativo: true });
  
  res.json({
    mensagem: 'Restaurante restaurado com sucesso',
    restaurante
  });
};
```

### 3. Validações para UPDATE

**Adicionar em `restauranteValidator.js`:**

```javascript
exports.updateValidation = [
  param('id')
    .isInt({ min: 1 }).withMessage('ID inválido'),
  
  body('nome')
    .trim()
    .notEmpty().withMessage('Nome é obrigatório')
    .isLength({ min: 3, max: 100 }).withMessage('Nome deve ter entre 3 e 100 caracteres'),
  
  body('categoria')
    .trim()
    .notEmpty().withMessage('Categoria é obrigatória')
    .isIn(['Italiana', 'Japonesa', 'Brasileira', 'Mexicana', 'Árabe', 'Hamburgueria', 'Pizzaria', 'Vegetariana', 'Outra'])
    .withMessage('Categoria inválida'),
  
  body('endereco')
    .optional()
    .trim(),
  
  body('telefone')
    .optional()
    .trim()
    .matches(/^[\d\s\(\)\-\+]+$/).withMessage('Telefone inválido'),
  
  body('descricao')
    .optional()
    .trim()
];

exports.partialUpdateValidation = [
  param('id')
    .isInt({ min: 1 }).withMessage('ID inválido'),
  
  body('nome')
    .optional()
    .trim()
    .notEmpty().withMessage('Nome não pode ser vazio')
    .isLength({ min: 3, max: 100 }).withMessage('Nome deve ter entre 3 e 100 caracteres'),
  
  body('categoria')
    .optional()
    .trim()
    .isIn(['Italiana', 'Japonesa', 'Brasileira', 'Mexicana', 'Árabe', 'Hamburgueria', 'Pizzaria', 'Vegetariana', 'Outra'])
    .withMessage('Categoria inválida'),
  
  body('telefone')
    .optional()
    .trim()
    .matches(/^[\d\s\(\)\-\+]+$/).withMessage('Telefone inválido')
];
```

### 4. Atualizando as Rotas

**Atualizar `restauranteRoutes.js`:**

```javascript
const {
  createValidation,
  updateValidation,
  partialUpdateValidation,
  idValidation,
  queryValidation
} = require('../validators/restauranteValidator');

// ... rotas anteriores ...

// UPDATE (completo)
router.put('/:id',
  updateValidation,
  validate,
  asyncHandler(restauranteController.update)
);

// PATCH (parcial)
router.patch('/:id',
  partialUpdateValidation,
  validate,
  asyncHandler(restauranteController.partialUpdate)
);

// SOFT DELETE
router.delete('/:id',
  idValidation,
  validate,
  asyncHandler(restauranteController.softDelete)
);

// HARD DELETE
router.delete('/:id/permanente',
  idValidation,
  validate,
  asyncHandler(restauranteController.hardDelete)
);

// RESTORE
router.post('/:id/restaurar',
  idValidation,
  validate,
  asyncHandler(restauranteController.restore)
);

module.exports = router;
```

### 5. Diferença entre PUT e PATCH

**PUT - Atualização Completa:**
- Substitui o recurso inteiro
- Todos os campos devem ser enviados
- Campos não enviados são perdidos/resetados

**PATCH - Atualização Parcial:**
- Atualiza apenas campos específicos
- Apenas campos enviados são modificados
- Campos não enviados permanecem inalterados

**Exemplo:**

```javascript
// Estado inicial
{
  "id": 1,
  "nome": "Pizza Bella",
  "categoria": "Italiana",
  "telefone": "(11) 98765-4321"
}

// PUT - Deve enviar todos os campos
PUT /api/restaurantes/1
{
  "nome": "Pizza Bella Premium",
  "categoria": "Italiana",
  "endereco": "Rua Nova, 456",
  "telefone": "(11) 98765-4321"
}

// PATCH - Envia apenas o que quer mudar
PATCH /api/restaurantes/1
{
  "nome": "Pizza Bella Premium"
}
// Resultado: apenas nome muda, resto permanece igual
```

### 6. Soft Delete vs Hard Delete

**Soft Delete (Recomendado):**
- Não remove dados fisicamente
- Marca como inativo/deletado
- Permite recuperação
- Mantém histórico e integridade referencial

**Hard Delete:**
- Remove permanentemente do banco
- Não pode ser recuperado
- Pode quebrar integridade referencial
- Use apenas quando necessário (GDPR, dados sensíveis)

### 7. Testando UPDATE e DELETE

**Arquivo `test.http`:**

```http
### UPDATE Completo (PUT)
PUT {{baseUrl}}/restaurantes/1
Content-Type: {{contentType}}

{
  "nome": "Pizza Bella Premium",
  "categoria": "Pizzaria",
  "endereco": "Rua das Flores, 123 - Sala 10",
  "telefone": "(11) 98765-4321",
  "descricao": "A melhor pizza italiana da cidade!"
}

### UPDATE Parcial (PATCH) - Apenas nome
PATCH {{baseUrl}}/restaurantes/1
Content-Type: {{contentType}}

{
  "nome": "Pizza Bella Gourmet"
}

### UPDATE Parcial - Múltiplos campos
PATCH {{baseUrl}}/restaurantes/1
Content-Type: {{contentType}}

{
  "telefone": "(11) 3456-7890",
  "descricao": "Pizza artesanal com ingredientes premium"
}

### Soft Delete (desativar)
DELETE {{baseUrl}}/restaurantes/2

### Restaurar restaurante
POST {{baseUrl}}/restaurantes/2/restaurar

### Hard Delete (permanente)
DELETE {{baseUrl}}/restaurantes/2/permanente

### Teste de validação - ID inválido
PUT {{baseUrl}}/restaurantes/abc
Content-Type: {{contentType}}

{
  "nome": "Teste"
}

### Teste - Atualizar inexistente
PUT {{baseUrl}}/restaurantes/999
Content-Type: {{contentType}}

{
  "nome": "Restaurante Inexistente",
  "categoria": "Italiana"
}
```

### 8. Tratamento de Concorrência

Para evitar conflitos em atualizações simultâneas, use versionamento:

```javascript
// Adicionar campo version no modelo
const Restaurante = sequelize.define('restaurante', {
  // ... outros campos ...
  version: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  }
});

// No controller
exports.updateWithVersion = async (req, res) => {
  const { id } = req.params;
  const { version, ...updates } = req.body;
  
  const [numUpdated] = await Restaurante.update(
    {
      ...updates,
      version: version + 1
    },
    {
      where: {
        id,
        version  // Só atualiza se version for igual
      }
    }
  );
  
  if (numUpdated === 0) {
    throw new ApiError(409, 'Conflito de versão. O registro foi modificado por outro usuário.');
  }
  
  const restaurante = await Restaurante.findByPk(id);
  res.json({ mensagem: 'Atualizado com sucesso', restaurante });
};
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Bulk Delete

Crie um endpoint que deleta múltiplos restaurantes de uma vez:

```javascript
// DELETE /api/restaurantes/bulk
// Body: { "ids": [1, 2, 3] }
```

<details>
<summary>Ver solução</summary>

```javascript
exports.bulkDelete = async (req, res) => {
  const { ids } = req.body;
  
  if (!Array.isArray(ids) || ids.length === 0) {
    throw new ApiError(400, 'IDs deve ser um array não vazio');
  }
  
  const numDeleted = await Restaurante.update(
    { ativo: false },
    {
      where: {
        id: { [Op.in]: ids },
        ativo: true
      }
    }
  );
  
  res.json({
    mensagem: `${numDeleted} restaurante(s) desativado(s)`,
    idsProcessados: ids
  });
};

// Na rota
router.delete('/bulk',
  body('ids').isArray().withMessage('IDs deve ser um array'),
  validate,
  asyncHandler(restauranteController.bulkDelete)
);
```

</details>

### Exercício 2: Log de Alterações

Implemente um sistema simples de auditoria que registra quem e quando fez alterações:

<details>
<summary>Ver solução</summary>

```javascript
// Criar modelo de Log
const Log = sequelize.define('log', {
  entidade: DataTypes.STRING,
  entidade_id: DataTypes.INTEGER,
  acao: DataTypes.ENUM('create', 'update', 'delete'),
  usuario: DataTypes.STRING,
  dados_anteriores: DataTypes.JSONB,
  dados_novos: DataTypes.JSONB
});

// No controller, após update
const dadosAnteriores = restaurante.toJSON();
await restaurante.update(updates);

await Log.create({
  entidade: 'restaurante',
  entidade_id: restaurante.id,
  acao: 'update',
  usuario: req.user?.nome || 'sistema',
  dados_anteriores: dadosAnteriores,
  dados_novos: restaurante.toJSON()
});
```

</details>

## 💡 Conceitos-Chave

- **PUT** atualiza recurso completo
- **PATCH** atualiza parcialmente
- **Soft delete** marca como inativo
- **Hard delete** remove permanentemente
- Sempre validar **existência** antes de atualizar/deletar
- **Status 404** para recurso não encontrado
- **Status 409** para conflitos
- Considerar **integridade referencial** ao deletar

## ➡️ Próximos Passos

Com o CRUD completo, no próximo tutorial vamos configurar **CORS e middlewares de segurança** para proteger nossa API.

[➡️ Ir para Tutorial 8: CORS e Middlewares de Segurança](08-cors-middleware.md)

---

**Dica:** Sempre use soft delete em produção para permitir recuperação de dados!
