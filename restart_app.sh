#!/bin/bash
# Script para reiniciar a aplicação Flask

echo "Parando a aplicação Flask atual..."
pkill -f "python run.py" || echo "Nenhuma instância encontrada."

# Aguarde um momento para garantir que o servidor anterior foi encerrado
sleep 2

echo "Iniciando a aplicação Flask..."
cd "$(dirname "$0")"
python3 run.py > logs/flask.log 2>&1 &

# Aguarde a inicialização
sleep 2
echo "Aplicação reiniciada com sucesso!"

# Exiba informações úteis
echo ""
echo "A aplicação está rodando em: http://localhost:5000"
echo "Logs disponíveis em: logs/flask.log"
echo ""
echo "Para verificar a solução para a listagem de influenciadores:"
echo "1. Execute: python scripts/check_influencers.py"
echo "2. Se necessário: python scripts/seed_influencers.py"
echo "3. Teste a API: python scripts/test_api_endpoints.py"
