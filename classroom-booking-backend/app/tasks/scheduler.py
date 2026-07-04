from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.periodic_service import run_periodic_generation

scheduler = BackgroundScheduler()


def init_scheduler(app):
    """Initialize APScheduler for periodic tasks"""
    scheduler.add_job(
        func=lambda: run_periodic_generation_with_app(app),
        trigger=CronTrigger(day_of_week='mon', hour=0, minute=0),
        id='periodic_generation',
        name='Generate periodic reservations weekly',
        replace_existing=True
    )
    scheduler.start()
    return scheduler


def run_periodic_generation_with_app(app):
    """Run periodic generation within app context"""
    with app.app_context():
        run_periodic_generation()


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
