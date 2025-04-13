## 📊 ÉPICO 1 – Dashboard de Métricas Básicas

### 🧩 História 1.2  
#### **Título**: Como **influenciador**, quero **aplicar filtros por período e plataforma** para **personalizar minha visão de desempenho**.  
**Descrição**: Filtros responsivos e persistentes. Deve atualizar os gráficos e cards dinamicamente.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário seleciona "Últimos 7 dias" e "Instagram",  
  **Quando** aplica os filtros,  
  **Então** todas as métricas devem refletir os dados filtrados.  
- **Dado** que há um gráfico carregado,  
  **Quando** muda a plataforma,  
  **Então** o gráfico deve ser atualizado sem recarregar a página.

**Tarefas Técnicas**:  
- [ ] Criar componente `<DatePlatformFilter>` com dropdown e calendário.  
- [ ] Integrar filtros com API `/api/metrics?start=...&end=...&platform=...`.  
- [ ] Aplicar debounce para evitar múltiplas requisições seguidas.  
- [ ] Testar atualização automática dos gráficos e cards ao alterar filtros.

---

## 💬 ÉPICO 2 – Visualização de Análise de Sentimentos

### 🧩 História 2.2  
#### **Título**: Como **gerente de marketing**, quero **acessar comentários categorizados por sentimento** para **entender o porquê da polaridade**.  
**Descrição**: Após seleção de uma fatia do gráfico, uma lista de comentários deve ser exibida, com destaque para palavras-chave positivas/negativas.  
**Prioridade**: Should Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário clica em “Sentimento Positivo”,  
  **Quando** os comentários são exibidos,  
  **Então** palavras positivas devem aparecer realçadas (ex: "incrível", "amei").  
- **Dado** que um comentário possui emojis,  
  **Quando** ele for renderizado,  
  **Então** os emojis devem ser exibidos corretamente em todos dispositivos.

**Tarefas Técnicas**:  
- [ ] Criar componente `<CommentList>` com destaque semântico.  
- [ ] Aplicar expressão regular para identificar termos positivos/negativos.  
- [ ] Criar fallback para emojis não suportados por fontes locais.  
- [ ] Validar carregamento em menos de 2 segundos com 100 comentários.

---

## 📈 ÉPICO 3 – Comparativo de Benchmarking

### 🧩 História 3.2  
#### **Título**: Como **gerente**, quero **salvar comparações frequentes** para **não precisar refazer a seleção toda vez**.  
**Descrição**: Permitir salvar conjuntos de perfis para benchmarking com nome personalizado.  
**Prioridade**: Could Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário compara perfis,  
  **Quando** clica em “Salvar Comparação”,  
  **Então** deve informar um nome e salvar nos favoritos.  
- **Dado** que um conjunto salvo é acessado,  
  **Quando** ele é selecionado,  
  **Então** a comparação deve ser carregada com todos os parâmetros salvos.

**Tarefas Técnicas**:  
- [ ] Criar componente `<SavedComparisonSelector>` com autocomplete.  
- [ ] Criar endpoint `POST /api/comparisons/save`.  
- [ ] Salvar configurações localmente (localStorage) para fallback offline.  
- [ ] Testar carregamento correto dos perfis e métricas salvas.

---

## 📄 ÉPICO 4 – Customização de Relatórios

### 🧩 História 4.2  
#### **Título**: Como **administrador**, quero **escolher quais seções exibir no relatório PDF** para **personalizar a entrega ao cliente**.  
**Descrição**: Checkboxes para incluir/excluir seções (sentimentos, engajamento, etc.).  
**Prioridade**: Should Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário acessa a aba "Gerar Relatório",  
  **Quando** seleciona/desmarca uma seção,  
  **Então** a visualização deve refletir a seleção.  
- **Dado** que o PDF é gerado,  
  **Quando** as seções foram personalizadas,  
  **Então** ele deve conter apenas as seções marcadas.

**Tarefas Técnicas**:  
- [ ] Criar componente `<ReportSectionSelector>` com checkboxes.  
- [ ] Integrar com gerador de PDF (ex: jsPDF ou Puppeteer).  
- [ ] Garantir visualização prévia antes da exportação.  
- [ ] Criar testes unitários para diferentes combinações de seções.

---

## ♿ ÉPICO 5 – Acessibilidade e Responsividade

### 🧩 História 5.2  
#### **Título**: Como **usuário mobile**, quero **acessar gráficos em modo retrato** para **visualizar dados com clareza em telas pequenas**.  
**Descrição**: Os gráficos devem se adaptar com legendas reduzidas, tooltips maiores e colunas empilhadas.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que a largura da tela é inferior a 480px,  
  **Quando** o gráfico é carregado,  
  **Então** ele deve se reformatar automaticamente.  
- **Dado** que o usuário toca no gráfico,  
  **Quando** ele segura o toque,  
  **Então** o tooltip deve exibir informações detalhadas com fonte maior.

**Tarefas Técnicas**:  
- [ ] Implementar breakpoint em `<ChartWrapper>` usando Tailwind (`sm`, `md`, `lg`).  
- [ ] Testar layout responsivo com apexcharts para coluna empilhada.  
- [ ] Ajustar fonte e hitbox dos tooltips para mobile.  
- [ ] Validar no navegador com emulação de iPhone SE e Galaxy S.

---

## ✅ Checklist de Tarefas Globais

- [ ] Garantir performance com **lazy loading** de componentes.  
- [ ] Implementar loading skeletons com animação (`animate-pulse`).  
- [ ] Criar componente `<DataTooltip>` reutilizável.  
- [ ] Realizar testes de acessibilidade com Lighthouse e axe-core.  

---
