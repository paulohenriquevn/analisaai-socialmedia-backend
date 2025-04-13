# Solucionando Problemas com Tokens JWT

Este documento fornece orientações para resolver problemas comuns relacionados a autenticação e tokens JWT no sistema AnalisaAI Social Media.

## Problema: "Invalid token"

Se você estiver recebendo o erro "Invalid token" ao tentar acessar endpoints protegidos, verifique as seguintes possibilidades:

### 1. Formato do token na requisição

**Solução**: O token de acesso deve ser enviado no formato correto:

```
Authorization: Bearer seu_token_aqui
```

Verifique se:
- O prefixo "Bearer" está presente e tem um espaço após ele
- O token está completo e não foi truncado
- Não há espaços ou caracteres extras no token

**No Insomnia**:
- Verifique a autenticação na aba "Auth"
- Selecione "Bearer Token"
- Cole o token access_token recebido durante o login

### 2. Expiração do token

Os tokens de acesso expiram após 1 hora. Se o token expirou, você receberá um erro "Token has expired".

**Solução**: Use o endpoint de refresh para obter um novo token de acesso.

1. Acesse a rota `/api/auth/refresh` com o refresh_token no cabeçalho
2. Copie o novo access_token retornado
3. Atualize a variável de ambiente ACCESS_TOKEN com o novo valor

### 3. Token inválido ou malformado

Se você estiver usando um token incompleto, modificado ou gerado incorretamente, receberá o erro "Invalid token".

**Solução**:
1. Execute o fluxo de login novamente para obter tokens frescos
2. Verifique se o token não foi modificado durante a cópia/colagem
3. Verifique se não há quebras de linha ou espaços extras no token

### 4. Configuração de ambiente

Para testes, certifique-se de que todas as variáveis de ambiente necessárias estão definidas corretamente.

**Solução**:
1. Verifique se a SECRET_KEY e JWT_SECRET_KEY estão definidas se estiver em ambiente de produção
2. Se estiver em ambiente de desenvolvimento, os valores padrão devem funcionar

### 5. Dicas para o Insomnia

Para configurar corretamente os tokens no Insomnia:

1. **Fazer login e armazenar tokens automaticamente**:
   - Na resposta do login, clique com o botão direito do mouse no token de acesso
   - Selecione "Set Environment Variable" e defina como ACCESS_TOKEN
   - Repita o processo para o REFRESH_TOKEN

2. **Configurar a visualização de tokens específicos**:
   - Edite o ambiente no canto superior direito
   - Adicione novas variáveis ACCESS_TOKEN e REFRESH_TOKEN
   - Mantenha esses valores atualizados após cada login/refresh

3. **Verificar se o token está sendo enviado**:
   - Na requisição, vá para a aba "Timeline"
   - Verifique se o cabeçalho Authorization está sendo enviado corretamente

## Outras dicas úteis

### Testar a autenticação

Para verificar rapidamente se sua autenticação está funcionando:

1. Use o endpoint `/api/auth/profile` com seu token de acesso
2. Se funcionar, você verá seus dados de usuário
3. Se falhar, você terá uma mensagem de erro mais detalhada

### Limpar cookies e armazenamento local

Se estiver testando em um navegador:

1. Limpe os cookies e o armazenamento local do navegador
2. Faça login novamente para obter tokens frescos

### Verificar logs do servidor

Se você tiver acesso aos logs do servidor, eles geralmente contêm informações mais detalhadas sobre problemas de autenticação.

Procure mensagens de erro relacionadas a:
- JWT invalid signatures
- Payload validation errors
- Token expiration issues

## Medidas adicionais

Se nenhuma das soluções acima resolver o problema:

1. **Limpe completamente o ambiente de teste**:
   - Exclua todas as variáveis de ambiente no Insomnia
   - Reconfigure todas as variáveis necessárias
   - Faça login novamente para obter tokens frescos

2. **Verifique a configuração do servidor**:
   - Confirme se a configuração JWT está correta
   - Verifique se a aplicação está usando a mesma SECRET_KEY para validação

3. **Contate suporte técnico**:
   - Forneça os detalhes completos do erro
   - Inclua capturas de tela da configuração (sem expor os tokens)
   - Descreva as etapas exatas para reproduzir o problema