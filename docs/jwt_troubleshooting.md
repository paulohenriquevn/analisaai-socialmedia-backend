# Solução de Problemas de Autenticação JWT

Este documento contém instruções sobre como resolver problemas comuns de autenticação JWT no backend do Analisa.ai Social Media.

## Problema: Token Inválido

Quando você recebe erros "Invalid token" (Token Inválido) ao tentar acessar endpoints protegidos, mesmo após fazer login novamente, isso pode ser causado por uma das seguintes razões:

1. **JWT_SECRET_KEY alterada**: O servidor está usando uma chave secreta diferente da que foi usada para gerar o token
2. **Conflito de cache**: A implementação de cache está interferindo na validação do token
3. **Ordem de inicialização**: A ordem de inicialização das extensões Flask pode afetar a validação do token
4. **Ambiente desatualizado**: Variáveis de ambiente não estão sendo carregadas corretamente

## Solução Rápida

Para resolver problemas de JWT, execute os scripts de diagnóstico e correção:

```bash
# Teste a autenticação JWT
python test_jwt.py

# Se o teste falhar, execute o script de correção
python fix_jwt_app.py

# Reinicie a aplicação após as correções
./restart_app.sh

# Faça login novamente para obter novos tokens
```

## Verificações Manuais

Se os scripts não resolverem o problema, verifique:

1. **Arquivo .env**: Verifique se as chaves JWT_SECRET_KEY e SECRET_KEY estão definidas corretamente
   ```
   JWT_SECRET_KEY=sua-chave-secreta
   SECRET_KEY=outra-chave-secreta
   ```

2. **Ordem de Inicialização**: Em `app/extensions.py`, verifique se o JWT é inicializado antes do cache
   ```python
   # Ordem correta:
   jwt.init_app(app)
   # Registrar handlers de erro JWT
   register_jwt_handlers(jwt)
   # Depois inicializar cache
   cache.init_app(app)
   ```

3. **Cache Personalizado**: Certifique-se que a configuração do cache não está interferindo
   ```python
   cache_config = {
       'CACHE_TYPE': 'SimpleCache',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'analisaai_',  # Prefixo para evitar colisões
   }
   ```

4. **Logs**: Verifique os logs em `logs/analisaai.log` para erros relacionados à JWT

## Gerando Novos Tokens

Se você precisar gerar novos tokens manualmente, use:

```python
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

# Gere tokens com uma hora e 30 dias de validade respectivamente
access_token = create_access_token(
    identity=user_id,
    expires_delta=timedelta(hours=1)
)

refresh_token = create_refresh_token(
    identity=user_id, 
    expires_delta=timedelta(days=30)
)
```

## Análise de Tokens JWT

Para depurar tokens JWT, você pode usar a ferramenta online [jwt.io](https://jwt.io/).

1. Cole seu token JWT no campo esquerdo
2. Verifique os campos `payload` e `exp` (expiração)
3. Se quiser verificar a assinatura, insira sua `JWT_SECRET_KEY` no campo "Verify Signature"

## Referências

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Documentação do Python JWT](https://pyjwt.readthedocs.io/en/latest/)
- [Best Practices for JWT](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)