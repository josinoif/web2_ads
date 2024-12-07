### Introdução ao `useMemo`

O `useMemo` é um hook do React projetado para otimizar o desempenho de componentes funcionais, memorizando valores computados e garantindo que cálculos caros sejam reexecutados apenas quando suas dependências mudarem. Em aplicações React, funções de renderização são chamadas frequentemente, e isso pode ser custoso quando há operações intensivas, como cálculos matemáticos, filtragem de listas ou processamento de grandes conjuntos de dados.

Antes do `useMemo`, o React não fornecia uma forma nativa de evitar a recomputação de valores entre renderizações, o que frequentemente resultava em código menos eficiente. O `useMemo` resolve esse problema ao armazenar em cache os resultados de cálculos, garantindo que eles só sejam recalculados quando necessário.

---

### **Vantagens e Desvantagens de Usar o `useMemo`**

#### **Vantagens:**
1. **Evita Recomputação Desnecessária**: Reduz o custo computacional ao reutilizar valores memorizados.
2. **Melhora o Desempenho**: Ideal para operações intensivas, como cálculos complexos ou manipulação de grandes listas.
3. **Integração Natural**: Funciona perfeitamente em componentes funcionais e pode ser combinado com outros hooks, como `useCallback`.
4. **Facilidade de Implementação**: A API é simples e intuitiva, tornando sua aplicação direta.

#### **Desvantagens:**
1. **Sobrecarga de Memorização**: Em alguns casos, o custo de memorização pode ser maior do que o custo de recomputação, especialmente para operações simples.
2. **Complexidade Desnecessária**: Pode adicionar complexidade em cenários onde o impacto de reprocessar dados é mínimo.
3. **Dependências Incorretas**: Um uso inadequado de dependências pode levar a bugs ou comportamento inesperado.

---

### **Casos de Uso Comuns do `useMemo`**

1. **Filtragem de Listas**: Otimizar a exibição de listas filtradas.
   ```jsx
   import React, { useState, useMemo } from "react";

   const FilteredList = () => {
     const [filter, setFilter] = useState("");
     const [items] = useState(["apple", "banana", "cherry", "date", "elderberry"]);

     const filteredItems = useMemo(() => {
       return items.filter((item) => item.toLowerCase().includes(filter.toLowerCase()));
     }, [filter, items]);

     return (
       <div>
         <input
           type="text"
           placeholder="Filter items"
           value={filter}
           onChange={(e) => setFilter(e.target.value)}
         />
         <ul>
           {filteredItems.map((item, index) => (
             <li key={index}>{item}</li>
           ))}
         </ul>
       </div>
     );
   };

   export default FilteredList;
   ```

2. **Cálculos Intensivos**: Prevenir cálculos repetidos em operações pesadas.
   ```jsx
   import React, { useState, useMemo } from "react";

   const ExpensiveCalculation = ({ num }) => {
     console.log("Calculating...");
     return num ** 2; // Simulação de operação cara
   };

   const CalculationComponent = () => {
     const [number, setNumber] = useState(0);

     const squared = useMemo(() => ExpensiveCalculation({ num: number }), [number]);

     return (
       <div>
         <input
           type="number"
           value={number}
           onChange={(e) => setNumber(Number(e.target.value))}
         />
         <p>Result: {squared}</p>
       </div>
     );
   };

   export default CalculationComponent;
   ```

3. **Otimização de Renderização**: Garantir que objetos ou listas criados em tempo de renderização não sejam recriados desnecessariamente.
   ```jsx
   import React, { useState, useMemo } from "react";

   const RenderOptimization = () => {
     const [count, setCount] = useState(0);

     const memoizedObject = useMemo(() => {
       return { value: count };
     }, [count]);

     return (
       <div>
         <button onClick={() => setCount((prev) => prev + 1)}>Increment</button>
         <ChildComponent object={memoizedObject} />
       </div>
     );
   };

   const ChildComponent = React.memo(({ object }) => {
     console.log("Child re-rendered");
     return <p>Value: {object.value}</p>;
   });

   export default RenderOptimization;
   ```

4. **Formatação de Dados**: Transformar ou formatar dados antes de exibir.
   ```jsx
   import React, { useState, useMemo } from "react";

   const FormattedList = () => {
     const [data] = useState([1000, 2000, 3000]);

     const formattedData = useMemo(() => {
       return data.map((num) => `$${num.toFixed(2)}`);
     }, [data]);

     return (
       <ul>
         {formattedData.map((item, index) => (
           <li key={index}>{item}</li>
         ))}
       </ul>
     );
   };

   export default FormattedList;
   ```

---

### **Conclusão**

O `useMemo` é uma ferramenta poderosa para otimizar a performance de aplicações React, garantindo que cálculos e transformações de dados sejam feitos de maneira eficiente. Ele é especialmente útil em cenários com operações custosas ou renderizações frequentes. No entanto, seu uso deve ser avaliado caso a caso, já que memorização excessiva pode adicionar complexidade desnecessária. Bem utilizado, o `useMemo` é indispensável para manter o desempenho em aplicações React modernas.