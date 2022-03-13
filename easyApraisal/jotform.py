import pandas as pd
import re
from collections import Counter
from datetime import datetime

timenow = datetime.now().strftime('%Y%m%d-%H%M%S')
outfile = f'jotformOutput-{timenow}.xlsx'


dffinal = pd.read_excel('Output.xlsx', sheet_name='rules', usecols=['Name','Source','Xpaths','Notes'])

jotForm = pd.read_excel('RESIDENTIAL_2_STOREY_12022-02-22_09_42_54.xlsx')
jotForm = jotForm.fillna('')
jotForm = jotForm.T.reset_index(drop=False)
jotForm.columns = ['Xpaths','value']



# dffinal = dffinal.merge(jotForm, on='Xpaths', how='left')
if 'value' in dffinal.columns:
    dffinal = dffinal.drop('value', axis=1)
dfdict = {}
for xpath in dffinal['Xpaths']:
    if xpath in jotForm['Xpaths'].values:
        dfdict[xpath] = jotForm[jotForm['Xpaths'] == xpath]['value'].values[0]


#transforms
dfdict['Percent complete'] = jotForm.loc[jotForm['Xpaths']=='Percent complete','value'].apply(lambda x: f'{x}%' if x else '').values[0]

dfdict['Interior finish'] = jotForm.loc[jotForm['Xpaths']=='Interior finish','value'].apply(lambda x: (re.findall('\d+',str(x)) + ['100'])[0]).values[0]


dfdict['Water heater fuel'] = jotForm.loc[jotForm['Xpaths']=='Water heater fuel','value'].apply(lambda x: 'Tankless' if x=='Tankless' else 'Tank').values[0]

# basement
basement = jotForm.loc[jotForm['Xpaths']=='Basement finish','value'].fillna('').values.tolist()[0]
basementfull = jotForm.loc[jotForm['Xpaths']=='Basement','value'].fillna('').values[0]
dfdict['Basement'] = ','.join([x for x in [basement,basementfull] if x])

#bedrooms ? Bedroom - basement
bedrooms = jotForm.loc[jotForm['Xpaths'].str.contains('Bedroom -'),'value'].values
nbedrooms = len([b for b in bedrooms if b])
dfdict['Bedrooms'] = nbedrooms


#bathrooms ? Bathroom - basement
bathrooms = jotForm.loc[jotForm['Xpaths'].str.contains('Bathroom -'),'value'].values
bathrooms = [(re.findall(r'Pieces: ?(\d+)',str(b))+[''])[0] for b in bathrooms if b]
bathrooms = [b for b in bathrooms if b]
if len(bathrooms)<1:
    dfdict['Bathrooms'] = ''
elif len(set(bathrooms))==1:
    dfdict['Bathrooms'] = bathrooms[0]+'pc'
else:
    bathroomcounts = dict(Counter(bathrooms))
    bathroomtext = ','.join([f'{v}x{k}pc' if v>1 else f'{k}pc' for k,v in bathroomcounts.items()])
    dfdict['Bathrooms'] = bathroomtext

# Insultation
InsulationAG = jotForm.loc[jotForm['Xpaths']=='Insulation AG','value'].fillna('').values[0]
insulationbsm = jotForm.loc[jotForm['Xpaths']=='Basement insulation','value'].fillna('').values[0]
dfdict['Insultation'] = (InsulationAG +','+ insulationbsm).replace('\n',',').strip()

# built in
builtinterms = "Stove, Oven, Dishwasher, Garburator, Vacuum, Security system, Fireplace, Skylight, Solarium, HR ventilator, Central air, Air cleaner, Sauna, Jetted tub, Garage opener, pool, Sump pump".lower().split(', ')
valuetext = ' '.join(jotForm['value'].fillna('').astype('str').values).lower()
pattern = re.compile(r'\b(?:%s)\b' % '|'.join(builtinterms), re.IGNORECASE)
builtinfount = set(re.findall(pattern, valuetext))
builtintext = ','.join([x for x in builtinterms if x.lower() in builtinfount])
builtintext = builtintext.replace('pool', 'swimming pool')
dfdict['Built-in/extras'] = builtintext

if 'pool' in builtinfount:
    pools = ['Aboveground pool','Belowground pool','pool']
    pooltext = (re.findall(r'\b(?:%s)\b' % '|'.join(pools) ,valuetext, re.IGNORECASE) + [''])[0]
    dfdict['Pool'] = pooltext

# exterior improvements
exclude = 'Garden, Gardens, Mature tree, Mature trees, Shed, Shrubs, Sodded lawn'.lower().split(', ')
pattern = re.compile(r'\b(?:%s)\b' % '|'.join(exclude), re.IGNORECASE)
exteriorfount = jotForm.loc[jotForm['Xpaths']=='Exterior improvements front','value'].fillna('').values[0]
exteriorfount = re.sub(pattern,'', exteriorfount)
# exteriorfount = re.sub(r'[\n\r]+',',',exteriorfount)
dfdict['Exterior improvements front'] = exteriorfount

#driveway
driveway = jotForm.loc[jotForm['Xpaths']=='Driveway width','value'].fillna('').values[0]
drivewayMa = jotForm.loc[jotForm['Xpaths']=='Driveway material','value'].fillna('').values[0]
dfdict['Driveway'] = ' '.join([driveway,drivewayMa]).strip()




# flooring
floora = jotForm.loc[jotForm['Xpaths'].str.contains('floor',False).fillna(False),'value'].values
floorb = jotForm.loc[jotForm['value'].str.contains('floor',False).fillna(False),'value'].values

floora = [f.strip() for f in floora if f.strip()]
floorb = [re.findall(r'flooring:(.*?),', f, re.I) for f in floorb if f]
floorb = [t for f in floorb for t in f if t]
floorb = [f.strip() for f in floorb if f.strip()]
floors = ', '.join(set(floora+floorb))
dfdict['Flooring'] = floors

#   dfdict['HBU comment'] comment
propertyType = jotForm.loc[jotForm['Xpaths']=='Property type','value'].values[0]

if propertyType in ['Single family dwelling','Acreage','Townhouse']:
    dfdict['HBU comment'] = "The appraiser has considered the zoning, economic and market trends, expectations of immediate area, the financial and physical attributes of the site and concludes that the highest and best use of this site as if vacant is for a residential single family dwelling as per City Zoning and Official Plan. There is no assemblage."
elif propertyType in ['Duplex','Tri-plex','Fourplex']:
    dfdict['HBU comment'] = "The appraiser has considered the zoning, economic and market trends, expectations of immediate area, the financial and physical attributes of the site and concludes that the highest and best use of this site as if vacant is for a multiresidential as per City Zoning and Official Plan. There is no assemblage."
elif propertyType in ["Condominium"]:
    dfdict['HBU comment'] = "As this appraisal applies to a single unit of a multi-unit complex, the value estimate of the land underlying the building is beyond the scope of this assignment and is not developed in this report. The Highest and Best Use for the site, as though vacant, is therefore not addressed. There is no assemblage."


# Type of inspection
inspectionType = jotForm.loc[jotForm['Xpaths']=='Type of inspection','value'].values[0]
dfdict['Type of inspection'] = 'Exterior inspection only' if inspectionType=='Exterior' else ''


# Effective age/economic life
effectiveAge = jotForm.loc[jotForm['Xpaths']=='Effective age','value'].values[0]
dfdict['Effective age/economic life'] = effectiveAge/60


for k,v in dfdict.items():
    if isinstance(v,str):
        dfdict[k] = v.replace('\n',',').strip()

# rooms

rooms = jotForm.loc[jotForm['Xpaths'].str.contains('room -')].reset_index(drop=True)

def row2rooms(row):
    namebase = row['Xpaths']
    level = namebase.split('-')[-1].strip().upper()
    roomtype = namebase.split('-')[0].upper().replace('ROOM','').strip()
    if roomtype=='BED':
        roomtype = 'BEDROOMS'
    if roomtype=='BATH':
        roomtype = 'PARTIAL BATH'
    rowvalue = row['value']
    if not rowvalue:
        return []
    lines = re.split(r'[,\n]',rowvalue.strip())
    rooms = []
    newroom = {"level":level,"roomtype":roomtype}
    feature = None
    for i,line in enumerate(lines):
        if ':' in line:
            if feature == 'Other':
                rooms.append(newroom)
                newroom = {"level":level,"roomtype":roomtype}
            feature, value = line.split(':')
            feature = feature.strip()
            value = value.strip()
            if feature == 'Pieces' and roomtype == 'PARTIAL BATH':
                if int(value) >= 3:
                    newroom['roomtype'] = 'FULL BATH'
            if feature == 'Room type' and roomtype == 'OTHER':
                newroom['roomtype'] = value
            if value:
                newroom[feature] = value
        else:
            if not newroom:
                continue
            newroom[feature] += ','+line
    rooms.append(newroom)
    return rooms

allrooms = []
for i,row in rooms.iterrows():
    allrooms+=row2rooms(row)


alllroomsdf = pd.DataFrame(allrooms)
levelorder = {'MAIN':1,'SECONDARY':3,'UPPER':2,'EXTRA LEVEL':4,'BASEMENT':10,'LOWER':11}

alllroomsdf['levelorder'] = alllroomsdf['level'].map(levelorder).fillna(8)
alllroomsdf.sort_values(by=['levelorder','roomtype'],inplace=True)
alllroomsdf.reset_index(drop=True,inplace=True)

for i,row in alllroomsdf.iterrows():
    subroomdf = alllroomsdf[:i]
    level = row['level']
    roomtype = row['roomtype']
    roomindex = len(subroomdf.loc[(subroomdf['level']==level) & (subroomdf['roomtype']==roomtype)])
    alllroomsdf.loc[i,'roomindex'] = str(int(roomindex+1))



abovedf = alllroomsdf.loc[~alllroomsdf['level'].isin(['BASEMENT','LOWER'])].reset_index(drop=True)
basementdf = alllroomsdf.loc[alllroomsdf['level'].isin(['BASEMENT','LOWER'])].reset_index(drop=True)


entrances = jotForm.loc[jotForm['Xpaths'].str.contains('entrance', False)].reset_index()
entrances['Xpaths'] = entrances['Xpaths'].str.replace('entrances','').str.upper().str.strip()
aboveentrance = entrances.loc[~entrances['Xpaths'].isin(['BASEMENT','LOWER'])].reset_index(drop=True)
basemententrance = entrances.loc[entrances['Xpaths'].isin(['BASEMENT','LOWER'])].reset_index(drop=True)
# above rooms

def countRooms(abovedf, entrances):
    roomcounts = pd.pivot_table(abovedf, values='roomindex', index=['level'], columns=['roomtype'], aggfunc='count').reset_index()


    countcolumns = ['level','ENTRANCES','LIVING','DINING','KITCHEN','FAMILY','BEDROOMS','DEN','FULL BATH','PARTIAL BATH','LAUNDRY']

    countcolumns= countcolumns + [col for col in roomcounts.columns if col not in countcolumns]
    for col in countcolumns:
        if col not in roomcounts.columns:
            roomcounts[col] = None

    roomcounts = roomcounts[countcolumns]
    roomcounts['level'] = roomcounts['level'].str.upper()

    for _, row in entrances.iterrows():
        level = row['Xpaths']
        if level in ['BASEMENT','LOWER']:
            continue
        if level in roomcounts['level'].values:
            roomcounts.loc[roomcounts['level']==level,'ENTRANCES'] = row['value']
        else:
            roomcounts = roomcounts.append({'level':level,'ENTRANCES':row['value']},ignore_index=True)

    total = roomcounts.sum(axis=0).to_frame().T
    total['level'] = 'TOTAL'
    roomcounts = pd.concat([roomcounts,total],axis=0)
    return roomcounts


roomcounts = countRooms(abovedf, aboveentrance)
basementcounts = countRooms(basementdf, basemententrance)

def row2roomdesc(row):
    descmidel = ''
    for key in row.keys():
        if key in ['level','roomindex','roomtype','levelorder','Other']:
            continue
        if pd.isna(row[key]):
            continue
        if key in ['Windows','Closets']:
            descmidel += row[key]+', '
            continue
        descmidel += row[key] + ' '+key+', '

    if not pd.isna(row['Other']) and row['Other']:
        descmidel += row['Other']
    else:
        descmidel = descmidel.strip(', ')
    if row['roomindex'] == '1':
        roomdesc = f"{row['roomtype']} ({descmidel})"
    else:
        roomdesc = f"{row['roomtype']}{row['roomindex']} ({descmidel})"
    return roomdesc

def floordesc(floor,abovedf, aboveentrance, basementtype='' ):
    if floor != 'BASEMENT':
        basementtype =''
    floordesc = f' {basementtype} {floor} floor comprises'
    floorentry = aboveentrance.loc[aboveentrance['Xpaths']==floor]
    if len(floorentry)>0:
        floordesc += f' {floorentry["value"].values[0]} entrance(s),'
    roomdescs = ', '.join(abovedf.loc[abovedf['level']==floor,'desc'].values).replace('BEDROOMS', 'BEDROOM')
    floordesc += f' {roomdescs}.'
    FLOOR_CEILING = jotForm.loc[jotForm['Xpaths'].str.contains(f'{floor} CEILING',False)]
    if len(FLOOR_CEILING)>0:
        FLOOR_CEILING = FLOOR_CEILING['value'].values[0]
    else:
        FLOOR_CEILING = ''
    FLOOR_FLOORING = jotForm.loc[jotForm['Xpaths'].str.contains(f'{floor} FLOORING',False)]
    if len(FLOOR_FLOORING)>0:
        FLOOR_FLOORING = FLOOR_FLOORING['value'].values[0]
    else:
        FLOOR_FLOORING = ''
    if FLOOR_CEILING or FLOOR_FLOORING:
        floordesc += f" This floor is finished with "
        if FLOOR_CEILING:
            FLOOR_CEILING += ' ceiling'
        else:
            FLOOR_CEILING = ''
        if FLOOR_FLOORING:
            FLOOR_FLOORING += ' flooring'
        else:
            FLOOR_FLOORING = ''
        if FLOOR_CEILING and FLOOR_FLOORING:
            floordesc += ' and '.join([FLOOR_CEILING,FLOOR_FLOORING])
        else:
            floordesc += FLOOR_CEILING or FLOOR_FLOORING
        floordesc += 'throughout, unless otherwise specified.'
    return floordesc

basementdf['desc'] = basementdf.apply(row2roomdesc,axis=1)
abovedf['desc'] = abovedf.apply(row2roomdesc,axis=1)

# - basement desc
basement = jotForm.loc[jotForm['Xpaths']=='Basement','value'].values[0]

if basement == 'None':
    basementDesc = "The subject does not have a basement."
# elif basement in ['Crawl space','Partial','Full']:
else:
    basementDesc = floordesc('BASEMENT',basementdf, basemententrance, basementtype=basement )

if basementDesc:
    dfdict['Basement finish'] = 'The '+basementDesc

# - building rooms
BUILDING_TYPE = jotForm.loc[jotForm['Xpaths']=='Building type','value'].values[0]
STYLE   = jotForm.loc[jotForm['Xpaths']=='Style','value'].values[0]
PROPERTY_TYPE = jotForm.loc[jotForm['Xpaths']=='Property type','value'].values[0]
NATURE_OF_DISTRICT = jotForm.loc[jotForm['Xpaths']=='Nature of district','value'].values[0]
CITY = jotForm.loc[jotForm['Xpaths']=='City','value'].values[0]
EXTERIOR_FINISH_CONDITION = jotForm.loc[jotForm['Xpaths']=='Exterior finish condition','value'].values[0]
CONDITION_CONFORMITY = jotForm.loc[jotForm['Xpaths']=='Condition conformity','value'].values[0]
roomdesc = f"Subject is a {BUILDING_TYPE} {STYLE} {PROPERTY_TYPE} in a {NATURE_OF_DISTRICT} neighbourhood in {CITY}. Exterior building appearance is considered {EXTERIOR_FINISH_CONDITION} and quality of construction is {CONDITION_CONFORMITY} to other homes of this class and age in the immediate area." 
roomdesc = roomdesc.replace('\n','')
roomdesc += '\n\n'
for floor in abovedf['level'].values:
    roomdesc += floordesc(floor,abovedf, aboveentrance)

if roomdesc:
    dfdict['Building improvements'] = roomdesc
        

# --------------------------- TO DO ENDS ---------------------------

# Garages/carports/parking facilities
garagedesc = ''
GARAGE_TYPE = jotForm.loc[jotForm['Xpaths']=='Garage type','value'].values[0]
if not pd.isna(GARAGE_TYPE) and GARAGE_TYPE:
    GARAGE_PANEL = jotForm.loc[jotForm['Xpaths'].str.contains('Garage panel', False),'value'].values[0]
    if not pd.isna(GARAGE_PANEL) and GARAGE_PANEL:
        garagedesc += f'a {GARAGE_TYPE} garage ({GARAGE_PANEL}amp electrical panel);'
    else:
        garagedesc += f'a {GARAGE_TYPE} garage;'
streetvalue = jotForm.loc[jotForm['Xpaths']=='Parking'].values[0]
if 'Carport' in streetvalue:
    CARPORT_WIDTH = jotForm.loc[jotForm['Xpaths']=='Carport width','value'].values[0]
    garagedesc+= f'{CARPORT_WIDTH} carport;'

DRIVEWAY_WIDTH = jotForm.loc[jotForm['Xpaths']=='Driveway width','value'].values[0]
if not pd.isna(DRIVEWAY_WIDTH) and DRIVEWAY_WIDTH:
    DRIVEWAY_MATERIAL = jotForm.loc[jotForm['Xpaths']=='Driveway material','value'].values[0]
    garagedesc+= f'{DRIVEWAY_WIDTH} {DRIVEWAY_MATERIAL} driveway;'
if garagedesc:
    dfdict['Garages/carports/parking facilities'] = 'The subject has '+ garagedesc + 'street parking.'

# 3. Site improvements
siteimprov = ''
EXTERIOR_IMPROVEMENTS_FRONT = jotForm.loc[jotForm['Xpaths']=='Exterior improvements front','value'].values[0]
if not pd.isna(EXTERIOR_IMPROVEMENTS_FRONT) and EXTERIOR_IMPROVEMENTS_FRONT:
    siteimprov += f"Front: {EXTERIOR_IMPROVEMENTS_FRONT}." 

EXTERIOR_IMPROVEMENTS_REAR = jotForm.loc[jotForm['Xpaths']=='Exterior improvements rear','value'].values[0]
if not pd.isna(EXTERIOR_IMPROVEMENTS_REAR) and EXTERIOR_IMPROVEMENTS_REAR:
    siteimprov += f"Rear: {EXTERIOR_IMPROVEMENTS_REAR}."
FENCE_MATERIAL = jotForm.loc[jotForm['Xpaths']=='Fence material','value'].values[0]
if FENCE_MATERIAL:
    siteimprov = re.sub(r'fence-(.*?)[\n ]',rf'fence-\1\({FENCE_MATERIAL}\)',siteimprov, flags=re.I)

SHED_FEATURES = jotForm.loc[jotForm['Xpaths']=='Shed features','value'].values[0]
SHED_ELECTRICAL_PANEL = jotForm.loc[jotForm['Xpaths']=='Shed electrical panel','value'].values[0]
shedfeature = [SHED_FEATURES,SHED_ELECTRICAL_PANEL]
shedfeature = [x for x in shedfeature if x.strip()]
shedfeature = ','.join(shedfeature)
if shedfeature:
    siteimprov = re.sub(r'shed-(.*?)[\n ]',rf'shed-\1\({shedfeature}\)',siteimprov, flags=re.I)
dfdict['Site improvements'] = siteimprov


# Site comment
'''
If PROPERTY_TYPE in inspection form = Single family dwelling OR Acreage OR Townhouse OR Duplex OR Tri-plex OR Fourplex”, write: The title was not searched for easements; this appraisal assumes no easements are present which may affect it. The site is # at grade and # in configuration. The subject site abuts # on all sides. Landscaping appears to be maintained in LANDSCAPING fashion for the area it appears CONDITION_CONFORMITY in condition and SIZE_CONFORMITY in size to adjacent properties. A survey was not provided and thus the effect of any potential easements could not be determined for this appraisal report.

If = Condominium, write: As this appraisal applies to a condominium, the value estimate of the land underlying the building is beyond the scope of this assignment and is not developed in this report. The common property includes COMMON_ELEMENTS.

'''
propertyType = jotForm.loc[jotForm['Xpaths']=='Property type','value'].values[0]



n1 = '#' 
n2 = '#' 
n3 = '#' 

if propertyType in ['Single family dwelling','Acreage','Townhouse','Duplex','Tri-plex','Fourplex']:
    CONDITION_CONFORMITY = jotForm.loc[jotForm['Xpaths'].str.upper()=='CONDITION CONFORMITY','value'].values[0]
    SIZE_CONFORMITY = jotForm.loc[jotForm['Xpaths'].str.upper()=='SIZE CONFORMITY','value'].values[0]
    LANDSCAPING = jotForm.loc[jotForm['Xpaths'].str.upper()=='LANDSCAPING','value'].values[0]
    dfdict['Site comment'] = f"The title was not searched for easements; this appraisal assumes no easements are present which may affect it. The site is {n1} at grade and {n2} in configuration. The subject site abuts {n3} on all sides. Landscaping appears to be maintained in {LANDSCAPING} fashion for the area it appears {CONDITION_CONFORMITY} in condition and {SIZE_CONFORMITY} in size to adjacent properties. A survey was not provided and thus the effect of any potential easements could not be determined for this appraisal report."

elif propertyType in ["Condominium"]:
    COMMON_ELEMENTS = jotForm.loc[jotForm['Xpaths'].str.upper()=='COMMON ELEMENTS','value'].values[0]
    dfdict['Site comment'] = f"As this appraisal applies to a condominium, the value estimate of the land underlying the building is beyond the scope of this assignment and is not developed in this report. The common property includes {COMMON_ELEMENTS}."


# constants
dfdict['Insulation info source'] = "Building code"
dfdict['Plumbing info source'] = "Building code"
dfdict['Economic life'] = 60

dfdict['Rent reconciliation'] = "Given the subject's size and condition, the estimated rental range of $ #  to $ #, excluding utilities, is reasonable and supportable if the entire property is rented."
dfdict['Rent comparison comment'] ="""
                            The days on market for comparables 1-3 ranged from # days to # days, indicating that there is stable demand in the area for rentals of similar type of property.

                            Comparable 1 is a #, # lease and is similar in condition and size. Property has # bedrooms and # baths like subject.
                            Comparable 2 1 is a #, # lease and is similar in condition and size. Property has # bedrooms and # baths like subject.
                            Comparable 3 1 is a #, # lease and is similar in condition and size. Property has # bedrooms and # baths like subject.

                            """
dfdict['Analysis comments'] = """
                            Comparable sales examined offered good overall comparability with the subject and were chosen from similar style properties that sold recently in the subject's market area. They are similarly improved in terms of design, utility, quality of improvements and accommodation. To equate the subject property to the sales presented, an adjustment process has been adopted. Comparables have been adjusted for factors such as differences in quality and condition of interior improvements, liveable floor area (LFA), bathroom facilities, and parking facilities, where applicable. Due to lack of similar sale comparables, an expanded area and sale time search have been conducted. A time adjustment as per HPI has been applied.

                            Comparable 1 is a #, # sale. The property’s interior condition is # to subject. Property has
                            Comparable 2 is a #, # sale. The property’s interior condition is # to subject. Property has
                            Comparable 3 is a #, # sale. The property’s interior condition is # to subject. Property has

                            No locational adjustment has been made these properties have similar neighbourhood amenities. The comparable LFA has a range is # SqFt to # SqFt. The unadjusted values ranged from $ # to $ # and the adjusted values ranged from $ # to $ # . Given the subject’s size, location, and condition, equal weight is accorded to the comparables after adjustments for variances identified. According to consideration of this appraisal, the subject's final estimated value of $ # is considered to be supported.

                            """


dftable = pd.DataFrame()
dftable['Name'] = dfdict.keys()
dftable['value'] = dfdict.values()
# dftable['value'] = dftable['value'].apply(lambda x: x.strip().replace('\n',',') if x and isinstance(x, str) else x)

dffinal = dffinal.merge(dftable,on='Name',how='left')


with pd.ExcelWriter(outfile) as writer:
    dffinal.to_excel(writer, sheet_name='jotformout', index=False)
    roomcounts.to_excel(writer, sheet_name='uppercounts', index=False)
    basementcounts.to_excel(writer, sheet_name='basementcounts', index=False)
    