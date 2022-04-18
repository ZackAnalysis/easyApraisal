import re

def addressHandel(info):
    address = info.get('Street address','').strip()
    street = address.split(',')[0].strip()
    city = (address.split(',') + [''])[1].strip()
    province = 'ON'
    postal = (['']+re.findall(r'[A-Z]\d[A-Z] \d[A-Z]\d',address.upper()))[-1]
    city_province_postal = ('NOTL' if 'Niagara on the Lake' else city) + ', ON ' + postal
    info.update( {
        'addressraw':address,
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
    city = info.get('City','')
    Municipalitytext = ''
    Municipality = neighbourhood.split('/')
    if len(Municipality)>=3:
        Municipalitytext = ', '.join(Municipality[1:-1])
    Municipality += ', '+neighbourhood
    neighbourhood = (['']+neighbourhood.split('-'))[-1].strip()
    Municipality += ', '+neighbourhood
    MDN = city + ', ' + neighbourhood
    info.update( {
        "Municipality, District, Neighbourhood":MDN.strip(),
        "Neighbourhood":neighbourhood
    })
    return info

def MLS_id(info):
    MLS_id = info.get('MLS id','')
    MLS_id = 'MLS# '+(['']+MLS_id.split(':'))[-1].strip()
    if MLS_id:
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
    listingdate = info.get('Listing date','')
    if pendingdate:
        pendingdate = datetime.strptime(pendingdate,'%m/%d/%Y').strftime('%b. %d, %Y')
    if listingdate:
        listingdate = datetime.strptime(listingdate,'%m/%d/%Y').strftime('%b. %d, %Y')
    info.update( {
        "Pending date":pendingdate,
        "Listing date":listingdate
    })
    return info

def soldlistprice(info):
    soldprice = info.get('Sold price','')
    listprice = info.get('List price','')
    ppf = ''
    soldprice = soldprice.replace('$','').replace('.00','').strip()
    listprice = listprice.replace('.00','').strip()
    if soldprice:
        footage = info.get('AG Fin SF','')
        if footage:
            try:
                sp = ''.join(re.findall(r'[\d\.]+',soldprice))
                ft = ''.join(re.findall(r'[\d\.]+',footage))
                ppf = int(float(sp)/float(ft))
                ppf = '$'+str(ppf)
            except:
                ppf = ''
    info.update( {
        "Sold price":soldprice,
        "List price":listprice,
        "Price per square foot":ppf
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
    parkingdesc = (garage.split('/') + [''])[0]
    garageType = 'Single'
    if not garage or garage.lower().strip() == 'none':
        garage = '#N/A'
        garageType = ''
    else:
        space = info.get('Garage spaces','').strip()
        try:
            space = float(space)
            if int(space) == 1:
                spacetext = 'Single'
            elif int(space) == 2:
                spacetext = 'Double'
            elif int(space) == 3:
                spacetext = 'Triple'
            elif int(space) == 4:
                spacetext = 'Quadruple'
            elif int(space) == 5:
                spacetext = 'Quintuple'
            elif int(space) > 5:
                spacetext = 'more than 5'
            else:
                spacetext = space
        except:
            spacetext = ''
        # garageTypes = ['ATTACHED','DETACHED','BUILT-IN','CARPORT','COVERED','INSIDE ENTRY','TANDEM','UNDERGROUND']
        garageType = re.findall(r'(Attached|Detached|Built-in|Carport|Covered|Inside Entry|Tandem|Underground) Garage',garage, re.I)
        if len(garageType) == 1:
            info['Garage'] = ' '.join([spacetext,  garageType[0]]).strip()
        elif garageType:
            info['Garage'] = ', '.join(garageType) + ', space:' + spacetext # NOTE might change it later
        elif spacetext:
            info['Garage'] = 'space:' + spacetext
        else:
            info['Garage'] = ''

        
        testdrive = garage.split('//')
        testdrive = [ g for g in testdrive if 'garage' not in g.lower() ]
        if len(testdrive)>0:
            drivedesc = ' '.join(testdrive)
            # driveoption = ['Circular','Front Yard','Lane / Alley', 'Private Single','Private Double','Private Triple',' Surface / Open']
            driveoption = re.findall(r'(Circular|Front Yard|Lane / Alley|Single|Double|Triple|Surface / Open)',drivedesc, re.I)
            if len(driveoption)>0:
                info['Driveway'] = ', '.join(driveoption)
            material =  re.findall(r'Asphalt|Concrete|Gravel|Interlock',drivedesc, re.I)
            if len(material)>0:
                info['Driveway'] += ' '+' '.join(material)

    # elif re.findall(r'Double|Triple',garage):
    #     garageType = re.findall(r'Double|Triple',garage)[0]
    # garage = garageType +' ' + (re.findall(r'Attached|Detached',garage)+[''])[0]
    # info.update( {
    #     "Garage":garage
    # })
    Parkingspace = info.get('Parking spaces','').strip()
    Parkingspace = re.findall(r'[\d\.]+',Parkingspace)
    try:
        Parkingspace = float(Parkingspace[0].strip())
    except:
        info.update( {
            "Parking spaces":'#N/A'
        })
        return info
    if Parkingspace > 0:
        if 'Underground' in parkingdesc:
            info.update( {
                "Parking spaces":f'{Parkingspace} B/G'
            })
        else:
            info.update( {
                "Parking spaces":f'{Parkingspace} A/G'
            })
    else:
        info.update( {
            "Parking spaces":'#N/A'
        })

    return info

def Propertytype(info):
    propertytype = info.get('Property type','')
    propertytype = (re.findall(r'is \'(.*)\'',propertytype) + [''])[0]
    info.update( {
        "Property type":propertytype
    })
    return info

def CommonInterest(info):
    CommonInterest = info.get('Common interest','')
    CommonInterest = CommonInterest.replace('/None','').strip()
    info.update( {
        "Common interest":CommonInterest
    })
    return info

def getage(info):
    from datetime import datetime
    yearBuilt = info.get('Year built','')
    if yearBuilt:
        try:
            yearBuilt = int(yearBuilt)
            age = datetime.now().year - yearBuilt
            age = f'{age} yrs'
        except:
            age = ''
        info.update( {
            "Age":age
        })
    return info



# def driveway(info):
#     driveway = info.get('Driveway','')
#     material = (re.findall(r'(Wood|Concrete|Asphalt)',driveway, re.I) + [''])[0]
#     material = f' WIDTH MATERIAL {material}' if material else ''
#     width = len(re.findall(r'Attached|Detached',driveway, re.I))
#     if len(width) == 0:
#         width = ''
#     elif len(width) == 1:
#         width = 'Single'
#     elif len(width) == 2:
#         width = 'Double'
#     elif len(width) == 3:
#         width = 'Triple'
#     elif len(width) == 4:
#         width = 'Quad'
    
#     info.update( {
#         "Driveway":width + material
#     })
#     return info

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
    info = Propertytype(info)
    info = CommonInterest(info)
    info = getage(info)


    return info

