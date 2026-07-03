import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import User, Classroom, Reservation, Approval, PeriodicRule

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Classroom': Classroom,
        'Reservation': Reservation,
        'Approval': Approval,
        'PeriodicRule': PeriodicRule
    }


@app.cli.command('init-db')
def init_db():
    """Initialize database tables."""
    db.create_all()
    print('Database tables created.')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
