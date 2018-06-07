'''
Query ASF catalog with SNWE bounds (manually entered, or using arbitrary polygon
bounding box)

Outputs 2 JSON metadata files for S1A and S1B from ASF Vertex
Outputs 1 merged GeoJSON inventory file

Author: Scott Henderson
Date: 10/2017
'''

import argparse
import requests
import json
import shapely.wkt
from shapely.geometry import box, mapping
import pandas as pd
import geopandas as gpd
import os
import sys


def load_asf_json(jsonfile):
    ''' Convert JSON metadata from asf query to dataframe '''
    with open(jsonfile) as f:
        meta = json.load(f)[0] #list of scene dictionaries

    df = pd.DataFrame(meta)
    polygons = df.stringFootprint.apply(shapely.wkt.loads)
    gf = gpd.GeoDataFrame(df,
                          crs={'init': 'epsg:4326'},
                          geometry=polygons)

    gf['timeStamp'] = pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes

    return gf

def summarize_orbits(gf):
    '''
    break inventory into separate dataframes by relative orbit
    in most cases, inventory includes 2 adjacent frames (same date)
    '''
    # NOTE: could probably avoid for loop w/ hirearchical index?
    #df115 = gf.groupby('relativeOrbit').get_group('115')
    #gb = gf.groupby(['relativeOrbit', 'sceneDateString'])
    #df = gb.get_group( ('93', '2017-05-11') )  # entire dataframes
    # just polygons:
    #gb.geometry.get_group( ('93', '2017-05-11') ) #.values
    # just files nFrames
    #gb.granuleName.get_group( ('93', '2017-05-11') ) #.tolist()
    # Alternatively
    #gf.loc[gb.groups[ ('93', '2017-05-11') ], ('granuleName','geometry')]
    for orb in gf.relativeOrbit.unique():
        df = gf.query('relativeOrbit == @orb')
        gb = df.groupby('sceneDateString')
        nFrames = gb.granuleName.count()
        #frameLists = gb.granuleName.apply(lambda x: list(x))
        df = df.loc[:,['sceneDateString','dateStamp','platform']] #consider list of granuleName
        #Only keep one frame per date, not necessarily all intersecting...
        DF  = df.drop_duplicates('sceneDateString').reset_index(drop=True)
        DF.sort_values('sceneDateString', inplace=True)
        DF.reset_index(inplace=True, drop=True)
        timeDeltas = DF.dateStamp.diff()
        DF['dt'] = timeDeltas.dt.days
        #DF.dt.iloc[0] #Causes set w/ copy warning...
        DF.loc[0, 'dt']=0
        DF['dt'] = DF.dt.astype('i2')
        DF['nFrames'] = nFrames.values
        DF.drop('dateStamp', axis=1, inplace=True)
        #DF.set_index('date') # convert to datetime difference
        DF.to_csv('acquisitions_{}.csv'.format(orb))

def save_shapefiles(gf, master, slave):
    '''
    NOTE: alernative is to use shapely/geopandas to check overlapping area
    Save shapefiles of master & slave to confirm overlap in GE
    '''
    print('TODO')


def save_geojson_footprints(gf):
    '''
    Saves all frames from each date as separate geojson file for comparison on github
    '''
    attributes = ('granuleName','downloadUrl','geometry') #NOTE: could add IPF version...
    gb = gf.groupby(['relativeOrbit', 'sceneDateString'])
    S = gf.groupby('relativeOrbit').sceneDateString.unique() #series w/ list of unique dates
    for orbit, dateList in S.iteritems():
        os.makedirs(orbit)
        for date in dateList:

            dftmp = gf.loc[gb.groups[ (orbit, date) ], attributes].reset_index(drop=True)
            outname = os.path.join(orbit, date+'.geojson')
            dftmp.to_file(outname, driver='GeoJSON')

def summarize_inventory(gf):
    '''
    Basic statistics for each track
    '''
    dfS = pd.DataFrame(index=gf.relativeOrbit.unique())
    dfS['Start'] = gf.groupby('relativeOrbit').sceneDateString.min()
    dfS['Stop'] =  gf.groupby('relativeOrbit').sceneDateString.max()
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
    '''
    Merge Sentinel 1A and Sentinel 1B into single dataframe
    '''
    gfA = load_asf_json(s1Afile)
    gfB = load_asf_json(s1Bfile)
    gf = pd.concat([gfA,gfB])
    gf.reset_index(inplace=True)
    return gf


def save_inventory(gf, outname='query.geojson', format='GeoJSON'):
    '''
    Save entire inventory as a GeoJSON file (render on github)
    '''
    # WARNING: overwrites existing file
    if os.path.isfile(outname):
        os.remove(outname)
    # NOTE: can't save pandas Timestamps!
    #ValueError: Invalid field type <class 'pandas._libs.tslib.Timestamp'>
    gf.drop(['timeStamp', 'dateStamp'], axis=1, inplace=True)
    gf.to_file(outname, driver=format)
    print('Saved inventory: ', outname)

def download_scene(downloadUrl):
    '''
    aria2c --http-auth-challenge=true --http-user=CHANGE_ME --http-passwd='CHANGE_ME' "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_EW_GRDM_1SDH_20151003T040339_20151003T040351_007983_00B2A6_7377&output=metalink"
    '''
    print('Requires ~/.netrc file')
    cmd = 'wget -nc -c {}'.format() #nc won't overwrite. -c continuous if unfinished
    print(cmd)
    os.system(cmd)
    #use requests.get(auth=())

def query_asf(snwe, sat='1A', format='json'):
    '''
    takes list of [south, north, west, east]
    '''
    print('Querying ASF Vertex...')
    miny, maxy, minx, maxx = snwe
    roi = shapely.geometry.box(minx, miny, maxx, maxy)
    polygonWKT = roi.to_wkt()

    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    #relativeOrbit=$ORBIT
    data=dict(intersectsWith=polygonWKT,
            platform='Sentinel-{}'.format(sat),
            processingLevel='SLC',
            beamMode='IW',
            output=format)

    r = requests.get(baseurl, params=data)
    with open('query_S{}.{}'.format(sat,format), 'w') as j:
        j.write(r.text)

    #Directly to dataframe
    #df = pd.DataFrame(r.json()[0])


def ogr2snwe(args):
    gf = gpd.read_file(args.input)
    gf.to_crs(epsg=4326, inplace=True)
    poly = gf.geometry.convex_hull
    if args.buffer:
        poly = poly.buffer(args.buffer)
    W,S,E,N = poly.bounds.values[0]
    args.roi = [S,N,W,E]


def snwe2file(args):
    '''
    Use shapely to convert to GeoJSON & WKT
    '''
    S,N,W,E = args.roi
    roi = box(W, S, E, N)
    with open('snwe.json', 'w') as j:
        json.dump(mapping(roi), j)
    with open('snwe.wkt', 'w') as w:
        w.write(roi.to_wkt())
    with open('snwe.txt', 'w') as t:
        snweList = '[{0:.3f}, {1:.3f}, {2:.3f}, {3:.3f}]'.format(S,N,W,E)
        t.write(snweList)
    print(snweList)


def main(args):
    ''' control function'''
    if args.input:
        ogr2snwe(args)
    snwe2file(args)
    query_asf(args.roi, '1A')
    query_asf(args.roi, '1B')
    gf = merge_inventories('query_S1A.json', 'query_S1B.json')
    summarize_inventory(gf)
    summarize_orbits(gf)
    save_inventory(gf)
    if args.csvs:
        query_asf(args.roi, '1A','csv')
    if args.kmls:
        query_asf(args.roi, '1A','kml')
    if args.footprints:
	    save_geojson_footprints(gf) #NOTE: takes a while...
