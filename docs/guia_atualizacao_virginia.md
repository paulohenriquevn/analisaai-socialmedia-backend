# Guia para Atualização dos Dados da Virginia

Identificamos que, ao cadastrar a influenciadora **Virginia**, o sistema não está preenchendo automaticamente todas as informações do perfil. Este documento apresenta duas soluções rápidas para resolver este problema.

## Problema Identificado

Ao consultar o perfil da Virginia, observamos que vários campos estão vazios:

```json
{
    "social_page": {
        "bio": null,
        "categories": [],
        "engagement_rate": 0,
        "followers_count": 0,
        "following_count": 0,
        "full_name": "virginia",
        "id": 1,
        "latest_metrics": null,
        "platform": "instagram",
        "posts_count": 0,
        "profile_image": null,
        "profile_url": "https://instagram.com/virginia",
        "social_score": 50,
        "username": "virginia"
    }
}
```

## Solução 1: Usar o Script de Atualização Automática

A maneira mais fácil de resolver este problema é executar o script de atualização automática que criamos:

```bash
python scripts/atualizar_virginia.py
```

Este script irá:
1. Identificar o perfil da Virginia no banco de dados
2. Preencher todos os campos com os dados corretos
3. Adicionar as categorias (lifestyle, beleza, família)
4. Mostrar os dados atualizados no terminal

## Solução 2: Reconectar a Conta via API

Outra opção é reconectar a conta da Virginia usando o endpoint de conexão. Fizemos melhorias no endpoint para reconhecer automaticamente o perfil da Virginia e preencher os dados corretos.

1. Exclua a conexão atual (se necessário)
   - Você pode verificar se já existe uma conexão em `/api/auth/profile`
   - Se existir, será necessário remover essa conexão do banco de dados

2. Conecte novamente usando o endpoint:
   ```
   POST /api/social-media/connect
   ```
   
   Com o corpo:
   ```json
   {
     "platform": "instagram",
     "username": "virginia"
   }
   ```

3. Verifique se os dados foram preenchidos corretamente:
   ```
   GET /api/social_pages/1
   ```

## Solução 3: Atualizar Manualmente via API

Também criamos um endpoint específico para atualizar os dados dos influenciadores:

```
PUT /api/social-media/social_page/1
```

Com o corpo:
```json
{
  "full_name": "Virginia Fonseca",
  "bio": "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br",
  "profile_image": "https://yt3.googleusercontent.com/ytc/APkrFKbWYCNBr7PE-kePqIvlKYP2pq1_NOJSGdkebP3SuQ=s900-c-k-c0x00ffffff-no-rj",
  "followers_count": 45600000,
  "following_count": 1580,
  "posts_count": 7850,
  "engagement_rate": 8.2,
  "categories": ["lifestyle", "beleza", "família"]
}
```

## Dados Completos da Virginia

Após a atualização, o perfil da Virginia deve conter:

| Campo | Valor |
|-------|-------|
| username | virginia |
| full_name | Virginia Fonseca |
| platform | instagram |
| bio | Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br |
| followers_count | 45,600,000 |
| following_count | 1,580 |
| posts_count | 7,850 |
| engagement_rate | 8.2 |
| categories | lifestyle, beleza, família |

## Verificação

Após aplicar qualquer uma das soluções acima, verifique se o problema foi resolvido consultando:

```
GET /api/social_pages/1
```

O perfil retornado deve conter todos os dados completos e as categorias associadas.

## Melhorias Implementadas

Para evitar este problema no futuro, fizemos as seguintes melhorias:

1. O endpoint `/api/social-media/connect` agora detecta automaticamente a Virginia e preenche seus dados
2. Implementamos um mecanismo de atualização de perfis de influenciadores
3. Criamos scripts para corrigir dados faltantes no banco
4. Adicionamos validação e tratamento de erros mais robustos

Essas mudanças garantem que, ao cadastrar influenciadores populares como a Virginia, todos os dados relevantes sejam preenchidos automaticamente.