# Otimização de Horários para Postagem

## Visão Geral

O recurso de Otimização de Horários para Postagem permite aos usuários identificar os melhores momentos para publicar conteúdo em redes sociais, visando maximizar o alcance e engajamento. O sistema analisa o histórico de desempenho de posts anteriores, identifica padrões e fornece recomendações personalizadas.

## Recursos Principais

- **Análise de Engajamento por Horário**: Identifica padrões de engajamento em diferentes horários do dia
- **Segmentação por Dia da Semana**: Análise detalhada do desempenho por dia da semana
- **Recomendações por Tipo de Conteúdo**: Identificação de horários ideais específicos para diferentes tipos de conteúdo (imagem, vídeo, carrossel, etc.)
- **Comparação com Benchmarks**: Comparação do desempenho com médias da indústria
- **Recomendações Personalizadas**: Sugestões adaptadas ao perfil específico do usuário e seu histórico

## Endpoints da API

### Melhores Horários para Postagem

- **Endpoint**: `/api/analytics/posting-time/best-times`
- **Método**: GET
- **Descrição**: Retorna análise dos melhores horários para postagem com base no histórico
- **Parâmetros**:
  - `platform` (opcional): Plataforma específica (instagram, facebook, tiktok)
  - `content_type` (opcional): Tipo de conteúdo (image, video, carousel, text)
  - `days` (opcional, padrão: 90): Quantidade de dias para análise

### Desempenho por Tipo de Conteúdo

- **Endpoint**: `/api/analytics/posting-time/content-types`
- **Método**: GET
- **Descrição**: Análise de desempenho segmentada por tipo de conteúdo
- **Parâmetros**:
  - `platform` (opcional): Filtrar por plataforma
  - `days` (opcional, padrão: 90): Quantidade de dias para análise

### Análise por Dia da Semana

- **Endpoint**: `/api/analytics/posting-time/days-of-week`
- **Método**: GET
- **Descrição**: Análise detalhada de desempenho por dia da semana
- **Parâmetros**:
  - `platform` (opcional): Filtrar por plataforma
  - `days` (opcional, padrão: 90): Quantidade de dias para análise

### Benchmarks da Indústria

- **Endpoint**: `/api/analytics/posting-time/benchmarks`
- **Método**: GET
- **Descrição**: Benchmarks da indústria para comparação
- **Parâmetros**:
  - `platform` (opcional): Filtrar por plataforma
  - `category` (opcional): Filtrar por categoria

### Recomendações Personalizadas

- **Endpoint**: `/api/analytics/posting-time/recommendations`
- **Método**: GET
- **Descrição**: Recomendações personalizadas combinando dados do usuário e benchmarks
- **Parâmetros**:
  - `platform` (opcional): Filtrar por plataforma
  - `content_type` (opcional): Filtrar por tipo de conteúdo

## Estrutura de Dados

### Horários Recomendados

```json
{
  "recommendations": {
    "best_times": {
      "Monday": {
        "recommended": [
          {
            "hour": 12,
            "formatted_hour": "12:00",
            "avg_engagement": 153.42,
            "post_count": 15,
            "confidence": 0.9
          },
          {
            "hour": 18,
            "formatted_hour": "18:00",
            "avg_engagement": 142.18,
            "post_count": 12,
            "confidence": 0.8
          }
        ],
        "benchmark_comparison": [
          {
            "hour": 19,
            "formatted_hour": "19:00",
            "avg_engagement": 128.75,
            "post_count": 450
          }
        ]
      },
      // Outros dias da semana...
    },
    "best_days": [
      {
        "day": "Wednesday",
        "avg_engagement": 162.37,
        "post_count": 45
      },
      // Outros melhores dias...
    ],
    "best_content_types": [
      {
        "type": "video",
        "avg_engagement": 185.29,
        "confidence": 0.95,
        "benchmark_engagement": 155.40,
        "relative_performance": 19.23
      },
      // Outros tipos de conteúdo...
    ],
    "by_platform": {
      "instagram": {
        "avg_engagement": 145.62,
        "post_count": 87,
        "reliability": 0.9,
        "benchmark_engagement": 125.33,
        "relative_performance": 16.19
      },
      // Outras plataformas...
    }
  },
  "source": "user_data",
  "message": "Recomendações baseadas no seu histórico de postagens.",
  "data_points": 105,
  "analyzed_period_days": 90,
  "is_reliable": true,
  "last_updated": "2025-04-13T10:15:30.123456"
}
```

## Algoritmo de Análise

O sistema utiliza as seguintes técnicas para determinar os melhores horários:

1. **Análise Histórica**: Examina os últimos 90 dias (por padrão) de posts
2. **Correlação Temporal**: Identifica padrões entre horário de postagem e engajamento
3. **Segmentação Multidimensional**:
   - Por plataforma (Instagram, Facebook, TikTok)
   - Por tipo de conteúdo (imagem, vídeo, carrossel, texto)
   - Por dia da semana
   - Por hora do dia
4. **Avaliação de Confiabilidade**: Atribui níveis de confiança baseados no volume de dados disponíveis

## Recomendações Personalizadas

As recomendações são geradas usando:

1. **Dados do Usuário**: Histórico de desempenho personalizado
2. **Benchmarks da Indústria**: Comparação com padrões do setor
3. **Combinação Inteligente**: Quando os dados do usuário são insuficientes, o sistema se apoia mais nos benchmarks

## Melhores Práticas

- **Volume de Dados**: Quanto mais dados históricos, mais precisas são as recomendações
- **Consistência de Métricas**: O sistema acompanha e compara métricas como:
  - Número de curtidas
  - Comentários
  - Compartilhamentos
  - Visualizações
  - Taxa de engajamento geral
- **Segmentação de Conteúdo**: Classificar corretamente o tipo de conteúdo melhora a precisão das recomendações

## Implementação Técnica

### Modelos de Dados

- `SocialPost`: Armazena informações sobre publicações e seus dados de engajamento
  - `content_type`: Tipo de conteúdo (imagem, vídeo, carrossel, etc.)
  - `posted_at`: Data/hora da publicação
  - `engagement_rate`: Taxa de engajamento calculada

### Serviços

- `PostingTimeService`: Implementa a lógica de análise de horários
  - `get_best_posting_times()`: Analisa melhores horários por dia/hora
  - `get_content_type_performance()`: Avalia performance por tipo de conteúdo
  - `get_day_of_week_analysis()`: Análise detalhada por dia da semana
  - `get_industry_benchmarks()`: Busca e compara com benchmarks do setor
  - `get_personalized_recommendations()`: Gera recomendações personalizadas

### Cache

A funcionalidade utiliza cache para otimizar o desempenho:
- Resultados armazenados em cache por 24 horas
- Cache invalidado automaticamente quando novos dados são importados
- Economia de recursos computacionais para cálculos complexos

## Exemplos de Uso

### Consultar Melhores Horários

```javascript
// Exemplo de chamada em JavaScript
const response = await fetch('/api/analytics/posting-time/best-times?platform=instagram&days=90');
const data = await response.json();

// Obter os melhores horários para segunda-feira
const mondayBestTimes = data.recommendations.best_times.Monday;
console.log(`Melhor horário: ${mondayBestTimes.recommended[0].formatted_hour}`);
console.log(`Engajamento médio: ${mondayBestTimes.recommended[0].avg_engagement}`);
```

### Analisar Desempenho por Tipo de Conteúdo

```javascript
// Exemplo de chamada em JavaScript
const response = await fetch('/api/analytics/posting-time/content-types');
const data = await response.json();

// Verificar qual tipo de conteúdo tem melhor desempenho
const contentTypes = Object.entries(data.performance)
  .sort((a, b) => b[1].avg_engagement - a[1].avg_engagement);

console.log(`Tipo de conteúdo mais efetivo: ${contentTypes[0][0]}`);
console.log(`Engajamento médio: ${contentTypes[0][1].avg_engagement}`);
```