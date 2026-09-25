"""Inference for ``QUANT_FASTLANE_HPIT_V1`` (pure Python, deterministic).

Unit: the daily net ``r_ex,t`` series of one calendar-time portfolio, given on a
contiguous span of vendor sessions with ``None`` where the book held no
position. The annualized alpha is ``252 x`` the mean over non-missing sessions,
so every statistic below is written for that *ratio* mean
``m = sum(d_t x_t) / sum(d_t)`` (``d_t`` = 1 if the session is active) through
its linearization ``u_t = d_t (x_t - m) / dbar``; with no gaps this is the
ordinary sample mean.

* :func:`studentized_block_bootstrap` - primary test (sealed): one-sided
  (H1: mean > 0) studentized moving-block bootstrap, block 80, B = 10,000, seed
  20260924. Observed studentizer: Bartlett lag-window long-run variance with
  window = block (Goetze & Kuensch 1996); bootstrap studentizer: the variance of
  the k = ceil(n / block) resampled block means (the "natural" MBB variance);
  bootstrap statistics are centred at the MBB expectation (Lahiri 2003).
  p = (1 + #{t* >= t}) / (1 + B); one-sided 95 % upper bound by percentile-t.
* :func:`fixed_b_hac_test` - co-check (sealed): HAC t-test, Bartlett kernel,
  bandwidth M = b n with b = 0.1, fixed-b (Kiefer & Vogelsang 2005) null.
  The null distribution is NOT taken from a recalled table: it is simulated by
  :func:`simulate_fixed_b_null` (seeded, see ``FIXED_B_NULL``) and stored as
  upper-tail quantiles; p-values interpolate that table.
* :func:`deflated_sharpe` - Bailey & Lopez de Prado (2014), N = N_trials.
* :func:`holm` - Holm step-down adjusted p-values over <= 3 finalists.
* :func:`romano_wolf_stepdown` - Romano & Wolf (2005) studentized step-down
  on a joint moving-block bootstrap (shared block draws), plus Hansen's (2005)
  SPA p-value as a reported cross-check.

Randomness comes only from :class:`SplitMix64` (seeded, version-independent),
never from the ``random`` module, so a sealed seed yields the same draws on
every Python version.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Mapping, Sequence

MASK64 = (1 << 64) - 1
TRADING_DAYS = 252
EULER_GAMMA = 0.5772156649015329
_NORMAL = NormalDist()


class InsufficientData(ValueError):
    """Too few observations for the requested statistic."""


class SplitMix64:
    """SplitMix64 (Steele, Lea & Flood 2014): small, seeded, platform-independent."""

    def __init__(self, seed: int) -> None:
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError("seed must be an integer")
        self.state = seed & MASK64

    def next64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def below(self, n: int) -> int:
        """Uniform integer in [0, n) without modulo bias (rejection sampling)."""
        if n <= 0:
            raise ValueError("n must be positive")
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            r = self.next64()
            if r < limit:
                return r % n

    def uniform(self) -> float:
        """Uniform float in (0, 1] with 53 random bits."""
        return ((self.next64() >> 11) + 1) * (1.0 / (1 << 53))

    def normal_pair(self) -> tuple[float, float]:
        """Two independent N(0, 1) draws (Box-Muller)."""
        r = math.sqrt(-2.0 * math.log(self.uniform()))
        theta = 2.0 * math.pi * self.uniform()
        return r * math.cos(theta), r * math.sin(theta)


# --- series preparation --------------------------------------------------------------

def _prepare(values: Sequence[float | None]) -> tuple[list[float], list[int], float, list[float]]:
    """Return (x with 0 for gaps, d indicators, ratio mean m, linearized u)."""
    n = len(values)
    if n == 0:
        raise InsufficientData("empty series")
    x, d = [], []
    for v in values:
        if v is None:
            x.append(0.0)
            d.append(0)
        else:
            f = float(v)
            if not math.isfinite(f):
                raise ValueError(f"non-finite observation {v!r}")
            x.append(f)
            d.append(1)
    count = sum(d)
    if count < 2:
        raise InsufficientData("fewer than two active sessions")
    m = sum(x) / count
    dbar = count / n
    u = [dt * (xt - m) / dbar for xt, dt in zip(x, d)]
    return x, d, m, u


def active_values(values: Sequence[float | None]) -> list[float]:
    return [float(v) for v in values if v is not None]


def ratio_mean(values: Sequence[float | None]) -> float:
    active = active_values(values)
    if not active:
        raise InsufficientData("no active session")
    return sum(active) / len(active)


def bartlett_lrv(u: Sequence[float], bandwidth: float) -> float:
    """Bartlett long-run variance sum_{|j|<M} (1 - |j|/M) gamma_j (u demeaned).

    Integer M uses the exact partial-sum identity of Kiefer & Vogelsang (2002),
    ``(2/(nM)) [sum_{t<n} S_t^2 - sum_{t<n-M} S_t S_{t+M}]`` (O(n)); otherwise
    the autocovariances are summed directly.
    """
    n = len(u)
    if n < 2:
        raise InsufficientData("need at least two observations")
    M = float(bandwidth)
    if not math.isfinite(M) or M <= 0:
        raise ValueError("bandwidth must be positive")
    mean = sum(u) / n
    v = [a - mean for a in u]
    if M >= 1 and M == int(M):
        mi = int(M)
        partial, s = [], 0.0
        for a in v:
            s += a
            partial.append(s)
        a2 = sum(partial[t] * partial[t] for t in range(n - 1))
        cross = sum(partial[t] * partial[t + mi] for t in range(max(0, n - mi - 1)))
        return 2.0 * (a2 - cross) / (n * mi)
    total = sum(a * a for a in v) / n
    j = 1
    while j < M and j < n:
        gamma = sum(v[t] * v[t + j] for t in range(n - j)) / n
        total += 2.0 * (1.0 - j / M) * gamma
        j += 1
    return total


# --- primary test: studentized moving-block bootstrap ------------------------------------

def _block_sums(x: Sequence[float], d: Sequence[int], block: int) -> tuple[list[float], list[int]]:
    n = len(x)
    px, pd = [0.0], [0]
    for xt, dt in zip(x, d):
        px.append(px[-1] + xt)
        pd.append(pd[-1] + dt)
    return ([px[s + block] - px[s] for s in range(n - block + 1)],
            [pd[s + block] - pd[s] for s in range(n - block + 1)])


def _t_star(A: Sequence[float], D: Sequence[int], idx: Sequence[int], block: int, k: int,
            m_tilde: float) -> tuple[float, bool]:
    sa = 0.0
    sd = 0
    for i in idx:
        sa += A[i]
        sd += D[i]
    if sd == 0:
        return 0.0, True
    length = k * block
    ms = sa / sd
    scale = block * sd / length
    q = 0.0
    for i in idx:
        r = A[i] - ms * D[i]
        q += r * r
    s2 = (block / k) * q / (scale * scale)
    diff = ms - m_tilde
    if s2 <= 0.0:
        return (0.0 if diff == 0 else math.copysign(math.inf, diff)), False
    return math.sqrt(length) * diff / math.sqrt(s2), False


def _studentized(m: float, se: float) -> float:
    if se > 0:
        return m / se
    return 0.0 if m == 0 else math.copysign(math.inf, m)


def studentized_block_bootstrap(values: Sequence[float | None], *, block: int, draws: int,
                                seed: int, level: float = 0.95) -> dict:
    """One-sided (H1: mean > 0) studentized MBB test of the ratio mean."""
    x, d, m, u = _prepare(values)
    n = len(x)
    if not isinstance(block, int) or block < 2:
        raise ValueError("block must be an integer >= 2")
    if n < block:
        raise InsufficientData(f"series of {n} sessions is shorter than one {block}-session block")
    if draws < 1:
        raise ValueError("draws must be >= 1")
    sigma2 = bartlett_lrv(u, block)
    se = math.sqrt(max(sigma2, 0.0) / n)
    t_obs = _studentized(m, se)
    A, D = _block_sums(x, d, block)
    nb = len(A)
    k = -(-n // block)
    m_tilde = sum(A) / sum(D)
    rng = SplitMix64(seed)
    t_stars = []
    degenerate = 0
    for _ in range(draws):
        idx = [rng.below(nb) for _ in range(k)]
        t, empty = _t_star(A, D, idx, block, k, m_tilde)
        degenerate += empty
        t_stars.append(t)
    exceed = sum(1 for t in t_stars if t >= t_obs)
    p = (1 + exceed) / (1 + draws)
    ordered = sorted(t_stars)
    q_low = ordered[max(0, math.ceil(round((1.0 - level) * draws, 9)) - 1)]
    upper = m - q_low * se if math.isfinite(q_low) else math.inf
    return {
        "test": "STUDENTIZED_MOVING_BLOCK_BOOTSTRAP_ONE_SIDED",
        "n_sessions": n, "n_active": sum(d), "mean": m, "se": se, "t": t_obs,
        "p_value": p, "block": block, "blocks_per_draw": k, "draws": draws, "seed": seed,
        "degenerate_draws": degenerate, "level": level, "t_star_lower_quantile": q_low,
        "upper_bound_mean": upper, "upper_bound_annual": TRADING_DAYS * upper,
        "mean_annual": TRADING_DAYS * m,
    }


# --- co-check: fixed-b HAC t-test ----------------------------------------------------------

# Fixed-b null of the Bartlett HAC t-statistic at b = 0.1 (Kiefer & Vogelsang 2005
# asymptotics), NOT copied from a recalled table: simulated by
# simulate_fixed_b_null(b=0.1, steps=2000, reps=200_000, seed=20260924) - i.i.d. N(0, 1)
# series of 2,000 steps (SplitMix64 + Box-Muller), M = 200, t = sqrt(T) mean / sqrt(Omega),
# followed by fixed_b_quantile_table(..., FIXED_B_TAIL_PROBS). Upper-tail quantiles q(p) with
# P(t >= q(p)) = p (order statistic ceil((1 - p) R)); Monte Carlo s.e. of q(0.05) ~ 0.006.
# Cross-checks: the same run at T = 1,000 gives q(0.05) = 1.8370; the Kiefer-Vogelsang (2005)
# Bartlett polynomial as recalled (1.6449 + 2.1859 b + 0.3142 b^2 - 0.3427 b^3 = 1.8663 at
# b = 0.1) could not be verified against the paper here (see PROTOCOL_CLARIFICATIONS C16).
FIXED_B_NULL = {
    "kernel": "Bartlett",
    "b": 0.1,
    "method": "seeded Monte Carlo of the HAC t under i.i.d. N(0,1), T=2000, M=bT; "
              "Kiefer & Vogelsang (2005) fixed-b asymptotics",
    "steps": 2000,
    "reps": 200_000,
    "seed": 20260924,
}
_FIXED_B_QUANTILES: tuple[tuple[float, float], ...] = (
    (0.5, 0.0022), (0.49, 0.0296), (0.48, 0.0552), (0.47, 0.0809),
    (0.46, 0.1089), (0.45, 0.1357), (0.44, 0.1632), (0.43, 0.1901),
    (0.42, 0.2162), (0.41, 0.2449), (0.4, 0.2712), (0.39, 0.2978),
    (0.38, 0.3267), (0.37, 0.3558), (0.36, 0.3851), (0.35, 0.4143),
    (0.34, 0.4429), (0.33, 0.4727), (0.32, 0.5030), (0.31, 0.5340),
    (0.3, 0.5653), (0.29, 0.5954), (0.28, 0.6275), (0.27, 0.6605),
    (0.26, 0.6937), (0.25, 0.7282), (0.24, 0.7619), (0.23, 0.7986),
    (0.22, 0.8337), (0.21, 0.8711), (0.2, 0.9095), (0.19, 0.9507),
    (0.18, 0.9926), (0.17, 1.0344), (0.16, 1.0796), (0.15, 1.1266),
    (0.14, 1.1754), (0.13, 1.2291), (0.12, 1.2826), (0.11, 1.3440),
    (0.1, 1.4090), (0.09, 1.4803), (0.08, 1.5555), (0.07, 1.6382),
    (0.06, 1.7334), (0.05, 1.8373), (0.04, 1.9681), (0.03, 2.1341),
    (0.02, 2.3572), (0.01, 2.7052), (0.009, 2.7571), (0.008, 2.8148),
    (0.007, 2.8894), (0.006, 2.9615), (0.005, 3.0520), (0.004, 3.1563),
    (0.003, 3.2980), (0.002, 3.5003), (0.001, 3.8497), (0.0005, 4.1583),
    (0.0002, 4.7196), (0.0001, 5.0924),
)


def simulate_fixed_b_null(*, b: float, steps: int, reps: int, seed: int) -> list[float]:
    """Sorted simulated HAC t-statistics under the null (for the fixed-b table)."""
    mi = b * steps
    if mi != int(mi) or mi < 1:
        raise ValueError("b * steps must be a positive integer")
    mi = int(mi)
    rng = SplitMix64(seed)
    out = []
    root = math.sqrt(steps)
    for _ in range(reps):
        x = []
        while len(x) < steps:
            x.extend(rng.normal_pair())
        x = x[:steps]
        m = sum(x) / steps
        partial, s = [], 0.0
        for a in x:
            s += a - m
            partial.append(s)
        a2 = sum(partial[t] * partial[t] for t in range(steps - 1))
        cross = sum(partial[t] * partial[t + mi] for t in range(steps - mi - 1))
        omega = 2.0 * (a2 - cross) / (steps * mi)
        out.append(root * m / math.sqrt(omega))
    out.sort()
    return out


def fixed_b_quantile_table(sorted_stats: Sequence[float],
                           tail_probs: Sequence[float]) -> list[tuple[float, float]]:
    reps = len(sorted_stats)
    return [(p, sorted_stats[max(0, math.ceil((1.0 - p) * reps) - 1)]) for p in tail_probs]


FIXED_B_TAIL_PROBS = tuple([round(0.50 - 0.01 * i, 4) for i in range(50)]
                           + [round(0.009 - 0.001 * i, 4) for i in range(9)]
                           + [0.0005, 0.0002, 0.0001])


def _table() -> tuple[tuple[float, float], ...]:
    if not _FIXED_B_QUANTILES:
        raise RuntimeError("fixed-b quantile table is missing")
    return _FIXED_B_QUANTILES


# Lead decision on PROTOCOL_CLARIFICATIONS C16 (pre-outcome): the simulated table and the
# Kiefer-Vogelsang (2005) Bartlett cubic polynomials cv(b) = a0 + a1 b + a2 b^2 + a3 b^3
# (coefficients as recalled, not verified against the paper here) disagree slightly. The
# co-check must use whichever is MORE conservative. So the statistic is deflated by the largest
# polynomial/simulation ratio over the tabulated levels, floored at 1. A wrong recalled
# coefficient can only make the co-check stricter, never looser.
KV2005_BARTLETT_POLY: dict[float, tuple[float, float, float, float]] = {
    0.10: (1.2816, 1.3040, 0.5135, -0.3386),
    0.05: (1.6449, 2.1859, 0.3142, -0.3427),
    0.025: (1.9600, 2.9694, 0.4160, -0.5324),
}


def _kv_poly(tail: float, b: float) -> float:
    a0, a1, a2, a3 = KV2005_BARTLETT_POLY[tail]
    return a0 + a1 * b + a2 * b * b + a3 * b ** 3


def _simulated_quantile(tail: float) -> float:
    table = _table()                       # descending p, ascending q
    for (p_hi, q_lo), (p_lo, q_hi) in zip(table, table[1:]):
        if p_lo <= tail <= p_hi:
            if p_hi == p_lo:
                return q_lo
            return q_lo + (q_hi - q_lo) * (p_hi - tail) / (p_hi - p_lo)
    raise ValueError(f"tail {tail} outside the fixed-b table")


def conservative_scale() -> float:
    """Largest KV-polynomial / simulated-quantile ratio at b = FIXED_B_NULL['b'], floored at 1."""
    b = float(FIXED_B_NULL["b"])
    ratios = [_kv_poly(t, b) / _simulated_quantile(t) for t in KV2005_BARTLETT_POLY]
    return max(1.0, *ratios)


def fixed_b_critical_value(tail: float = 0.05) -> float:
    for p, q in _table():
        if abs(p - tail) < 1e-12:
            return q * conservative_scale()
    raise ValueError(f"no tabulated fixed-b quantile for tail {tail}")


def fixed_b_pvalue(t: float) -> float:
    """One-sided P(T >= t) under the fixed-b null (symmetric), by linear interpolation.

    Beyond the smallest tabulated tail (1e-4) the p-value is reported as 1e-4
    (conservative for any Holm threshold used here). A positive statistic is first deflated
    by ``conservative_scale()`` (lead decision on C16), so the p-value is never smaller than
    the one implied by either the simulated table or the Kiefer-Vogelsang polynomials.
    """
    table = _table()                       # descending p, ascending q
    if not math.isfinite(t):
        return table[-1][0] if t > 0 else 1.0
    if t < 0:
        return 1.0 - _raw_fixed_b_pvalue(-t)
    return _raw_fixed_b_pvalue(t / conservative_scale())


def _raw_fixed_b_pvalue(t: float) -> float:
    table = _table()
    if t <= table[0][1]:                   # between 0 and the median quantile (~0)
        return table[0][0]
    for (p_hi, q_lo), (p_lo, q_hi) in zip(table, table[1:]):
        if q_lo <= t <= q_hi:
            if q_hi == q_lo:
                return p_lo
            return p_hi + (p_lo - p_hi) * (t - q_lo) / (q_hi - q_lo)
    return table[-1][0]


def fixed_b_hac_test(values: Sequence[float | None], *, b: float, kernel: str = "Bartlett",
                     level: float = 0.95) -> dict:
    """One-sided fixed-b HAC t-test of the ratio mean (Bartlett, M = b n)."""
    if kernel != "Bartlett" or b != FIXED_B_NULL["b"]:
        raise ValueError("only the sealed Bartlett b = 0.1 fixed-b null is tabulated")
    x, d, m, u = _prepare(values)
    n = len(x)
    omega = bartlett_lrv(u, b * n)
    se = math.sqrt(max(omega, 0.0) / n)
    t = _studentized(m, se)
    cv = fixed_b_critical_value(round(1.0 - level, 10))
    upper = m + cv * se
    return {
        "test": "FIXED_B_HAC_T_ONE_SIDED", "kernel": kernel, "b": b, "bandwidth": b * n,
        "n_sessions": n, "n_active": sum(d), "mean": m, "se": se, "t": t,
        "p_value": fixed_b_pvalue(t), "critical_value": cv, "level": level,
        "critical_value_source": {k: FIXED_B_NULL[k] for k in ("method", "steps", "reps",
                                                                 "seed")},
        "upper_bound_mean": upper, "upper_bound_annual": TRADING_DAYS * upper,
        "mean_annual": TRADING_DAYS * m,
    }


# --- multiplicity -------------------------------------------------------------------------

def holm(pvalues: Mapping[str, float]) -> dict[str, float]:
    """Holm (1979) step-down adjusted p-values (monotone, capped at 1)."""
    items = sorted(pvalues.items(), key=lambda kv: (kv[1], kv[0]))
    m = len(items)
    out: dict[str, float] = {}
    running = 0.0
    for i, (key, p) in enumerate(items):
        if not (0.0 <= p <= 1.0):
            raise ValueError(f"p-value {p!r} for {key} outside [0, 1]")
        running = max(running, min(1.0, (m - i) * p))
        out[key] = running
    return out


def sharpe_moments(values: Sequence[float | None]) -> dict:
    """Per-session Sharpe (sample sd) with biased skewness and non-excess kurtosis."""
    xs = active_values(values)
    n = len(xs)
    if n < 3:
        raise InsufficientData("need at least three active sessions")
    mean = sum(xs) / n
    m2 = sum((v - mean) ** 2 for v in xs) / n
    if m2 <= 0:
        raise InsufficientData("zero-variance series")
    m3 = sum((v - mean) ** 3 for v in xs) / n
    m4 = sum((v - mean) ** 4 for v in xs) / n
    sd = math.sqrt(m2 * n / (n - 1))
    return {"n": n, "mean": mean, "sd": sd, "sr": mean / sd,
            "skew": m3 / m2 ** 1.5, "kurtosis": m4 / (m2 * m2)}


def floored_sr_variance(cross_variance: float, sr: float, n_obs: int) -> float:
    """V[SR] for the DSR, floored at the sampling variance of the per-period SR estimate,
    ``(1 + SR^2 / 2) / n`` (Lo 2002, i.i.d.), so N_trials always deflates (C21)."""
    if n_obs < 1:
        raise InsufficientData("need at least one observation")
    return max(float(cross_variance), (1.0 + 0.5 * sr * sr) / n_obs)


def expected_max_sharpe(sr_variance: float, n_trials: int) -> float:
    """SR_0 = sqrt(V) ((1 - g) Phi^-1(1 - 1/N) + g Phi^-1(1 - 1/(N e)))."""
    if n_trials < 2 or sr_variance <= 0:
        return 0.0
    return math.sqrt(sr_variance) * ((1.0 - EULER_GAMMA) * _NORMAL.inv_cdf(1.0 - 1.0 / n_trials)
                                     + EULER_GAMMA * _NORMAL.inv_cdf(1.0 - 1.0 / (n_trials * math.e)))


def deflated_sharpe(*, sr: float, n_obs: int, skew: float, kurtosis: float,
                    sr_variance: float, n_trials: int) -> dict:
    """Bailey & Lopez de Prado (2014), J. Portfolio Management 40(5)."""
    if n_obs < 2:
        raise InsufficientData("DSR needs at least two observations")
    sr0 = expected_max_sharpe(sr_variance, n_trials)
    denom = 1.0 - skew * sr + (kurtosis - 1.0) / 4.0 * sr * sr
    if denom <= 0:
        return {"dsr": 0.0, "sr0": sr0, "z": None, "valid": False, "n_trials": n_trials}
    z = (sr - sr0) * math.sqrt(n_obs - 1) / math.sqrt(denom)
    return {"dsr": _NORMAL.cdf(z), "sr0": sr0, "z": z, "valid": True, "n_trials": n_trials}


def align(series: Mapping[str, tuple[int, Sequence[float | None]]]) -> tuple[int, dict]:
    """Pad (start_index, values) series with None onto their common index span."""
    if not series:
        raise InsufficientData("no series")
    start = min(s for s, _ in series.values())
    end = max(s + len(v) for s, v in series.values())
    out = {}
    for key, (s, v) in series.items():
        out[key] = [None] * (s - start) + list(v) + [None] * (end - s - len(v))
    return start, out


def romano_wolf_stepdown(series: Mapping[str, Sequence[float | None]], *, block: int, draws: int,
                         seed: int) -> dict:
    """One-sided studentized Romano-Wolf step-down and Hansen SPA on a joint MBB.

    All series must share one index span (use :func:`align`); the same block
    draws are applied to every series, preserving their cross-dependence.
    """
    keys = sorted(series)
    if not keys:
        raise InsufficientData("no series")
    n = len(series[keys[0]])
    if any(len(series[k]) != n for k in keys):
        raise ValueError("series must be aligned to one span")
    if n < block:
        raise InsufficientData("span shorter than one block")
    prepared = {}
    t_obs = {}
    for key in keys:
        x, d, m, u = _prepare(series[key])
        se = math.sqrt(max(bartlett_lrv(u, block), 0.0) / n)
        A, D = _block_sums(x, d, block)
        sd = sum(D)
        prepared[key] = (A, D, sum(A) / sd if sd else 0.0)
        t_obs[key] = _studentized(m, se)
    nb = n - block + 1
    k = -(-n // block)
    rng = SplitMix64(seed)
    stars = {key: [] for key in keys}
    for _ in range(draws):
        idx = [rng.below(nb) for _ in range(k)]
        for key in keys:
            A, D, m_tilde = prepared[key]
            stars[key].append(_t_star(A, D, idx, block, k, m_tilde)[0])
    order = sorted(keys, key=lambda key: (-t_obs[key], key))
    adjusted: dict[str, float] = {}
    running = 0.0
    for j, key in enumerate(order):
        remaining = order[j:]
        exceed = 0
        for b in range(draws):
            if max(stars[r][b] for r in remaining) >= t_obs[key]:
                exceed += 1
        running = max(running, (1 + exceed) / (1 + draws))
        adjusted[key] = running
    threshold = math.sqrt(2.0 * math.log(math.log(n))) if n > 15 else 0.0
    shift = {key: (t_obs[key] if t_obs[key] <= -threshold else 0.0) for key in keys}
    spa_stat = max(0.0, max(t_obs.values()))
    spa_exceed = 0
    for b in range(draws):
        stat = max(0.0, max(stars[key][b] + shift[key] for key in keys))
        spa_exceed += stat >= spa_stat
    return {"method": "ROMANO_WOLF_STEPDOWN_STUDENTIZED_ONE_SIDED", "block": block,
            "draws": draws, "seed": seed, "n_sessions": n, "t": t_obs, "p_adjusted": adjusted,
            "spa": {"method": "HANSEN_SPA_CONSISTENT_STUDENTIZED", "statistic": spa_stat,
                    "p_value": (1 + spa_exceed) / (1 + draws), "role": "cross-check only"}}
