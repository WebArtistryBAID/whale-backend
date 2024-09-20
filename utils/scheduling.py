from apscheduler.schedulers.background import BackgroundScheduler

from data import database
from utils import crud
from utils.dependencies import TIME_ZONE


def enable_ordering():
    with database.ind_db() as db:
        crud.update_settings(db, "shop-open", "1")


def disable_ordering():
    with database.ind_db() as db:
        crud.update_settings(db, "shop-open", "0")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=TIME_ZONE)
    scheduler.add_job(enable_ordering, "cron", hour=10, minute=0)
    scheduler.add_job(disable_ordering, "cron", hour=16, minute=0)
    scheduler.start()
    return scheduler
