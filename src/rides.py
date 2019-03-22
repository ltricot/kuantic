from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
    
import matplotlib.pyplot as plt
import seaborn as sns
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
    dat['markers'] = dat.diffs > pd.Timedelta(minutes=1)
    dat['_gid'] = dat.markers.cumsum()

    for col in ['prev_timestamp', 'diffs', 'markers']:
        del dat[col]
    return dat.groupby('_gid')

def get_diffs(df, kid):
    dat = df[df.kuantic_id == kid].sort_values(by='timestamp')
    print(dat.timestamp.to_csv())

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
    for NC in range(2, min(15, len(coords))):
        clt = KMeans(n_clusters=NC)
        clt.fit(coords)

        if len(set(clt.labels_)) < 2:
            continue

        S = silhouette_score(coords, clt.labels_)
        if S > bestS:
            bestS = S
            bestNC = NC

    return bestNC, bestS


## scripts
def get_cluster_scores(df):
    # output in csv format
    print('kuantic_id,n_clusters,score')
    for kid in df.kuantic_id.unique():
        rides = get_rides(kid, df)
        fmto = get_bounds(rides)
        k, s = cluscore(fmto)
        print(f'{kid},{k},{s}')

def plot_rides(df, kid):
    rides = get_rides(kid, df)
    coords = get_bounds(rides)
    for f1, f2, t1, t2 in coords:
        plt.plot([t1, f1], [t2, f2])
    plt.show()

def plot_cluster(df, kid, nc):
    from matplotlib import collections as mc

    coords = get_bounds(get_rides(kid, df))
    # coords = coords.reshape(-1, 2, 2)
    # coords.sort(axis=1)
    # coords = coords.reshape(-1, 4)
    # tos = coords[:, [2, 3]]
    clt = KMeans(n_clusters=nc)
    clt.fit(coords)

    lc = len(set(clt.labels_))
    colors = np.asarray([  # assume max -n 7 which is optimistic
        (0, 0, 0, 1), (0.5, 0, 0, 1), (0, 0.5, 0, 1), (0, 0, 0.5, 1),
        (0.5, 0.5, 0, 1), (0, 0.5, 0.5, 1), (0.5, 0, 0.5, 1),
    ])

    lines = mc.LineCollection(
        coords.reshape(-1, 2, 2)[:, :, ::-1],
        colors=colors[clt.labels_],
    )

    fig, ax = plt.subplots()
    ax.add_collection(lines)
    ax.autoscale()
    ax.margins(0.1)

    # plt.scatter(coords[:, 0], coords[:, 1], c=clt.labels_, cmap='viridis')
    plt.show()

def plot_nice_rides(df, kid, nc):
    rides = get_rides(kid, df)
    coords = get_bounds(rides)

    clt = KMeans(n_clusters=nc)
    clt.fit(coords)

    lc = len(set(clt.labels_))
    colors = np.asarray([  # assume max -n 7 which is optimistic
        (0, 0, 0, 1), (0.5, 0, 0, 1), (0, 0.5, 0, 1), (0, 0, 0.5, 1),
        (0.5, 0.5, 0, 1), (0, 0.5, 0.5, 1), (0.5, 0, 0.5, 1),
    ])

    for i, (k, gb) in enumerate(rides):
        lat = gb.latitude.values
        lon = gb.longitude.values

        plt.plot(lon, lat, color=colors[clt.labels_[i]])
        plt.xlim([2.20, 2.48])
        plt.ylim([48.81, 48.9])
        plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('car troops analysis')
    parser.add_argument('-i', '--init', type=str, default=None)
    parser.add_argument('-k', '--kid', type=str, default=None)
    parser.add_argument('-n', '--nc', type=int, default=2)
    parser.add_argument('what', type=str)

    args = parser.parse_args()

    scripts = {
        'cluscore': get_cluster_scores,
        'rides': plot_rides,
        'cluster': plot_cluster,
        'nice': plot_nice_rides,
        'diffs': get_diffs,
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
    cargs = [df]
    if args.what in ['rides', 'cluster', 'nice', 'diffs']:
        cargs.append(args.kid)
    if args.what in ['cluster', 'nice']:
        cargs.append(args.nc)
    scripts[args.what].__call__(*cargs)
