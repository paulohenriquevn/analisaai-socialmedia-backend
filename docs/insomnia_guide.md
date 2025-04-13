# Guia de Uso da Collection do Insomnia

Este guia explica como utilizar a collection do Insomnia para testar as APIs do AnalisaAI Social Media.

## Configuração Inicial

1. **Instale o Insomnia**: Baixe e instale o Insomnia em [insomnia.rest](https://insomnia.rest/)

2. **Importe a Collection**:
   - Abra o Insomnia
   - Vá em Application > Preferences > Data > Import Data > From File
   - Selecione o arquivo `insomnia_collection.json`

3. **Selecione o Ambiente**:
   - No canto superior direito, selecione "Development" para usar o ambiente de desenvolvimento local

## Autenticação

A maioria dos endpoints exige autenticação. Siga estes passos para obter um token:

1. **Crie uma Conta**:
   - Use a requisição "Register" para criar uma conta
   - Preencha username, email e password

2. **Faça Login**:
   - Use a requisição "Login" com suas credenciais
   - A resposta incluirá um access_token e refresh_token

3. **Configure os Tokens**:
   - Clique no ambiente no canto superior direito
   - Edite o ambiente e preencha ACCESS_TOKEN e REFRESH_TOKEN com os valores recebidos
   - Todos os outros requests usarão automaticamente esses tokens

4. **Atualize o Token**:
   - Se o token expirar, use a requisição "Refresh Token"
   - Atualize o valor do ACCESS_TOKEN no ambiente

## Estrutura da Collection

A collection está organizada nas seguintes pastas:

### Authentication
- Register - Criar uma nova conta
- Login - Fazer login e obter tokens
- Refresh Token - Atualizar o token de acesso
- Logout - Encerrar a sessão

### Users
- Get Profile - Ver perfil do usuário
- Update Profile - Atualizar informações do perfil
- Change Password - Alterar senha

### Influencers
- Get Influencer - Obter detalhes de um influenciador
- List Influencers - Listar influenciadores com filtros

### Search
- Search Influencers - Buscar influenciadores por palavra-chave
- Search Categories - Buscar categorias de influenciadores

### Analytics
- Influencer Growth - Obter métricas de crescimento
- Benchmarks - Obter benchmarks da plataforma
- Recommendations - Obter recomendações de influenciadores
- Dashboard - Obter dados consolidados do dashboard
- Dashboard Refresh - Forçar atualização dos dados do dashboard

### Sentiment Analysis
- Analyze Sentiment - Analisar sentimento de um texto
- Get Post Comments - Obter comentários de um post com análise
- Get Post Sentiment - Obter análise de sentimento de um post
- Get Influencer Sentiment - Obter análise de sentimento de um influenciador
- Fetch Post Comments - Buscar e analisar comentários de um post
- Batch Analyze - Analisar sentimento de múltiplos textos

### Posting Time Optimization
- Best Posting Times - Obter melhores horários para postagem
- Content Type Performance - Analisar desempenho por tipo de conteúdo
- Day of Week Analysis - Analisar desempenho por dia da semana
- Industry Benchmarks - Obter benchmarks da indústria para horários
- Personalized Recommendations - Obter recomendações personalizadas

## Exemplos de Uso

### Fluxo Básico de Autenticação

1. Crie uma conta com "Register"
2. Faça login com "Login"
3. Copie o ACCESS_TOKEN e o REFRESH_TOKEN para o ambiente
4. Acesse "Get Profile" para verificar se a autenticação está funcionando

### Análise de Sentimentos

1. Use "Analyze Sentiment" para analisar o sentimento de um texto específico
2. Use "Get Post Sentiment" para ver a análise completa de um post (substitua o ID)
3. Use "Batch Analyze" para analisar vários textos de uma vez

### Otimização de Horários

1. Use "Best Posting Times" para ver os melhores horários por dia da semana
2. Use "Content Type Performance" para analisar o desempenho por tipo de conteúdo
3. Use "Personalized Recommendations" para obter recomendações personalizadas

## Parâmetros e Filtros

Muitos endpoints aceitam parâmetros para filtrar ou personalizar os resultados:

### Filtros de Plataforma
- `platform`: instagram, facebook, tiktok

### Filtros de Conteúdo
- `content_type`: image, video, carousel, text

### Filtros de Tempo
- `timeframe`: day, week, month, year
- `time_range`: número de dias (30, 60, 90, etc.)
- `days`: número de dias para análise (30 a 365)

### Filtros de Métricas
- `min_followers`: número mínimo de seguidores
- `min_engagement`: taxa mínima de engajamento

## Solução de Problemas

- **Token Expirado**: Use "Refresh Token" para obter um novo token
- **Erro 401**: Verifique se você configurou corretamente o ACCESS_TOKEN
- **Erro 400**: Verifique os parâmetros da requisição
- **Erro 404**: Verifique se o ID do recurso existe
- **Erro 500**: Erro interno do servidor, verifique os logs