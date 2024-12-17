import asyncio
import datetime


async def wait_until(when: datetime.datetime):
    """Wait until the specified datetime by waiting exponentially smaller intervals. (Input must be timezone-aware, use UTC)"""
    _min_step = 30
    
    if isinstance(when, datetime.datetime):
        while True:
            delay = (when - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
            if delay <= _min_step:
                break
            await asyncio.sleep(delay / 2)
        await asyncio.sleep(delay)


def scheduled():
    """Decorate with @scheduled() to add a function to the bot's main loop"""
    def wrapper(func):
        func._judd_scheduled = True
        return func
    return wrapper