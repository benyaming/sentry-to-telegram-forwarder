import os
import json

import uvicorn
import aiohttp
import betterlogging
from fastapi import FastAPI, Request


app = FastAPI()
logger = betterlogging.get_colorized_logger('forwarder')


@app.post('/sentry-report')
async def handle_report(request: Request):
    resp = await request.json()

    msg = f'<b> ERROR IN [{resp["project"].upper()}]!</b>\n\n' \
          f'<b>Message:</b> <code>{resp["message"]}</code>\n' \
          f'<b>User data:</b> \n<code>{json.dumps(resp["event"]["user"], indent=2)}</code>'

    s = aiohttp.ClientSession()
    url = f'https://api.telegram.org/bot{os.getenv("TOKEN")}/sendmessage'
    data = {
        'chat_id': os.getenv("CHANNEL_ID"),
        'parse_mode': 'HTML',
        'text': msg,
        'reply_markup': {
            'inline_keyboard': [
                [{'text': 'Open issue', 'url': resp['url']}]]
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data) as response:
            logger.info(await response.json())

    await s.close()


uvicorn.run(app, port=8000, host='127.0.0.1' if not os.getenv('DOCKER_MODE') else '0.0.0.0')
