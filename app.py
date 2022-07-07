import asyncio
import random
import os
import json
import requests
from pyppeteer import launch

API_TOKEN = os.environ['API_KEY']
SITE = os.environ['SITE']

class pdata:
    msg_id = None
    chat_id = None
    eNumber = None
    lasttname = None
    firstname = None
    is_occupied = False
    
def notification(msg):
    notify = requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={pdata.chat_id}&text={msg}')
    x = json.loads(notify.text)
    pdata.msg_id = list(x.values())[1]['message_id']
    return notify

def update(msg):
    update = requests.get(f'https://api.telegram.org/bot{API_TOKEN}/editMessageText?chat_id={pdata.chat_id}&message_id={pdata.msg_id}&text={msg}')
    return update

async def main():
    browser = await launch(headless=True, args=['--ignore-certificate-errors', '--no-sandbox'], 
                            handleSIGINT=False,
                            handleSIGTERM=False,
                            handleSIGHUP=False)
    page = await browser.newPage()

    try:
        await page.goto(SITE)
        notification('🧾 Verifying account information.')
        await page.type('#eregid', str(pdata().eNumber))
        await page.type('#lname', pdata().lasttname)
        await page.type('#fname',  pdata().firstname)

        await page.click('#hhw')
        await page.click('button[name="peos"]')
    

        await page.waitFor(1500)
        current_url = page.url
        if(current_url != SITE + 'hhw.php'):
            update('⚠ Account not found! Use /retry to try again.')
            await browser.close()
        else:
            update('✅ Account Verified!')
            await page.waitFor(1000)
            update('🧾 Exam in progress!')

            moduleNum = 0
            retry = 0
            while True:
                try:   
                    if moduleNum >= 7: 
                        update(f'ℹ You have passed the examination.\n\nSign in with your PEOS account in [ peos.dmw.gov.ph ] to view and download your certificate')
                        break
                    moduleNum +=1
                    update(f'ℹ Module {moduleNum} Status: ⌛ PENDING')
                    await page.click(f'a[href="{moduleNum}"]')
                    await page.waitFor(1000)
                    await page.click('.getQuestionsHHW')
                    await page.waitFor(1000)
                    for idx in range(5):
                        choice = await page.querySelectorAll(f'#inlineRadio{random.randint(1,2)}')
                        await choice[idx].click()
                    await page.click('button[type="submit"]')
                    
                    await page.waitFor(1000)
                    if(await page.xpath('//a[contains(text(), "Let\'s review again!")]')):
                        moduleNum-=1
                        retry += 1
                        print(f'> Module {moduleNum} Status: X FAILED, Retrying')
                        if retry == 3:
                            update(f'ℹ Module {moduleNum} is taking longer than expected. Please be patient.')
                        elif retry == 5:
                            update('⏳ Almost done...')
                    else:
                        retry = 0 
                        print(f'> Module {moduleNum} Status: ✓ PASSED')
                        update(f'🔰 Module {moduleNum} Status: ✓ PASSED')
                except:
                    moduleNum-=1
                    
            await page.click(f'a[href="8"]')

            await page.waitFor(2000)
            _Name = await page.evaluate("document.querySelectorAll('input')[1].getAttribute('value')")
            _CertID = await page.evaluate("document.querySelectorAll('input')[0].getAttribute('value')")

            notification(f'👤 Name: {str(_Name).upper()}\n🧾 CertID: {_CertID}')
            pdata.chat_id = None
            print('👤 Name:',str(_Name).upper())
            print('🧾 CertID:',_CertID)

    except Exception as e:
        notification('Something went wrong. Use /retry to try again.')
        print(e)
    finally:
        pdata.is_occupied = False
        print('Process closed')
        await browser.close()
        
def runme():
    asyncio.run(main())
