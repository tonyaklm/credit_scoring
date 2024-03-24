from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.tasks import check_agreements


def start_pe_scheduler():
    pe_scheduler = AsyncIOScheduler()
    pe_scheduler.add_job(check_agreements, 'interval', minutes=1)
    pe_scheduler.start()