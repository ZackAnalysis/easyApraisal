import re

def addressHandel(info):
    address = info.get('Street address','')
    street = address.split(',')[0]
    city = (address.split(',') + [''])[1]
    province = 'ON'
    postal = (['']+re.findall(r'[A-Z]\d[A-Z] \d[A-Z]\d',address.upper()))[-1]
    city_province_postal = city + ', ON ' + postal
    info.update( {
        'Street address':street,
        "City":city,
        "Province":province,
        "Postal Code":postal,
        "City Province Postal Code":city_province_postal,
    })
    return info

def agbeds(info):
    AG_Beds = info.get('AG Beds','')
    AG_Beds = (re.findall(r'\( *(\d)',AG_Beds)+[''])[0]
    info.update( {
        "AG Beds":AG_Beds
    })
    return info

def neighbourhood(info):
    neighbourhood = info.get('Neighbourhood','')
    neighbourhood = (['']+neighbourhood.split('-'))[-1].strip()
    info.update( {
        "Neighbourhood":neighbourhood
    })
    return info

def MLS_id(info):
    MLS_id = info.get('MLS id','')
    MLS_id = 'MLS# '+(['']+MLS_id.split(':'))[-1].strip()
    info.update( {
        "MLS id":MLS_id
    })
    return info

def condofee(info):
    condofee = info.get('Condo fee','')
    condofee = (condofee.split('/')+[''])[0].replace('.00','').strip()
    info.update( {
        "Condo fee":condofee
    })
    return info

def pendingdate(info):
    from datetime import datetime
    pendingdate = info.get('Pending date','')
    pendingdate = datetime.strptime(pendingdate,'%m/%d/%Y').strftime('%b.%d,%Y')
    info.update( {
        "Pending date":pendingdate
    })
    return info

def soldlistprice(info):
    soldprice = info.get('Sold Price','')
    listprice = info.get('List Price','')
    soldprice = soldprice.replace('$','').replace('.00','').strip()
    listprice = listprice.replace('.00','').strip()
    info.update( {
        "Sold price":soldprice,
        "List price":listprice
    })
    return info

def dom(info):
    dom = info.get('DOM','')
    dom = (dom.split('/') + [''])[0]
    info.update( {
        "DOM":dom
    })
    return info

def basement(info):
    basement = info.get('Basement','')
    basement = basement.replace('Basement:','').strip()
    info.update( {
        "Basement":basement
    })
    return info

def garage(info):
    garage = info.get('Garage','')
    garageType = 'Single'
    if not garage or garage.lower().strip() == 'none':
        garage = '#N/A'
        garageType = ''
    elif re.findall(r'Double|Triple',garage):
        garageType = re.findall(r'Double|Triple',garage)[0]
    garage = garageType +' ' + (re.findall(r'Attached|Detached',garage)+[''])[0]
    info.update( {
        "Garage":garage
    })
    return info

def tranforms(info):
    info = addressHandel(info)
    info = agbeds(info)
    info = neighbourhood(info)
    info = MLS_id(info)
    info = condofee(info)
    info = pendingdate(info)
    info = soldlistprice(info)
    info = dom(info)
    info = basement(info)
    info = garage(info)

    return info
