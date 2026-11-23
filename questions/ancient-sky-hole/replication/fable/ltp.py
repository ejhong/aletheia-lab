"""Long-term precession of the equator pole, Vondrak, Capitaine & Wallace (2011, A&A 534, A22;
corrigendum 2012, A&A 541, C1), written independently for this replication from the published
series as used by SOFA/ERFA eraLtpequ. Vectorised over the epoch.

ltpequ(epj) returns the unit vector of the mean north celestial pole of date in the J2000 mean
equator-and-equinox frame (GCRS to within the 0.02 arcsec frame bias, ignored here).
"""
import numpy as np

DAS2R = np.pi / (180.0 * 3600.0)

# Polynomial coefficients for X and Y of the pole (arcsec, powers of T in Julian centuries).
_XYPOL = np.array([
    [5453.282155, 0.4252841, -0.00037173, -0.000000152],
    [-73750.930350, -0.7675452, -0.00018725, 0.000000231],
])
# Periodic terms: period (centuries), cos-coefficient X, cos-coefficient Y, sin-coefficient X, sin-coefficient Y.
_XYPER = np.array([
    [256.75, -819.940624, 75004.344875, 81491.287984, 1558.515853],
    [708.15, -8444.676815, 624.033993, 787.163481, 7774.939698],
    [274.20, 2600.009459, 1251.136893, 1251.296102, -2219.534038],
    [241.45, 2755.175630, -1102.212834, -1257.950837, -2523.969396],
    [2309.00, -167.659835, -2660.664980, -2966.799730, 247.850422],
    [492.20, 871.855056, 699.291817, 639.744522, -846.485643],
    [396.10, 44.769698, 153.167220, 131.600209, -1393.124055],
    [288.90, -512.313065, -950.865637, -445.040117, 368.526116],
    [231.10, -819.415595, 499.754645, 584.522874, 749.045012],
    [1610.00, -538.071099, -145.188210, -89.756563, 444.704518],
    [620.00, -189.793622, 558.116553, 524.429630, 235.934465],
    [157.87, -402.922932, -23.923029, -13.549067, 374.049623],
    [220.30, 179.516345, -165.405086, -210.157124, -171.330180],
    [1200.00, -9.814756, 9.344131, -44.919798, -22.899655],
])


def ltpequ(epj):
    epj = np.asarray(epj, dtype=float)
    t = (epj - 2000.0) / 100.0
    w = 2.0 * np.pi * t
    a = w[..., None] / _XYPER[:, 0]
    c, s = np.cos(a), np.sin(a)
    x = (c * _XYPER[:, 1] + s * _XYPER[:, 3]).sum(-1)
    y = (c * _XYPER[:, 2] + s * _XYPER[:, 4]).sum(-1)
    tp = np.stack([np.ones_like(t), t, t * t, t * t * t], -1)
    x = x + (tp * _XYPOL[0]).sum(-1)
    y = y + (tp * _XYPOL[1]).sum(-1)
    x = x * DAS2R
    y = y * DAS2R
    z = np.sqrt(np.clip(1.0 - x * x - y * y, 0.0, None))
    return np.stack([x, y, z], -1)
