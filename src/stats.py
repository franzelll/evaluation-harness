import numpy as np
from scipy.stats import ttest_rel, wilcoxon


def paired_tests(xs, ys):
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]
    ys = ys[mask]
    if len(xs) < 3:
        return {"n": len(xs), "t": np.nan, "tp": np.nan, "w": np.nan, "wp": np.nan}
    t, tp = ttest_rel(xs, ys)
    try:
        w, wp = wilcoxon(xs, ys)
    except ValueError:
        w, wp = np.nan, np.nan
    return {
        "n": len(xs),
        "t": float(t),
        "tp": float(tp),
        "w": float(w),
        "wp": float(wp),
    }


def cohens_d(xs, ys):
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]
    ys = ys[mask]
    if len(xs) < 3:
        return np.nan
    s = np.sqrt(((xs.std(ddof=1) ** 2) + (ys.std(ddof=1) ** 2)) / 2)
    return float((ys.mean() - xs.mean()) / s) if s > 0 else np.nan


def bootstrap_ci(diffs, B=5000, alpha=0.05, rng=None):
    rng = np.random.default_rng(rng)
    diffs = np.asarray(diffs)
    boots = []
    n = len(diffs)
    for _ in range(B):
        idx = rng.integers(0, n, n)
        boots.append(diffs[idx].mean())
    boots = np.sort(boots)
    lo = boots[int((alpha / 2) * B)]
    hi = boots[int((1 - alpha / 2) * B)]
    return float(lo), float(hi)


def holm_correction(pvals):
    # returns dict: index -> adjusted_p
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [None] * m
    for k, i in enumerate(order, start=1):
        adj[i] = min(1.0, (m - k + 1) * pvals[i])
    return adj
