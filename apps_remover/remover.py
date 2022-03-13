from datetime import datetime
from database import Bot_apps, CRM
import aioschedule
import asyncio

crm = CRM()
apps = Bot_apps()

async def track():
    for app in await crm.get_crm_apps():
        if not await apps.check_app(app_id=app[1]):
            await crm.delete_app_history(app[0])
            await crm.delete_crm_app(app[0])

async def check():
    aioschedule.every(1).minutes.do(track)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(check())
