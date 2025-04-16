from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

def init_app(app):
    from app.api.auth import bp as auth_bp
    from app.api.users import bp as users_bp
    
    api.register_blueprint(auth_bp, url_prefix='/auth')
    api.register_blueprint(users_bp, url_prefix='/users')
    
    app.register_blueprint(api)
    
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({"message": "Welcome to Analisa.ai Social Media API"})