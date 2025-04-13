# 📦 Analisa.ai Social Media

Analisa.ai Social Media é uma plataforma de análise de redes sociais que utiliza IA para avaliar influenciadores. O sistema precisa ser escalável, seguro e integrável com APIs de redes sociais (Instagram, TikTok, Facebook), além de processar grandes volumes de dados em tempo quase real.

Além disso, o backend deve ser capaz de considerar as características do público-alvo de cada influenciador, como faixa etária, interesses, localização e perfil de consumo. Isso garantirá que os insights gerados sejam contextualizados e mais relevantes para os objetivos de marketing e comunicação das marcas que utilizam a plataforma.

---

## Épico 1: Autenticação e Autorização Segura

### História 1.1: Como administrador do sistema, quero implementar autenticação OAuth 2.0 com as redes sociais para garantir acesso seguro e controle de permissões de usuários.
**Prioridade**: Must Have  
**Story Points**: 5  
**Tasks**:
- Implementar fluxo OAuth 2.0 para Instagram e TikTok.
- Armazenar tokens criptografados (AES-256).
- Implementar middleware JWT.
- Criar RBAC com permissões por role.

**Critérios de Aceite**:
- GWT 1: Dado login bem-sucedido, Quando o token é gerado, Então ele deve conter roles válidas.
- GWT 2: Dado token expirado, Quando uma requisição for feita, Então o sistema retorna 401.
- GWT 3: Dado o armazenamento de token, Quando verificado, Então ele deve estar criptografado.

---

## Épico 2: Integração com APIs de Redes Sociais

### História 2.1: Como cliente influenciador, quero conectar minha conta do Instagram para monitorar meu desempenho de forma automatizada.
**Prioridade**: Must Have  
**Story Points**: 5  
**Tasks**:
- Coletar posts, curtidas, comentários via Instagram Graph API.
- Criar fallback para erro 429.
- Armazenar métricas em PostgreSQL.
- Cache com Redis (10min).

**Critérios de Aceite**:
- GWT 1: Dado o consentimento, Quando a coleta inicia, Então os dados dos 10 últimos posts devem ser salvos.
- GWT 2: Dado erro 429, Quando detectado, Então a retentativa ocorre após 1 hora.
- GWT 3: Dado cache ativo, Quando consulta for repetida, Então dados vêm do Redis.

### História 2.2: Como usuário TikTok, quero conectar minha conta e coletar dados dos vídeos para comparar meu engajamento com influenciadores concorrentes.
**Prioridade**: Should Have  
**Story Points**: 8  
**Tasks**:
- Implementar autenticação TikTok Business API.
- Coletar dados de vídeos.
- Criar fallback para indisponibilidade da API.

**Critérios de Aceite**:
- GWT 1: Dado integração com TikTok, Quando a sincronização é feita, Então vídeos e métricas devem estar salvos.
- GWT 2: Dado falha da API, Quando detectada, Então uma nova tentativa ocorre após 15 min.

---

## Épico 3: Gestão de Erros e Resiliência

### História 3.1: Como administrador do sistema, quero registrar e tratar erros de forma resiliente para evitar perda de dados e garantir estabilidade.
**Prioridade**: Must Have  
**Story Points**: 5  
**Tasks**:
- Middleware de erros global.
- Sistema de logs com Loki.
- Backoff exponencial para retentativas.
- Alertas Slack/Email.

**Critérios de Aceite**:
- GWT 1: Dado erro, Quando ocorre, Então ele é logado com stacktrace.
- GWT 2: Dado timeout, Quando ocorre, Então o sistema tenta até 3 vezes.
- GWT 3: Dado falha crítica, Quando detectada, Então alerta é enviado.

---

## Épico 4: Otimização de Desempenho e Cache

### História 4.1: Como cliente influenciador, quero acessar métricas em tempo real com baixa latência para tomar decisões rápidas nas campanhas.
**Prioridade**: Must Have  
**Story Points**: 8  
**Tasks**:
- Criar cache Redis para KPIs.
- Otimizar queries SQL (PostgreSQL).
- Testar com Locust.
- Monitorar via Grafana.

**Critérios de Aceite**:
- GWT 1: Dado cache ativo, Quando métrica requisitada, Então latência < 200ms.
- GWT 2: Dado cache ausente, Quando consulta SQL, Então resposta em < 500ms.
- GWT 3: Dado carga de 10k usuários, Quando simulada, Então sistema mantém latência < 500ms p/ 95%.

---

## Épico 5: Análise de Sentimentos

### História 5.1: Como analista de dados, quero analisar o sentimento de comentários para entender a percepção do público sobre o conteúdo.
**Prioridade**: Must Have  
**Story Points**: 5  
**Tasks**:
- Criar microserviço com modelo BERT.
- Rota `/sentimentos` para comentários.
- Armazenar polaridade.

**Critérios de Aceite**:
- GWT 1: Dado 100 comentários, Quando enviados, Então polaridade é retornada em até 10s.
- GWT 2: Dado comentário irrelevante, Quando detectado, Então ele é rotulado como neutro.

---

## Épico 6: Relatórios e Exportação

### História 6.1: Como cliente marca, quero gerar relatórios automáticos semanais em PDF para monitorar o desempenho da minha campanha.
**Prioridade**: Should Have  
**Story Points**: 5  
**Tasks**:
- Criar templates PDF (WeasyPrint).
- Endpoint `/relatorios/pdf`.
- Exportação XLSX.

**Critérios de Aceite**:
- GWT 1: Dado encerramento da semana, Quando for gerado, Então o relatório PDF deve estar disponível.
- GWT 2: Dado clique em "Exportar", Quando XLSX for solicitado, Então download inicia.

---

## Épico 7: IA Generativa para Recomendação

### História 7.1: Como influenciador, quero receber recomendações automáticas com base no meu desempenho para melhorar meu engajamento.
**Prioridade**: Could Have  
**Story Points**: 8  
**Tasks**:
- Treinar modelo de recomendação.
- Integração com GPT-4 para legendas.
- Endpoint `/recomendacoes`.

**Critérios de Aceite**:
- GWT 1: Dado histórico de posts, Quando recomendação for solicitada, Então horário, tipo e legenda devem ser exibidos.
- GWT 2: Dado falta de histórico, Quando solicitado, Então mensagem de dados insuficientes deve ser mostrada.

Ótimo! Vamos adicionar as duas funcionalidades sugeridas ao sistema **Analisa.ai - Social Media**, de forma alinhada com a estrutura atual dos épicos e histórias de usuário que você já definiu.

---

## 🧩 Novos Épicos e Histórias de Usuário

### 📌 Épico 8: Área Freemium e Score Simplificado

#### **História 8.1 – Score Geral para Usuários Gratuitos**
**Título**: Como usuário gratuito, quero visualizar um score geral da minha página social para entender minha performance e ser incentivado a migrar para o plano pago.  
**Descrição**: A área freemium exibe um *score agregado* (ex: 0 a 100) baseado em engajamento, frequência de postagens e crescimento de seguidores, sem exibir métricas detalhadas (ex: sem gráficos de comentários, horários, tipos de conteúdo).  
**Prioridade**: Must Have  
**Story Points**: 5  
**Tasks**:
- Criar endpoint `/freemium/score` que calcula e retorna apenas o score agregado.
- Separar plano gratuito de pago via RBAC.
- Criar lógica de upsell: “Quer ver mais? Atualize seu plano!”.
- Armazenar score básico no Redis para acesso rápido.
- Ajustar frontend para mostrar score e call-to-action.

**Critérios de Aceite** (GWT):
- Dado um usuário freemium, Quando ele acessar seu painel, Então deve ver apenas o score geral.
- Dado um usuário freemium, Quando clicar em "Ver detalhes", Então deve ser redirecionado para a tela de upgrade de plano.

---

### 📌 Épico 9: Segmentação por Nicho e Público-Alvo

#### **História 9.1 – Análise Baseada no Público-Alvo da Página**
**Título**: Como cliente premium, quero que a análise da minha página leve em consideração meu público-alvo para que os insights sejam mais relevantes.  
**Descrição**: O sistema deve considerar o nicho do influenciador (ex: Finanças, Nutrição, Estética, Tecnologia) para ajustar o cálculo de benchmarks e recomendações.  
**Prioridade**: Must Have  
**Story Points**: 8  
**Tasks**:
- Adicionar campo `nicho` no cadastro de página social (ex: enum: ["Finanças", "Nutrição", "Moda"...]).
- Criar repositório de benchmarks por nicho (engajamento médio, frequência ideal etc.).
- Adaptar o cálculo de score e recomendações baseado no nicho selecionado.
- Ajustar mensagens do sistema e recomendação de horário/postagem com base no público.
- Permitir alteração de nicho pelo usuário autenticado.

**Critérios de Aceite**:
- Dado um influenciador de Finanças, Quando o score for calculado, Então ele deve ser comparado com o benchmark do nicho de Finanças.
- Dado alteração de nicho, Quando salva, Então a análise deve refletir essa mudança imediatamente.

---
