from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings

scheduler = AsyncIOScheduler()

def start_scheduler():
    from app.services.checker import run_all_checks
    scheduler.add_job(
        run_all_checks,
        trigger="interval",
        seconds=settings.poll_interval,
        id="polling_job",
        replace_existing=True,
    )
    scheduler.start()