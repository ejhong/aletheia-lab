"""Synthetic wall models rendered as elevation at fine resolution (metres), shared by the sensitivity scripts.

Each model returns a function (along, across) -> elevation in metres, defined in wall-local coordinates
(along the wall axis, across it), plus a description. Discrete stones are half-ellipsoids.
"""
import math
import numpy as np


def gaussian_ridge(length_m, fwhm_m, height_m):
    s = fwhm_m / 2.355
    def f(al, ac):
        return height_m * np.exp(-0.5 * (ac / s) ** 2) * (np.abs(al) <= length_m / 2)
    return f


def stone_line(length_m, rng, n_per_m, d_sampler, h_ratio, band_m, target_mean_vol=None):
    """Stones (half-ellipsoids, horizontal diameter d, height h_ratio*d) at random positions along the axis,
    centres scattered uniformly within +-band_m/2 across it. Overlaps take the maximum."""
    n = max(1, int(round(n_per_m * length_m)))
    al0 = rng.uniform(-length_m / 2, length_m / 2, n)
    ac0 = rng.uniform(-band_m / 2, band_m / 2, n)
    d = d_sampler(rng, n)
    if target_mean_vol is not None:  # rescale sizes so the mean stone volume matches the published total
        vol = (2.0 / 3.0) * math.pi * (d / 2) ** 2 * (h_ratio * d)
        d = d * (target_mean_vol / vol.mean()) ** (1 / 3)
    h = h_ratio * d
    def f(al, ac):
        z = np.zeros(np.broadcast(al, ac).shape)
        for a, c, di, hi in zip(al0, ac0, d, h):
            r2 = ((al - a) ** 2 + (ac - c) ** 2) / (di / 2) ** 2
            m = r2 < 1
            if m.any():
                z[m] = np.maximum(z[m], hi * np.sqrt(1 - r2[m]))
        return z
    return f, dict(n_stones=int(n), mean_d=float(d.mean()), max_h=float(h.max()), mean_h=float(h.mean()),
                   volume_m3=float(((2/3) * math.pi * (d/2)**2 * h).sum()))


def blinkerwall(length_m, rng):
    """Volume-matched to Geersen et al. 2024: 1,673 stones, 52.75 m3, along 971 m; width generally < 2 m."""
    return stone_line(length_m, rng, 1673 / 971, lambda r, n: r.lognormal(math.log(0.4), 0.45, n), 0.6, 1.2,
                      target_mean_vol=52.75 / 1673)


def blinkerwall_upper(length_m, rng):
    """Generous upper bound: one stone per metre, diameters 0.6-1.2 m, heights 0.42-0.84 m (all under 1 m)."""
    return stone_line(length_m, rng, 1.0, lambda r, n: r.uniform(0.6, 1.2, n), 0.7, 1.2)


def boulder_line(length_m, rng, d_lo, d_hi, h_ratio, spacing_m):
    return stone_line(length_m, rng, 1.0 / spacing_m, lambda r, n: r.uniform(d_lo, d_hi, n), h_ratio, 0.6)


def render(fun, px_m, half_px, az_deg, sub=0.1, offset=(0.0, 0.0)):
    """Render fun on a (2*half_px) square of output pixels of size px_m centred on the wall centre, as the
    block mean of a fine grid (cell `sub` metres). offset = sub-pixel shift (metres) of the wall centre."""
    f = int(round(px_m / sub)); n = 2 * half_px * f
    c = (np.arange(n) + 0.5) * sub - half_px * px_m
    xx, yy = np.meshgrid(c - offset[0], c - offset[1])  # x east (columns), y down (rows)
    rad = math.radians(az_deg); vx, vy = math.sin(rad), -math.cos(rad)
    al = xx * vx + yy * vy; ac = -xx * vy + yy * vx
    # only evaluate near the wall to save time
    z = np.zeros_like(xx)
    near = np.abs(ac) < 4.0
    z[near] = fun(al[near], ac[near])
    return z.reshape(2 * half_px, f, 2 * half_px, f).mean(axis=(1, 3))


def blinkerwall_single_file(length_m, rng):
    """As blinkerwall() but with all stones in single file (centres within a 0.3 m band): the most continuous
    arrangement the published count and volume allow."""
    return stone_line(length_m, rng, 1673 / 971, lambda r, n: r.lognormal(math.log(0.4), 0.45, n), 0.6, 0.3,
                      target_mean_vol=52.75 / 1673)
