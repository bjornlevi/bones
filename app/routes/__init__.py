from .main import bp as main_bp
from .readme import bp as readme_bp
from .admin import bp as admin_bp
from .health import bp as health_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(readme_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)
