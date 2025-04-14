# Guia da Collection do Insomnia para AnalisaAI Social Media

Este guia explica como usar a collection do Insomnia organizada por jornadas de usuário para teste e desenvolvimento do backend do AnalisaAI Social Media.

## Sobre a Collection

A collection está organizada em **jornadas numeradas** que representam fluxos de uso comuns da aplicação. Dentro de cada jornada, as requisições estão organizadas na ordem em que normalmente seriam executadas.

## Importando a Collection

1. Abra o Insomnia
2. Clique em **Create** → **Import from File**
3. Selecione o arquivo `analisaai_insomnia_collection.json`
4. A collection será importada com todas as jornadas e requisições

## Estrutura da Collection

### Jornadas Disponíveis

1. **Jornada de Onboarding**
   - Verificar status da API
   - Registrar usuário
   - Login
   - Renovar token
   - Obter perfil de usuário

2. **Jornada de Conexão de Redes Sociais**
   - Conectar Facebook
   - Conectar Instagram
   - Conectar TikTok
   - Cadastrar rede social manualmente
   - Atualizar dados de influenciador

3. **Jornada de Gerenciamento de Influenciadores**
   - Listar influenciadores
   - Ver detalhes de influenciador
   - Pesquisar influenciador
   - Busca avançada de influenciadores
   - Listar categorias

4. **Jornada de Métricas de Engajamento**
   - Obter métricas de engajamento
   - Calcular métricas de engajamento
   - Calcular todas as métricas de engajamento

5. **Jornada de Métricas de Alcance**
   - Obter métricas de alcance
   - Calcular métricas de alcance
   - Calcular todas as métricas de alcance

6. **Jornada de Métricas de Crescimento**
   - Obter métricas de crescimento
   - Calcular métricas de crescimento
   - Calcular todas as métricas de crescimento

7. **Jornada de Pontuação de Relevância**
   - Obter pontuação de relevância
   - Calcular pontuação de relevância
   - Calcular todas as pontuações de relevância
   - Comparar pontuações

8. **Jornada de Visualização de Dashboard**
   - Visualização de engajamento
   - Visualização de alcance
   - Visualização de crescimento
   - Visualização de pontuação
   - Dashboard completo
   - Comparação de influenciadores

9. **Jornada de Análise de Sentimento**
   - Analisar sentimento de texto
   - Análise de sentimento do influenciador
   - Análise de sentimento do post
   - Comentários com análise de sentimento

10. **Jornada de Otimização de Horários**
    - Melhores horários
    - Análise por dia da semana
    - Desempenho por tipo de conteúdo
    - Recomendações personalizadas

## Configuração de Ambiente

A collection inclui três ambientes:

1. **Base Environment**
   - Variáveis comuns compartilhadas entre todos os ambientes

2. **Development**
   - Configurado para ambiente de desenvolvimento local (`http://localhost:5000`)

3. **Production**
   - Configurado para ambiente de produção (`https://api.analisaai.com`)

### Variáveis de Ambiente

- `BASE_URL`: URL base da API
- `ACCESS_TOKEN`: Token de acesso JWT para autenticação
- `REFRESH_TOKEN`: Token de atualização JWT

## Uso Recomendado

Para utilizar corretamente a collection e testar os fluxos da aplicação:

1. Comece pela **Jornada de Onboarding** para registrar e autenticar-se
2. A requisição de login automaticamente preenche as variáveis `ACCESS_TOKEN` e `REFRESH_TOKEN`
3. Em seguida, use a **Jornada de Conexão de Redes Sociais** para conectar contas
4. Prossiga pelas jornadas na ordem numerada para uma experiência coerente

## Renovação de Token

O token de acesso expira após um determinado período. Para continuar usando a API:

1. Use a requisição **1.4 Renovar Token** na Jornada de Onboarding
2. A resposta fornecerá um novo token de acesso
3. A variável `ACCESS_TOKEN` será atualizada automaticamente

## Fluxos Comuns

### 1. Registrar e Conectar Contas
- 1.2 Registrar Usuário
- 1.3 Login
- 2.1-2.3 Conectar redes sociais (Facebook/Instagram/TikTok)

### 2. Gerenciar Influenciadores
- 3.1 Listar Influenciadores
- 3.2 Detalhes do Influenciador
- 3.4 Busca Avançada de Influenciadores

### 3. Obter Análises
- 4.1, 5.1, 6.1, 7.1 Obter métricas (engajamento, alcance, crescimento, pontuação)
- 8.5 Dashboard completo
- 9.2 Análise de sentimento do influenciador
- 10.1 Melhores horários de postagem

### 4. Calcular Novas Métricas
- 4.2, 5.2, 6.2, 7.2 Calcular métricas específicas
- 4.3, 5.3, 6.3, 7.3 Calcular todas as métricas

### 5. Obter Visualizações para Dashboard
- 8.1-8.4 Visualizações específicas (engajamento, alcance, crescimento, pontuação)
- 8.5 Dashboard completo
- 8.6 Comparação entre influenciadores

## Notas

- Os endpoints calculadores (`/calculate`) são POST pois criam ou atualizam dados no servidor
- Os endpoints de visualização (`/visualization`) formatam dados para consumo direto por um frontend
- Todos os endpoints (exceto login e registro) requerem um token JWT válido
- Os IDs de influenciadores em cada requisição devem ser substituídos por IDs reais do seu ambiente