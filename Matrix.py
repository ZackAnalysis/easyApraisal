#pip installed html5lib
#pip install selenium
#pip install webdriver_manager
#pip install lxml
#pip install pandas


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time,re
import json
import pandas as pd
import base64
import importlib.resources as importlib_resources
from datetime import datetime, timedelta
import pickle

import warnings
warnings.filterwarnings("ignore")

# accounts = json.loads(importlib_resources.read_text('easyApraisal','account.json'))
# username = base64.b64decode(accounts['username'].encode()).decode()
# password = base64.b64decode(accounts['password'].encode()).decode()



accounts= {"niagara_url":"https://matrix.itsorealestate.ca/"}
class Matrix():
    def __init__(self) -> None:
        self.niagara = accounts['niagara_url']
        self.info = {
            'main':{},
            'comparable 1':{},
            'comparable 2':{},
            'comparable 3':{},
            'comparable 4':{},
            'comparable 5':{},
            'comparable 6':{}
        }
        self.testmlsid = "40186898"
        # self.rules = pd.DataFrame()
        rulefile = 'Output.xlsx'
        self.rules = pd.read_excel(rulefile, sheet_name='rules', usecols=['Name','Source','Xpaths','Notes'])

    def clearData(self):
        self.info = {
            'main':{},
            'comparable 1':{},
            'comparable 2':{},
            'comparable 3':{},
            'comparable 4':{},
            'comparable 5':{},
            'comparable 6':{}
        }


    def startBrowser(self):
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.waits =WebDriverWait(self.driver,15)
        except Exception as e:
            print(e)
            print('Chrome driver not found, please install chrome driver or check your Environment Variables settings')
            print('https://chromedriver.chromium.org/downloads')
            return 'Please install chrome driver or check your Environment Variables settings'
            

        return 'Browser started'

    def testwiki(self, term):
        self.driver.get(f'https://en.wikipedia.org/wiki/{term}')
        return self.driver.page_source

    def login(self, username, password, site='niagara'):
        print('Logging in...')
        if site == 'niagara':
            matrix_url = self.niagara
        self.driver.get(matrix_url)
        self.waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="clareity"]')))
        userbox = self.driver.find_element(By.XPATH,'//*[@id="clareity"]')
        userbox.click()
        time.sleep(0.5)
        userbox.send_keys(username)
        time.sleep(0.5)
        passbox = self.driver.find_element(By.XPATH,'//*[@id="security"]')

        passbox.click()
        time.sleep(0.5)
        passbox.send_keys(password)
        time.sleep(0.5)
        self.driver.find_element(By.XPATH,'//*[@id="loginbtn"]').click()
        self.waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="1253"]/img')))
        try:
            time.sleep(1)
            # self.gotoHousePage(self.testmlsid)
            self.driver.get('https://matrix.itsorealestate.ca/Matrix/MyMatrix')
        except Exception as e:
            self.driver.find_element(By.XPATH,'//span[text()="Continue"]').click()
            time.sleep(1)
            self.driver.get('https://matrix.itsorealestate.ca/Matrix/MyMatrix')
            # print(e)
        return 'Logged in'


        

    def gotoHousePage(self,mlsid, refresh=False, target='main'):
        if refresh:
            self.info[target] = {'MLS':mlsid}    
        self.driver.get('https://matrix.itsorealestate.ca/Matrix/RosterSearch')
        self.driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_tbSpeedBar"]').send_keys(mlsid)
        self.driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_lnkGo"]/span/i').click()
        self.waits.until(ec.visibility_of_element_located((By.LINK_TEXT,mlsid)))
        self.driver.find_element(By.LINK_TEXT,mlsid).click()
        self.waits.until(ec.visibility_of_element_located((By.LINK_TEXT,'Listing')))
        self.driver.find_element(By.XPATH,'//a[text()="Listing"]').click()


    def scrapListing(self, target='main'):
        # listing page
        self.driver.find_element(By.XPATH,'//a[text()="Listing"]').click()
        for i,row in self.rules.dropna(subset = ['Xpaths']).loc[self.rules['Source'].apply(lambda x:'Matrix-listing' in str(x))].iterrows():
            print(row['Name'],'---------')
            try:
                self.info[target][row['Name']] = self.driver.find_element(By.XPATH,row['Xpaths']).text
            except Exception as e:
                print(row['Name'],'xpath helper error:',row['Xpaths'])
                self.info[target][row['Name']] = ''
        try:
            lotfront = self.driver.find_element(By.XPATH,"//*[starts-with(text(),'Lot') and contains(text(),'Front (Ft): ')]/following::span[1] ").text
            lotdepth = self.driver.find_element(By.XPATH,"//*[starts-with(text(),'Lot') and contains(text(),'Depth (Ft): ')]/following::span[1]").text
            self.info[target]['Lot dimensions Matrix'] = f"{lotfront}'x{lotdepth}'"
            try:
                self.info[target]['Lot area fallback'] = float(lotfront) * float(lotdepth)
            except:
                self.info[target]['Lot area fallback'] ='not found in Matrix or GeoWarehouse'
        except Exception as e:
            print(e)
            print('Lot Front/Depth not found')
            pass
        try:
            pin = self.driver.find_element(By.XPATH,"//*[starts-with(text(),'PIN: ')]/following::span[1]").text
            self.info[target]['PIN'] = pin
        except Exception as e:
            print(e)
            print('PIN not found')
            pass
        print('Listing scraped')   
        # self.driver.find_element(By.XPATH,'//span[text()="Garage & Parking: "]/following::td').text

        


        # add your xpath here
        # history page
    def scrapHistory(self, target='main'):
        self.driver.find_element(By.XPATH,'//a[text()="History"]').click()
        time.sleep(2)
        try:
            self.info[target]['historyPriceLatest'] = self.driver.find_element(By.XPATH,'//div[contains(@class,"d119m_show")]//span[text()="Chg By"]/following::tr[1]//td[3]').text
        except Exception as e:
            print(e)
            pass
        rows = self.driver.find_elements(By.XPATH,'//td[@class="d299m10"]//tr')
        rowscells = [row.find_elements(By.XPATH,'td') for row in rows]
        texts = [cell.text.strip() for row in rowscells for cell in row ]
        lists = [line for line in texts if line.startswith('List Agt')]
        row = lists[-3]
        allrows = []
        for row in lists:
            rowdata = {}
            dates = re.findall(r'(\d{2}/\d{2}/\d{2})',row)
            datas = [dates[n] for n in range(0,len(dates),2)]
            if len(dates)<4:
                continue
            rowdata['MLS'] = (re.findall(r'MLS# *(\w+?) *Type', row) + [''])[0]
            rowdata['listdate'] = datas[-2]
            rowdata['solddate'] = datas[0]

            prices = re.findall(r'\$[\d,]+',row)
            rowdata['listprice'] = prices[-1]
            rowdata['soldprice'] = prices[0]
            
            rowdata['status'] =' '.join(row.split(datas[0])[0].strip().split('\n')[-1].strip().split(' ')[1:])
            allrows.append(rowdata)
        histdf = pd.DataFrame(allrows).drop_duplicates()
        histdf['solddate'] = pd.to_datetime(histdf['solddate'])
        histdf['listdate'] = pd.to_datetime(histdf['listdate'])
        self.info[target]['lastdate'] = max(histdf['solddate'].max(),histdf['listdate'].max())
        histdf = histdf.loc[histdf['listdate']>= '2010-01-01']
        histdf = histdf.sort_values(by='solddate').reset_index(drop=True)
        # histdf = histdf[histdf['solddate'].dt.year >= datetime.now().year -10].reset_index(drop=True)
        y1listed = histdf.loc[histdf['solddate'] > datetime.now() - timedelta(days=365),:]
        if len(y1listed) > 0:
            self.info[target]['Listed within 1 year'] = 'Yes'
        else:
            self.info[target]['Listed within 1 year'] = 'No'

        fullsentencs = 'The subject was listed '
        for i, row in histdf.iterrows():
            status = row['status'].lower()
            listdate = datetime.strftime(row['listdate'],'%b %d, %Y')
            solddate = datetime.strftime(row['solddate'],'%b %d, %Y')
            listprice = row['listprice']
            soldprice = row['soldprice']
            mlsnum = row['MLS']
            if status == 'Closed': # Closed, Pending, Cancelled, Expired
                text =  f' {listdate} for {listprice} and the listing sold on {solddate} at {soldprice} ({mlsnum}); '
            elif status == 'Pending':
                text =  f' {listdate} for {listprice} and the listing received a pending offer on {solddate} for {soldprice} ({mlsnum}); '
            else:
                text =  f' {listdate} for {listprice} and the listing {status} on {solddate} ({mlsnum}); '
            fullsentencs += text
        if fullsentencs.endswith('; '):
                fullsentencs = fullsentencs[:-2] + '.'
        lastlist = histdf.iloc[-1]
        if lastlist['listdate'] < datetime.now() - timedelta(days=365) and lastlist['status'] in  ['Closed', 'Cancelled', 'Expired']:
            self.info[target]['Currently listed'] = 'No'
        else:
            self.info[target]['Currently listed'] = 'Yes'
        
        self.info[target]['Listing history'] = re.sub(r' +',' ',fullsentencs)
        self.info[target]['historyDataFrame'] = histdf

        print('scraping history done')



    def scrapRooms(self, target='main'):
        # self.driver.find_element(By.XPATH,'//a[text()="Rooms"]').click()

        # NOTE: change matrix back to self

        self.driver.find_element(By.XPATH,'//a[text()="Rooms"]').click()
        time.sleep(2)

        
        # rows = self.driver.find_elements(By.XPATH,'//span[contains(text(),"Bathroom")]/parent::td/parent::tr')
        rows = self.driver.find_elements(By.XPATH,'//div[@class="mtx-containerNavTabs"]/following::div[1]//tr')

        rowscells = [row.find_elements(By.XPATH,'td') for row in rows]
        data = []
        for row in rowscells:
            celltext = [cell.text for cell in row]
            if len(celltext) != 8:
                celltext = celltext[:3] + ['']*(7-len(celltext)) + celltext[-1:]
            data.append(celltext)

        # data = [[c.text  for c in row.find_elements(By.XPATH,'./td')] for row in rows]
        roomdf = pd.DataFrame(columns=['id','room','level','dimensions','sp5','sp6','sp7','room features'],data=data).dropna(subset=['room'])
        roomdf['room'] = roomdf['room'].apply(lambda x: str(x).strip() if str(x).strip() else None)
        roomdf['level'] = roomdf['level'].apply(lambda x: str(x).strip() if str(x).strip() else None)
        roomdf = roomdf.dropna(subset=['room','level'])
        roomcounts = len(roomdf[~((roomdf['room'] == 'Foyer')|(roomdf['level'].isin(['Lower','Basement','lower','basement','Level'])))])
        self.info[target]['AG Rooms'] = roomcounts

        # AG Bath
        bathdf = roomdf[roomdf['room'].apply(lambda x: 'bathroom' in str(x).lower())]
        bathuse = bathdf.loc[~bathdf['level'].isin(['Lower','Basement','lower','basement'])]
        bathuse['nfeatures'] = bathuse['room features'].apply(lambda x: int((re.findall('(\d+?)-Piece',str(x)) + [1])[0]))
        nfull = len(bathuse.query('nfeatures >= 3'))
        nhalf = len(bathuse.query('nfeatures <3'))
        fullpart = f'{nfull}F' if nfull > 0 else ''
        halfpart = f'{nhalf}H' if nhalf > 0 else ''
        self.info[target]['AG Baths'] = f'{fullpart}{halfpart}'
        self.info[target]['bathDataFrame'] = roomdf
        # AG bath above
        print('scraping rooms done')

    def getMatrix(self,target='main'):
        self.scrapListing(target=target)
        self.scrapRooms(target=target)
        self.scrapHistory(target=target)

    def savepickle(self,mls=''):
        today = datetime.strftime(datetime.now(),'_%Y%m%d_%H%M%S')
        filename = f'tmpscrapingdata_{mls}{today}.pickle'
        with open(filename, 'wb') as f:
            pickle.dump(self.info, f)

    def loginGeowarehouse(self, target='main'):
        try:
            self.gotoHousePage('40159781',refresh=False)
            time.sleep(2)
            self.info[target]['geolink'] = self.driver.find_element(By.XPATH,'//a[text()="Get from GeoWarehouse"]').get_attribute('href')
            self.driver.get(self.info[target]['geolink'])
            #https://matrix.itsorealestate.ca/Matrix/Special/ThirdPartyFormPost.aspx?n=GeoWarehouse&ikey=123730261
        except Exception as e:
            return 'ERROR getting geowharehouse login link, you can try to login manually, e.g msl 40159781:' + str(e)
        time.sleep(2)
        return 'loggedin geowarehouse'

    def gotoGeowharehousePage(self, target='main'):
        current_url = self.driver.current_url 
        if not current_url.startswith('https://collaboration.geowarehouse.ca'):
            self.loginGeowarehouse()
        if self.info[target].get('PIN'):
            searchTerm = self.info[target]['PIN']
        else:
            addressline = self.info[target].get('Street address','').split(',')[0]
            postalcode = self.info[target].get('Postal Code','')
            searchTerm = f'{addressline}, {postalcode}'
            if not postalcode:
                print('GEOWAREHOUSE ERROE: run listings first to get address')
                return
        self.driver.find_element(By.XPATH,'//input[@ng-model="searchText"]').clear()
        self.driver.find_element(By.XPATH,'//input[@ng-model="searchText"]').send_keys(searchTerm)
        self.driver.find_element(By.XPATH,'//input[@ng-model="searchText"]').send_keys(Keys.ENTER)

        try:
            # self.driver.find_element(By.XPATH,'//a[@class="anchor-ul"]/parent::p').text
            self.waits.until(ec.visibility_of_element_located((By.LINK_TEXT,'Property Report')))
            self.driver.find_element(By.XPATH,'//a[text()="Property Report"]').click()
            time.sleep(2)
        except Exception as e:
            print('ERROR: geowarehouse search failed, you can try to search manually',e)


    def scrapeGeowahrehouse(self, target='main'):
        # legal description
        try:
            if self.driver.find_element(By.XPATH,'//a[@ng-click="morelegaldesc()"]').text == 'more':
                self.driver.find_element(By.XPATH,'//a[@ng-click="morelegaldesc()"]').click()
                time.sleep(1)
        except Exception as e:
            print('no  button "more" for legal description',e)
        try:
            self.info[target]['Legal description'] = self.driver.find_element(By.XPATH,'//div[@class="legaldesc ng-binding"]').text.strip(' less')
        except Exception as e:
            print('no legal description',e)

        # Lot dimensions short GW
        try:
            front = self.driver.find_element(By.XPATH,'//div[@class="frontage ng-binding"]').text
            depth = self.driver.find_element(By.XPATH,'//div[@class="depth ng-binding"]').text
            front = (re.findall('[\d,\.]+',front) + [''])[0]
            depth = (re.findall('[\d,\.]+',depth) + [''])[0]
            if front and depth:
                self.info[target]['Lot dimensions short GW'] = f'{front}ftx{depth}ft'
                self.info[target]['Lot dimensions short GW (formatted)'] = f"{front}'x{depth}'"
                try:
                    self.info[target]['Lot area fallback'] = float(front) * float(depth)
                except Exception as e:
                    pass
            else:
                self.info[target]['Lot dimensions short GW'] = 'not found'
        except Exception as e:
            print('no lot dimensions short GW',e)

 

        # tax year and value
        try:
            houseValues = self.driver.find_element(By.XPATH,'//div[contains(text(),"Assessed Value")]//parent:: div').text.split('\n')
            assessed = houseValues[2].strip().replace('$','').replace(',','').strip()
            try:
                self.info[target]['Assessed value'] = int(assessed)
            except:
                self.info[target]['Assessed value'] = None
            self.info[target]['Assessed value']
            taxyear = (re.findall('\d{4}',houseValues[5]) + [''])[0]
            if taxyear:
                self.info[target]['Tax year']  = taxyear
                self.info[target]['Assessment date'] = f'Phased in {taxyear}'
        except Exception as e:
            print('no tax year and value',e)

        # lot dimensions long GW
        try:
            self.info[target]['Lot dimensions long GW'] = self.driver.find_element(By.XPATH,'//div[@class="measurements"]').text.replace('Measurements:','').strip().replace(' ','')
        except Exception as e:
            print('no lot dimensions long GW',e)

        # lot area
        try:
            area = self.driver.find_element(By.XPATH,'//div[@class="area"]').text.replace('Area:','').strip()
            areanums = (re.findall('[\d,\.]+',area) + [''])[0].replace(',','')
            if areanums:
                area = float(areanums)
                acres = area/43560
            if acres >1:
                self.info[target]['Lot area'] = f'{acres:.2f} acres'
                self.info[target]['Lot area unit'] = 'acres'
            else:
                self.info[target]['Lot area'] = f'{area:.2f} Sq.Ft. +/-'
                self.info[target]['Lot area unit'] = 'Sq.Ft.'
        except Exception as e:
            print('no lot area',e)

        # sales history
        try:
            salesdf = pd.read_html(self.driver.find_element(By.XPATH,'//table[@ng-show="salePresent"]/parent::div').get_attribute('innerHTML'))[0]
            salesdf['Sale Date'] = pd.to_datetime(salesdf['Sale Date'],errors='coerce')
            salesdfuse = salesdf.loc[salesdf['Sale Date']>='2010-01-01'].sort_values(by='Sale Date')
            y3rows = salesdfuse.loc[salesdf['Sale Date']>=(datetime.now() - timedelta(days=365*3))]
        except Exception as e:
            print('no sales history',e)
            return
        if len(y3rows)>0:
            self.info[target]['Sold within 3 years'] = 'Yes'
        else:
            self.info[target]['Sold within 3 years'] = 'No'
        if len(salesdfuse)==0:
            self.info[target]['Sales history'] = 'According to GeoWaharehouse, the subject has not been transferred in the last ten years.'
        else:
            salestext = 'According to GeoWarehouse, the subject was transferred ' 
            for _, row in salesdfuse.iterrows():
                date = row['Sale Date'].strftime('%b %d, %Y')
                price = row['Sale Amount']
                salestext += f' {date} for {price}; '
            if salestext.endswith('; '):
                salestext = salestext[:-2] + '.'
            self.info[target]['Sale history'] = re.sub(r' +',' ',salestext)
        return


    def tranform(self, target):
        from transforms import tranforms
        self.info[target] = tranforms(self.info[target])

    def to_frame(self, filename = None):
        from datetime import datetime
        timenow = datetime.now().strftime('_%Y%m%d_%H%M%S')
        if not filename:
            mls = self.info['main'].get('MLS id','')
            mls = mls.replace('MLS#','').strip()
            filename = 'Matrix_'+  mls
        filename = filename.replace('.xlsx','')+timenow+'.xlsx'
        infoalldf = pd.DataFrame()
        for target in self.info:
            infodf =pd.DataFrame([self.info[target]]).T
            infodf.columns = [target]
            infoalldf = pd.concat([infoalldf,infodf],axis=1)
        infoalldf = self.rules[['Name']].merge(infoalldf,left_on='Name', right_index=True,how='left')
        return infoalldf

    def to_file(self, filename = None):
        from datetime import datetime
        timenow = datetime.now().strftime('_%Y%m%d_%H%M%S')
        if not filename:
            mls = self.info['main'].get('MLS id','')
            mls = mls.replace('MLS#','').strip()
            filename = 'Matrix_'+  mls
        filename = filename.replace('.xlsx','')+timenow+'.xlsx'
        infoalldf = pd.DataFrame()
        for target in self.info:
            infodf =pd.DataFrame([self.info[target]]).T
            infodf.columns = [target]
            infoalldf = pd.concat([infoalldf,infodf],axis=1)
        infoalldf = self.rules[['Name']].merge(infoalldf,left_on='Name', right_index=True,how='left')
        infoalldf.to_excel(filename,index=False)
        print('Saved to file: ',filename)
        return filename
    
    # def singleScarpe(self,mlsid):
    #     self.login()
    #     self.gotoHousePage(mlsid)
    #     self.scrapListing()
    #     self.tranform()
    #     self.to_file(mlsid)
    #     self.close()


    def close(self):
        self.driver.close()

    


if __name__ == '__main__':
    username = 'CA8074'
    password = 'Henrycub1'
    matrix = Matrix()
    matrix.login(username='',password='')
    matrix.gotoHousePage('40159781') # 40159781
    matrix.getMatrix(target='main')
    matrix.loginGeowarehouse()
    matrix.gotoGeowharehousePage()
    matrix.scrapeGeowahrehouse()


    matrix.to_file()
    # https://collaboration.geowarehouse.ca/gema-web/#!/home?type=modal&r=1644368282849