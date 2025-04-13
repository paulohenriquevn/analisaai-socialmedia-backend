**Prompt para Criação de Épicos, Histórias de Usuário, Tasks e Critérios de Aceite**  
**Contexto**: Você é o Product Owner do **Analisa.ai - Social Media** e precisa estruturar o backlog do produto seguindo metodologias ágeis. O objetivo é garantir clareza, priorização e rastreabilidade para a equipe de desenvolvimento.  

Analisa.ai - Social Media é uma plataforma de análise de redes sociais que utiliza IA para avaliar influenciadores. O sistema precisa ser escalável, seguro e integrável com APIs de redes sociais (Instagram, TikTok, Facebook), além de processar grandes volumes de dados em tempo quase real.

Além disso, o backend deve ser capaz de considerar as características do público-alvo de cada influenciador, como faixa etária, interesses, localização e perfil de consumo. Isso garantirá que os insights gerados sejam contextualizados e mais relevantes para os objetivos de marketing e comunicação das marcas que utilizam a plataforma.

---

### **Diretrizes Gerais**  
1. **Épicos**:  
   - Representam iniciativas estratégicas de alto nível.  
   - Devem ser divididos em **histórias de usuário** e **tasks**.  
   - Exemplo: *"Integração com APIs de Redes Sociais"*.  

2. **Histórias de Usuário**:  
   - Seguir o formato **INVEST** (Independent, Negotiable, Valuable, Estimable, Small, Testable).  
   - Usar a estrutura: *"Como [persona], quero [objetivo] para [benefício]."*  

3. **Tasks**:  
   - Ações técnicas específicas para concluir uma história.  
   - Devem ser mensuráveis e atribuíveis a um desenvolvedor.  

4. **Critérios de Aceite**:  
   - Lista de condições obrigatórias para validar a conclusão da história.  
   - Usar formato **GWT** (Given-When-Then) para cenários de teste.  

---

### **Exemplo Detalhado**  
#### **Épico 1: Coleta e Processamento de Dados de Redes Sociais**  
**Descrição**: Permitir a integração segura e escalável com APIs de redes sociais para coletar métricas de engajamento, alcance e crescimento.  

---

#### **História de Usuário 1.1**  
**Título**: Como **usuário do Instagram**, quero **coletar dados de posts e stories** para **analisar meu desempenho semanal**.  

**Tasks**:  
1. Implementar autenticação OAuth 2.0 com a API do Instagram.  
2. Criar endpoint `/instagram/posts` para buscar posts (incluindo curtidas, comentários e shares).  
3. Desenvolver sistema de cache para evitar exceder rate limits da API.  
4. Adicionar logging de erros para falhas na coleta de dados.  

**Critérios de Aceite**:  
- **Dado** que o usuário conectou sua conta do Instagram,  
  **Quando** acessa a seção "Desempenho Semanal",  
  **Então** o sistema deve exibir dados dos últimos 7 dias, com precisão de 99%.  
- **Dado** que a API do Instagram retorna um erro 429 (rate limit),  
  **Quando** o sistema detecta o erro,  
  **Então** deve retomar a coleta após 1 hora e notificar o usuário via email.  

---

#### **História de Usuário 1.2**  
**Título**: Como **analista de dados**, quero **processar dados brutos em tempo real** para **gerar métricas de engajamento consolidado**.  

**Tasks**:  
1. Configurar pipeline Apache Kafka para streaming de dados.  
2. Desenvolver script Python para calcular engajamento: `(curtidas + comentários + shares) / seguidores * 100`.  
3. Integrar resultados ao PostgreSQL para consultas analíticas.  

**Critérios de Aceite**:  
- **Dado** um novo post coletado,  
  **Quando** o pipeline é executado,  
  **Então** o engajamento deve ser calculado em menos de 5 segundos.  
- **Dado** um post com 0 seguidores,  
  **Quando** o cálculo é acionado,  
  **Então** o sistema deve retornar 0% de engajamento e registrar um aviso.  

---

### **Template para Novos Épicos**  
```markdown  
#### **Épico X: [Nome do Épico]**  
**Descrição**: [Objetivo estratégico e impacto no produto].  

---  

#### **História de Usuário X.Y**  
**Título**: Como [persona], quero [ação] para [motivo].  

**Tasks**:  
1. [Task técnica específica].  
2. [Task técnica específica].  

**Critérios de Aceite**:  
- **Dado** [condição inicial],  
  **Quando** [ação ou evento],  
  **Então** [resultado esperado].  
```  

---

### **Regras para Priorização**  
1. **MoSCoW**:  
   - **Must Have**: Essencial para o MVP (ex: autenticação OAuth).  
   - **Should Have**: Importante, mas não crítico (ex: modo escuro).  
   - **Could Have**: Melhoria opcional (ex: exportar relatórios em XLSX).  
   - **Won’t Have**: Descarte para versões futuras.  

2. **Pontuação de Complexidade**:  
   - Usar **Fibonacci** (1, 2, 3, 5, 8) para estimar esforço.  
   - Exemplo: História 1.1 = 5 pontos (complexidade média).  

---

### **Validação e Best Practices**  
1. **Revisão de Histórias**:  
   - Garantir que cada história tenha pelo menos 3 critérios de aceite.  
   - Evitar termos vagos como "melhorar desempenho" (especificar métricas: ex: "latência < 500ms").  

2. **Exemplo de Má Prática**:  
   - **História Ruim**: *"Fazer a integração com o TikTok"* (falta de contexto e critérios).  
   - **História Boa**: *"Como usuário do TikTok, quero coletar dados de vídeos para comparar meu desempenho com concorrentes."*  
--- 

**Instrução Final**:  
Preencha o template abaixo para o **Épico 2: Análise de Sentimentos em Tempo Real**, garantindo que as histórias, tasks e critérios de aceite sejam tão detalhados quanto o exemplo fornecido.