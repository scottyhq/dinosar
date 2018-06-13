"""Functions for querying ASF archive."""

import requests
import json
import shapely.wkt
from shapely.geometry import box, mapping
import pandas as pd
import geopandas as gpd
import os


def load_asf_json(jsonfile):
    """Convert JSON metadata from ASF query to dataframe."""
    with open(jsonfile) as f:
        meta = json.load(f)[0]  # list of scene dictionaries

    df = pd.DataFrame(meta)
    polygons = df.stringFootprint.apply(shapely.wkt.loads)
    gf = gpd.GeoDataFrame(df,
                          crs={'init': 'epsg:4326'},
                          geometry=polygons)

    gf['timeStamp'] = pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(
                                            lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes

    return gf


def summarize_orbits(gf):
    """Break inventory into separate dataframes by relative orbit."""
    for orb in gf.relativeOrbit.unique():
        df = gf.query('relativeOrbit == @orb')
        gb = df.groupby('sceneDateString')
        nFrames = gb.granuleName.count()
        df = df.loc[:, ['sceneDateString', 'dateStamp', 'platform']]
        # Only keep one frame per date
        DF = df.drop_duplicates('sceneDateString').reset_index(drop=True)
        DF.sort_values('sceneDateString', inplace=True)
        DF.reset_index(inplace=True, drop=True)
        timeDeltas = DF.dateStamp.diff()
        DF['dt'] = timeDeltas.dt.days
        DF.loc[0, 'dt'] = 0
        DF['dt'] = DF.dt.astype('i2')
        DF['nFrames'] = nFrames.values
        DF.drop('dateStamp', axis=1, inplace=True)
        # DF.set_index('date') # convert to datetime difference
        DF.to_csv('acquisitions_{}.csv'.format(orb))


def save_geojson_footprints(gf):
    """Save all frames from each date as separate geojson file."""
    attributes = ('granuleName', 'downloadUrl', 'geometry')
    gb = gf.groupby(['relativeOrbit', 'sceneDateString'])
    S = gf.groupby('relativeOrbit').sceneDateString.unique()
    for orbit, dateList in S.iteritems():
        os.makedirs(orbit)
        for date in dateList:
            dftmp = gf.loc[gb.groups[(orbit, date)], attributes].reset_index(drop=True)
            outname = os.path.join(orbit, date+'.geojson')
            dftmp.to_file(outname, driver='GeoJSON')


def summarize_inventory(gf):
    """Get basic statistics for each track."""
    dfS = pd.DataFrame(index=gf.relativeOrbit.unique())
    dfS['Start'] = gf.groupby('relativeOrbit').sceneDateString.min()
    dfS['Stop'] = gf.groupby('relativeOrbit').sceneDateString.max()
    dfS['Dates'] = gf.groupby('relativeOrbit').sceneDateString.nunique()
    dfS['Frames'] = gf.groupby('relativeOrbit').sceneDateString.count()
    dfS['Direction'] = gf.groupby('relativeOrbit').flightDirection.first()
    dfS['UTC'] = gf.groupby('relativeOrbit').utc.first()
    dfS.sort_index(inplace=True, ascending=False)
    dfS.index.name = 'Orbit'
    dfS.to_csv('inventory_summary.csv')
    print(dfS)
    size = dfS.Frames.sum()*5 / 1e3
    print('Approximate Archive size = {} Tb'.format(size))


def merge_inventories(s1Afile, s1Bfile):
    """Merge Sentinel 1A and Sentinel 1B into single dataframe."""
    gfA = load_asf_json(s1Afile)
    gfB = load_asf_json(s1Bfile)
    gf = pd.concat([gfA, gfB])
    gf.reset_index(inplace=True)
    return gf


def save_inventory(gf, outname='query.geojson', format='GeoJSON'):
    """Save entire inventory as a GeoJSON file (render on github)."""
    # WARNING: overwrites existing file
    if os.path.isfile(outname):
        os.remove(outname)
    # NOTE: can't save pandas Timestamps!
    # ValueError: Invalid field type <class 'pandas._libs.tslib.Timestamp'>
    gf.drop(['timeStamp', 'dateStamp'], axis=1, inplace=True)
    gf.to_file(outname, driver=format)
    print('Saved inventory: ', outname)


def download_scene(downloadUrl):
    """Download a granule using aria2c.

    aria2c --http-auth-challenge=true \
           --http-user=CHANGE_ME \
           --http-passwd='CHANGE_ME'
           "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_EW_GRDM_1SDH_20151003T040339_20151003T040351_007983_00B2A6_7377&output=metalink"
    """
    print('Requires ~/.netrc file')
    cmd = 'wget -nc -c {}'.format()  # nc won't overwrite. -c continuous if unfinished
    print(cmd)
    os.system(cmd)
    # use requests.get(auth=())


def query_asf(snwe, sat='1A', format='json'):
    '''
    takes list of [south, north, west, east]
    '''
    print('Querying ASF Vertex...')
    miny, maxy, minx, maxx = snwe
    roi = shapely.geometry.box(minx, miny, maxx, maxy)
    polygonWKT = roi.to_wkt()

    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    # relativeOrbit=$ORBIT
    data = dict(intersectsWith=polygonWKT,
                platform='Sentinel-{}'.format(sat),
                processingLevel='SLC',
                beamMode='IW',
                output=format)

    r = requests.get(baseurl, params=data, timeout=100)
    # Save Directly to dataframe
    # df = pd.DataFrame(r.json()[0])
    with open('query_S{}.{}'.format(sat, format), 'w') as j:
        j.write(r.text)


def ogr2snwe(vectorFile, buffer=None):
    """Convert ogr shape to South,North,West,East bounds."""
    gf = gpd.read_file(vectorFile)
    gf.to_crs(epsg=4326, inplace=True)
    poly = gf.geometry.convex_hull
    if buffer:
        poly = poly.buffer(buffer)
    W, S, E, N = poly.bounds.values[0]
    return [S, N, W, E]


def snwe2file(snwe):
    """Use Shapely to convert to GeoJSON & WKT."""
    S, N, W, E = snwe
    roi = box(W, S, E, N)
    with open('snwe.json', 'w') as j:
        json.dump(mapping(roi), j)
    with open('snwe.wkt', 'w') as w:
        w.write(roi.to_wkt())
    with open('snwe.txt', 'w') as t:
        snweList = '[{0:.3f}, {1:.3f}, {2:.3f}, {3:.3f}]'.format(S, N, W, E)
        t.write(snweList)
    print(snweList)
