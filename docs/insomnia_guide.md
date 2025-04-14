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
   - Use a requisição "1.1.2 Registrar Usuário" para criar uma conta
   - Preencha username, email e password

2. **Faça Login**:
   - Use a requisição "1.1.3 Login" com suas credenciais
   - A resposta incluirá um access_token e refresh_token

3. **Configure os Tokens Automaticamente**:
   - Após receber a resposta do login, clique com o botão direito no valor do token
   - Selecione "Set Environment Variable" > "ACCESS_TOKEN"
   - Faça o mesmo para o refresh_token e defina como "REFRESH_TOKEN"
   - Todos os outros requests usarão automaticamente esses tokens

4. **Atualize o Token Manualmente**:
   - Se preferir, você também pode copiar manualmente os tokens
   - Clique no ambiente no canto superior direito
   - Edite o ambiente e cole os valores em ACCESS_TOKEN e REFRESH_TOKEN

5. **Quando o Token Expirar**:
   - Se um token expirar (erro 401), use a requisição "1.1.4 Renovar Token"
   - Essa requisição usará o REFRESH_TOKEN para obter um novo ACCESS_TOKEN
   - Atualize o valor do ACCESS_TOKEN no ambiente

## Estrutura da Collection por Jornadas

A collection está organizada em três jornadas principais de usuário:

### 1. Jornada de Onboarding
Fluxo de registro, autenticação e conexão de redes sociais.

- **1.1 Autenticação e Registro**
  - 1.1.1 Status da Autenticação
  - 1.1.2 Registrar Usuário
  - 1.1.3 Login
  - 1.1.4 Renovar Token
  - 1.1.5 Perfil do Usuário

- **1.2 Conexão de Redes Sociais**
  - 1.2.1 Conectar Facebook
  - 1.2.2 Conectar Instagram
  - 1.2.3 Conectar TikTok
  - 1.2.4 Cadastrar Rede Social Manualmente

### 2. Jornada de Influenciadores
Busca, análise e gerenciamento de influenciadores.

- **2.1 Gerenciamento de Influenciadores**
  - 2.1.1 Listar Influenciadores
  - 2.1.2 Detalhes do Influenciador
  - 2.1.3 Pesquisar Influenciador

- **2.2 Busca Avançada**
  - 2.2.1 Buscar Influenciadores
  - 2.2.2 Listar Categorias

### 3. Jornada de Análise de Dados
Análises e insights sobre performance nas redes sociais.

- **3.1 Analytics Gerais**
  - 3.1.1 Crescimento do Influenciador
  - 3.1.2 Benchmarks de Plataforma
  - 3.1.3 Recomendações de Influenciadores
  - 3.1.4 Métricas Consolidadas
  - 3.1.5 Distribuição de Plataformas
  - 3.1.6 Insights por Categoria

- **3.2 Análise de Sentimento**
  - 3.2.1 Analisar Sentimento
  - 3.2.2 Comentários do Post
  - 3.2.3 Sentimento do Post
  - 3.2.4 Sentimento do Influenciador
  - 3.2.5 Buscar Comentários
  - 3.2.6 Análise em Lote

- **3.3 Otimização de Horários**
  - 3.3.1 Melhores Horários
  - 3.3.2 Performance por Tipo de Conteúdo
  - 3.3.3 Análise por Dia da Semana
  - 3.3.4 Benchmarks da Indústria
  - 3.3.5 Recomendações Personalizadas

## Criando Variáveis de Ambiente

Para facilitar o uso de diferentes ambientes de desenvolvimento, você pode configurar variáveis:

1. **Clique no menu suspenso de ambientes** no canto superior direito
2. **Selecione "Manage Environments"**
3. **Edite o ambiente "Development"**
4. **Configure as seguintes variáveis**:
   ```json
   {
     "BASE_URL": "http://localhost:5000",
     "ACCESS_TOKEN": "",
     "REFRESH_TOKEN": ""
   }
   ```
5. **Para um ambiente de produção**, duplique e ajuste conforme necessário:
   ```json
   {
     "BASE_URL": "https://api.analisaai.com",
     "ACCESS_TOKEN": "",
     "REFRESH_TOKEN": ""
   }
   ```

## Exemplos de Uso Recomendados

### Fluxo Completo de Onboarding

1. Use "1.1.2 Registrar Usuário" para criar uma conta
2. Use "1.1.3 Login" para obter tokens
3. Configure os tokens no ambiente (automática ou manualmente)
4. Use "1.1.5 Perfil do Usuário" para verificar a autenticação
5. Use "1.2.4 Cadastrar Rede Social Manualmente" para conectar uma rede social

### Análise de Sentimentos

1. Use "3.2.1 Analisar Sentimento" para análise rápida de um comentário
2. Use "3.2.3 Sentimento do Post" para análise completa de um post
3. Use "3.2.4 Sentimento do Influenciador" para análise de todos os posts
4. Use "3.2.6 Análise em Lote" para processar múltiplos textos simultaneamente

### Otimização de Horários de Postagem

1. Use "3.3.1 Melhores Horários" para ver os melhores horários por plataforma
2. Use "3.3.2 Performance por Tipo de Conteúdo" para um post específico
3. Use "3.3.3 Análise por Dia da Semana" para padrões semanais
4. Use "3.3.5 Recomendações Personalizadas" para recomendações específicas

## Parâmetros e Filtros Comuns

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

## Solução de Problemas de Autenticação

### Erro 401 (Unauthorized)

Se você receber um erro 401, verifique:

1. **Formato do Token**:
   - Certifique-se de que o token está no formato correto na aba Auth
   - Deve estar configurado como "Bearer Token"
   - Não deve incluir o prefixo "Bearer" manualmente

2. **Validade do Token**:
   - Use o script `scripts/test_token.py` para verificar se o token expirou:
   ```bash
   python scripts/test_token.py "seu_token_aqui"
   ```

3. **Renovação do Token**:
   - Se o token expirou, use "1.1.4 Renovar Token"
   - Atualize o valor do ACCESS_TOKEN no ambiente

4. **Configuração Manual**:
   - Se os tokens não estiverem funcionando, tente configurá-los manualmente
   - Copie o token completo da resposta do login
   - Verifique se não há espaços extras ou caracteres inválidos

### Outros Erros Comuns

- **Erro 400**: Verifique se os parâmetros da requisição estão corretos
- **Erro 404**: Verifique se o ID do recurso existe
- **Erro 409**: Conflito (ex: tentativa de conectar uma rede social já vinculada)
- **Erro 500**: Erro interno do servidor, verifique os logs ou contate o suporte

Para problemas persistentes de autenticação, consulte o documento `token_troubleshooting_steps.md` para um guia detalhado de solução de problemas.