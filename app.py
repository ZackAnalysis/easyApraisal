from flask import Flask, render_template, request, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    from easyApraisal.Matrix import Matrix
    import io
    data = request.form
    username = data.get('username')
    passwd = data.get('passwd')
    inputfile = data.get('inputfile')
    matrixid = data.get('matrixid')
    if not username or not passwd  or not matrixid:
        return 'Please enter username, password, and matrix id, <a href="/">go back and try again</a>'
    matrix = Matrix(username, passwd)
    matrix.login()
    matrix.gotoHousePage(matrixid)
    matrix.scrapListing()
    matrix.tranform()
    df = matrix.to_dataframe()
    # import pandas as pd
    # df = pd.DataFrame({'value':['test']})
    datastream = io.BytesIO()
    df.to_excel(datastream,index=False)
    headers = {
        'Content-Disposition': f'attachment; filename=MatrixOut_{matrixid}.xlsx',
        'Content-type': 'application/vnd.ms-excel'
    }
    return Response(datastream.getvalue(), mimetype='application/vnd.ms-excel', headers=headers) 


app.run()