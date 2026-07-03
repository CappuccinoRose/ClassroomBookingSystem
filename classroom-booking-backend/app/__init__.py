from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.classroom_controller import classroom_bp
    from app.controllers.reservation_controller import reservation_bp
    from app.controllers.admin_controller import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(classroom_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': '接口不存在', 'data': None}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': '服务器内部错误', 'data': None}, 500

    return app
