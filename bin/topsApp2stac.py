#!/usr/bin/env python
"""
For output/ folder from topsApp2aws.py, create STAC-compliant JSON metadata.

Fields to possibly add:
- path, orbitIDs
- mean incidence
- mean heading
- local & UTM acquisition time
- ground pixel size/resolution
- ncol, nrol

Add common metadata fields to 'collection.json'?

/Users/scott/Documents/GitHub/stac-spec/json-spec
"""
import argparse
import rasterio
# import rasterio.features
import ast
import datetime
import json
import os

import xml.etree.ElementTree as ET
from collections import OrderedDict


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='create STAC metadata')
    parser.add_argument('-i', type=str, dest='intDir', required=True,
                        help='int- directory from topsApp2aws')
    parser.add_argument('-c', type=str, dest='catalog', required=False,
                        help='STAC catalog.json file')

    return parser


def read_stac_json(stacFile):
    """Read STAC-compliant JSON into python dictionary.

    NOTE: default dictionary order only preserved in python > 3.6

    """
    with open(stacFile) as handle:
        meta = json.loads(handle.read())

    return meta


def write_stac_json(dictionary, stacFile):
    """Write python dictionary to STAC-compliant json."""
    with open(stacFile, 'w') as fp:
        json.dump(dictionary, fp, indent=2)


def filename2datetime(safeFile):
    """Get acquisition time in STAC-compliant format."""
    timestr = safeFile.split('_')[5]
    dt = datetime.datetime.strptime(timestr, '%Y%m%dT%H%M%S')

    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def update_catalog(catalog, intDir):
    """Add new STAC item to STAC catalog."""
    # newline = {'child': 'item', 'href': itemJsonFile}
    # newline = {'rel': 'item', 'href': itemJsonFile}
    href = '{0}/{0}.json'.format(intDir)
    newline = {'rel': 'item', 'href': href}
    catalogDict = read_stac_json(catalog)
    catalogDict['links'].append(newline)
    write_stac_json(catalogDict, catalog)


def publish_to_s3(s3Bucket):
    """Push json files to s3 bucket."""
    print('TODO')


def read_topsAppxml(xmlFile):
    """Get select metadata info from topsApp.xml."""
    tree = ET.parse(xmlFile)
    root = tree.getroot()

    topsParams = OrderedDict()
    for A in ['master', 'slave']:
        topsParams[A] = OrderedDict()
        querySafe = f".//component[@name='{A}']/property[@name='safe']/value"
        val = root.findall(querySafe)[0].text
        if val.startswith('['):
            val = ast.literal_eval(val)
        topsParams[A]['safe'] = val

    # Read specific topsinsar properties
    # list = ast.literal_eval("[1,2,3]") #to convert lists in strings
    props = ['unwrapper name', 'swaths', 'geocode bounding box', 'demfilename']
    for P in props:
        val = root.findall(f".//property[@name='{P}']/value")[0].text
        if val.startswith('['):
            val = ast.literal_eval(val)
        topsParams[P] = val

    return topsParams


def read_isce_log(isceLog):
    """Get select metadata info from isce.log file."""
    isceMeta = OrderedDict()

    def get_value(lines, prefix):
        tmp = [li for li in lines if li.startswith(prefix)]
        return tmp[0].split('=')[1].strip()

    with open(isceLog, 'r') as log:
        lines = log.readlines()

    isceMeta['procDate'] = lines[0].split(' - ')[0]
    isceMeta['isceVersion'] = lines[0].split(' - ')[-1].split(',')[0]
    isceMeta['svnVersion'] = lines[0].split(' - ')[-1].split(',')[1]

    prefix = 'master.sensor.ascendingnodetime'
    isceMeta['masterDate'] = get_value(lines, prefix)

    prefix = 'slave.sensor.ascendingnodetime'
    isceMeta['slaveDate'] = get_value(lines, prefix)

    return isceMeta


def add_topsParams(intDir, stac_item):
    """Add metadata from isce metadata to stac item."""
    # dateStr = filename2datetime(topsParams['master']['safe'][0])
    topsParams = read_topsAppxml(os.path.join(intDir, 'topsApp.xml'))
    isceMeta = read_isce_log(os.path.join(intDir, 'isce.log'))
    topsParams.update(isceMeta)

    stac_item['properties']['isce:master'] = topsParams['master']['safe']
    stac_item['properties']['isce:slave'] = topsParams['slave']['safe']
    stac_item['properties']['isce:unwrapper'] = topsParams['unwrapper name']
    stac_item['properties']['isce:swaths'] = topsParams['swaths']
    stac_item['properties']['isce:dem'] = topsParams['demfilename']
    stac_item['properties']['isce:procdate'] = topsParams['procDate']
    stac_item['properties']['isce:isceversion'] = topsParams['isceVersion']

    return stac_item


def create_stac_json(intDir, catalog):
    """Create a STAC-compliant JSON ITEM based on image metadata.

    STAC item information comes from geocoded file, catalog is stac geoJSON

    links to orginal files
    baselineAPI=http://baseline.asf.alaska.edu/#/baseline?
    searchAPI=https://api.daac.asf.alaska.edu/services/search/param?
    granule=S1B_IW_SLC__1SDV_20171204T020107_20171204T020134_008563_00F32F_A825
    #f'{baselineAPI}granule={granule}''
    #f'{searchAPI}granule_list={granule}'

    Assumes EPSG 4326
    """
    stac_catalog = read_stac_json(catalog)
    catalogURL = os.path.split(stac_catalog['links'][0]['href'])[0]
    s3Bucket = catalogURL.split('.')[0].split('/')[-1]
    s3URL = "s3://" + s3Bucket

    outfile = intDir + '.json'

    stac_item = OrderedDict()
    stac_item['type'] = 'Feature'
    # NOTE: should be unique ID (e.g. path, dates)
    stac_item['id'] = intDir

    inFile = 'amplitude-cog-rgb.tif'
    with rasterio.open(os.path.join(intDir, inFile), nodata=0.0) as ds:
        bbox = list(ds.bounds)

    stac_item['bbox'] = bbox
    stac_item['geometry'] = OrderedDict()
    stac_item['geometry']['type'] = 'Polygon'
    stac_item['geometry']['coordinates'] = [[
                                    [bbox[0], bbox[1]],
                                    [bbox[2], bbox[1]],
                                    [bbox[2], bbox[3]],
                                    [bbox[0], bbox[3]],
                                    [bbox[0], bbox[1]],
                                    ]]

    stac_item['properties'] = OrderedDict()
    stac_item['properties']['provider'] = 'UW Geodesy Lab'
    # Use master date for datetime
    timestr = intDir.split('-')[1]
    dt = datetime.datetime.strptime(timestr, '%Y%m%d')
    dateStr = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    stac_item['properties']['datetime'] = dateStr
    # Removed from Item since this is defined at catalog level
    # stac_item['properties']['license'] = 'CC-BY-SA-3.0'

    # URL to this JSON file
    stac_item['links'] = OrderedDict()
    stac_item['links']['self'] = OrderedDict()
    stac_item['links']['self']['rel'] = 'self'
    stac_item['links']['self']['href'] = f'{catalogURL}/{intDir}/{outfile}'

    stac_item['links']['catalog'] = OrderedDict()
    stac_item['links']['catalog']['rel'] = 'catalog'
    stac_item['links']['catalog']['href'] = catalogURL + '/catalog.json'

    # Can implement later...
    # stac_item['links']['collection'] = OrderedDict()
    # stac_item['links']['collection']['rel'] = 'collection'
    # stac_item['links']['collection']['href']

    thumbnail = inFile.replace('.tif', '-thumb.jpeg')
    stac_item['assets'] = OrderedDict()
    stac_item['assets']['thumbnail'] = OrderedDict()
    # stac_item['assets']['thumbnail']['href'] = f'{catalogURL}/{intDir}/{thumbnail}'
    stac_item['assets']['thumbnail']['href'] = thumbnail
    stac_item['assets']['thumbnail']['type'] = 'jpeg'

    # Add pre-rendered RGB images
    for im in ['coherence-cog-rgb',
               'unwrapped-phase-cog-rgb',
               'amplitude-cog-rgb']:
        stac_item['assets'][im] = OrderedDict()
        stac_item['assets'][im]['href'] = im + '.tif'
        stac_item['assets'][im]['type'] = 'GeoTiff'
        stac_item['assets'][im]['cog'] = 'True'
    # Preview image chosen by 'format' key
    stac_item['assets']['amplitude-cog-rgb']['format'] = 'cog'

    # Add single-band images
    images = ['amplitude',
              'coherence',
              'elevation',
              'heading',
              'incidence',
              'unwrapped-phase']
    for im in images:
        stac_item['assets'][im] = OrderedDict()
        # stac_item['assets'][im]['href'] = s3URL + '/' + im + '-cog.tif'
        stac_item['assets'][im]['href'] = im + '-cog.tif'
        stac_item['assets'][im]['type'] = 'GeoTiff'
        stac_item['assets'][im]['cog'] = 'True'

    # Earth-obervation profile information is additional
    stac_item['properties']['eo:epsg'] = 4326

    # Optionally store topsApp and ISCE metadata

    return stac_item


def main(parser):
    """Create STAC ITEM JSON and add to catalog."""
    args = parser.parse_args()
    stacDict = create_stac_json(args.intDir, args.catalog)
    stacDict = add_topsParams(args.intDir, stacDict)
    outfile = './{0}/{0}.json'.format(args.intDir)
    write_stac_json(stacDict, outfile)
    update_catalog(args.catalog, args.intDir)
    print(f'Wrote {outfile}, updated {args.catalog}')


# Get interferogram name from command line argument
if __name__ == '__main__':
    parser = cmdLineParse()
    main(parser)
