"""
JWT blacklist helpers for Flask-JWT-Extended.
"""
from flask import current_app

def add_token_to_blacklist(jti):
    redis = current_app.redis
    redis.set(f"jwt_blacklist:{jti}", 1)

def is_token_revoked(jwt_payload):
    redis = current_app.redis
    jti = jwt_payload["jti"]
    entry = redis.get(f"jwt_blacklist:{jti}")
    return entry is not None
