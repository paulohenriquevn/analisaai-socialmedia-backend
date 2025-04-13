## ✅ **Backlog de Histórias de Usuário – Frontend**

---

### 📊 **Épico 1: Dashboard de Métricas Básicas**

#### **Título**: Como **influenciador digital**, quero **ver minhas principais métricas em cards e gráficos interativos** para **acompanhar meu desempenho diário**.  
**Descrição**: O painel inicial deve exibir métricas de engajamento, alcance e crescimento em cards com destaque visual. Gráficos devem ser interativos e responsivos.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário acessa o dashboard,  
  **Quando** ele entra na aba "Visão Geral",  
  **Então** deve visualizar cards com métricas de Engajamento, Alcance e Crescimento.  
- **Dado** que existem mais de 500 registros,  
  **Quando** os dados são carregados,  
  **Então** a renderização dos gráficos deve ocorrer em até 2 segundos.  
- **Dado** um clique em um card,  
  **Quando** o usuário interage,  
  **Então** deve ser redirecionado para a análise detalhada daquela métrica.

---

### 💬 **Épico 2: Visualização de Análise de Sentimentos**

#### **Título**: Como **gerente de marketing**, quero **visualizar a análise de sentimentos dos comentários em um gráfico de pizza e lista detalhada**, para **entender a percepção da audiência**.  
**Descrição**: Mostrar distribuição entre sentimentos positivos, neutros e negativos. Ao clicar em uma fatia, exibir exemplos de comentários com destaque das palavras-chave.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o gráfico de sentimentos foi carregado,  
  **Quando** o usuário clica em uma categoria (ex: negativo),  
  **Então** deve visualizar os comentários associados àquela categoria.  
- **Dado** que o gráfico exibe os dados,  
  **Quando** o usuário passa o cursor sobre uma fatia,  
  **Então** deve aparecer um tooltip com percentual e volume.  
- **Dado** uma tela menor que 480px,  
  **Quando** o gráfico é exibido,  
  **Então** ele deve adaptar para visualização vertical.

---

### 📈 **Épico 3: Comparativo de Benchmarking**

#### **Título**: Como **gerente de marketing**, quero **comparar meus dados com os de concorrentes diretos** para **avaliar meu posicionamento no mercado**.  
**Descrição**: Permitir selecionar até 3 perfis para comparação. Exibir gráfico de barras com Engajamento, Alcance e Crescimento lado a lado.  
**Prioridade**: Should Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário seleciona influenciadores no filtro,  
  **Quando** clica em "Comparar",  
  **Então** deve aparecer um gráfico de barras com cores distintas.  
- **Dado** que há mais de três perfis selecionados,  
  **Quando** o usuário tenta comparar,  
  **Então** uma mensagem de erro deve orientar a reduzir a seleção.  
- **Dado** que a comparação é exibida,  
  **Quando** o usuário clica sobre uma barra,  
  **Então** um tooltip deve exibir os valores exatos das métricas.

---

### 📄 **Épico 4: Customização de Relatórios**

#### **Título**: Como **administrador da plataforma**, quero **personalizar relatórios com logotipo e identidade visual** para **entregar documentos profissionais aos clientes**.  
**Descrição**: Permitir upload de logotipo, escolha de cores, seleção de KPIs e geração de relatórios em PDF.  
**Prioridade**: Should Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário acessa o menu de personalização,  
  **Quando** realiza o upload de um logo,  
  **Então** ele deve ser exibido em pré-visualização do relatório.  
- **Dado** que o relatório foi personalizado,  
  **Quando** o botão "Gerar PDF" é clicado,  
  **Então** o arquivo deve ser gerado com as configurações visuais escolhidas.  
- **Dado** que a identidade visual foi definida,  
  **Quando** um novo relatório é exportado,  
  **Então** ele deve manter a mesma identidade até alteração manual.

---

### ♿ **Épico 5: Acessibilidade e Responsividade**

#### **Título**: Como **usuário com deficiência visual**, quero **navegar pelo sistema usando teclado e leitores de tela**, para **ter uma experiência de uso inclusiva**.  
**Descrição**: Todos os elementos devem ter foco navegável, alt text e labels descritivas. Deve seguir as diretrizes WCAG 2.1 AA.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário usa apenas o teclado,  
  **Quando** navega entre os componentes,  
  **Então** o foco deve ser visível e a navegação funcional.  
- **Dado** um leitor de tela ativo,  
  **Quando** o cursor foca em um botão ou card,  
  **Então** o elemento deve ser descrito corretamente.  
- **Dado** que o contraste de cores é necessário,  
  **Quando** o usuário alterna para o modo escuro,  
  **Então** todos os textos devem permanecer legíveis.

---

