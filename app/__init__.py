from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kocak-sql-secret-key'
    
    # Register blueprints
    from app.modules.server_status import server_bp
    from app.modules.db_manager import db_bp
    from app.modules.api import api_bp
    
    app.register_blueprint(server_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(api_bp)
    
    return app
