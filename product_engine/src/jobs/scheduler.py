from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.tasks import check_agreements

pe_scheduler = AsyncIOScheduler()
pe_scheduler.add_job(check_agreements, 'interval', minutes=1)
