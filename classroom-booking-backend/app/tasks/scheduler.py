from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.periodic_service import run_periodic_generation

scheduler = BackgroundScheduler()


def init_scheduler(app):
    """Initialize and start the background scheduler."""
    scheduler.add_job(
        func=lambda: run_periodic_generation_with_app(app),
        trigger=CronTrigger(hour=0, minute=5),
        id='periodic_generation',
        name='Generate periodic reservations',
        replace_existing=True
    )
    scheduler.start()
    app.logger.info('Scheduler started.')


def run_periodic_generation_with_app(app):
    with app.app_context():
        run_periodic_generation()
