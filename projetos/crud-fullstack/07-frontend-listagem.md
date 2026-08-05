# Módulo 07 - Frontend: Listagem de Receitas

Neste módulo, você vai criar os componentes de listagem de receitas, incluindo cards estilizados, filtros por categoria, busca por nome e modal de detalhes.

## Objetivos do Módulo

- ✅ Criar componente ReceitaCard com Tailwind
- ✅ Criar componente ReceitaLista com filtros
- ✅ Implementar busca por nome
- ✅ Implementar filtro por categoria
- ✅ Criar modal de detalhes da receita
- ✅ Adicionar loading states e estados vazios
- ✅ Implementar função de deletar

---

## 1. Criando o Card de Receita

### Crie o arquivo `src/components/ReceitaCard.jsx`:

```javascript
'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ReceitaCard({ receita, onDelete }) {
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async (e) => {
        e.preventDefault();
        
        if (!confirm(`Tem certeza que deseja deletar a receita "${receita.nome}"?`)) {
            return;
        }

        setIsDeleting(true);
        try {
            await onDelete(receita.id);
        } catch (error) {
            setIsDeleting(false);
        }
    };

    // Define cor do badge por categoria
    const getCategoriaStyle = (categoria) => {
        const estilos = {
            'Sobremesa': 'bg-pink-100 text-pink-800 border-pink-200',
            'Prato Principal': 'bg-green-100 text-green-800 border-green-200',
            'Entrada': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'Lanche': 'bg-blue-100 text-blue-800 border-blue-200',
            'Bebida': 'bg-purple-100 text-purple-800 border-purple-200'
        };
        return estilos[categoria] || 'bg-gray-100 text-gray-800 border-gray-200';
    };

    // Define emoji por categoria
    const getCategoriaEmoji = (categoria) => {
        const emojis = {
            'Sobremesa': '🍰',
            'Prato Principal': '🍽️',
            'Entrada': '🥗',
            'Lanche': '🥪',
            'Bebida': '🥤'
        };
        return emojis[categoria] || '🍴';
    };

    return (
        <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group">
            {/* Imagem placeholder com gradiente */}
            <div className="h-48 bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 flex items-center justify-center relative overflow-hidden">
                <span className="text-6xl group-hover:scale-110 transition-transform duration-300">
                    {getCategoriaEmoji(receita.categoria)}
                </span>
                
                {/* Overlay com gradiente no hover */}
                <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
            </div>

            <div className="p-5">
                {/* Badge de Categoria */}
                <div className="mb-3">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border ${getCategoriaStyle(receita.categoria)}`}>
                        {receita.categoria}
                    </span>
                </div>

                {/* Nome da Receita */}
                <h3 className="text-xl font-bold text-gray-800 mb-3 line-clamp-2 group-hover:text-purple-600 transition-colors">
                    {receita.nome}
                </h3>

                {/* Informações */}
                <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                        <span>⏱️</span>
                        <span>{receita.tempo_preparo} min</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <span>🍽️</span>
                        <span>{receita.rendimento}</span>
                    </div>
                </div>

                {/* Ingredientes Resumo */}
                {receita.ingredientes_resumo && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        <strong className="text-gray-700">Ingredientes:</strong>{' '}
                        {receita.ingredientes_resumo}
                    </p>
                )}

                {/* Botões de Ação */}
                <div className="flex gap-2 pt-4 border-t border-gray-100">
                    <Link
                        href={`/receitas/${receita.id}`}
                        className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-center py-2 px-4 rounded-lg font-medium transition-colors duration-200"
                    >
                        Ver Detalhes
                    </Link>
                    
                    <Link
                        href={`/receitas/editar/${receita.id}`}
                        className="bg-gray-100 hover:bg-gray-200 text-gray-700 p-2 rounded-lg transition-colors duration-200"
                        title="Editar receita"
                    >
                        ✏️
                    </Link>
                    
                    <button
                        onClick={handleDelete}
                        disabled={isDeleting}
                        className="bg-red-50 hover:bg-red-100 text-red-600 p-2 rounded-lg transition-colors duration-200 disabled:opacity-50"
                        title="Deletar receita"
                    >
                        {isDeleting ? '⏳' : '🗑️'}
                    </button>
                </div>
            </div>
        </div>
    );
}
```

**Explicação dos recursos do card:**

**1. Gradiente dinâmico:**
```javascript
className="h-48 bg-gradient-to-br from-purple-400 via-pink-500 to-red-500"
```
- Gradiente diagonal com 3 cores
- `h-48`: Altura fixa de 12rem (192px)

**2. Animações no hover:**
```javascript
className="group-hover:scale-110 transition-transform duration-300"
```
- `group-hover`: Ativa quando o mouse passa no card pai
- `scale-110`: Aumenta em 10%

**3. Line clamp (truncar texto):**
```javascript
className="line-clamp-2"
```
- Limita o texto a 2 linhas
- Adiciona "..." automaticamente

---

## 2. Criando a Lista de Receitas

### Crie o arquivo `src/components/ReceitaLista.jsx`:

```javascript
'use client';

import { useState, useEffect } from 'react';
import { receitasService } from '@/services/api';
import toast from 'react-hot-toast';
import ReceitaCard from './ReceitaCard';

export default function ReceitaLista() {
    const [receitas, setReceitas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filtroCategoria, setFiltroCategoria] = useState('');
    const [busca, setBusca] = useState('');
    const [termoBusca, setTermoBusca] = useState('');

    // Categorias disponíveis
    const categorias = [
        'Sobremesa',
        'Prato Principal',
        'Entrada',
        'Lanche',
        'Bebida'
    ];

    // Carrega receitas ao montar o componente
    useEffect(() => {
        carregarReceitas();
    }, []);

    // Função para carregar todas as receitas
    const carregarReceitas = async () => {
        try {
            setLoading(true);
            const response = await receitasService.listarTodas();
            setReceitas(response.data || []);
            setFiltroCategoria('');
            setTermoBusca('');
        } catch (error) {
            console.error('Erro ao carregar receitas:', error);
            toast.error('Erro ao carregar receitas');
        } finally {
            setLoading(false);
        }
    };

    // Função para deletar receita
    const handleDelete = async (id) => {
        try {
            await receitasService.deletar(id);
            toast.success('Receita deletada com sucesso!');
            
            // Remove da lista sem recarregar
            setReceitas(receitas.filter(r => r.id !== id));
        } catch (error) {
            console.error('Erro ao deletar receita:', error);
            toast.error(error.response?.data?.message || 'Erro ao deletar receita');
        }
    };

    // Função para filtrar por categoria
    const handleFiltrarCategoria = async (categoria) => {
        setFiltroCategoria(categoria);
        setBusca('');
        setTermoBusca('');
        
        if (categoria === '') {
            carregarReceitas();
            return;
        }

        try {
            setLoading(true);
            const response = await receitasService.filtrarPorCategoria(categoria);
            setReceitas(response.data || []);
        } catch (error) {
            console.error('Erro ao filtrar receitas:', error);
            toast.error('Erro ao filtrar receitas');
        } finally {
            setLoading(false);
        }
    };

    // Função para buscar por nome
    const handleBuscar = async (e) => {
        e.preventDefault();
        
        const termo = busca.trim();
        
        if (!termo) {
            carregarReceitas();
            return;
        }

        try {
            setLoading(true);
            setFiltroCategoria('');
            setTermoBusca(termo);
            const response = await receitasService.buscarPorNome(termo);
            setReceitas(response.data || []);
        } catch (error) {
            console.error('Erro ao buscar receitas:', error);
            toast.error('Erro ao buscar receitas');
        } finally {
            setLoading(false);
        }
    };

    // Função para limpar filtros
    const limparFiltros = () => {
        setBusca('');
        setTermoBusca('');
        setFiltroCategoria('');
        carregarReceitas();
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Cabeçalho */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">
                    🍳 Minhas Receitas
                </h1>
                <p className="text-gray-600">
                    Explore e gerencie suas receitas culinárias favoritas
                </p>
            </div>

            {/* Barra de Filtros e Busca */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <div className="grid md:grid-cols-2 gap-4">
                    {/* Busca por Nome */}
                    <div>
                        <label className="label">
                            🔍 Buscar por nome
                        </label>
                        <form onSubmit={handleBuscar} className="flex gap-2">
                            <input
                                type="text"
                                placeholder="Digite o nome da receita..."
                                value={busca}
                                onChange={(e) => setBusca(e.target.value)}
                                className="input-field flex-1"
                            />
                            <button
                                type="submit"
                                className="btn-primary px-6"
                            >
                                Buscar
                            </button>
                        </form>
                    </div>

                    {/* Filtro por Categoria */}
                    <div>
                        <label className="label">
                            🏷️ Filtrar por categoria
                        </label>
                        <select
                            value={filtroCategoria}
                            onChange={(e) => handleFiltrarCategoria(e.target.value)}
                            className="input-field"
                        >
                            <option value="">Todas as categorias</option>
                            {categorias.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Indicador de Filtro Ativo */}
                {(filtroCategoria || termoBusca) && (
                    <div className="mt-4 flex items-center gap-2 flex-wrap">
                        <span className="text-sm text-gray-600">Filtros ativos:</span>
                        {termoBusca && (
                            <span className="inline-flex items-center gap-2 bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                                Busca: "{termoBusca}"
                            </span>
                        )}
                        {filtroCategoria && (
                            <span className="inline-flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                Categoria: {filtroCategoria}
                            </span>
                        )}
                        <button
                            onClick={limparFiltros}
                            className="text-sm text-red-600 hover:text-red-700 underline"
                        >
                            Limpar filtros
                        </button>
                    </div>
                )}
            </div>

            {/* Loading State */}
            {loading && (
                <div className="flex flex-col items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
                    <p className="text-gray-600">Carregando receitas...</p>
                </div>
            )}

            {/* Grid de Receitas */}
            {!loading && receitas.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
                    {receitas.map(receita => (
                        <ReceitaCard
                            key={receita.id}
                            receita={receita}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            {/* Estado Vazio */}
            {!loading && receitas.length === 0 && (
                <div className="text-center py-20">
                    <div className="text-6xl mb-4">📭</div>
                    <h3 className="text-2xl font-semibold text-gray-800 mb-2">
                        Nenhuma receita encontrada
                    </h3>
                    <p className="text-gray-600 mb-6">
                        {termoBusca || filtroCategoria
                            ? 'Tente ajustar os filtros de busca ou limpar os filtros.'
                            : 'Comece criando sua primeira receita!'}
                    </p>
                    {!termoBusca && !filtroCategoria && (
                        <a
                            href="/receitas/novo"
                            className="inline-block btn-primary"
                        >
                            ➕ Criar Primeira Receita
                        </a>
                    )}
                </div>
            )}

            {/* Contador de Resultados */}
            {!loading && receitas.length > 0 && (
                <div className="mt-8 text-center text-gray-600">
                    <p>
                        Exibindo <strong>{receitas.length}</strong> receita{receitas.length !== 1 ? 's' : ''}
                        {termoBusca && ` para "${termoBusca}"`}
                        {filtroCategoria && ` na categoria "${filtroCategoria}"`}
                    </p>
                </div>
            )}
        </div>
    );
}
```

---

## 3. Atualizando a Página Principal

### Edite `src/app/page.js` para usar a lista:

```javascript
import ReceitaLista from '@/components/ReceitaLista';

export default function Home() {
  return <ReceitaLista />;
}
```

**Muito mais simples!** A página principal agora apenas renderiza o componente de lista.

---

## 4. Criando a Página de Detalhes

### Crie a pasta e arquivo `src/app/receitas/[id]/page.js`:

```bash
mkdir -p src/app/receitas/\[id\]
```

### Adicione o conteúdo:

```javascript
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { receitasService } from '@/services/api';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function ReceitaDetalhes() {
    const params = useParams();
    const router = useRouter();
    const [receita, setReceita] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        carregarReceita();
    }, [params.id]);

    const carregarReceita = async () => {
        try {
            setLoading(true);
            const response = await receitasService.buscarPorId(params.id);
            setReceita(response.data);
        } catch (error) {
            console.error('Erro ao carregar receita:', error);
            toast.error('Erro ao carregar receita');
            router.push('/');
        } finally {
            setLoading(false);
        }
    };

    const handleDeletar = async () => {
        if (!confirm(`Tem certeza que deseja deletar "${receita.nome}"?`)) {
            return;
        }

        try {
            await receitasService.deletar(params.id);
            toast.success('Receita deletada com sucesso!');
            router.push('/');
        } catch (error) {
            console.error('Erro ao deletar:', error);
            toast.error('Erro ao deletar receita');
        }
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-20 flex justify-center items-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600"></div>
            </div>
        );
    }

    if (!receita) {
        return null;
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            {/* Botão Voltar */}
            <Link
                href="/"
                className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-6"
            >
                <span>←</span> Voltar para lista
            </Link>

            {/* Card da Receita */}
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                {/* Cabeçalho com Gradiente */}
                <div className="h-64 bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 flex items-center justify-center relative">
                    <span className="text-9xl">🍽️</span>
                </div>

                {/* Conteúdo */}
                <div className="p-8">
                    {/* Categoria */}
                    <div className="mb-4">
                        <span className="inline-block px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold border border-purple-200">
                            {receita.categoria}
                        </span>
                    </div>

                    {/* Nome */}
                    <h1 className="text-4xl font-bold text-gray-800 mb-4">
                        {receita.nome}
                    </h1>

                    {/* Informações Básicas */}
                    <div className="flex flex-wrap gap-6 mb-8 pb-6 border-b border-gray-200">
                        <div className="flex items-center gap-2 text-gray-700">
                            <span className="text-2xl">⏱️</span>
                            <div>
                                <p className="text-sm text-gray-500">Tempo de Preparo</p>
                                <p className="font-semibold">{receita.tempo_preparo} minutos</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                            <span className="text-2xl">🍽️</span>
                            <div>
                                <p className="text-sm text-gray-500">Rendimento</p>
                                <p className="font-semibold">{receita.rendimento}</p>
                            </div>
                        </div>
                    </div>

                    {/* Ingredientes */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                            <span>🥕</span> Ingredientes
                        </h2>
                        <div className="bg-gray-50 rounded-lg p-6">
                            <ul className="space-y-3">
                                {receita.ingredientes && receita.ingredientes.map((ing, index) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <span className="text-purple-600 mt-1">•</span>
                                        <span className="text-gray-700">
                                            <strong>{ing.quantidade} {ing.unidade_medida}</strong> de {ing.nome}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Modo de Preparo */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                            <span>👨‍🍳</span> Modo de Preparo
                        </h2>
                        <div className="bg-gray-50 rounded-lg p-6">
                            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                                {receita.modo_preparo}
                            </p>
                        </div>
                    </div>

                    {/* Botões de Ação */}
                    <div className="flex gap-3 pt-6 border-t border-gray-200">
                        <Link
                            href={`/receitas/editar/${receita.id}`}
                            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-center py-3 px-6 rounded-lg font-medium transition-colors"
                        >
                            ✏️ Editar Receita
                        </Link>
                        <button
                            onClick={handleDeletar}
                            className="bg-red-50 hover:bg-red-100 text-red-600 py-3 px-6 rounded-lg font-medium transition-colors"
                        >
                            🗑️ Deletar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
```

---

## 5. Testando a Aplicação

### Passo 1: Certifique-se de que o backend está rodando

```bash
cd crud-receitas/backend
npm run dev
```

### Passo 2: Inicie o Next.js

```bash
cd crud-receitas/frontend
npm run dev
```

### Passo 3: Teste as funcionalidades

Acesse [http://localhost:3000](http://localhost:3000) e teste:

**✅ Listagem:**
- Cards de receitas aparecem em grid
- Gradientes coloridos nos cards

**✅ Filtros:**
- Selecione uma categoria
- Digite um nome e busque
- Limpe os filtros

**✅ Detalhes:**
- Clique em "Ver Detalhes"
- Veja ingredientes e modo de preparo
- Volte para a lista

**✅ Deletar:**
- Clique no ícone de lixeira
- Confirme a exclusão
- Receita some da lista

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou cards de receitas com gradientes e animações
- ✅ Implementou listagem com grid responsivo
- ✅ Adicionou filtros por categoria
- ✅ Implementou busca por nome
- ✅ Criou página de detalhes completa
- ✅ Implementou função de deletar
- ✅ Adicionou loading states e estados vazios
- ✅ Usou Tailwind para estilização moderna

---

## Próximo Passo

Agora vamos criar o formulário dinâmico para adicionar e editar receitas com múltiplos ingredientes!

**➡️ Próximo:** [Módulo 08 - Frontend: Formulário de Receitas](08-frontend-formulario.md)

---

## Dicas Importantes

💡 **Grid responsivo** com `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

💡 **Gradientes** ficam lindos com `bg-gradient-to-br from-X via-Y to-Z`

💡 **`line-clamp-2`** trunca texto em 2 linhas automaticamente

💡 **`whitespace-pre-line`** preserva quebras de linha do texto
