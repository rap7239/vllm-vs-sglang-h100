def percentile(values: list[float], p: float) -> float | None:
    """The p-th percentile (0-100) of values, blending the two nearest values."""
    if not values:
        return None

    s = sorted(values)
    k = (len(s) - 1) * p / 100

    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)