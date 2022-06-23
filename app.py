import asyncio
import random
import constants as key
from pyppeteer import launch
import requests


class pdata:
    eNumber = None
    lasttname = None
    firstname = None
    chat_id = None
    is_occupied = False
def notification(msg):
    notify = requests.get(f'https://api.telegram.org/bot{key.API_TOKEN}/sendMessage?chat_id={pdata.chat_id}&text={msg}')
    return notify

async def main():
    browser = await launch(headless=True, args=['--ignore-certificate-errors', '--no-sandbox'], 
                            handleSIGINT=False,
                            handleSIGTERM=False,
                            handleSIGHUP=False)
    page = await browser.newPage()

    try:
        await page.goto(key.SITE)

        await page.type('#eregid', str(pdata().eNumber))
        await page.type('#lname', pdata().lasttname)
        await page.type('#fname',  pdata().firstname)

        await page.click('#hhw')
        await page.click('button[name="peos"]')
    

        await page.waitFor(1500)
        current_url = page.url
        if(current_url != key.SITE + 'hhw.php'):
            notification('⚠ Account not found! Use /retry to try again.')
            await browser.close()
        else:
            notification('✅ Account Verified!')
            await page.waitFor(1000)
            notification('🧾 Exam in progress!')

            moduleNum = 0
            retry = 0
            while True:
                try:
                    if moduleNum >= 7: break
                    moduleNum +=1
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
                        print(f'> Module {moduleNum} Status: X FAILED')
                        if retry == 3:
                            notification(f'ℹ Module {moduleNum + 1} is taking longer than expected. Please be patient.')
                        elif retry == 5:
                            notification('⏳ Almost done...')
                    else:
                        retry = 0 
                        print(f'> Module {moduleNum} Status: ✓ PASSED')
                        notification(f'🔰 Module {moduleNum} Status: ✓ PASSED')
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
