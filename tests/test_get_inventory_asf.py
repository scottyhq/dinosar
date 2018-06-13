from dinosar.archive import asf

import requests
import os.path
import geopandas as gpd


def test_get_list():
    """Check retrieving specific frame information in inventory."""
    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    granules = [
        'S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA',
        'S1A_IW_SLC__1SSV_20150526T015345_20150526T015412_006086_007E23_34D6',
        ]
    paramDict = dict(granule_list=granules,
                     output='json')
    r = requests.get(baseurl, params=paramDict, verify=False, timeout=(5, 10))
    print(r.url)
    print(r.status_code)
    assert r.status_code == 200


def test_get_inventory():
    """Default region of interest query should work."""
    os.chdir('./tests/tmp')
    asf.query_asf([0.611, 1.048, -78.196, -77.522], 'S1A')
    asf.query_asf([0.611, 1.048, -78.196, -77.522], 'S1B')
    os.chdir('../../')

    assert os.path.isfile('./tests/data/query_S1A.json')
    assert os.path.isfile('./tests/data/query_S1B.json')


def test_load_inventory():
    """Load GeoJSON into GeoDataFrame."""
    gf = asf.load_asf_json('./tests/data/query_S1A.json')

    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_merge_inventory():
    """Merge S1A and S1B inventories."""
    gf = asf.merge_inventories('./tests/data/query_S1A.json',
                               './tests/data/query_S1A.json')

    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_extract_bounds():
    """Extract SNWE bounds from a OGR-recognized vector file."""
    bounds = asf.ogr2snwe('./tests/data/UnionGap.shp')

    assert type(bounds) == list
    assert len(bounds) == 4
    assert bounds == [46.51905923587083,
                      46.53477259526909,
                      -120.471510549134,
                      -120.4502650392162]
