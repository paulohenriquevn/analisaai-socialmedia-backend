#!/usr/bin/env python3
"""
Script para atualizar o perfil da Virginia diretamente no banco de dados.
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicione o diretório pai ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importe após ajustar o path
from app import create_app
from app.models.social_page import Influencer, Category
from app.extensions import db

# Crie uma instância do app
app = create_app()

def atualizar_virginia():
    """Atualiza os dados da Virginia diretamente no banco de dados."""
    with app.app_context():
        # Busca a Virginia pelo ID (assumindo que o ID é 1 conforme mostrado)
        virginia = Influencer.query.filter_by(username="virginia", platform="instagram").first()
        
        if not virginia:
            logger.error("Virginia não encontrada no banco de dados!")
            return False
        
        logger.info(f"Encontrada Virginia com ID {virginia.id}")
        
        # Dados completos da Virginia
        virginia.full_name = "Virginia Fonseca"
        virginia.bio = "Mãe da Maria Alice e Maria Flor. Casada com @zecaragoing. Contato: contato@virginiadoces.com.br"
        virginia.profile_image = "https://yt3.googleusercontent.com/ytc/APkrFKbWYCNBr7PE-kePqIvlKYP2pq1_NOJSGdkebP3SuQ=s900-c-k-c0x00ffffff-no-rj"
        virginia.followers_count = 45600000
        virginia.following_count = 1580
        virginia.posts_count = 7850
        virginia.engagement_rate = 8.2
        virginia.social_score = 92.5
        
        # Adicionar categorias
        categorias = ["lifestyle", "beleza", "família"]
        categoria_objs = []
        
        for cat_nome in categorias:
            # Busca ou cria a categoria
            categoria = Category.query.filter_by(name=cat_nome).first()
            if not categoria:
                categoria = Category(name=cat_nome, description=f"Categoria de {cat_nome}")
                db.session.add(categoria)
                logger.info(f"Criada categoria: {cat_nome}")
            
            categoria_objs.append(categoria)
        
        # Associa categorias à Virginia
        virginia.categories = categoria_objs
        
        # Salva as alterações
        db.session.commit()
        logger.info("Perfil da Virginia atualizado com sucesso!")
        
        # Exibe os dados atualizados
        logger.info("\n=== DADOS ATUALIZADOS ===")
        logger.info(f"Nome completo: {virginia.full_name}")
        logger.info(f"Bio: {virginia.bio}")
        logger.info(f"Seguidores: {virginia.followers_count:,}")
        logger.info(f"Seguindo: {virginia.following_count:,}")
        logger.info(f"Posts: {virginia.posts_count:,}")
        logger.info(f"Taxa de engajamento: {virginia.engagement_rate}%")
        logger.info(f"Score social: {virginia.social_score}")
        logger.info(f"Categorias: {', '.join([c.name for c in virginia.categories])}")
        
        return True

if __name__ == "__main__":
    logger.info("Iniciando atualização do perfil da Virginia...")
    if atualizar_virginia():
        logger.info("\nPerfil atualizado com sucesso! Agora você pode verificar o endpoint /api/influencers")
    else:
        logger.error("\nFalha ao atualizar o perfil. Por favor, verifique os logs.")