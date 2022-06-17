import asyncio
import random
import constants as key
from pyppeteer import launch
import requests

API_TOKEN = '5560316134:AAEHvQhnGireamMnJzDNA-vqLbU5OW5H2aw'
CHAT_ID = '879252455'
class pdata:
    # eNumber = 2022061411717
    # lasttname = 'nunez'
    # firstname = 'joselyn'
    eNumber = None
    lasttname = None
    firstname = None

def notification(msg):
    notify = requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}')
    return notify

async def main():
    browser = await launch(headless=False, args=['--ignore-certificate-errors', '--no-sandbox'], 
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
        try:
            current_url = page.url
            if(current_url != key.SITE + 'hhw.php'):
                notification('Account not found!')
            else:
                notification('Account Verified!\nSetting up..')
        except Exception as e:
            print(e)
            await browser.close()
            
        moduleNum = 0
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
                    print(f'> Module {moduleNum} Status: X FAILED',end='\r')
                    # await page.click(f'a[href="{moduleNum}"]')
                    moduleNum-=1
                else: 
                    print(f'> Module {moduleNum} Status: ✓ PASSED')
                    notification(f'█ Module {moduleNum} Status: ✓ PASSED')
            except Exception as e:
                moduleNum-=1
                # print(e)
        await page.waitFor(1000)        
        await page.click(f'a[href="8"]')
        while True:
            try:
                _Name = await page.evaluate("document.querySelectorAll('input')[1].getAttribute('value')")
                _CertID = await page.evaluate("document.querySelectorAll('input')[0].getAttribute('value')")
            except:
                pass
            else:
               break 
        notification(f'Name: {str(_Name).upper()}\nCertID: {_CertID}')
        print('Name:',str(_Name).upper())
        print('CertID:',_CertID)
        await browser.close()
    except Exception as e:
        notification('Something went wrong. Use /retry to try again.')
        print(e)
        await browser.close()

def runme():
    asyncio.run(main())