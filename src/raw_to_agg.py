###
# from opendata
# sparce csv -> dense hdf
###

from tqdm import tqdm # _notebook as tqdm
import numpy as np
import pandas as pd

def c_geo_point_2d(x):
    out = []
    for i in x.split(','):
        try:
            out.append(float(i))
        except ValueError as msg:
            return [np.nan,np.nan]
            raise(ValueError(' x='+str(x)))
    return out
converters = {'geo_point_2d':c_geo_point_2d }

positions = pd.read_csv('opendata/referentiel-comptages-routiers.csv',delimiter=';',converters=converters)
positions['lat']=positions['geo_point_2d'].apply(lambda x:x[0])
positions['lon']=positions['geo_point_2d'].apply(lambda x:x[1])

from collections import defaultdict
posdict = defaultdict(lambda :{'lat':0,'lon':0})
for j,i in positions[['id_arc_tra','lat','lon']].iterrows():
    id_arc_tra = float(i.id_arc_tra)
    lat = i.lat
    lon = i.lon
    posdict[id_arc_tra]={'lat':lat,'lon':lon}

# positions.head(5)

# positions.columns

import sqlite3 as sql
# !rm data/referentiel-comptages-routiers.sqlite
with sql.connect('opendata/referentiel-comptages-routiers.sqlite') as conn:
    positions[['id_arc_tra','lat','lon']].to_sql('where',conn,index=False,if_exists='append')

# print np.iinfo(np.int16)
# print np.finfo(np.float16)

conn = sql.connect('traffic.db')

in_it = pd.read_csv('opendata/comptages-routiers-permanents.csv',delimiter=';',parse_dates=['horodate'],chunksize=50000,
                    dtype={'id_arc_trafic':np.int16, # this is NOT bcs I'm pedantic
                           'debit':np.float16,       # but bcs otherwise it won't infer the right columns types
                           'taux':np.float16})       # and will bail out with a misterious "ValueError"

for chunk in tqdm(in_it):
    try:
        # line by line pre-processing
        chunk.debit = chunk.debit.apply(lambda x: 0 if np.isnan(x) else x)
        chunk.taux = chunk.taux.apply(lambda x: 0 if np.isnan(x) else x)
        chunk=chunk.assign(hour=chunk.horodate.apply(lambda x:x.hour))
        chunk=chunk.assign(month=chunk.horodate.apply(lambda x:x.month))
        chunk=chunk.assign(BDay=chunk.horodate.apply(lambda x:x.isoweekday() not in (6,7)))
        # map from counter id to its position
        chunk = chunk.assign(lat=chunk.id_arc_trafic.apply(lambda x:posdict[float(x)]['lat']))
        chunk = chunk.assign(lon=chunk.id_arc_trafic.apply(lambda x:posdict[float(x)]['lon']))        
        chunk = chunk[['hour','month','BDay','debit','taux','id_arc_trafic','lat','lon']]        
        
        chunk.to_sql('traffic',conn,if_exists='append')
    except ValueError as msg:
        print(msg)
        print(chunk)
        break

print('part 1: done')

#safety checks
conn.commit()
cur = conn.cursor()
cur.execute('SELECT DISTINCT month FROM traffic')
cur.fetchall()

cur.execute('select count(hour) from traffic')
cur.fetchall()[0]

# aggregate by hour, month, and traffic counter (id_arc_trafic)
sql_query = 'SELECT hour,month,id_arc_trafic,AVG(debit),AVG(taux),lat,lon FROM traffic WHERE BDay GROUP BY hour, month, id_arc_trafic;'

out = pd.HDFStore('traffic/aggregates.hdf')
for rows in tqdm(pd.read_sql_query(sql_query,conn,chunksize=200)):
    out.append(key = '/aggregates',value = rows)

agg = out['/aggregates']
out.close()
