### **Histórias de Usuário para a Landing Page do Analisa.ai**

---

#### **📌 Épico 6: Landing Page de Conversão**  
**Objetivo**: Criar uma landing page persuasiva com área freemium para gerar leads qualificados e impulsionar vendas dos planos Pro e Premium.  

---

### **História 6.1 – Avaliação Freemium de Score Social**  
**Título**: Como **usuário visitante**, quero **avaliar meu perfil de rede social gratuitamente** para **entender meu potencial antes de comprar a versão paga**.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário insere um link de perfil (ex: Instagram),  
  **Quando** clica em "Gerar Score Gratuito",  
  **Então** o sistema deve calcular e exibir o score usando a fórmula base (engajamento, alcance, crescimento, sentimento).  
- **Dado** que o score é exibido,  
  **Quando** o usuário rola a página,  
  **Então** deve ver um comparativo destacando recursos exclusivos do plano Premium (ex: "No Premium, veja análises detalhadas por post").  
- **Dado** que o score é inferior a 50/100,  
  **Quando** a página é carregada,  
  **Então** exibir uma mensagem motivacional com CTA personalizado (ex: "Eleve seu engajamento com nossas dicas Pro!").  

**Tarefas Técnicas**:  
- [ ] Criar componente `<ScoreCalculator>` integrado à API `/api/freemium-score`.  
- [ ] Implementar validação de URLs de redes sociais (regex para Instagram/TikTok).  
- [ ] Adicionar skeleton loading durante o cálculo do score.  
- [ ] Desenvolver modal de upsell após exibição do score.  

---

### **História 6.2 – Comparação Persuasiva de Planos**  
**Título**: Como **usuário indeciso**, quero **comparar recursos dos planos Freemium, Pro e Premium** para **escolher a melhor opção para minhas necessidades**.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário acessa a seção de planos,  
  **Quando** passa o cursor sobre o card "Premium",  
  **Então** deve ver um destaque visual (ex: borda roxa animada) e selo "Mais Popular".  
- **Dado** que o usuário está em mobile,  
  **Quando** visualiza a tabela de comparação,  
  **Então** deve poder rolar horizontalmente para ver todas as colunas.  
- **Dado** que o usuário clica em "Assinar Pro",  
  **Então** deve ser redirecionado para um checkout pré-preenchido com o plano selecionado.  

**Tarefas Técnicas**:  
- [ ] Criar componente `<PlanComparisonTable>` com toggle anual/mensal.  
- [ ] Implementar hover effects usando Tailwind CSS (ex: `group-hover:scale-105`).  
- [ ] Integrar com API de checkout (ex: Stripe) para redirecionamento.  
- [ ] Garantir responsividade com overflow-x em mobile.  

---

### **História 6.3 – Seção de Social Proof com Cases de Sucesso**  
**Título**: Como **usuário cético**, quero **ver depoimentos e resultados reais de clientes** para **confiar na eficácia da plataforma**.  
**Prioridade**: Should Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário rola até a seção de cases,  
  **Quando** os cards são exibidos,  
  **Então** deve haver autoplay de vídeos curtos (15s) com depoimentos.  
- **Dado** que um case inclui métricas,  
  **Quando** o usuário clica em "Ver Detalhes",  
  **Então** deve expandir um gráfico de crescimento pós-uso da plataforma.  
- **Dado** que o usuário está logado como visitante,  
  **Quando** vê os cases,  
  **Então** deve aparecer um CTA flutuante: "Comece seu teste grátis e seja nosso próximo case!".  

**Tarefas Técnicas**:  
- [ ] Criar componente `<CaseStudyCarousel>` com suporte a vídeos (YouTube/Vimeo).  
- [ ] Implementar lazy loading para imagens e vídeos.  
- [ ] Desenvolver overlay de CTA flutuante com `position: sticky`.  

---

### **História 6.4 – Copywriting Otimizado para Conversão**  
**Título**: Como **empresa**, quero **textos persuasivos e claros na landing page** para **aumentar a taxa de conversão de visitantes em leads**.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que o usuário lê o cabeçalho,  
  **Quando** a página é carregada,  
  **Então** deve ver uma headline com verbo de ação (ex: "Aumente seu engajamento em 300% com IA").  
- **Dado** que o usuário interage com a seção freemium,  
  **Quando** insere um email,  
  **Então** deve receber um ebook gratuito via email com título "5 Estratégias para Bombar nas Redes".  
- **Dado** que o usuário abandona a página,  
  **Quando** tenta sair,  
  **Então** deve aparecer um pop-up de saída com oferta de desconto (ex: "15% OFF se você assinar agora!").  

**Tarefas Técnicas**:  
- [ ] Aplicar técnicas de copywriting em headlines, CTAs e microtextos.  
- [ ] Integrar formulário de captura de emails com Mailchimp.  
- [ ] Implementar exit-intent pop-up usando a API `mouseleave`.  

---

### **História 6.5 – Acessibilidade e Performance**  
**Título**: Como **usuário com deficiência visual**, quero **navegar pela landing page com leitor de tela** para **acessar todas as informações sem barreiras**.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  
- **Dado** que um elemento interativo (ex: botão) é focado,  
  **Quando** o leitor de tela está ativo,  
  **Então** deve anunciar claramente sua função (ex: "Botão: Gerar Score Gratuito").  
- **Dado** que a página é carregada,  
  **Quando** auditada pelo Lighthouse,  
  **Então** deve atingir pelo menos 90 em Performance e 100 em Acessibilidade.  
- **Dado** que uma imagem ilustrativa é exibida,  
  **Quando** inspecionada,  
  **Então** deve ter `alt text` descritivo (ex: "Gráfico mostrando crescimento de 200% no engajamento").  

**Tarefas Técnicas**:  
- [ ] Implementar ARIA labels em componentes complexos (ex: carrossel).  
- [ ] Otimizar imagens com compressão WebP e lazy loading.  
- [ ] Testar contrastes de cores com ferramentas como Contrast Checker.  

---

### **Componentes Prioritários**  
1. **`<FreemiumScoreCalculator>`**:  
   - Input de URL + botão de ação.  
   - Exibição de score com animação de progresso (ex: círculo SVG preenchido gradualmente).  
2. **`<UpsellModal>`**:  
   - Comparativo lado a lado entre freemium e premium.  
   - Botão "Upgrade" com efeito hover em destaque (#FF6B6B).  
3. **`<ExitIntentPopup>`**:  
   - Triggers de saída de página.  
   - Campos para email e cupom de desconto.  

---

### **Notas de Copywriting**  
- **Headline Principal**: "Descubra Seu Potencial nas Redes: Analise Seu Perfil Grátis em 30 Segundos! 🚀"  
- **CTA Freemium**: "Quero Meu Score Agora →" (cor: #6D28D9 com borda brilhante).  
- **Texto de Upsell**: "No **Premium**, você tem: ✔️ Análise por post, ✔️ Comparação com concorrentes, ✔️ Relatórios semanais automáticos."  
- **Garantia**: "7 dias de reembolso. Sem pegadinhas. ❤️"  


### **História 7.1 – Otimização de SEO e Gestão de Google Ads**  
**Título**: Como **equipe de marketing**, queremos **aplicar técnicas avançadas de SEO e Google Ads** para **atrair tráfego qualificado e aumentar conversões na landing page**.  
**Prioridade**: Must Have.  
**Critérios de Aceite**:  

#### **Para SEO**:  
- **Dado** que a landing page está publicada,  
  **Quando** auditada por ferramentas como SEMrush ou Ahrefs,  
  **Então** deve ter:  
  - Meta título e descrição otimizados com palavras-chave (ex: "Analise Seu Score de Influenciador Grátis | Analisa.ai").  
  - Headers (H1, H2) estruturados com keywords primárias e secundárias (ex: "Aumente Seu Engajamento em Redes Sociais").  
  - Velocidade de carregamento acima de 90 no PageSpeed Insights.  
- **Dado** que há conteúdo novo publicado (ex: blog integrado),  
  **Quando** indexado pelo Google,  
  **Então** deve aparecer nas 3 primeiras posições para buscas como "como aumentar engajamento no Instagram".  

#### **Para Google Ads**:  
- **Dado** que uma campanha está ativa,  
  **Quando** um usuário pesquisa "analisar desempenho redes sociais",  
  **Então** deve ver um anúncio destacado com CTA claro (ex: "Teste Grátis Seu Score Social!").  
- **Dado** que o usuário clica no anúncio,  
  **Quando** acessa a landing page,  
  **Então** deve ser direcionado para uma versão específica do URL com parâmetros UTM para rastreamento.  
- **Dado** que a taxa de conversão é inferior a 5%,  
  **Quando** analisado no Google Analytics,  
  **Então** o sistema deve sugerir ajustes no copywriting ou no design via integração com ChatGPT-4.  

---

### **Tarefas Técnicas**:  
- [ ] Implementar **schema markup** para destacar a ferramenta freemium em rich snippets (ex: "Avaliação Gratuita: 30s").  
- [ ] Criar URLs amigáveis e redirecionamentos 301 para evitar conteúdo duplicado.  
- [ ] Configurar **Google Search Console** e **Google Analytics 4** para monitorar tráfego e keywords.  
- [ ] Desenvolver landing pages segmentadas para campanhas de Ads (ex: `/ads/instagram-score`).  
- [ ] Integrar API do Google Ads para automação de lances e relatórios em tempo real.  
- [ ] Aplicar **A/B testing** em elementos-chave:  
  - CTAs (ex: "Teste Grátis" vs. "Descubra Seu Score").  
  - Cores do botão (roxo institucional vs. vermelho de destaque).  
- [ ] Otimizar imagens com lazy loading e formato WebP para melhorar performance.  

---

### **Melhores Práticas Implementadas**:  
1. **SEO Técnico**:  
   - Compressão GZIP/Brotli para arquivos estáticos.  
   - Sitemap XML gerado dinamicamente via Angular Universal.  
   - Canonical tags em todas as páginas.  
2. **SEO de Conteúdo**:  
   - Blog com artigos otimizados (ex: "10 Estratégias para Aumentar Seguidores").  
   - FAQ section com schema markup para featured snippets.  
3. **Google Ads**:  
   - Uso de **palavras-chave de cauda longa** (ex: "melhor ferramenta análise Instagram grátis").  
   - Remarketing dinâmico para usuários que abandonaram o cálculo do score.  
   - Extensões de anúncio: links para casos de sucesso e preços.  
4. **Monitoramento**:  
   - Alertas automáticos para quedas de ranking ou CTR.  
   - Dashboard no Looker Studio com métricas-chave: CPC, CPA, ROAS.  

---

### **Exemplo de Estrutura de Campanha no Google Ads**:  
| Grupo de Anúncios | Palavras-Chave                  | Cabeçalho 1                 | Descrição                                  | CTA               |  
|--------------------|----------------------------------|-----------------------------|--------------------------------------------|-------------------|  
| Score Grátis       | "analisar perfil Instagram"     | **Seu Score em 30s!**       | "Descubra seu potencial com IA. Grátis!"   | "Teste Agora →"   |  
| Planos Premium     | "ferramenta análise social page"| **Torne-se um Expert!**     | "Relatórios detalhados e comparações. "    | "Assine Premium"  |  

---

### **Notas de Copywriting para SEO/Ads**:  
- **Títulos**: Use números e verbos de ação (ex: "Aumente 50% Seu Engajamento em 1 Mês").  
- **Meta Descrições**: Inclua CTAs e keywords (ex: "Analise grátis seu perfil social. Relatórios profissionais com IA!").  
- **Texto de Anúncio**: Destaque a urgência (ex: "Oferta Limitada: 7 Dias Premium Grátis!").  

---

### **Critérios de Sucesso**:  
- Aumento de 40% no tráfego orgânico em 3 meses.  
- CTR de anúncios acima de 8%.  
- CPA (Custo por Aquisição) abaixo de US$ 20.


---

### **Fluxo Ideal de Conversão**  
1. Usuário insere URL → Gera score → Vê upsell → Compara planos → Assina Premium.  
2. Fallback: Usuário deixa email → Recebe drip de emails com cases + desconto progressivo.

