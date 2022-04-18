from datetime import datetime
from flask import Flask, render_template, request, Response, make_response, jsonify
from numpy import mat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


username= 'ca8074'
password= 'Spring2022H'

accounts= {"niagara_url":"https://matrix.itsorealestate.ca/"}
driver = webdriver.Chrome(ChromeDriverManager().install())
waits =WebDriverWait(driver,15)

rulefile = 'Output.xlsx'
rules = pd.read_excel(rulefile, sheet_name='rules', usecols=['Name','Source','Xpaths','Notes'], engine='openpyxl')


app = Flask(__name__)

def login(driver, username, password, site='niagara'):
    print('Logging in...')
    if site == 'niagara':
        matrix_url = 'https://matrix.itsorealestate.ca/'
    driver.get(matrix_url)
    waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="clareity"]')))
    userbox = driver.find_element(By.XPATH,'//*[@id="clareity"]')
    userbox.click()
    time.sleep(0.5)
    userbox.send_keys(username)
    time.sleep(0.5)
    passbox = driver.find_element(By.XPATH,'//*[@id="security"]')

    passbox.click()
    time.sleep(0.5)
    passbox.send_keys(password)
    time.sleep(0.5)
    driver.find_element(By.XPATH,'//*[@id="loginbtn"]').click()
    waits.until(ec.visibility_of_element_located((By.XPATH,'//*[@id="1253"]/img')))
    try:
        time.sleep(1)
        # driver.gotoHousePage(driver.testmlsid)
        driver.get('https://matrix.itsorealestate.ca/Matrix/MyMatrix')
    except Exception as e:
        driver.find_element(By.XPATH,'//span[text()="Continue"]').click()
        time.sleep(1)
        driver.get('https://matrix.itsorealestate.ca/Matrix/MyMatrix')
        # print(e)
    return 'Logged in'


login(driver, username, password, site='niagara')

def scrapListing(info, target='main'):
    global driver
    global rules
    driver.find_element(By.XPATH,'//a[text()="Listing"]').click()
    for i,row in rules.dropna(subset = ['Xpaths']).loc[rules['Source'].apply(lambda x:'Matrix-listing' in str(x))].iterrows():
        print(row['Name'],'---------')
        try:
            info[target][row['Name']] = driver.find_element(By.XPATH,row['Xpaths']).text
        except Exception as e:
            print(row['Name'],'xpath helper error:',row['Xpaths'])
            info[target][row['Name']] = ''
    try:
        lotfront = driver.find_element(By.XPATH,"//*[starts-with(text(),'Lot') and contains(text(),'Front (Ft): ')]/following::span[1] ").text
        lotdepth = driver.find_element(By.XPATH,"//*[starts-with(text(),'Lot') and contains(text(),'Depth (Ft): ')]/following::span[1]").text
        info[target]['Lot dimensions Matrix'] = f"{lotfront}'x{lotdepth}'"
        try:
            info[target]['Lot area fallback'] = float(lotfront) * float(lotdepth)
        except:
            info[target]['Lot area fallback'] ='not found in Matrix or GeoWarehouse'
    except Exception as e:
        print(e)
        print('Lot Front/Depth not found')
        pass
    try:
        pin = driver.find_element(By.XPATH,"//*[starts-with(text(),'PIN: ')]/following::span[1]").text
        info[target]['PIN'] = pin
    except Exception as e:
        print(e)
        print('PIN not found')
        pass
    print('Listing scraped')   


@app.get('/keepalive')
def keepalive():
    global driver
    mlsid = '40186898'
    driver.get('https://matrix.itsorealestate.ca/Matrix/RosterSearch')
    driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_tbSpeedBar"]').send_keys(mlsid)
    driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_lnkGo"]/span/i').click()


@app.get('scrapeMatrix')
def scrapeMatrix():
    global driver
    args = request.args
    mlsid = args.get(mlsid)
    if not mlsid:
        return jsonify({"error":"no mlsid"})
    driver.get('https://matrix.itsorealestate.ca/Matrix/RosterSearch')
    driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_tbSpeedBar"]').send_keys(mlsid)
    driver.find_element(By.XPATH,'//*[@id="ctl01_m_ucSpeedBar_m_lnkGo"]/span/i').click()
    time.sleep(1)
    scrapListing()

    



        # driver.find_element(By.XPATH,'//span[text()="Garage & Parking: "]/following::td').text

        


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
        
        self.info[target]['Listing history'] = re.sub(r' +','',fullsentencs)
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
        self.rules = pd.DataFrame()

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
            
        rulefile = 'Output.xlsx'
        self.rules = pd.read_excel(rulefile, sheet_name='rules', usecols=['Name','Source','Xpaths','Notes'])
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
'''
User: walshch1
Pass: Spring2022H

my.rahb.ca 

'''

app = Flask(__name__)
matrix = Matrix()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/startbrowser', methods=['POST'])
def startbrowser():
    global matrix
    matrix.startBrowser()
    return 'browser started'

@app.route('/clearData', methods=['POST'])
def clearData():
    global matrix
    matrix.clearData()
    return 'data cleaned, you can start new job now'

@app.route('/login', methods=['POST'])
def login():
    global matrix
    username = request.form.get('username')
    password = request.form.get('password')
    msg = matrix.login(username, password, site='niagara')
    return msg

@app.route('/loginGeowarehouse', methods=['POST'])
def loginGeowarehouse():
    global matrix
    msg = matrix.loginGeowarehouse()
    return msg

@app.route('/getdata', methods=['POST'])
def getdata():
    global matrix
    job = request.form.get('job')
    mls = request.form.get('mslid')
    target = request.form.get('target')

    if job == 'gotoHousePage':
        matrix.gotoHousePage(mls)
        return 'house page reached'
    if job == 'matrix':
        matrix.getMatrix(target)
        drivematerial = request.form.get('drivematerial')
        CONDITION = request.form.get('interiorCondition')
        RECENCY = '#ERRORinHistroy'
        EXPLANATION = request.form.get('interiorExplanation')
        if EXPLANATION:
            EXPLANATION = 'in ' + EXPLANATION
        setting = request.form.get('setting')
        if drivematerial:
            driveway = matrix.info[target].get('Driveway','')
            matrix.info[target]['Driveway'] = driveway + '| ' + drivematerial
        comparedate = matrix.info[target].get('lastdate',None)
        if comparedate:
            try:
                datadelta = (datetime.now() - comparedate).days
                if datadelta <= 90:
                    RECENCY = 'recent'
                elif datadelta <= 120:
                    RECENCY = 'slightly dated'
                else:
                    RECENCY = 'dated'
            except Exception as e:
                print('bad date',e)
        matrix.info[target]['Setting'] = setting
        if target != 'main':
            matrix.info[target]['CompareStates'] = f"{target} is a {RECENCY}, nearby sale and its interior condition is {CONDITION} to the subject {EXPLANATION}. The property has"
    if job == 'gotoGeowharehousePage':
        matrix.gotoGeowharehousePage(target)
        return 'geowarehouse page reached'
    if job == 'scrapeGeowahrehouse':
        matrix.scrapeGeowahrehouse(target)
        configuration = request.form.get('configuration','')
        matrix.info[target]['Configuration'] += configuration
        return 'scraped geowarehouse'
    if job == 'tofile':
        filename = matrix.to_file()
        return 'saved to file: '+filename
    main = matrix.info['main'].get('MLS id','').strip()
    return f'added {job} data from {mls} as {target} form main property: {main}'


app.run(port=5433)