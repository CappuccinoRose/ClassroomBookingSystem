from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.classroom_controller import classroom_bp
    from app.controllers.reservation_controller import reservation_bp
    from app.controllers.admin_controller import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(classroom_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(admin_bp)

    @app.route('/api/health')
    def health_check():
        return {'code': 200, 'message': '服务正常运行', 'data': None}

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
