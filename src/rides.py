import pandas as pd
import sys


def _init_df(df):
    df['timestamp'] = pd.to_datetime(
        df.utc, format='%Y-%m-%d %H:%M:%S')
    return df

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

def plot(coords):
    for f1, f2, t1, t2 in coords:
        plt.plot([f1, t1], [f2, t2])

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.spatial.distance import cdist
    from sklearn.manifold import TSNE

    df = _init_df(pd.read_csv('data/Detailed Paris final 02-04 2017.csv'))
    for veh in df.kuantic_id.unique():
        rides = get_rides(veh, df)

        if len(rides) > 30:
            fmto = get_bounds(rides)
            print(f'{veh},{len(rides)}')
            plot(fmto)
            plt.show()

