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
        matrix.savepickle(mls)
        matrix.tranform(target)
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
            PROXIMITY = 'nearby'
            matrix.info[target]['CompareStates'] = f"{target} is a {RECENCY}, nearby sale and its interior condition is {CONDITION} to the subject {EXPLANATION}. The property has"

            f"{target} is a {RECENCY}, {PROXIMITY} sale and its interior condition is {CONDITION} to the subject in {EXPLANATION}. Property has"
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
    try:
        matrixdf = matrix.to_frame()
        compares = [matrix.info[t]['CompareStates'] for t in matrix.info  if matrix.info[t]['CompareStates']]
        comparetext = '\n'.join(compares)
        if comparetext:
            matrix.info['main']['CompareStates'] = f'''Comparable sales examined offered good overall comparability with the subject and were chosen from similar style properties that sold recently in the subject's market area. They are similarly improved in terms of design, utility, quality of improvements and accommodation. To equate the subject property to the sales presented, an adjustment process has been adopted. Comparables have been adjusted for factors such as differences in quality and condition of interior improvements, liveable floor area (LFA), bathroom facilities, and parking facilities, where applicable. Due to lack of similar sale comparables, an expanded area and sale time search have been conducted. A time adjustment as per HPI has been applied.

{comparetext}

No locational adjustment has been made these properties have similar neighbourhood amenities. The comparable LFA has a range is # SqFt to # SqFt. The unadjusted values ranged from $ # to $ # and the adjusted values ranged from $ # to $ # . Given the subject's size, location, and condition, equal weight is accorded to the comparables after adjustments for variances identified. According to consideration of this appraisal, the subject's final estimated value of $ # is considered to be supported.'''
        # matrixfile = request.files.get('matrixfile').read()
    except Exception as e:
        matrixdf = pd.DataFrame()

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