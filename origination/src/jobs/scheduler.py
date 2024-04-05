from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.tasks import scan_and_send_applications

orig_scheduler = AsyncIOScheduler()
orig_scheduler.add_job(scan_and_send_applications, 'interval', minutes=1)
