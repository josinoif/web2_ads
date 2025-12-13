# Módulo 08 - Frontend: Formulário de Receitas

Neste módulo, você vai criar o formulário dinâmico para cadastrar e editar receitas, incluindo a gestão de múltiplos ingredientes de forma interativa.

## Objetivos do Módulo

- ✅ Criar formulário de cadastro de receitas
- ✅ Implementar adição/remoção dinâmica de ingredientes
- ✅ Criar autocomplete de ingredientes
- ✅ Implementar validações no frontend
- ✅ Reutilizar formulário para edição
- ✅ Adicionar feedback visual com toast

---

## 1. Criando o Componente de Formulário

### Crie o arquivo `src/components/ReceitaForm.jsx`:

```javascript
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { receitasService, ingredientesService } from '@/services/api';
import toast from 'react-hot-toast';

export default function ReceitaForm({ receitaId = null }) {
    const router = useRouter();
    const isEdicao = !!receitaId;

    // Estado do formulário
    const [formData, setFormData] = useState({
        nome: '',
        categoria: '',
        tempo_preparo: '',
        rendimento: '',
        modo_preparo: ''
    });

    // Estado dos ingredientes da receita
    const [ingredientesReceita, setIngredientesReceita] = useState([
        { ingrediente_id: '', quantidade: '', unidade_medida: 'unidade(s)' }
    ]);

    // Lista de todos os ingredientes disponíveis
    const [ingredientesDisponiveis, setIngredientesDisponiveis] = useState([]);
    
    // Estados de controle
    const [loading, setLoading] = useState(false);
    const [carregando, setCarregando] = useState(isEdicao);

    // Categorias disponíveis
    const categorias = [
        'Sobremesa',
        'Prato Principal',
        'Entrada',
        'Lanche',
        'Bebida'
    ];

    // Unidades de medida disponíveis
    const unidadesMedida = [
        'unidade(s)',
        'grama(s)',
        'kg',
        'ml',
        'litro(s)',
        'xícara(s)',
        'colher(es) de sopa',
        'colher(es) de chá',
        'pitada(s)',
        'a gosto'
    ];

    // Carrega ingredientes disponíveis e dados da receita (se edição)
    useEffect(() => {
        carregarIngredientes();
        if (isEdicao) {
            carregarReceita();
        }
    }, [receitaId]);

    // Carrega todos os ingredientes do banco
    const carregarIngredientes = async () => {
        try {
            const response = await ingredientesService.listarTodos();
            setIngredientesDisponiveis(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar ingredientes:', error);
            toast.error('Erro ao carregar ingredientes');
        }
    };

    // Carrega dados da receita para edição
    const carregarReceita = async () => {
        try {
            setCarregando(true);
            const response = await receitasService.buscarPorId(receitaId);
            const receita = response.data;

            // Preenche o formulário
            setFormData({
                nome: receita.nome,
                categoria: receita.categoria,
                tempo_preparo: receita.tempo_preparo,
                rendimento: receita.rendimento,
                modo_preparo: receita.modo_preparo
            });

            // Preenche os ingredientes
            if (receita.ingredientes && receita.ingredientes.length > 0) {
                setIngredientesReceita(
                    receita.ingredientes.map(ing => ({
                        ingrediente_id: ing.ingrediente_id,
                        quantidade: ing.quantidade,
                        unidade_medida: ing.unidade_medida
                    }))
                );
            }
        } catch (error) {
            console.error('Erro ao carregar receita:', error);
            toast.error('Erro ao carregar receita');
            router.push('/');
        } finally {
            setCarregando(false);
        }
    };

    // Atualiza campos do formulário
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Adiciona um novo campo de ingrediente
    const adicionarIngrediente = () => {
        setIngredientesReceita([
            ...ingredientesReceita,
            { ingrediente_id: '', quantidade: '', unidade_medida: 'unidade(s)' }
        ]);
    };

    // Remove um campo de ingrediente
    const removerIngrediente = (index) => {
        if (ingredientesReceita.length === 1) {
            toast.error('Deve haver pelo menos 1 ingrediente');
            return;
        }
        
        const novosIngredientes = ingredientesReceita.filter((_, i) => i !== index);
        setIngredientesReceita(novosIngredientes);
    };

    // Atualiza um ingrediente específico
    const handleIngredienteChange = (index, campo, valor) => {
        const novosIngredientes = [...ingredientesReceita];
        novosIngredientes[index][campo] = valor;
        setIngredientesReceita(novosIngredientes);
    };

    // Validação do formulário
    const validarFormulario = () => {
        if (!formData.nome.trim()) {
            toast.error('Nome da receita é obrigatório');
            return false;
        }

        if (!formData.categoria) {
            toast.error('Selecione uma categoria');
            return false;
        }

        if (!formData.tempo_preparo || formData.tempo_preparo <= 0) {
            toast.error('Tempo de preparo deve ser maior que 0');
            return false;
        }

        if (!formData.rendimento.trim()) {
            toast.error('Rendimento é obrigatório');
            return false;
        }

        if (!formData.modo_preparo.trim()) {
            toast.error('Modo de preparo é obrigatório');
            return false;
        }

        // Valida ingredientes
        for (let i = 0; i < ingredientesReceita.length; i++) {
            const ing = ingredientesReceita[i];
            
            if (!ing.ingrediente_id) {
                toast.error(`Selecione o ingrediente #${i + 1}`);
                return false;
            }

            if (!ing.quantidade || ing.quantidade <= 0) {
                toast.error(`Quantidade do ingrediente #${i + 1} deve ser maior que 0`);
                return false;
            }
        }

        // Verifica ingredientes duplicados
        const idsIngredientes = ingredientesReceita.map(i => i.ingrediente_id);
        const idsUnicos = new Set(idsIngredientes);
        if (idsUnicos.size !== idsIngredientes.length) {
            toast.error('Há ingredientes duplicados na lista');
            return false;
        }

        return true;
    };

    // Submete o formulário
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validarFormulario()) {
            return;
        }

        try {
            setLoading(true);

            const dados = {
                ...formData,
                tempo_preparo: parseInt(formData.tempo_preparo),
                ingredientes: ingredientesReceita.map(ing => ({
                    ingrediente_id: parseInt(ing.ingrediente_id),
                    quantidade: parseFloat(ing.quantidade),
                    unidade_medida: ing.unidade_medida
                }))
            };

            if (isEdicao) {
                await receitasService.atualizar(receitaId, dados);
                toast.success('Receita atualizada com sucesso!');
            } else {
                await receitasService.criar(dados);
                toast.success('Receita criada com sucesso!');
            }

            router.push('/');
        } catch (error) {
            console.error('Erro ao salvar receita:', error);
            const mensagem = error.response?.data?.message || 'Erro ao salvar receita';
            toast.error(mensagem);
        } finally {
            setLoading(false);
        }
    };

    // Loading inicial (para edição)
    if (carregando) {
        return (
            <div className="container mx-auto px-4 py-20 flex justify-center items-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            {/* Cabeçalho */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">
                    {isEdicao ? '✏️ Editar Receita' : '➕ Nova Receita'}
                </h1>
                <p className="text-gray-600">
                    {isEdicao 
                        ? 'Atualize as informações da sua receita' 
                        : 'Preencha os dados da sua nova receita'}
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Card: Informações Básicas */}
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <span>📝</span> Informações Básicas
                    </h2>

                    <div className="space-y-4">
                        {/* Nome */}
                        <div>
                            <label htmlFor="nome" className="label">
                                Nome da Receita *
                            </label>
                            <input
                                type="text"
                                id="nome"
                                name="nome"
                                value={formData.nome}
                                onChange={handleChange}
                                placeholder="Ex: Bolo de Chocolate"
                                className="input-field"
                                required
                            />
                        </div>

                        <div className="grid md:grid-cols-2 gap-4">
                            {/* Categoria */}
                            <div>
                                <label htmlFor="categoria" className="label">
                                    Categoria *
                                </label>
                                <select
                                    id="categoria"
                                    name="categoria"
                                    value={formData.categoria}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                >
                                    <option value="">Selecione...</option>
                                    {categorias.map(cat => (
                                        <option key={cat} value={cat}>{cat}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Tempo de Preparo */}
                            <div>
                                <label htmlFor="tempo_preparo" className="label">
                                    Tempo de Preparo (minutos) *
                                </label>
                                <input
                                    type="number"
                                    id="tempo_preparo"
                                    name="tempo_preparo"
                                    value={formData.tempo_preparo}
                                    onChange={handleChange}
                                    placeholder="Ex: 30"
                                    min="1"
                                    className="input-field"
                                    required
                                />
                            </div>
                        </div>

                        {/* Rendimento */}
                        <div>
                            <label htmlFor="rendimento" className="label">
                                Rendimento *
                            </label>
                            <input
                                type="text"
                                id="rendimento"
                                name="rendimento"
                                value={formData.rendimento}
                                onChange={handleChange}
                                placeholder="Ex: 8 porções"
                                className="input-field"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Card: Ingredientes */}
                <div className="card">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                            <span>🥕</span> Ingredientes
                        </h2>
                        <button
                            type="button"
                            onClick={adicionarIngrediente}
                            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            <span>➕</span> Adicionar Ingrediente
                        </button>
                    </div>

                    <div className="space-y-4">
                        {ingredientesReceita.map((ingrediente, index) => (
                            <div key={index} className="bg-gray-50 p-4 rounded-lg">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-sm font-semibold text-gray-700">
                                        Ingrediente #{index + 1}
                                    </span>
                                    {ingredientesReceita.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={() => removerIngrediente(index)}
                                            className="text-red-600 hover:text-red-700 text-sm font-medium"
                                        >
                                            🗑️ Remover
                                        </button>
                                    )}
                                </div>

                                <div className="grid md:grid-cols-3 gap-3">
                                    {/* Ingrediente */}
                                    <div className="md:col-span-1">
                                        <label className="label text-sm">
                                            Ingrediente *
                                        </label>
                                        <select
                                            value={ingrediente.ingrediente_id}
                                            onChange={(e) => handleIngredienteChange(index, 'ingrediente_id', e.target.value)}
                                            className="input-field"
                                            required
                                        >
                                            <option value="">Selecione...</option>
                                            {ingredientesDisponiveis.map(ing => (
                                                <option key={ing.id} value={ing.id}>
                                                    {ing.nome}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Quantidade */}
                                    <div>
                                        <label className="label text-sm">
                                            Quantidade *
                                        </label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            min="0.01"
                                            value={ingrediente.quantidade}
                                            onChange={(e) => handleIngredienteChange(index, 'quantidade', e.target.value)}
                                            placeholder="Ex: 2"
                                            className="input-field"
                                            required
                                        />
                                    </div>

                                    {/* Unidade de Medida */}
                                    <div>
                                        <label className="label text-sm">
                                            Unidade *
                                        </label>
                                        <select
                                            value={ingrediente.unidade_medida}
                                            onChange={(e) => handleIngredienteChange(index, 'unidade_medida', e.target.value)}
                                            className="input-field"
                                            required
                                        >
                                            {unidadesMedida.map(unidade => (
                                                <option key={unidade} value={unidade}>
                                                    {unidade}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Dica */}
                    <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm text-blue-800">
                            💡 <strong>Dica:</strong> Se o ingrediente não estiver na lista, 
                            você pode cadastrá-lo através do menu Ingredientes antes de criar a receita.
                        </p>
                    </div>
                </div>

                {/* Card: Modo de Preparo */}
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <span>👨‍🍳</span> Modo de Preparo
                    </h2>

                    <div>
                        <label htmlFor="modo_preparo" className="label">
                            Instruções *
                        </label>
                        <textarea
                            id="modo_preparo"
                            name="modo_preparo"
                            value={formData.modo_preparo}
                            onChange={handleChange}
                            placeholder="Descreva passo a passo como preparar a receita..."
                            rows="10"
                            className="input-field resize-y"
                            required
                        />
                        <p className="text-sm text-gray-500 mt-2">
                            Descreva cada passo da receita de forma clara e detalhada.
                        </p>
                    </div>
                </div>

                {/* Botões de Ação */}
                <div className="flex gap-4">
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                {isEdicao ? 'Atualizando...' : 'Salvando...'}
                            </span>
                        ) : (
                            <span>{isEdicao ? '✅ Atualizar Receita' : '➕ Criar Receita'}</span>
                        )}
                    </button>

                    <button
                        type="button"
                        onClick={() => router.push('/')}
                        className="px-8 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                    >
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    );
}
```

---

## 2. Criando a Página de Nova Receita

### Crie a pasta e arquivo `src/app/receitas/novo/page.js`:

```bash
mkdir -p src/app/receitas/novo
```

```javascript
import ReceitaForm from '@/components/ReceitaForm';

export default function NovaReceitaPage() {
    return <ReceitaForm />;
}
```

---

## 3. Criando a Página de Edição

### Crie a pasta e arquivo `src/app/receitas/editar/[id]/page.js`:

```bash
mkdir -p src/app/receitas/editar/\[id\]
```

```javascript
'use client';

import { useParams } from 'next/navigation';
import ReceitaForm from '@/components/ReceitaForm';

export default function EditarReceitaPage() {
    const params = useParams();
    
    return <ReceitaForm receitaId={params.id} />;
}
```

---

## 4. Criando Página de Ingredientes (Bônus)

> **📝 Nota:** O Navbar já foi criado completamente no Módulo 06 com todos os links necessários (Receitas, Nova Receita e Ingredientes). Não é necessário fazer alterações nele neste módulo.

Para gerenciar ingredientes antes de criar receitas, vamos criar uma página simples:

### Crie `src/app/ingredientes/page.js`:

```bash
mkdir -p src/app/ingredientes
```

```javascript
'use client';

import { useState, useEffect } from 'react';
import { ingredientesService } from '@/services/api';
import toast from 'react-hot-toast';

export default function IngredientesPage() {
    const [ingredientes, setIngredientes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [nome, setNome] = useState('');
    const [editando, setEditando] = useState(null);

    useEffect(() => {
        carregarIngredientes();
    }, []);

    const carregarIngredientes = async () => {
        try {
            setLoading(true);
            const response = await ingredientesService.listarTodos();
            setIngredientes(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar ingredientes:', error);
            toast.error('Erro ao carregar ingredientes');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!nome.trim()) {
            toast.error('Digite o nome do ingrediente');
            return;
        }

        try {
            if (editando) {
                await ingredientesService.atualizar(editando.id, { nome });
                toast.success('Ingrediente atualizado!');
                setEditando(null);
            } else {
                await ingredientesService.criar({ nome });
                toast.success('Ingrediente criado!');
            }
            
            setNome('');
            carregarIngredientes();
        } catch (error) {
            console.error('Erro ao salvar ingrediente:', error);
            toast.error(error.response?.data?.message || 'Erro ao salvar ingrediente');
        }
    };

    const handleEditar = (ingrediente) => {
        setEditando(ingrediente);
        setNome(ingrediente.nome);
    };

    const handleDeletar = async (id, nome) => {
        if (!confirm(`Deletar "${nome}"?`)) return;

        try {
            await ingredientesService.deletar(id);
            toast.success('Ingrediente deletado!');
            carregarIngredientes();
        } catch (error) {
            console.error('Erro ao deletar:', error);
            toast.error(error.response?.data?.message || 'Erro ao deletar ingrediente');
        }
    };

    const handleCancelar = () => {
        setEditando(null);
        setNome('');
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-20 flex justify-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">
                    🥕 Gerenciar Ingredientes
                </h1>
                <p className="text-gray-600">
                    Cadastre os ingredientes que você usa nas suas receitas
                </p>
            </div>

            {/* Formulário */}
            <form onSubmit={handleSubmit} className="card mb-8">
                <label className="label">
                    {editando ? 'Editar Ingrediente' : 'Novo Ingrediente'}
                </label>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={nome}
                        onChange={(e) => setNome(e.target.value)}
                        placeholder="Ex: Farinha de Trigo"
                        className="input-field flex-1"
                    />
                    <button type="submit" className="btn-primary px-6">
                        {editando ? '✅ Atualizar' : '➕ Adicionar'}
                    </button>
                    {editando && (
                        <button
                            type="button"
                            onClick={handleCancelar}
                            className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                        >
                            Cancelar
                        </button>
                    )}
                </div>
            </form>

            {/* Lista */}
            <div className="card">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                    📋 Ingredientes Cadastrados ({ingredientes.length})
                </h2>

                {ingredientes.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">
                        Nenhum ingrediente cadastrado ainda.
                    </p>
                ) : (
                    <div className="space-y-2">
                        {ingredientes.map(ing => (
                            <div
                                key={ing.id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                            >
                                <span className="font-medium text-gray-800">
                                    {ing.nome}
                                </span>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleEditar(ing)}
                                        className="text-blue-600 hover:text-blue-700 px-3 py-1"
                                    >
                                        ✏️ Editar
                                    </button>
                                    <button
                                        onClick={() => handleDeletar(ing.id, ing.nome)}
                                        className="text-red-600 hover:text-red-700 px-3 py-1"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
```

---

## 5. Testando o Formulário

### Passo 1: Cadastre alguns ingredientes

1. Acesse [http://localhost:3000/ingredientes](http://localhost:3000/ingredientes)
2. Cadastre: Farinha de Trigo, Açúcar, Ovos, Leite, Chocolate em Pó, Fermento

### Passo 2: Crie uma receita

1. Clique em "➕ Nova Receita" no navbar
2. Preencha os dados:
   - **Nome:** Bolo de Chocolate
   - **Categoria:** Sobremesa
   - **Tempo:** 45 minutos
   - **Rendimento:** 8 porções
3. Adicione ingredientes:
   - 2 xícaras de Farinha de Trigo
   - 1 xícara de Açúcar
   - 3 unidades de Ovos
   - 1 xícara de Leite
   - 1/2 xícara de Chocolate em Pó
   - 1 colher de sopa de Fermento
4. Escreva o modo de preparo
5. Clique em "Criar Receita"

### Passo 3: Edite a receita

1. Na lista, clique em "Ver Detalhes"
2. Clique em "Editar Receita"
3. Altere algum dado
4. Salve as alterações

---

## 6. Funcionalidades Implementadas

### ✅ Formulário Dinâmico
- Adição/remoção de ingredientes
- Validações em tempo real
- Feedback visual com toast

### ✅ Reutilização do Componente
- Mesmo componente para criar e editar
- Detecta o modo através da prop `receitaId`

### ✅ Validações
- Campos obrigatórios
- Valores numéricos positivos
- Ingredientes duplicados
- Pelo menos 1 ingrediente

### ✅ UX Melhorada
- Loading states
- Mensagens de sucesso/erro
- Confirmações antes de ações destrutivas
- Cancelamento de edições

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou formulário completo de receitas
- ✅ Implementou gestão dinâmica de ingredientes
- ✅ Adicionou validações robustas
- ✅ Reutilizou componentes (criar e editar)
- ✅ Criou página de gerenciamento de ingredientes
- ✅ Implementou feedback visual com toasts

---

## Próximo Passo

Agora vamos finalizar o projeto com testes, melhorias de UX e deploy!

**➡️ Próximo:** [Módulo 09 - Integração Final e Deploy](09-integracao-final.md)

---

## Dicas Importantes

💡 **Arrays dinâmicos** use `map` e `filter` para manipular

💡 **Validações** sempre faça no frontend E no backend

💡 **UX** use loading states e mensagens claras

💡 **Componentização** reutilize ao máximo os componentes
