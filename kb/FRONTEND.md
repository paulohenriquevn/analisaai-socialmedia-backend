Você é responsável por desenvolver a interface do usuário (UI/UX) do ** Analisa.ai - Social Media**, uma plataforma de análise de redes sociais que utiliza IA para avaliar influenciadores. O sistema precisa ser escalável, seguro e integrável com APIs de redes sociais (Instagram, TikTok, Facebook), além de processar grandes volumes de dados em tempo quase real.

Além disso, o backend deve ser capaz de considerar as características do público-alvo de cada influenciador, como faixa etária, interesses, localização e perfil de consumo. Isso garantirá que os insights gerados sejam contextualizados e mais relevantes para os objetivos de marketing e comunicação das marcas que utilizam a plataforma.


---

### **Diretrizes Técnicas**  
1. **Tecnologias Principais**:  
   - **Framework**: Angular.  
   - **Visualização de Dados**: apexcharts.  
   - **Estilização**: Tailwind CSS.  

2. **Tarefas Prioritárias**:  
   - **Painel de Controle Interativo**:  
     - Gráficos dinâmicos (ex: linha para crescimento de seguidores, pizza para distribuição de engajamento).  
     - Filtros por período, plataforma e tipo de conteúdo (ex: vídeos, posts, stories).  
   - **Integração com Backend**:  
     - Consumo de APIs RESTful para buscar métricas em tempo real.  
     - Exemplo de chamada para dados de engajamento:  
       ```typescript  
       const fetchEngagementData = async (influencerId: string) => {  
         const response = await axios.get(`/api/engagement/${influencerId}`);  
         return response.data;  
       };  
       ```  
   - **Responsividade**:  
     - Garantir compatibilidade com dispositivos móveis (ex: tabelas scrolláveis em telas pequenas).  

3. **Componentes Reutilizáveis**:  
   - Criar um componente `<MetricCard>` para exibir KPIs (ex: "Engajamento: 8,5%", "Alcance: 1,2M").  
---

### **Requisitos de UI/UX**  
1. **Design System**:  
   - Seguir o Figma fornecido pela equipe de design.  
   - Cores primárias: `primary: 265 83% 45%;` (roxo institucional), `#FF6B6B` (destaque para alertas).  
2. **Acessibilidade**:  
   - Garantir contrastes adequados (WCAG AA).  
   - Suporte a navegação por teclado e leitores de tela.  
3. **Microinterações**:  
   - Animações suaves ao filtrar dados ou carregar gráficos.  
   - Tooltips em gráficos para detalhar métricas específicas.  

---

### **Entregáveis Esperados**  
   - Painel com gráficos básicos (engajamento, alcance) e lista de posts recentes.  
   - Integração com API do Instagram.  
   - Dashboard comparativo (benchmarking com concorrentes).  
   - Modo escuro e exportação de relatórios em PDF.  

---

### **Desafios Técnicos**  
- **Problema**: Atualização em tempo real de métricas sem sobrecarregar a API.  
  - **Solução**: Usar WebSocket ou polling inteligente (ex: atualizar a cada 30s).  
- **Problema**: Renderização de grandes datasets em gráficos sem lag.  
  - **Solução**: Paginação ou agregação de dados no backend antes do envio.  
--
**Instrução Final**:  
Apresente uma proposta de arquitetura frontend, lista de componentes prioritários e cronograma para as primeiras 4 semanas. Justifique escolhas (ex: React vs. Angular) com base em escalabilidade e ecossistema.