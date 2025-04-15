#!/usr/bin/env python3
"""
Script para adicionar influenciadores de exemplo ao banco de dados.
Isso ajudará a verificar se o problema está na ausência de dados ou na API.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Adicione o diretório pai ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importe após ajustar o path
from app import create_app
from app.models.social_page import Influencer, Category, InfluencerMetric
from app.extensions import db

# Crie uma instância do app
app = create_app()

# Lista de influenciadores de exemplo para adicionar
SAMPLE_INFLUENCERS = [
    {
        "username": "virginia",
        "full_name": "Virginia Fonseca",
        "platform": "instagram",
        "profile_url": "https://instagram.com/virginia",
        "profile_image": "https://example.com/virginia.jpg",
        "bio": "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing",
        "followers_count": 45600000,
        "following_count": 1580,
        "posts_count": 7850,
        "engagement_rate": 8.2,
        "social_score": 92.5,
        "categories": ["lifestyle", "beleza", "família"]
    },
    {
        "username": "gkay",
        "full_name": "Gessica Kayane",
        "platform": "instagram",
        "profile_url": "https://instagram.com/gkay",
        "profile_image": "https://example.com/gkay.jpg",
        "bio": "Comediante e influenciadora digital",
        "followers_count": 20300000,
        "following_count": 2100,
        "posts_count": 5230,
        "engagement_rate": 7.8,
        "social_score": 88.3,
        "categories": ["humor", "lifestyle", "entretenimento"]
    },
    {
        "username": "whinderssonnunes",
        "full_name": "Whindersson Nunes",
        "platform": "instagram",
        "profile_url": "https://instagram.com/whinderssonnunes",
        "profile_image": "https://example.com/whindersson.jpg",
        "bio": "Comediante, ator e músico",
        "followers_count": 57800000,
        "following_count": 950,
        "posts_count": 3720,
        "engagement_rate": 9.1,
        "social_score": 95.2,
        "categories": ["humor", "música", "entretenimento"]
    },
    {
        "username": "juliette",
        "full_name": "Juliette Freire",
        "platform": "instagram",
        "profile_url": "https://instagram.com/juliette",
        "profile_image": "https://example.com/juliette.jpg",
        "bio": "Maquiadora, advogada e cantora",
        "followers_count": 33500000,
        "following_count": 1200,
        "posts_count": 1850,
        "engagement_rate": 8.9,
        "social_score": 93.7,
        "categories": ["lifestyle", "moda", "música"]
    },
    {
        "username": "luisasonza",
        "full_name": "Luísa Sonza",
        "platform": "instagram",
        "profile_url": "https://instagram.com/luisasonza",
        "profile_image": "https://example.com/luisa.jpg",
        "bio": "Cantora e compositora",
        "followers_count": 29700000,
        "following_count": 890,
        "posts_count": 2450,
        "engagement_rate": 7.6,
        "social_score": 91.3,
        "categories": ["música", "lifestyle", "moda"]
    }
]

def create_or_get_category(name):
    """Cria ou recupera uma categoria pelo nome."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        category = Category(name=name, description=f"Categoria de {name}")
        db.session.add(category)
    return category

def add_sample_influencers():
    """Adiciona influenciadores de exemplo ao banco de dados."""
    with app.app_context():
        # Verifica se já existem influenciadores
        if Influencer.query.count() > 0:
            print("Já existem influenciadores no banco de dados.")
            proceed = input("Deseja adicionar mais exemplos? (s/n): ")
            if proceed.lower() != 's':
                return

        for influencer_data in SAMPLE_INFLUENCERS:
            # Verifica se o influencer já existe
            existing = Influencer.query.filter_by(
                username=influencer_data["username"],
                platform=influencer_data["platform"]
            ).first()
            
            if existing:
                print(f"Influenciador {influencer_data['username']} já existe.")
                continue

            # Cria categorias
            categories = []
            for category_name in influencer_data.pop("categories", []):
                categories.append(create_or_get_category(category_name))
            
            # Cria o influenciador
            influencer = Influencer(**influencer_data)
            influencer.categories = categories
            db.session.add(influencer)
            
            # Adiciona métricas de exemplo
            today = datetime.utcnow().date()
            
            # Métricas para os últimos 30 dias
            for days_ago in range(30, 0, -5):  # Adiciona a cada 5 dias
                date = today - timedelta(days=days_ago)
                # Calcula valores que variam um pouco ao longo do tempo
                followers = int(influencer_data["followers_count"] * (1 - days_ago/100))
                engagement = round(influencer_data["engagement_rate"] * (1 - random.uniform(0, 0.2)), 1)
                posts = max(0, influencer_data["posts_count"] - int(days_ago/2))
                
                # Cria a métrica
                metric = InfluencerMetric(
                    influencer=influencer,
                    date=date,
                    followers=followers,
                    engagement=engagement,
                    posts=posts,
                    likes=int(followers * engagement / 100),
                    comments=int(followers * engagement / 1000),
                    shares=int(followers * engagement / 5000),
                    views=int(followers * 2)
                )
                db.session.add(metric)
            
            print(f"Adicionado influenciador: {influencer_data['username']}")
        
        # Commit das mudanças
        db.session.commit()
        print(f"\nForam adicionados {len(SAMPLE_INFLUENCERS)} influenciadores ao banco de dados.")

def fix_pagination_issue():
    """Tenta corrigir problemas conhecidos com paginação em SQLAlchemy."""
    with app.app_context():
        try:
            # Executar uma consulta simples para testar a paginação
            page = Influencer.query.paginate(page=1, per_page=3)
            print(f"Teste de paginação: {len(page.items)} itens na primeira página de 3")
            print("Paginação funcionando corretamente.")
        except Exception as e:
            print(f"Erro de paginação: {str(e)}")
            print("Tentando corrigir...")
            
            # Algumas versões do SQLAlchemy têm problemas com paginate()
            try:
                # Forçar um upgrade de dependências
                import pkg_resources
                sqlalchemy_version = pkg_resources.get_distribution("sqlalchemy").version
                print(f"Versão do SQLAlchemy: {sqlalchemy_version}")
                
                # Oferecer solução alternativa
                print("\nSoluções potenciais:")
                print("1. Atualize o SQLAlchemy: 'pip install --upgrade sqlalchemy'")
                print("2. Modifique o endpoint para usar um método alternativo de paginação")
                
                # Teste manual alternativo
                query = Influencer.query
                items = query.limit(3).offset(0).all()
                print(f"Teste manual: {len(items)} itens encontrados com limit/offset")
            except:
                print("Não foi possível determinar a versão do SQLAlchemy.")

if __name__ == '__main__':
    print("=== Adicionando Influenciadores de Exemplo ===")
    try:
        add_sample_influencers()
        print("\n=== Verificando Problemas de Paginação ===")
        fix_pagination_issue()
    except Exception as e:
        print(f"Erro: {str(e)}")
        
    print("\nExecute o script check_influencers.py para verificar se o problema foi resolvido.")