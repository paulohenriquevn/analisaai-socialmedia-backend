#!/usr/bin/env python3
"""
Script para verificar a existência de influenciadores no banco de dados.
Este script lista todos os influenciadores no banco de dados e verifica o funcionamento da API.
"""

import sys
import os
from flask import json

# Adicione o diretório pai ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importe após ajustar o path
from app import create_app
from app.models.influencer import Influencer
from app.extensions import db

# Crie uma instância do app
app = create_app()

def check_database():
    """Verificar influenciadores no banco de dados."""
    with app.app_context():
        # Contar influenciadores
        influencer_count = Influencer.query.count()
        print(f"Total de influenciadores no banco de dados: {influencer_count}")
        
        # Listar os primeiros 5 influenciadores (se existirem)
        if influencer_count > 0:
            influencers = Influencer.query.limit(5).all()
            print("\nPrimeiros 5 influenciadores:")
            for infl in influencers:
                print(f"ID: {infl.id}, Username: {infl.username}, Platform: {infl.platform}, Followers: {infl.followers_count}")
        else:
            print("\nNenhum influenciador encontrado no banco de dados.")
            print("Isso pode ser a causa do problema na listagem de influenciadores.")
            
def test_api_endpoint():
    """Testar o endpoint da API usando o cliente de teste do Flask."""
    with app.test_client() as client:
        # Criar um token falso para teste
        from app.services.security_service import create_test_token
        token = create_test_token(1)  # ID de usuário 1
        
        # Testar o endpoint
        response = client.get('/api/influencers', 
                             headers={'Authorization': f'Bearer {token}'})
        
        print("\nResposta da API:")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"Influenciadores retornados: {len(data.get('influencers', []))}")
            print(f"Meta: {data.get('meta', {})}")
        else:
            print(f"Erro na resposta: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    print("=== Verificação de Influenciadores ===")
    check_database()
    
    print("\n=== Teste do Endpoint da API ===")
    try:
        test_api_endpoint()
    except Exception as e:
        print(f"Erro ao testar o endpoint: {str(e)}")
        
    print("\n=== Sugestões de Solução ===")
    print("1. Se não há influenciadores no banco, adicione alguns usando o endpoint de lookup")
    print("2. Verifique se o modelo Influencer está correto e se a tabela existe no banco")
    print("3. Confira se há problemas na paginação do SQLAlchemy")
    print("4. Teste se a autenticação JWT está funcionando corretamente")