import json
import requests
import dotenv
import os
from lxml import html
import resend
import asyncio

dotenv.load_dotenv()

FROM_EMAIL = os.getenv('FROM_EMAIL')
TO_EMAIL = os.getenv('TO_EMAIL')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
resend.api_key=RESEND_API_KEY

def send_email(product):
    

    params: resend.Emails.SendParams = {
    "sender": f"Amazon Bot <{FROM_EMAIL}>",
    "to": [TO_EMAIL],
    "subject": "Product Available",
    "html": f'''<html>
    <head></head>
    <body>
    <p>Product is available in Amazon at https://www.amazon.in/dp/{product} </p>
    </body>
    </html>''',   
    }

    resend.Emails.send(params)


def check_availability(product):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    url = f'https://www.amazon.in/dp/{product}'
    response = requests.get(url, headers=headers)
    doc = html.fromstring(response.content)
    XPATH_AVAILABILITY = '//div[@id ="availability"]//text()'
    RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
    AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None
    if AVAILABILITY and 'Currently unavailable' in AVAILABILITY:
        return False
    return True


def job():
    with open('products.json') as f:
        data = json.load(f)
        copy = data.copy()
    for product in copy:
        available= check_availability(product)
        if available:
            send_email(product)
            data.pop(product, None)
    with open('products.json', 'w') as f:
        json.dump(data, f)





async def periodic():
    while True:
        job()
        await asyncio.sleep(300)

def stop():
    task.cancel()

loop = asyncio.get_event_loop()
task = loop.create_task(periodic())

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass


