Você é responsável por construir o backend do **Analisa.ai - Social Media**,uma plataforma de análise de redes sociais que utiliza IA para avaliar influenciadores. O sistema precisa ser escalável, seguro e integrável com APIs de redes sociais (Instagram, TikTok, Facebook).

Além disso, o backend deve ser capaz de considerar as características do público-alvo de cada influenciador, como faixa etária, interesses, localização e perfil de consumo. Isso garantirá que os insights gerados sejam contextualizados e mais relevantes para os objetivos de marketing e comunicação das marcas que utilizam a plataforma.



---

### **Diretrizes Técnicas**  
1. **Escolha de Tecnologias**:  
   - **Linguagens**: Python.  
   - **Banco de Dados**: PostgreSQL.  
   - **Fila/Streaming**: RabbitMQ para processamento assíncrono.  
   - **Cache**: Redis para otimizar consultas frequentes (ex: métricas de influenciadores).  

2. **Tarefas Prioritárias**:  
   - **Integração com APIs de Redes Sociais**:  
     - Implemente autenticação OAuth 2.0 para Instagram e TikTok.  
     - Garanta coleta contínua de dados mesmo com rate limits (ex: filas de retentativa).  
   - **Pipeline de Dados**:  
     - Crie um pipeline ETL para limpar, normalizar e armazenar dados brutos.  
     - Exemplo de código para cálculo de engajamento:  
       ```python  
       def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:  
           return ((likes + comments + shares) / followers) * 100 if followers > 0 else 0.0  
       ```  
   - **Segurança**:  
     - Criptografe dados sensíveis em repouso (AES-256) e trânsito (TLS 1.3).  
     - Implemente JWT para autenticação de API e controle de acesso baseado em roles (RBAC).  

3. **Desafios Técnicos**:  
   - **Problema**: APIs de redes sociais têm rate limits (ex: Instagram: 200 req/hora).  
     - **Solução Proposta**: Use filas prioritárias e cache de dados recentes.  
   - **Problema**: Dados inconsistentes (ex: posts deletados após coleta).  
     - **Solução Proposta**: Adicione checks de consistência no pipeline ETL.  

---

### **Requisitos de Colaboração**  
- **Com Frontend**: Forneça endpoints RESTful/GraphQL bem documentados para o painel de métricas.  
- **Com Cientistas de Dados**: Disponibilize dados via Kafka para treinamento de modelos de IA.  
- **Com DevOps**: Ajude a configurar CI/CD (GitHub Actions) e monitoramento (Prometheus/Grafana).  

---

### **Entregáveis Esperados**  
   - API funcional para coleta de dados do Instagram + cálculo básico de engajamento.  
   - Documentação Swagger/OpenAPI para integração com frontend.  

---

### **Critérios de Qualidade**  
- **Desempenho**: Latência < 500ms para 95% das requisições.  
- **Escalabilidade**: Suporte a 10.000 usuários concorrentes até Q3/2024.  
- **Conformidade**: LGPD/GDPR implementada (ex: anonimização de dados pessoais).  

---

**Perguntas para Reflexão**:  
1. Como estruturar o microsserviço de análise de dados para evitar acoplamento com o módulo de IA?  
2. Qual estratégia de sharding seria ideal para distribuir dados de influenciadores no MongoDB?  
3. Como lidar com a ausência de webhooks em algumas APIs (ex: TikTok)?  

---

**Instrução Final**:  
Proponha uma arquitetura inicial, escolha de tecnologias e cronograma para as primeiras 4 semanas. Justifique suas decisões com base em trade-offs (ex: velocidade vs. custo).