from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time,re
import json
import pandas as pd
import base64
import importlib.resources as importlib_resources


class Matrix():
    def __init__(self, headless=False) -> None:
        accounts = json.loads(importlib_resources.read_text('easyApraisal','account.json'))
        self.username = base64.b64decode(accounts['username'].encode()).decode()
        self.password = base64.b64decode(accounts['password'].encode()).decode()
        self.niagara = accounts['niagara_url']
        self.headless = headless
        try:
            if self.headless:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                self.driver = webdriver.Chrome(options=chrome_options)
            else:
                self.driver = webdriver.Chrome()
        except Exception as e:
            print('Chrome driver not found, please install chrome driver or check your Environment Variables settings')
            print('https://chromedriver.chromium.org/downloads')
            return
        self.waits =WebDriverWait(self.driver,15)
        self.testmlsid = "40186898"
        self.info = {}
        rulefile = importlib_resources.read_binary('easyApraisal','Output.xlsx')
        self.rules = pd.read_excel(rulefile, sheet_name='rules', usecols=['Name','Source','Xpaths','Notes'])


    def login(self, site='niagara'):
        
        if site == 'niagara':
            matrix_url = self.niagara
        self.driver.get(matrix_url)
        self.waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="clareity"]')))
        userbox = self.driver.find_element(By.XPATH,'//*[@id="clareity"]')
        userbox.click()
        time.sleep(0.5)
        userbox.send_keys(self.username)
        time.sleep(0.5)
        passbox = self.driver.find_element(By.XPATH,'//*[@id="security"]')

        passbox.click()
        time.sleep(0.5)
        passbox.send_keys(self.password)
        time.sleep(0.5)
        self.driver.find_element(By.XPATH,'//*[@id="loginbtn"]').click()
        self.waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="1253"]/img')))
        try:
            time.sleep(1)
            self.gotoHousePage(self.testmlsid)
        except Exception as e:
            if not self.headless:
                self.driver.find_element(By.XPATH,'//span[text()="Continue"]').click()
            else:
                print(e)

    def gotoHousePage(self,mlsid):
        self.info = {'MLS':mlsid}    
        self.driver.get('https://matrix.itsorealestate.ca/Matrix/RosterSearch')
        self.driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_tbSpeedBar"]').send_keys(mlsid)
        self.driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_lnkGo"]/span/i').click()
        self.waits.until(ec.visibility_of_element_located((By.LINK_TEXT,mlsid)))
        self.driver.find_element(By.LINK_TEXT,mlsid).click()
        self.waits.until(ec.visibility_of_element_located((By.LINK_TEXT,'Listing')))


    def scrapListing(self):
        # listing page
        self.driver.find_element(By.XPATH,'//a[text()="Listing"]').click()
        for i,row in self.rules.dropna(subset = ['Xpaths']).loc[self.rules['Source'].apply(lambda x:'Matrix-listing' in str(x))].iterrows():
            print(row['Name'],'---------')
            try:
                self.info[row['Name']] = self.driver.find_element(By.XPATH,row['Xpaths']).text
            except Exception as e:
                print(row['Name'],'xpath helper error:',row['Xpaths'])
                self.info[row['Name']] = ''

        # add your xpath here
        # history page
    def scrapHistory(self):
        self.driver.find_element(By.XPATH,'//a[text()="History"]').click()
        time.sleep(2)
        try:
            self.info['historyPriceLatest'] = self.driver.find_element(By.XPATH,'//div[contains(@class,"d119m_show")]//span[text()="Chg By"]/following::tr[1]//td[3]').text
        except Exception as e:
            print(e)
            pass
    
    def tranform(self):
        from easyApraisal.transforms import tranforms
        self.info = tranforms(self.info)

    def to_file(self, filename = None):
        from datetime import datetime
        timenow = datetime.now().strftime('_%Y%m%d_%H%M%S')
        if not filename:
            filename = 'Matrix_'+self.info.get(['MLS'],'')  
        filename = filename.replace('.xlsx','')+timenow+'.xlsx'
        infodf =pd.DataFrame([self.info]).T
        infodf.columns = ['value']
        infodf = self.rules.merge(infodf,left_on='Name', right_index=True,how='left')
        infodf.to_excel(filename,index=False)
    
    def singleScarpe(self,mlsid):
        self.login()
        self.gotoHousePage(mlsid)
        self.scrapListing()
        self.tranform()
        self.to_file(mlsid)
        self.close()


    def close(self):
        self.driver.close()

if __name__ == '__main__':
    matrix = Matrix()
    matrix.login()
    matrix.gotoHousePage(matrix.testmlsid)
    matrix.scrapListing()
    matrix.tranform()
    matrix.to_file()