# Guia Prático de Uso da API AnalisaAI

Este guia apresenta um passo a passo para utilizar a API do AnalisaAI Social Media para analisar o perfil da social_page 'Virginia Fonseca'. Você aprenderá a executar todas as chamadas (requests) da collection do Insomnia em uma sequência lógica.

## Requisitos

- [Insomnia](https://insomnia.rest/download) instalado
- Collection do Insomnia importada
- Credenciais de acesso à plataforma AnalisaAI

## 1. Jornada de Onboarding

### 1.1 Autenticação e Registro

#### 1.1.1 Status da Autenticação

**Request**: `GET {{BASE_URL}}/api/auth/auth-status`

```bash
# Nenhum parâmetro necessário
```

**Exemplo de resposta**:
```json
{
  "api_version": "1.0.0",
  "auth_status": "configured",
  "db_status": "connected"
}
```

#### 1.1.2 Registrar Usuário

**Request**: `POST {{BASE_URL}}/api/auth/register`

```json
{
  "username": "usuario_teste",
  "email": "usuario@teste.com",
  "password": "Senha@123"
}
```

**Exemplo de resposta**:
```json
{
  "message": "Usuário criado com sucesso",
  "user": {
    "id": 123,
    "username": "usuario_teste",
    "email": "usuario@teste.com"
  }
}
```

#### 1.1.3 Login

**Request**: `POST {{BASE_URL}}/api/auth/login`

```json
{
  "username": "usuario_teste",
  "password": "Senha@123"
}
```

**Exemplo de resposta**:
```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "user": {
    "id": 123,
    "username": "usuario_teste",
    "roles": ["user"]
  }
}
```

> **IMPORTANTE**: Configure a variável de ambiente `ACCESS_TOKEN` no Insomnia com o valor do access_token recebido. Para isso, clique com o botão direito no `access_token` da resposta, selecione "Set Environment Variable" e defina como "ACCESS_TOKEN".

#### 1.1.4 Verificar Perfil do Usuário

**Request**: `GET {{BASE_URL}}/api/auth/profile`

```bash
# Usando o token de acesso definido automaticamente
```

**Exemplo de resposta**:
```json
{
  "user": {
    "id": 123,
    "username": "usuario_teste",
    "email": "usuario@teste.com",
    "instagram_id": null,
    "facebook_id": null,
    "tiktok_id": null
  }
}
```

### 1.2 Conexão de Redes Sociais

#### 1.2.4 Cadastrar Rede Social Manualmente (Virginia no Instagram)

**Request**: `POST {{BASE_URL}}/api/social-media/connect`

```json
{
  "platform": "instagram",
  "username": "@virginia"
}
```

**Exemplo de resposta**:
```json
{
  "id": 123,
  "user_id": 123,
  "platform": "instagram",
  "external_id": "ig_a1b2c3d4e5f6g7h8",
  "username": "@virginia",
  "created_at": "2025-04-13T15:30:45Z"
}
```

## 2. Jornada de Influenciadores

### 2.1 Gerenciamento de Influenciadores

#### 2.1.1 Listar Influenciadores

**Request**: `GET {{BASE_URL}}/api/social_pages?page=1&per_page=10`

**Exemplo de resposta**:
```json
{
  "social_pages": [
    {
      "id": 1,
      "username": "virginia",
      "platform": "instagram",
      "followers_count": 45600000,
      "engagement_rate": 8.2,
      "social_score": 92.5
    },
    // Outros influenciadores...
  ],
  "pagination": {
    "total": 42,
    "page": 1,
    "per_page": 10,
    "total_pages": 5
  }
}
```

#### 2.1.2 Detalhes da social_page Virginia

**Request**: `GET {{BASE_URL}}/api/social_pages/1`  
(Supondo que o ID da Virginia seja 1, use o ID correto obtido na listagem)

**Exemplo de resposta**:
```json
{
  "id": 1,
  "username": "virginia",
  "full_name": "Virginia Fonseca",
  "platform": "instagram",
  "profile_url": "https://instagram.com/virginia",
  "profile_image": "https://instagram.fxxx.x.fbcdn.net/v/t51.xxx/virginia.jpg",
  "bio": "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br",
  "followers_count": 45600000,
  "following_count": 1580,
  "posts_count": 7850,
  "engagement_rate": 8.2,
  "social_score": 92.5,
  "categories": ["lifestyle", "beleza", "família"]
}
```

#### 2.1.3 Pesquisar Influenciador (Virginia)

**Request**: `POST {{BASE_URL}}/api/social_pages/lookup`

```json
{
  "username": "virginia",
  "platform": "instagram"
}
```

**Exemplo de resposta**:
```json
{
  "found": true,
  "social_page": {
    "id": 1,
    "username": "virginia",
    "full_name": "Virginia Fonseca",
    "platform": "instagram",
    "followers_count": 45600000,
    "engagement_rate": 8.2
  }
}
```

### 2.2 Busca Avançada

#### 2.2.1 Buscar Influenciadores (Lifestyle)

**Request**: `GET {{BASE_URL}}/api/search/social_pages?q=lifestyle&platform=instagram&min_followers=1000000`

**Exemplo de resposta**:
```json
{
  "results": [
    {
      "id": 1,
      "username": "virginia",
      "platform": "instagram",
      "followers_count": 45600000,
      "engagement_rate": 8.2,
      "match_score": 95.3
    },
    // Outros influenciadores...
  ],
  "total": 24,
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 3
  }
}
```

#### 2.2.2 Listar Categorias

**Request**: `GET {{BASE_URL}}/api/search/categories`

**Exemplo de resposta**:
```json
{
  "categories": [
    {"id": 1, "name": "lifestyle", "count": 124},
    {"id": 2, "name": "moda", "count": 98},
    {"id": 3, "name": "beleza", "count": 87},
    {"id": 4, "name": "família", "count": 65},
    // Outras categorias...
  ]
}
```

## 3. Jornada de Análise de Dados

### 3.1 Analytics Gerais

#### 3.1.1 Crescimento da social_page Virginia

**Request**: `GET {{BASE_URL}}/api/analytics/social_page/1/growth`  
(Supondo que o ID da Virginia seja 1)

**Exemplo de resposta**:
```json
{
  "social_page_id": 1,
  "username": "virginia",
  "platform": "instagram",
  "growth_metrics": {
    "followers": {
      "current": 45600000,
      "previous": 45200000,
      "growth_rate": 0.88,
      "growth_raw": 400000
    },
    "engagement": {
      "current": 8.2,
      "previous": 7.9,
      "growth_rate": 3.8,
      "growth_raw": 0.3
    },
    "posts_frequency": {
      "current": 2.3,
      "previous": 2.1,
      "growth_rate": 9.5,
      "growth_raw": 0.2
    }
  },
  "period": "30 dias"
}
```

#### 3.1.2 Benchmarks de Plataforma (Instagram)

**Request**: `GET {{BASE_URL}}/api/analytics/platform/benchmarks?platform=instagram`

**Exemplo de resposta**:
```json
{
  "platform": "instagram",
  "benchmarks": {
    "engagement_rate": {
      "overall": 2.4,
      "by_follower_count": [
        {"range": "1K-10K", "value": 4.2},
        {"range": "10K-100K", "value": 3.1},
        {"range": "100K-1M", "value": 2.3},
        {"range": "1M+", "value": 1.8}
      ]
    },
    "post_frequency": {
      "overall": 3.2,
      "by_category": [
        {"category": "lifestyle", "value": 4.5},
        {"category": "moda", "value": 3.8},
        {"category": "beleza", "value": 2.9}
      ]
    }
  }
}
```

### 3.2 Análise de Sentimento

#### 3.2.1 Analisar Sentimento de um Texto

**Request**: `POST {{BASE_URL}}/api/analytics/sentiment/analyze`

```json
{
  "text": "Adoro os produtos da Virginia, super recomendo! Qualidade incrível e preço justo."
}
```

**Exemplo de resposta**:
```json
{
  "text": "Adoro os produtos da Virginia, super recomendo! Qualidade incrível e preço justo.",
  "sentiment": "positive",
  "score": 0.85,
  "entities": [
    {"text": "Virginia", "type": "PERSON"},
    {"text": "produtos", "type": "PRODUCT"}
  ],
  "keywords": ["adoro", "super", "recomendo", "qualidade", "incrível", "preço justo"]
}
```

#### 3.2.4 Sentimento da social_page Virginia

**Request**: `GET {{BASE_URL}}/api/analytics/sentiment/social_page/1/sentiment`  
(Supondo que o ID da Virginia seja 1)

**Exemplo de resposta**:
```json
{
  "social_page_id": 1,
  "username": "virginia",
  "platform": "instagram",
  "overall_sentiment": {
    "positive": 76.3,
    "neutral": 18.5,
    "negative": 5.2,
    "sentiment_score": 0.71
  },
  "sentiment_trends": [
    {"date": "2025-03-01", "score": 0.68},
    {"date": "2025-03-15", "score": 0.72},
    {"date": "2025-04-01", "score": 0.71}
  ],
  "top_positive_topics": ["produtos", "conteúdo", "família"],
  "top_negative_topics": ["preço", "entrega", "atendimento"],
  "sample_count": 1250,
  "period": "30 dias"
}
```

#### 3.2.6 Análise em Lote (Comentários da Virginia)

**Request**: `POST {{BASE_URL}}/api/analytics/sentiment/batch-analyze`

```json
{
  "texts": [
    "Amo os produtos da Virginia, tudo muito bem feito!",
    "Comprei o batom e a qualidade não é tão boa quanto esperava.",
    "Adoro seus vídeos com a família, muito divertidos e autênticos!"
  ]
}
```

**Exemplo de resposta**:
```json
{
  "results": [
    {
      "text": "Amo os produtos da Virginia, tudo muito bem feito!",
      "sentiment": "positive",
      "score": 0.82
    },
    {
      "text": "Comprei o batom e a qualidade não é tão boa quanto esperava.",
      "sentiment": "negative",
      "score": -0.34
    },
    {
      "text": "Adoro seus vídeos com a família, muito divertidos e autênticos!",
      "sentiment": "positive",
      "score": 0.91
    }
  ],
  "summary": {
    "positive": 2,
    "neutral": 0,
    "negative": 1,
    "average_score": 0.46
  }
}
```

### 3.3 Otimização de Horários

#### 3.3.1 Melhores Horários para Postagem

**Request**: `GET {{BASE_URL}}/api/analytics/posting-time/best-times`

**Exemplo de resposta**:
```json
{
  "platform": "instagram",
  "best_posting_times": {
    "monday": ["10:00", "18:00", "21:00"],
    "tuesday": ["09:00", "17:00", "20:00"],
    "wednesday": ["10:00", "15:00", "19:00"],
    "thursday": ["11:00", "16:00", "21:00"],
    "friday": ["12:00", "17:00", "22:00"],
    "saturday": ["11:00", "15:00", "20:00"],
    "sunday": ["12:00", "16:00", "19:00"]
  },
  "overall_best_time": "19:00",
  "overall_best_day": "wednesday",
  "engagement_by_hour": [
    {"hour": "08:00", "engagement": 2.1},
    {"hour": "09:00", "engagement": 3.2},
    // Outras horas...
    {"hour": "22:00", "engagement": 4.3}
  ]
}
```

#### 3.3.2 Performance por Tipo de Conteúdo (Virginia)

**Request**: `GET {{BASE_URL}}/api/analytics/posting-time/content-types?social_page_id=1`  
(Supondo que o ID da Virginia seja 1)

**Exemplo de resposta**:
```json
{
  "social_page_id": 1,
  "username": "virginia",
  "platform": "instagram",
  "content_performance": {
    "image": {
      "engagement_rate": 7.8,
      "best_time": "18:00",
      "best_day": "wednesday"
    },
    "video": {
      "engagement_rate": 9.2,
      "best_time": "20:00",
      "best_day": "sunday"
    },
    "carousel": {
      "engagement_rate": 8.5,
      "best_time": "19:00",
      "best_day": "thursday"
    }
  },
  "recommended_content_type": "video"
}
```

#### 3.3.3 Análise por Dia da Semana (Virginia)

**Request**: `GET {{BASE_URL}}/api/analytics/posting-time/days-of-week?social_page_id=1`  
(Supondo que o ID da Virginia seja 1)

**Exemplo de resposta**:
```json
{
  "social_page_id": 1,
  "username": "virginia",
  "platform": "instagram",
  "day_performance": [
    {"day": "monday", "engagement_rate": 7.2, "post_count": 42},
    {"day": "tuesday", "engagement_rate": 7.5, "post_count": 38},
    {"day": "wednesday", "engagement_rate": 8.9, "post_count": 45},
    {"day": "thursday", "engagement_rate": 8.1, "post_count": 41},
    {"day": "friday", "engagement_rate": 8.7, "post_count": 52},
    {"day": "saturday", "engagement_rate": 9.3, "post_count": 58},
    {"day": "sunday", "engagement_rate": 8.5, "post_count": 47}
  ],
  "best_day": "saturday",
  "worst_day": "monday"
}
```

#### 3.3.5 Recomendações Personalizadas (Virginia)

**Request**: `GET {{BASE_URL}}/api/analytics/posting-time/recommendations?social_page_id=1`  
(Supondo que o ID da Virginia seja 1)

**Exemplo de resposta**:
```json
{
  "social_page_id": 1,
  "username": "virginia",
  "platform": "instagram",
  "personalized_recommendations": [
    {
      "content_type": "video",
      "subject": "família",
      "best_time": "20:00",
      "best_day": "sunday",
      "expected_engagement": 9.8
    },
    {
      "content_type": "carousel",
      "subject": "produtos",
      "best_time": "19:00",
      "best_day": "thursday",
      "expected_engagement": 9.1
    },
    {
      "content_type": "image",
      "subject": "lifestyle",
      "best_time": "18:00",
      "best_day": "wednesday",
      "expected_engagement": 8.3
    }
  ],
  "optimal_posting_schedule": {
    "monday": null,
    "tuesday": null,
    "wednesday": {"time": "18:00", "content_type": "image", "subject": "lifestyle"},
    "thursday": {"time": "19:00", "content_type": "carousel", "subject": "produtos"},
    "friday": null,
    "saturday": null,
    "sunday": {"time": "20:00", "content_type": "video", "subject": "família"}
  }
}
```

## Dicas de Uso

1. **Autenticação**: Sempre comece pela jornada de onboarding para obter os tokens de acesso.
2. **Tokens Expirados**: Se receber erro 401, use o endpoint de renovação de token (1.1.4).
3. **IDs Dinâmicos**: Substitua os IDs nos exemplos pelos IDs reais obtidos nas consultas.
4. **Parâmetros Opcionais**: Muitos endpoints aceitam parâmetros adicionais que podem ser explorados.
5. **Filtragem**: Use os parâmetros de filtragem para refinar resultados (plataforma, categoria, etc.).

## Solução de Problemas

- **Erro 401**: Token expirado - renovar token
- **Erro 400**: Verificar parâmetros da requisição
- **Erro 404**: Verificar se o ID do recurso existe
- **Erro 429**: Muitas requisições - aguardar alguns minutos
- **Erro 500**: Erro interno do servidor - contatar suporte

## Próximos Passos

1. Explore as funcionalidades de análise de sentimento com conteúdos reais da Virginia
2. Compare o desempenho dela com outros influenciadores do mesmo segmento
3. Utilize as recomendações de horário para otimizar seu próprio calendário de conteúdo
4. Analise tendências de crescimento ao longo do tempo