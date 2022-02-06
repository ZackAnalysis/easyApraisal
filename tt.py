from io import BytesIO
from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def hello_world():
    import io
    import pandas as pd
    df = pd.DataFrame([{'a':1,'b':2}])
    buffer = io.BytesIO()
    df.to_excel(buffer)
    headers = {
        'Content-Disposition': 'attachment; filename=output.xlsx',
        'Content-type': 'application/vnd.ms-excel'
    }
    return Response(buffer.getvalue(), mimetype='application/vnd.ms-excel', headers=headers)

app.run(port=5001)