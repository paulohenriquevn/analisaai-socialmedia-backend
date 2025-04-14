#!/usr/bin/env python3
"""
Script para testar o funcionamento da API e validar os tokens JWT.
"""

import sys
import os
import json
import requests
from urllib.parse import urljoin
import time

# Adicione o diretório pai ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure a URL base da API
BASE_URL = "http://localhost:5000/"

def login_and_get_token(username="testuser", password="password123"):
    """Faz login e obtém um token de acesso válido."""
    url = urljoin(BASE_URL, "api/auth/login")
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("tokens", {}).get("access_token")
        else:
            print(f"Erro ao fazer login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {str(e)}")
        return None

def test_influencers_endpoint(token):
    """Testa o endpoint de listagem de influenciadores."""
    if not token:
        print("Token não disponível. Não é possível testar o endpoint.")
        return
    
    url = urljoin(BASE_URL, "api/influencers")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"Testando endpoint: {url}")
        print(f"Usando token: {token[:15]}...")
        
        response = requests.get(url, headers=headers)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Resposta válida recebida!")
            
            # Verifica a estrutura da resposta
            if "influencers" in data:
                print(f"Número de influenciadores: {len(data['influencers'])}")
                
                # Verifica a paginação
                pagination = data.get("pagination", {})
                print(f"Detalhes da paginação: Página {pagination.get('page')}/{pagination.get('pages')}, Total: {pagination.get('total')}")
                
                if len(data['influencers']) == 0 and pagination.get('total', 0) > 0:
                    print("AVISO: Há influenciadores no banco mas nenhum foi retornado. Possível problema de paginação.")
                
                elif len(data['influencers']) == 0:
                    print("AVISO: Nenhum influenciador encontrado. Banco de dados pode estar vazio.")
                    print("Sugestão: Execute o script seed_influencers.py para adicionar exemplos.")
            else:
                print(f"ERRO: Formato da resposta não contém 'influencers'. Estrutura: {list(data.keys())}")
                print(f"Corpo da resposta: {response.text[:200]}...")
        
        elif response.status_code == 401:
            print("ERRO: Token inválido ou expirado. Problema de autenticação.")
            print(f"Resposta: {response.text}")
            
        elif response.status_code == 404:
            print("ERRO: Endpoint não encontrado. Verifique a URL e o registro do blueprint.")
            print(f"Resposta: {response.text}")
            
        elif response.status_code == 500:
            print("ERRO: Erro interno do servidor. Possível exceção não tratada.")
            print(f"Resposta: {response.text}")
            
        else:
            print(f"ERRO: Status code inesperado: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"Erro de conexão: {str(e)}")

def main():
    """Função principal que executa os testes."""
    print("=== Teste de Endpoints da API AnalisaAI ===\n")
    
    # Tenta fazer login e obter token
    print("1. Obtendo token de acesso...")
    token = login_and_get_token()
    
    if not token:
        print("\nNão foi possível obter um token. Verifique:\n" +
              "1. Se o servidor está rodando\n" +
              "2. Se as credenciais são válidas\n" +
              "3. Se o endpoint de login está funcionando\n")
        return
    
    # Testa o endpoint de influenciadores
    print("\n2. Testando endpoint de influenciadores...")
    test_influencers_endpoint(token)
    
    print("\n=== Sugestões de Solução ===")
    print("1. Verifique se há influenciadores no banco usando scripts/check_influencers.py")
    print("2. Adicione influenciadores de exemplo com scripts/seed_influencers.py")
    print("3. Confirme se a resposta JSON está no formato esperado pelo guia/frontend")
    print("4. Verifique os logs do servidor para erros não reportados")

if __name__ == "__main__":
    main()