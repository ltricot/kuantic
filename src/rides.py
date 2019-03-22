from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
    
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist

import pandas as pd
import sys


## caching & df init methods
def _init_df(df):
    df['timestamp'] = pd.to_datetime(
        df.utc, format='%Y-%m-%d %H:%M:%S')
    df = df[['kuantic_id', 'latitude', 'longitude', 'timestamp']]  # trim useless
    return df

def _cache(df):
    store = pd.HDFStore('store.h5')
    store['geo_time'] = df

def _get_cache():
    store = pd.HDFStore('store.h5')
    return store['geo_time']


## common utils
def get_rides(kid, df):
    dat = df[df.kuantic_id == kid].sort_values(by='timestamp')
    dat['prev_timestamp'] = df.timestamp.shift(-1)
    dat['diffs'] = dat.timestamp - dat.prev_timestamp
    dat['markers'] = dat.diffs > pd.Timedelta(minutes=5)
    dat['_gid'] = dat.markers.cumsum()

    for col in ['prev_timestamp', 'diffs', 'markers']:
        del dat[col]
    return dat.groupby('_gid')

def get_bounds(rides):
    dat = rides.agg(['first', 'last'])
    lats, longs = dat.latitude.values, dat.longitude.values
    coords = np.hstack((lats, longs))
    coords = coords[:, [0, 2, 1, 3]]  # get the right order
    return coords

def cluscore(coords):
    bestNC = 0
    bestS = -float('inf')

    # get best score for all k in 1..15
    for NC in range(2, 15):
        clt = KMeans(n_clusters=NC)
        clt.fit(coords)

        if len(set(clt.labels_)) < 2:
            continue

        S = silhouette_score(coords, clt.labels_)
        if S > bestS:
            bestS = S
            bestNC = NC

    return bestNC, bestS

def plot(coords):
    for f1, f2, t1, t2 in coords:
        plt.plot([f1, t1], [f2, t2])


## scripts
def get_cluster_scores(df):
    # output in csv format
    print('kuantic_id,n_clusters,score')
    for kid in df.kuantic_id.unique():
        rides = get_rides(kid, df)

        if len(rides) > 30:
            fmto = get_bounds(rides)
            k, s = cluscore(fmto)
            print(f'{kid},{k},{s}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('car troops analysis')
    parser.add_argument('-i', '--init', type=str, default=None)
    parser.add_argument('what', type=str)

    args = parser.parse_args()

    scripts = {
        'cluscore': get_cluster_scores,
    }

    # eary arg checking
    if args.what not in scripts:
        print(f'{args.what} is not a script')
        exit(1)

    # optional init of cache
    if args.init is not None:
        df = _init_df(pd.read_csv(args.init))
        _cache(df)
    else:
        df = _get_cache()

    # explicit call - zen of python
    scripts[args.what].__call__(df)
