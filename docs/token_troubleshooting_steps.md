# Guia Passo a Passo para Resolver "Invalid token"

Se você estiver recebendo o erro "Invalid token" ao usar a API AnalisaAI Social Media, siga este guia passo a passo para identificar e resolver o problema.

## Passo 1: Verificar se o Token Está Expirado

Os tokens de acesso expiram após 1 hora por padrão. Para verificar se o token expirou:

```bash
# Use o script de teste de token
python scripts/test_token.py "seu_token_aqui"
```

Se o token estiver expirado, a saída indicará isso com uma mensagem "❌ INVALID TOKEN: Expired".

**Solução**: Obtenha um novo token usando o endpoint de refresh ou fazendo login novamente.

## Passo 2: Verificar o Formato do Token na Requisição

Uma causa comum de erros é o formato incorreto do cabeçalho de autorização.

**Verificação**:
1. Abra o Insomnia
2. Vá para a requisição que está falhando
3. Vá para a aba "Auth"
4. Certifique-se de que:
   - O tipo de autenticação está definido como "Bearer Token"
   - O token não contém espaços extras, quebras de linha ou outros caracteres inválidos
   - O prefixo "Bearer" não foi incluído manualmente (o Insomnia adiciona automaticamente)

**Solução**: Corrija o formato do token conforme necessário.

## Passo 3: Verificar se o Token Foi Gerado Corretamente

Um "Invalid token" também pode indicar problemas na geração do token.

**Verificação**:
1. Use a coleção de depuração para fazer login:
   ```
   POST /api/auth/login
   
   {
     "username": "testuser",
     "password": "SecurePassword123"
   }
   ```

2. Verifique a resposta para confirmar que tokens válidos foram gerados
3. Copie manualmente o access_token para uso em outras requisições

**Solução**: Se o login não gerar tokens válidos, verifique as credenciais e tente criar um novo usuário de teste.

## Passo 4: Verificar a Configuração do Ambiente

Problemas de configuração do servidor podem afetar a validação de tokens.

**Verificação**:
1. Use o endpoint de depuração para verificar a configuração:
   ```
   GET /api/auth/auth-status
   ```

2. Verifique a resposta para garantir que a autenticação está funcionando corretamente

**Solução**: Se a configuração estiver incorreta, verifique as variáveis de ambiente do servidor e reinicie-o se necessário.

## Passo 5: Resolver Problemas com o Insomnia

O Insomnia pode às vezes ter problemas ao gerenciar variáveis de ambiente.

**Solução**:
1. Crie um novo ambiente no Insomnia
2. Defina as variáveis necessárias:
   - `BASE_URL`: "http://localhost:5000" (ou URL apropriada)
   - `ACCESS_TOKEN`: Deixe em branco inicialmente
   - `REFRESH_TOKEN`: Deixe em branco inicialmente

3. Faça login e atualize manualmente as variáveis de token
4. Teste uma requisição que exija autenticação

## Passo 6: Verificar Incompatibilidades de Tipo de Token

Se você estiver usando um token de atualização como token de acesso ou vice-versa, isso causará um erro "Invalid token".

**Verificação**:
1. Use o script de teste de token para verificar o tipo:
   ```bash
   python scripts/test_token.py "seu_token_aqui"
   ```

2. Verifique se na seção "PAYLOAD" o campo "type" está correto (normalmente "access" para tokens de acesso)

**Solução**: Use o token correto para cada tipo de requisição.

## Passo 7: Verificar Configurações CORS (para aplicações web)

Se você estiver usando o Insomnia, isso não será um problema, mas para clientes web, problemas de CORS podem afetar a autenticação.

**Verificação**:
1. Examine os cabeçalhos de resposta para ver se há problemas de CORS
2. Verifique se o servidor está configurado para permitir o cabeçalho Authorization

**Solução**: Isso não deve ser um problema com o Insomnia, mas é bom verificar as configurações do servidor.

## Passo 8: Executar Testes Manuais com curl

Às vezes, pode ser útil testar a API usando ferramentas mais básicas como curl para isolar problemas.

**Verificação**:
```bash
# Obter token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePassword123"}'

# Usar token (substitua TOKEN pelo token obtido)
curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer TOKEN"
```

**Solução**: Se o curl funcionar mas o Insomnia não, o problema está na configuração do cliente.

## Passo 9: Tentar com um Usuário Diferente

Às vezes, problemas específicos do usuário podem afetar a autenticação.

**Solução**:
1. Crie um novo usuário de teste
2. Tente fazer login com esse novo usuário
3. Teste as APIs protegidas com o novo token

## Passo 10: Verificar Versões das Bibliotecas

Problemas de incompatibilidade entre bibliotecas podem causar erros de autenticação.

**Verificação**:
1. Verifique a versão do Flask-JWT-Extended em uso
2. Confirme que todas as dependências estão atualizadas

**Solução**: Se houver problemas de versão, atualize as bibliotecas ou ajuste a configuração para manter a compatibilidade.

## Contato para Suporte

Se você seguiu todos estes passos e ainda está enfrentando problemas, contate o suporte técnico com:

1. O token exato que está causando o problema (com partes sensíveis ocultadas)
2. A resposta completa do erro
3. Os resultados do script de teste de token
4. Capturas de tela da configuração do Insomnia
5. Logs do servidor, se disponíveis

O suporte técnico poderá fornecer assistência mais específica para o seu caso.