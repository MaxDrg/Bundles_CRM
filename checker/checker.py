from datetime import datetime
from database import CRM
import aioschedule
import requests
import asyncio
import urllib
import os

crm = CRM()

async def track():
    time = datetime.now()
    if await crm.get_last_app():
        if not time.hour == (await crm.get_last_app())[0].hour:
            for dev in await crm.get_devs():
                dev = {'dev': dev[0]}
                params = urllib.parse.urlencode(dev, quote_via=urllib.parse.quote)
                headers = {"Authorization": f"Bearer {os.environ.get('APPSTORESPY_TOKEN')}"}
                
                sess = requests.session()
                response = sess.get(os.environ.get('APPSTORESPY_URL'), headers=headers, params=params)
                
                for data in response.json()['data']:
                    for app in await crm.get_apps():
                        if data['id'] == app[1]:
                            await crm.add_history(
                                data['installs_exact'] - app[2], 
                                app[0],
                                time
                            ) 
                            await crm.update_app(
                                app[0], 
                                data['installs_exact'], 
                                data['available'], 
                                data['updated']
                            )
    else:
        for dev in await crm.get_devs():
            dev = {'dev': dev[0]}
            params = urllib.parse.urlencode(dev, quote_via=urllib.parse.quote)
            headers = {"Authorization": f"Bearer {os.environ.get('APPSTORESPY_TOKEN')}"}
            
            sess = requests.session()
            response = sess.get(os.environ.get('APPSTORESPY_URL'), headers=headers, params=params)

            for data in response.json()['data']:
                for app in await crm.get_apps():
                    if data['id'] == app[1]:
                        await crm.add_history(
                            data['installs_exact'] - app[2], 
                            app[0],
                            time
                        ) 
                        await crm.update_app(
                            app[0], 
                            data['installs_exact'], 
                            data['available'], 
                            data['updated']
                        )

async def check():
    aioschedule.every(1).minutes.do(track)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(check())
