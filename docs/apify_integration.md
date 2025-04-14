# Apify API Integration

Este documento descreve como configurar e usar a integração com o Apify API para buscar dados de redes sociais no AnalisaAI.

## O que é o Apify?

Apify é uma plataforma que permite extrair dados da web de forma automatizada e escalável. Ela oferece diversos "atores" pré-construídos para extrair dados de várias plataformas como Instagram, TikTok, Facebook, entre outras.

## Configuração

Para usar a integração com o Apify, você precisa:

1. Criar uma conta no [Apify](https://apify.com/)
2. Obter uma API Key no painel de controle do Apify
3. Configurar a variável de ambiente `APIFY_API_KEY` com sua chave

### Configurando a API Key

A chave da API do Apify deve ser adicionada às variáveis de ambiente da aplicação. Você pode fazer isso:

- Diretamente no ambiente (recomendado para produção):
  ```bash
  export APIFY_API_KEY=sua_api_key_aqui
  ```

- No arquivo `.env` (para desenvolvimento):
  ```
  APIFY_API_KEY=sua_api_key_aqui
  ```

## Como funciona

A integração com o Apify API foi implementada como uma camada adicional de fallback no fluxo de busca de informações de perfis de redes sociais:

1. A aplicação primeiro tenta usar as APIs oficiais de cada plataforma
2. Se não for possível, tenta usar o Apify API
3. Se ainda não for possível, usa métodos de web scraping internos como último recurso

Essa abordagem em camadas garante maior confiabilidade na busca de dados.

## Endpoints de teste

A aplicação fornece endpoints de teste para verificar a integração com o Apify API:

- `GET /api/social_media/apify/instagram?username=nome_usuario` - Busca perfil do Instagram
- `GET /api/social_media/apify/tiktok?username=nome_usuario` - Busca perfil do TikTok
- `GET /api/social_media/apify/facebook?username=nome_usuario` - Busca perfil do Facebook

Todos os endpoints requerem autenticação (token JWT) e retornam os dados do perfil no formato padrão da API.

## Plataformas suportadas

A integração atual suporta as seguintes plataformas:

| Plataforma | Ator Apify | ID do Ator | Suporte |
|------------|------------|------------|---------|
| Instagram  | Instagram Scraper | shu8hvrXbJbY3Eb9W | Completo |
| TikTok     | TikTok Scraper | qhzXbQKch8FfpyG4T | Completo |
| Facebook   | Facebook Page Scraper | dtrungtin/facebook-page-scraper | Completo |

## Formato dos dados

Os dados retornados pelos atores do Apify são transformados para o formato padrão usado pela API AnalisaAI, garantindo consistência independentemente da fonte dos dados.

## Considerações sobre uso

- O Apify possui limites de uso baseados em seu plano de assinatura
- As consultas são feitas de forma assíncrona e podem levar alguns segundos para completar
- É recomendável implementar cache para reduzir o número de requisições ao Apify API
- Certifique-se de que os atores utilizados estão ativos e atualizados

## Exemplos de uso programático

Para usar o serviço Apify na sua aplicação:

```python
from app.services.apify_service import ApifyService

# Buscar perfil do Instagram
profile = ApifyService.fetch_instagram_profile('usuario_instagram')

# Buscar perfil do TikTok
profile = ApifyService.fetch_tiktok_profile('usuario_tiktok')

# Buscar perfil do Facebook
profile = ApifyService.fetch_facebook_profile('usuario_facebook')
```

O serviço utiliza a biblioteca oficial do Apify para Python (`apify-client`) para acessar a API, conforme o exemplo abaixo:

```python
from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("<YOUR_API_TOKEN>")

# Prepare the Actor input
run_input = {
    "directUrls": ["https://www.instagram.com/usuario/"],
    "resultsType": "details",
    "addParentData": True
}

# Run the actor and wait for it to finish
run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

Nossa implementação cuida de todo o processo de chamada da API, recuperação dos resultados e transformação para o formato padrão da aplicação.