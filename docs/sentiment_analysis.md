# Análise de Sentimentos em Comentários

## Visão Geral

O módulo de análise de sentimentos permite analisar os comentários de posts em redes sociais para identificar o sentimento expresso pelos usuários. O sistema classifica os comentários como positivos, neutros ou negativos, com base em técnicas de processamento de linguagem natural (NLP) otimizado para o português.

## Recursos

- **Análise de Sentimentos**: Classificação de textos em positivo, neutro e negativo
- **Detecção de Comentários Críticos**: Identificação de comentários com forte sentimento negativo
- **Coleta de Comentários**: Integração com APIs de redes sociais para obter comentários
- **Processamento de Gírias e Emojis**: Suporte para linguagem informal e emoji em redes sociais
- **Dashboard de Análise**: Visualização agregada de sentimentos por post ou influenciador

## Endpoints da API

### Análise de Texto Individual

- **Endpoint**: `/api/analytics/sentiment/analyze`
- **Método**: POST
- **Descrição**: Analisa o sentimento de um texto fornecido
- **Corpo da Requisição**:
  ```json
  {
    "text": "Texto a ser analisado"
  }
  ```
- **Resposta**:
  ```json
  {
    "text": "Texto a ser analisado",
    "sentiment": "positive",
    "score": 0.75,
    "is_critical": false
  }
  ```

### Análise em Lote

- **Endpoint**: `/api/analytics/sentiment/batch-analyze`
- **Método**: POST
- **Descrição**: Analisa o sentimento de múltiplos textos
- **Corpo da Requisição**:
  ```json
  {
    "texts": ["Texto 1", "Texto 2", "Texto 3"]
  }
  ```
- **Resposta**:
  ```json
  {
    "results": [
      {
        "sentiment": "positive",
        "score": 0.65,
        "is_critical": false
      },
      {
        "sentiment": "neutral",
        "score": 0.1,
        "is_critical": false
      },
      {
        "sentiment": "negative",
        "score": -0.8,
        "is_critical": true
      }
    ]
  }
  ```

### Análise de Post

- **Endpoint**: `/api/analytics/sentiment/post/{post_id}/sentiment`
- **Método**: GET
- **Descrição**: Obtém análise de sentimento consolidada para um post
- **Resposta**: Informações agregadas de sentimento para o post

### Análise de Influenciador

- **Endpoint**: `/api/analytics/sentiment/influencer/{influencer_id}/sentiment`
- **Método**: GET
- **Parâmetros da Query**:
  - `time_range`: Período em dias para análise (padrão: 30)
- **Descrição**: Obtém análise agregada de sentimentos para um influenciador
- **Resposta**: Dados de sentimento agregados por todos os posts do influenciador

### Comentários de Post

- **Endpoint**: `/api/analytics/sentiment/post/{post_id}/comments`
- **Método**: GET
- **Descrição**: Lista todos os comentários de um post com análise de sentimento

### Buscar Comentários

- **Endpoint**: `/api/analytics/sentiment/post/{post_id}/comments/fetch`
- **Método**: POST
- **Descrição**: Busca novos comentários da rede social e os analisa

## Modelo de Classificação

O sistema utiliza um modelo de análise de sentimentos baseado em:

1. **Pré-processamento de Texto**:
   - Normalização de texto (lowercase, remoção de caracteres especiais)
   - Tratamento de gírias comuns em redes sociais
   - Preservação de emojis para análise de sentimento

2. **Análise de Sentimento**:
   - Utiliza um modelo baseado em léxico de palavras com pontuações de sentimento
   - Análise de emojis para ajuste da pontuação de sentimento
   - Detecção de frases críticas específicas

3. **Critérios para Comentários Críticos**:
   - Pontuação de sentimento abaixo de -0.5
   - Presença de frases críticas específicas (e.g., "não funciona", "péssimo", "cancelar")

## Precisão

O modelo visa atingir uma precisão mínima de 80% na classificação de sentimentos, validada através de:

- Comparação manual de amostragem de comentários
- Métricas de precisão, recall e F1-score
- Ajuste contínuo baseado em feedback de usuários

## Integração com Redes Sociais

O sistema pode coletar comentários automaticamente das seguintes plataformas:

- Instagram (via Facebook Graph API)
- Facebook
- TikTok

## Requisitos

As seguintes dependências são necessárias para o funcionamento completo:

- NLTK com recursos para português
- scikit-learn
- emoji
- flask-caching (para armazenamento em cache de análises frequentes)

## Exemplos de Uso

### Analisar um Comentário

```python
from app.services.sentiment_service import SentimentService

# Analisar um comentário
result = SentimentService.analyze_sentiment("Amei esse produto! É perfeito! 😍")
print(result)
# {'sentiment': 'positive', 'score': 0.85, 'is_critical': False}

# Analisar um comentário negativo
result = SentimentService.analyze_sentiment("Não funciona, perdi meu dinheiro! Péssimo produto 😡")
print(result)
# {'sentiment': 'negative', 'score': -0.75, 'is_critical': True}
```

### Obter Análise de um Post

```python
from app.services.sentiment_service import SentimentService

# Obter análise de sentimento para um post
analysis = SentimentService.get_post_sentiment_analysis(post_id=123)

# Verificar distribuição de sentimentos
print(f"Positivos: {analysis['sentiment_distribution']['percentages']['positive']}%")
print(f"Neutros: {analysis['sentiment_distribution']['percentages']['neutral']}%")
print(f"Negativos: {analysis['sentiment_distribution']['percentages']['negative']}%")

# Verificar comentários críticos
if analysis['critical_comments']:
    print(f"Encontrados {len(analysis['critical_comments'])} comentários críticos")
```