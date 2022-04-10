from datetime import datetime
from flask import Flask, render_template, request, Response, make_response
from numpy import mat
from Matrix import Matrix

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

@app.route('/combine', methods=['POST'])
def combine():
    import pandas as pd
    import io
    from mergeMatrixJotform import merge_matrix_jotform
    from jotform import jotform
    global matrix
    matrixdf = matrix.to_frame()
    # matrixfile = request.files.get('matrixfile').read()

    jotformfile = request.files.get('jotformfile')
    if jotformfile:
        jotformfile = jotformfile.read()
    # matrixdf = pd.read_excel(io.BytesIO(matrixfile))
        jotformdf = pd.read_excel(io.BytesIO(jotformfile))
        jotformdf, roomcounts, basementcounts = jotform(jotformdf, matrix.rules)
        merged = merge_matrix_jotform(matrixdf, jotformdf)
    else:
        merged = matrixdf
        roomcounts = pd.DataFrame()
        basementcounts = pd.DataFrame()
    output = io.BytesIO()
    with pd.ExcelWriter(output) as writer:
        merged.to_excel(writer,sheet_name='main', index=False)
        roomcounts.to_excel(writer, sheet_name='uppercounts', index=False)
        basementcounts.to_excel(writer, sheet_name='basementcounts', index=False)

    r = make_response(output.getvalue())    
    # Defining correct excel headers
    r.headers["Content-Disposition"] = "attachment; filename=combined.xlsx"
    r.headers["Content-type"] = "application/x-xls"
    return r

app.run(port=5432)