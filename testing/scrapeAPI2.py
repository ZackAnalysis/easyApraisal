from datetime import datetime
from flask import Flask, render_template, request, Response, make_response, jsonify
from numpy import mat
from Matrix import Matrix
import warnings
warnings.filterwarnings("ignore")

'''
User: walshch1
Pass: Spring2022H

my.rahb.ca 

'''

app = Flask(__name__)
matrix = Matrix()
matrix.startBrowser()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clearData', methods=['POST'])
def clearData():
    global matrix
    matrix.clearData()
    return 'data cleaned, you can start new job now'

@app.route('/login', methods=['POST', 'GET'])
def login():
    global matrix
    username = request.form.get('username','ca8074')
    password = request.form.get('password','Spring2022H')
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
        return jsonify(matrix.info)
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
        return jsonify(matrix.info)
    if job == 'scrapeGeowahrehouse':
        matrix.scrapeGeowahrehouse(target)
        configuration = request.form.get('configuration','')
        matrix.info[target]['Configuration'] += configuration
        return jsonify(matrix.info)
    return jsonify(matrix.info)

app.run(port=5433)