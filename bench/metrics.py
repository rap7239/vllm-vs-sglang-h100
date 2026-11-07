PERCENTILES = (50,90,99)

def percentile(values: list[float], p: float) -> float | None:
    """The p-th percentile (0-100) of values, blending the two nearest values."""
    if not values:
        return None

    s = sorted(values)
    k = (len(s) - 1) * p / 100

    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def summarize(results: list[dict], wall_s: float) -> dict:
    """Turn one load point's per-request results into percentiles and throughput."""
    summary = {"requests": len(results), "wall_s": wall_s}

    series = {
        "ttft_ms": [r["ttft_ms"] for r in results if r["ttft_ms"] is not None],
        "tpot_ms": [r["tpot_ms"] for r in results if r["tpot_ms"] is not None],
        "e2e_ms": [r["e2e_ms"] for r in results],
        "itl_ms": [x for r in results for x in r["itl_ms"]],
    }

    for name,values in series.items():
        summary[f"{name}_mean"] = sum(values) / len(values) if values else None
        for p in PERCENTILES:
            summary[f"{name}_p{p}"] = percentile(values, p)


    out_tokens = sum(r["output_tokens"] or 0 for r in results)
    summary["output_tokens"] = out_tokens
    summary["input_tokens"] = sum(r["input_tokens"] or 0 for r in results)
    summary["output_tok_per_s"] = out_tokens / wall_s
    summary["request_per_s"] = len(results) / wall_s
    return summary