"""Test functions related to plotting."""
import dinosar.archive.plot as dplot
from dinosar.archive import asf
import contextlib
import os
import pytest


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


def test_plot_map(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        w, s, e, n = gf.geometry.cascaded_union.bounds
        snwe = [s, n, w, e]
        dplot.plot_map(gf, snwe)
        assert os.path.isfile("map.pdf")


def test_plot_timeline(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        plat1, plat2 = gf.platform.unique()
        dplot.plot_timeline(gf, plat1, plat2)
        assert os.path.isfile("timeline.pdf")


def test_plot_timeline_table(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        plat1, plat2 = gf.platform.unique()
        dplot.plot_timeline_table(gf)
        assert os.path.isfile("timeline_with_table.pdf")


def test_plot_timeline_sentinel(tmpdir):
    gf = asf.load_inventory("tests/data/query.geojson")
    with run_in(tmpdir):
        plat1, plat2 = gf.platform.unique()
        dplot.plot_timeline_sentinel(gf)
        assert os.path.isfile("timeline.pdf")
