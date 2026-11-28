"""Rerun the study's own program unmodified, redirecting its data/results folders and replacing its User-Agent.

usage: python -I rerun.py <repo>/questions/drowned-walls-submeter/analysis <data_dir> <results_dir>
<data_dir> must contain baltic/{Test_Areas.zip,Time_Series.zip,pangaea_988426_munitions.tab}; NOAA tiles are
fetched by the program's own functions into <data_dir>/huron_tiles with a generic User-Agent.
"""
import pathlib, sys, urllib.request

ana, data, res = (pathlib.Path(a).resolve() for a in sys.argv[1:4])
sys.path.insert(0, str(ana))
_Real = urllib.request.Request
def _generic(url, *a, headers=None, **k):  # strip the program's project-naming User-Agent
    return _Real(url, *a, headers={"User-Agent": "bathymetry-audit/1.0"}, **k)
urllib.request.Request = _generic
import run_submeter_scan as m  # noqa: E402
m.DATA, m.HURON_DIR, m.BALTIC_DIR, m.PREV_DIR, m.RES = data, data / "huron_tiles", data / "baltic", data / "previews", res
m.main()
