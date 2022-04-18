import requests
import pickle

with open('sampledata.pkl', 'rb') as f:
    sampledta = pickle.load(f)


job = 'gotoHousePage'
mslid = '40186898'
target = 'main'

query = {
    "job":job,
    "mslid":mslid,
    "target":target
}

job = 'matrix'
query = {
    "job":job,
    "mslid":mslid,
    "target":target
}


res = requests.post('http://localhost:5433/getdata', data=query)

print(res)