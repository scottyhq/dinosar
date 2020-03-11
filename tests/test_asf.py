"""Tests for querying ASF archive."""
from dinosar.archive import asf
import pytest
import requests
import os
import geopandas as gpd
import contextlib


@contextlib.contextmanager
def run_in(path):
    CWD = os.getcwd()
    os.chdir(path)
    try:
        yield
    except Exception as e:
        print(e)
        raise
    finally:
        os.chdir(CWD)


@pytest.mark.network
def test_query_asf(tmpdir):
    with run_in(tmpdir):
        asf.query_asf([0.611, 1.048, -78.196, -77.522], "S1A")
        asf.query_asf([0.611, 1.048, -78.196, -77.522], "S1B")
        assert os.path.isfile("query_S1A.json")
        assert os.path.isfile("query_S1B.json")


@pytest.mark.network
def test_get_list():
    """Check retrieving specific frame information in inventory."""
    baseurl = "https://api.daac.asf.alaska.edu/services/search/param"
    granules = [
        "S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA",
        "S1A_IW_SLC__1SSV_20150526T015345_20150526T015412_006086_007E23_34D6",
    ]
    paramDict = dict(granule_list=granules, output="json")
    r = requests.get(baseurl, params=paramDict, verify=True, timeout=(5, 10))
    print(r.url)
    print(r.status_code)
    assert r.status_code == 200


def test_ogr2swe():
    bounds = asf.ogr2snwe("tests/data/UnionGap.shp")
    assert type(bounds) == list
    assert len(bounds) == 4
    assert bounds == [
        46.51905923587083,
        46.53477259526909,
        -120.471510549134,
        -120.4502650392162,
    ]


def test_load_asf_json():
    gf = asf.load_asf_json("tests/data/query_S1A.json")
    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_merge_inventories():
    gf = asf.merge_inventories("tests/data/query_S1A.json", "tests/data/query_S1B.json")
    assert type(gf) == gpd.geodataframe.GeoDataFrame


def test_load_inventory():
    gf = asf.load_inventory("tests/data/query.geojson")
    assert type(gf) == gpd.geodataframe.GeoDataFrame


@pytest.mark.network
def test_get_orbit_url():
    gid = "S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA"
    url = asf.get_orbit_url(gid)
    assert type(url) == str
    assert url.endswith(".EOF")
    assert "AUX_POEORB" in url


def test_get_orbit_url_file():
    gid = "S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA"
    # url = asf.get_orbit_url_server(gid) Dont require server connection
    url = asf.get_orbit_url_file(gid, inventory="tests/data/poeorb.txt")
    assert type(url) == str
    assert url.endswith(".EOF")
    assert "AUX_POEORB" in url


def test_get_slc_urls():
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


def test_get_slc_names():
    acquisition_date = "20180320"
    path = 120
    gf = asf.load_inventory("tests/data/query.geojson")
    names = asf.get_slc_names(gf, acquisition_date, path)
    assert type(names) == list
    assert len(names) == 1
    assert (
        names[0]
        == "S1B_IW_SLC__1SDV_20180320T232821_20180320T232848_010121_01260A_0613.zip"
    )


def test_summarize_orbits(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        asf.summarize_orbits(gf)
        assert os.path.isfile("acquisitions_40.csv")


def test_save_geojson_footprints(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        asf.save_geojson_footprints(gf)
        assert os.path.isfile("40/2015-10-03.geojson")


def test_save_inventory(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        asf.save_inventory(gf, outname="test.geojson")
        assert os.path.isfile("test.geojson")


def test_snwe2file(tmpdir):
    snwe = [0.611, 1.048, -78.196, -77.522]
    with run_in(tmpdir):
        asf.snwe2file(snwe)
        assert os.path.isfile("snwe.json")
        assert os.path.isfile("snwe.wkt")
        assert os.path.isfile("snwe.txt")
