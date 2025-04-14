# Solução para Problemas na Listagem de Influenciadores

Este documento apresenta as possíveis causas e soluções para o problema de listagem de influenciadores na API AnalisaAI.

## Possíveis Causas do Problema

Após análise do código e da estrutura do sistema, identificamos as seguintes possíveis causas para o problema:

1. **Banco de dados vazio**: Não há influenciadores cadastrados no banco de dados.
2. **Inconsistência na resposta JSON**: Diferença entre o formato esperado (`pagination`) e o retornado (`meta`).
3. **Problemas com paginação SQLAlchemy**: Incompatibilidade ou erro na paginação dos resultados.
4. **Problemas de autenticação**: JWT não está sendo validado corretamente.
5. **Erro no registro do Blueprint**: A rota não está registrada corretamente.

## Como Verificar e Corrigir o Problema

### Passo 1: Verificar a Existência de Dados

Execute o script de verificação para confirmar se existem influenciadores no banco de dados:

```bash
python scripts/check_influencers.py
```

Se não houver influenciadores, execute o script de seed para adicionar exemplos:

```bash
python scripts/seed_influencers.py
```

### Passo 2: Corrigir o Formato da Resposta

O guia prático espera que o endpoint retorne os dados no seguinte formato:

```json
{
  "influencers": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 42,
    "total_pages": 5
  }
}
```

No entanto, a implementação original retornava:

```json
{
  "influencers": [...],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 42,
    "pages": 5
  }
}
```

**Solução**: Modificamos o código em `app/api/influencers/routes/__init__.py` para usar `pagination` em vez de `meta` na resposta.

### Passo 3: Verificar a Autenticação

Se o problema persistir, pode estar relacionado à autenticação JWT. Execute o script para testar a API com tokens válidos:

```bash
python scripts/test_api_endpoints.py
```

### Passo 4: Solucionar Problemas de Paginação

Se houver problemas com a função `paginate()` do SQLAlchemy, você pode implementar uma solução alternativa:

```python
# Implementação alternativa sem usar paginate()
query = Influencer.query
if platform:
    query = query.filter_by(platform=platform)

total = query.count()
items = query.order_by(Influencer.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
```

## Verificação Final

Após aplicar as correções, execute novamente o guia prático e verifique se o endpoint de listagem de influenciadores está funcionando corretamente.

## Lembre-se

1. Certifique-se de que o servidor está rodando quando executar os testes
2. Verifique os logs do servidor para mensagens de erro detalhadas
3. Confirme que o token JWT está válido e sendo enviado corretamente

## Comandos para Teste Rápido

Reinicie o servidor para aplicar as mudanças:

```bash
./restart_app.sh
```

Teste o endpoint com um token válido:

```bash
# Obtenha um token válido fazendo login
TOKEN=$(python -c 'from scripts.test_api_endpoints import login_and_get_token; print(login_and_get_token())')

# Teste o endpoint usando curl
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/influencers
```