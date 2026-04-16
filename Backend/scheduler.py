"""Background scheduler for auto-logout and other periodic tasks."""
import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import config
from database import AttendanceDB

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_auto_logout():
    """Check and process auto-logout for users who exceeded 9 hours."""
    try:
        logger.info("Starting auto-logout check...")
        pending_records = await AttendanceDB.get_pending_auto_logout()

        if not pending_records:
            logger.debug("No pending auto-logout records")
            return

        logout_count = 0
        for record in pending_records:
            user_id = record.get("user_id")
            check_in = record.get("check_in")

            if check_in:
                if isinstance(check_in, str):
                    check_in = datetime.fromisoformat(check_in)

                elapsed = datetime.utcnow() - check_in
                if elapsed >= timedelta(hours=config.AUTO_LOGOUT_HOURS):
                    result = await AttendanceDB.auto_logout_user(user_id)
                    if result:
                        logout_count += 1
                        logger.info(f"Auto-logout executed for {user_id}")

        logger.info(f"Auto-logout check completed. {logout_count} users logged out.")

    except Exception as e:
        logger.error(f"Error in auto-logout check: {str(e)}")


def start_scheduler():
    """Start the background scheduler."""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    try:
        # Add job for auto-logout check
        scheduler.add_job(
            check_auto_logout,
            trigger=IntervalTrigger(minutes=config.CHECK_INTERVAL_MINUTES),
            id="auto_logout_check",
            name="Auto-logout check",
            replace_existing=True
        )

        scheduler.start()
        logger.info(f"Scheduler started. Auto-logout check every {config.CHECK_INTERVAL_MINUTES} minutes")

    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")


def stop_scheduler():
    """Stop the background scheduler."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")


async def init_scheduler():
    """Initialize scheduler (for async contexts)."""
    try:
        # Add job for auto-logout check
        if not scheduler.get_job("auto_logout_check"):
            scheduler.add_job(
                check_auto_logout,
                trigger=IntervalTrigger(minutes=config.CHECK_INTERVAL_MINUTES),
                id="auto_logout_check",
                name="Auto-logout check",
            )

        if not scheduler.running:
            scheduler.start()
            logger.info(f"Async scheduler initialized. Auto-logout check every {config.CHECK_INTERVAL_MINUTES} minutes")

    except Exception as e:
        logger.error(f"Failed to initialize async scheduler: {str(e)}")
