#!/usr/bin/env python3
"""
Script para importar e atualizar os dados do perfil da Virginia como influencer.
Este script simula uma chamada à API /api/social-media/connect e depois
atualiza os dados com informações mais completas.
"""

import sys
import os
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicione o diretório pai ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importe após ajustar o path
from app import create_app
from app.models.user import User
from app.models.social_page import Influencer, Category
from app.extensions import db

# Crie uma instância do app
app = create_app()

# Base URL da API
BASE_URL = "http://localhost:5000"

def login(username, password):
    """Faz login e obtém tokens de acesso."""
    url = f"{BASE_URL}/api/auth/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            logger.info("Login bem-sucedido")
            return response.json()
        else:
            logger.error(f"Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao conectar para login: {str(e)}")
        return None

def connect_social_media(token, platform, username):
    """Conecta uma conta de mídia social."""
    url = f"{BASE_URL}/api/social-media/connect"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"platform": platform, "username": username}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 201:
            logger.info(f"Conta {platform} conectada com sucesso")
            return response.json()
        else:
            logger.error(f"Erro ao conectar conta: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao conectar para API: {str(e)}")
        return None

def update_influencer(token, influencer_id, data):
    """Atualiza os dados de um influenciador."""
    url = f"{BASE_URL}/api/social-media/influencer/{influencer_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Influenciador {influencer_id} atualizado com sucesso")
            return response.json()
        else:
            logger.error(f"Erro ao atualizar influenciador: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao conectar para API de atualização: {str(e)}")
        return None

def create_direct_in_db():
    """Cria o registro diretamente no banco de dados."""
    with app.app_context():
        # Verifica se já existe a influenciadora Virginia
        existing = Influencer.query.filter_by(
            username="virginia",
            platform="instagram"
        ).first()
        
        if existing:
            logger.info(f"Virginia já existe com ID {existing.id}")
            return existing.id
        
        # Cria as categorias
        categories = []
        for cat_name in ["lifestyle", "beleza", "família"]:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name, description=f"Categoria de {cat_name}")
                db.session.add(cat)
            categories.append(cat)
        
        # Dados completos da Virginia
        virginia_data = {
            "username": "virginia",
            "full_name": "Virginia Fonseca",
            "platform": "instagram",
            "profile_url": "https://instagram.com/virginia",
            "profile_image": "https://example.com/virginia.jpg",
            "bio": "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br",
            "followers_count": 45600000,
            "following_count": 1580,
            "posts_count": 7850,
            "engagement_rate": 8.2,
            "social_score": 92.5
        }
        
        # Cria a influenciadora
        influencer = Influencer(**virginia_data)
        influencer.categories = categories
        db.session.add(influencer)
        db.session.commit()
        
        logger.info(f"Virginia criada com ID {influencer.id}")
        return influencer.id

def main():
    """Função principal."""
    logger.info("=== Importando e atualizando perfil da Virginia ===")
    
    # Primeiro, criamos diretamente no banco de dados para garantir
    influencer_id = create_direct_in_db()
    
    # Tenta fazer o fluxo via API
    try:
        # Tenta fazer login
        login_result = login("admin", "admin123")
        if not login_result:
            logger.error("Não foi possível fazer login. Usando método alternativo.")
            return
        
        token = login_result.get("tokens", {}).get("access_token")
        if not token:
            logger.error("Token não encontrado na resposta de login.")
            return
        
        # Conecta a conta da Virginia
        connect_result = connect_social_media(token, "instagram", "@virginia")
        if not connect_result:
            logger.error("Não foi possível conectar a conta. Usando método alternativo.")
            return
        
        # Se chegou até aqui, atualiza os dados da Virginia
        influencer_id = connect_result.get("influencer_id")
        if not influencer_id:
            logger.error("ID do influenciador não encontrado na resposta.")
            return
        
        # Dados completos para atualização
        update_data = {
            "full_name": "Virginia Fonseca",
            "bio": "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br",
            "profile_image": "https://example.com/virginia.jpg",
            "followers_count": 45600000,
            "following_count": 1580,
            "posts_count": 7850,
            "engagement_rate": 8.2,
            "categories": ["lifestyle", "beleza", "família"]
        }
        
        update_result = update_influencer(token, influencer_id, update_data)
        if not update_result:
            logger.error("Não foi possível atualizar os dados da Virginia.")
            return
        
        logger.info("Perfil da Virginia importado e atualizado com sucesso!")
    
    except Exception as e:
        logger.error(f"Erro durante o processo: {str(e)}")
    
    finally:
        # Verifica se a Virginia está no banco de dados
        with app.app_context():
            virginia = Influencer.query.filter_by(username="virginia", platform="instagram").first()
            if virginia:
                logger.info(f"Virginia está no banco de dados com ID {virginia.id}")
                logger.info(f"Nome completo: {virginia.full_name}")
                logger.info(f"Seguidores: {virginia.followers_count:,}")
                logger.info(f"Engagement rate: {virginia.engagement_rate}%")
                
                # Lista influenciadores
                all_influencers = Influencer.query.all()
                logger.info(f"Total de influenciadores no banco: {len(all_influencers)}")
                for i, inf in enumerate(all_influencers, 1):
                    logger.info(f"{i}. {inf.username} ({inf.platform}) - ID: {inf.id}")
            else:
                logger.error("Virginia NÃO está no banco de dados!")

if __name__ == "__main__":
    main()