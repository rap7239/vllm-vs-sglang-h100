import itertools

import yaml


def expand_blocks(matrix: dict) -> list[dict]:
    """One entry per server start: framework x model x tp (x prefix_cache), across every block."""
    servers = []
    for block_name, block in matrix["blocks"].items():
        combos = itertools.product(block["frameworks"], block["models"], block["tp"],
                                   block.get("prefix_cache", [True]))
        for framework, model, tp, prefix_cache in combos:
            servers.append({
                "block": block_name, "gpus": block["gpus"],
                "framework": framework, "model": model, "tp": tp,
                "prefix_cache": prefix_cache, "workloads": block["workloads"],
            })
    return servers

def estimate(matrix: dict, servers: list[dict]) -> list[dict]:
    """Add points, minutes and GPU-hours to each server, using the budget's time estimates."""
    est = matrix["budget"]["estimate"]
    levels = len(matrix["load"]["concurrency"]) + len(matrix["load"]["request_rate"])
    for s in servers:
        s["points"] = len(s["workloads"]) * levels
        s["minutes"] = est["server_start_min"] + s["points"] * est["point_min"]
        s["gpu_hours"] = s["minutes"] / 60 * s["gpus"]
    return servers

if __name__ == "__main__":
    matrix = yaml.safe_load(open("configs/matrix.yaml"))
    servers = estimate(matrix, expand_blocks(matrix))
    budget = matrix["budget"]
    print(f"{'block':<11}{'gpus':>5}{'servers':>8}{'points':>7}{'min/srv':>8}{'gpu_h':>7}")
    for block in matrix["blocks"]:
        rows = [s for s in servers if s["block"] == block]
        print(f"{block:<11}{rows[0]['gpus']:>5}{len(rows):>8}{rows[0]['points']:>7}"
              f"{rows[0]['minutes']:>8}{sum(s['gpu_hours'] for s in rows):>7.1f}")
    gpu_h = sum(s["gpu_hours"] for s in servers)
    cost = gpu_h * budget["usd_per_gpu_hour"]
    print(f"\n{len(servers)} servers, {sum(s['points'] for s in servers)} points, "
          f"{sum(s['minutes'] for s in servers) / 60:.1f} h wall, {gpu_h:.1f} GPU-h, "
          f"${cost:.2f} of ${budget['cap_usd']} cap")