"""Tests for querying ASF archive."""
from dinosar.archive import asf

import requests
import os
import geopandas as gpd


def test_extract_bounds():
    """Extract SNWE bounds from a OGR-recognized vector file."""
    bounds = asf.ogr2snwe("tests/data/UnionGap.shp")

    assert type(bounds) == list
    assert len(bounds) == 4
    assert bounds == [
        46.51905923587083,
        46.53477259526909,
        -120.471510549134,
        -120.4502650392162,
    ]


def test_get_list():
    """Check retrieving specific frame information in inventory."""
    baseurl = "https://api.daac.asf.alaska.edu/services/search/param"
    granules = [
        "S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA",
        "S1A_IW_SLC__1SSV_20150526T015345_20150526T015412_006086_007E23_34D6",
    ]
    paramDict = dict(granule_list=granules, output="json")
    r = requests.get(baseurl, params=paramDict, verify=False, timeout=(5, 10))
    print(r.url)
    print(r.status_code)
    assert r.status_code == 200


def test_load_json():
    """Load GeoJSON into GeoDataFrame."""
    gf = asf.load_asf_json("tests/data/query_S1A.json")

    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_get_inventory(tmpdir):
    """Default region of interest query should work."""
    pwd = os.getcwd()
    os.chdir(tmpdir)
    asf.query_asf([0.611, 1.048, -78.196, -77.522], "S1A")
    asf.query_asf([0.611, 1.048, -78.196, -77.522], "S1B")
    os.chdir(pwd)

    s1ajson = tmpdir.join("query_S1A.json")
    s1bjson = tmpdir.join("query_S1B.json")

    assert os.path.isfile(s1ajson)
    assert os.path.isfile(s1bjson)


def test_merge_inventory():
    """Merge S1A and S1B inventories."""
    gf = asf.merge_inventories("tests/data/query_S1A.json", "tests/data/query_S1B.json")

    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_load_inventory():
    """Load GeoJSON into GeoDataFrame."""
    gf = asf.load_inventory("tests/data/query.geojson")

    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_get_orbit_url():
    """Get URL of precise orbit for a given granule."""
    gid = "S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA"
    # url = asf.get_orbit_url_server(gid) Dont require server connection
    url = asf.get_orbit_url_file(gid, inventory="tests/data/poeorb.txt")

    assert type(url) == str
    assert url.endswith(".EOF")
    assert "AUX_POEORB" in url


def test_get_slcs():
    """Retrieve SLCs from geopandas inventory."""
    acquisition_date = "20180320"
    path = 120
    gf = asf.load_inventory("tests/data/query.geojson")
    urls = asf.get_slc_urls(gf, acquisition_date, path)

    assert type(urls) == list
    assert len(urls) == 1
    assert (
        urls[0]
        == "https://datapool.asf.alaska.edu/SLC/SB/\
S1B_IW_SLC__1SDV_20180320T232821_20180320T232848_010121_01260A_0613.zip"
    )
