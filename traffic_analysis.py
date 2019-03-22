from cartopy import crs
import pylab as plt
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

df = pd.read_pickle('traffic/traffic_preprocessed.pkl')

df2 = df.groupby(['hour','month','dlo25','dla25']).agg({'AVG(debit)':'sum','AVG(taux)':'mean','lat':'mean','lon':'mean','time':'mean'})
df2.columns = df2.columns.get_level_values(0)


# Thresholding for better visualization
trh = 15000
df2.loc[df2['AVG(debit)']>trh,'AVG(debit)']=trh
# Save extents
DLO = df.lon.max(),df.lon.min()
DLA = df.lat.max(),df.lat.min()


# %pylab inline
from matplotlib.font_manager import FontProperties
from cartopy.io.img_tiles import OSM,StamenTerrain,GoogleTiles
from scipy.interpolate import griddata
from tqdm import tqdm_notebook as tqdm
font0 = FontProperties()
font0.set_family('serif')
font0.set_name('ubuntu')


class StamenToner(GoogleTiles):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://tile.stamen.com/toner/{}/{}/{}.png'.format(z, x, y)
        return url
    
imagery = OSM()
imagery = StamenToner()
# imagery = StamenTerrain()
# imagery = GoogleTiles()

fig = plt.figure(figsize=(12, 12))
ax = plt.axes(projection=imagery.crs)
ax.set_extent((DLO[0],DLO[1],DLA[0],DLA[1]))
# # Add the imagery to the map.
ax.add_image(imagery, 13)
fig.savefig('traffic_frames/mapST.jpg',bbox_inches='tight',dpi=96)
plt.close();

month_names="January February March April May June July August September October November December".split(" ")


debit_min = df['AVG(debit)'].min()
debit_max = df['AVG(debit)'].max()
norm = plt.Normalize(vmin=debit_min,vmax=debit_max)

fig = plt.figure(figsize=(12, 12))
ax = plt.axes(projection=imagery.crs)

dx = DLO[1]-DLO[0]
dy = DLA[1]-DLA[0]
eps = 0/100.
extent = (DLO[0]-eps*dx,DLO[1]+eps*dx,DLA[0]-eps*dy,DLA[1]+eps*dy)

for time in tqdm(sorted(df.time.unique())):

    ax.set_extent(extent)
    dftimed = df2[df2.time==time]
    try:
        curr_month = dftimed.index.get_level_values('month').values.mean()
        curr_month = int(curr_month)
        curr_hour  = dftimed.index.get_level_values('hour').values.mean()
    except:
        curr_month = dftimed.month.mean()
        curr_month = int(curr_month)
        curr_hour  = dftimed.hour.mean()

    xs,ys,vs = dftimed[['lon','lat','AVG(debit)']].values.T
    xi_x,xi_y = np.mgrid[DLO[0]:DLO[1]:100j,DLA[0]:DLA[1]:100j]
    vs = norm(vs)
    vi = griddata(zip(xs,ys),vs,(xi_x,xi_y),method='linear').T
    vs = plt.Normalize()(vs)

    ax.imshow(vi,extent=extent,
              transform=crs.PlateCarree(),cmap=plt.cm.jet,
              alpha=.25,zorder=10)

    ax.scatter(xs, ys, transform=crs.PlateCarree(), c=plt.cm.jet(vs), s=vs*200,lw=0,zorder=11)
    ax.text(0.85,0.7,"{1:.0f}:00 {0:s}".format(month_names[curr_month-1],curr_hour),
            fontsize=18, transform=ax.transAxes,va='center',ha='right', bbox=dict(facecolor='w', alpha=0.75),
           fontproperties=font0,zorder=11)
    ax.text(0,0,"Copyright (C) 2017 Guglielmo Saggiorato - map: Stamen Toner - data: opendata.paris.fr",fontsize=10,
           fontproperties=font0,transform=ax.transAxes,va='bottom',ha='left',zorder = 12)

    # make invisibility coat for the background
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    fout = 'fr{0:04d}'.format(time)
    fig.savefig('traffic_frames/{0:s}.png'.format(fout),bbox_inches='tight',dpi=96,transparent=True)

    os.system('convert traffic_frames/mapST.jpg traffic_frames/{0:s}.png -layers merge traffic_frames/combined/{0:s}.jpg'.format(fout))
    ax.cla()
#     break
plt.close()

# put it into movies
# cmd = "rm {fout:s}; cat {indir:s}/*.jpg | ffmpeg -f image2pipe -r {rate:d} -i - -vf scale={xscale:d}:-1 -c:v libvpx-vp9 -b:v 2M {fout:s}"
# cm = cmd.format(fout='traffic_25.webm',indir='traffic_frames/combined/',rate=10,xscale=640)
# os.system(cm)
