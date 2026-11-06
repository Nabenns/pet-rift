#!/usr/bin/env python3
"""Simulate Pet Rift rolls to verify the odds table (gate G1).

Reads design/economy.json, simulates N rolls per luck scenario using the SAME
algorithm as src/shared/Economy.luau (integer weights per 10.000, luck multiplies
chase tiers then renormalises, pity forces Divine at threshold).

This verifies the DOCUMENTED numbers. It does not replace the in-game harness.

Usage:
    python3 tools/sim_rolls.py                 # 100.000 rolls x luck 1.0/2.0/3.0
    python3 tools/sim_rolls.py --rolls 50000 --luck 1.5
"""
import argparse
import csv
import json
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
ECON = ROOT / "design" / "economy.json"
OUT_CSV = ROOT / "captures" / "G1-sim.csv"

SIGMA3 = 3.0


def load():
    return json.loads(ECON.read_text())


def int_weights(econ, luck):
    w = {t["id"]: round(t["weight"] * 100) for t in econ["tiers"]}
    for tier in econ["luck"]["applies_to"]:
        w[tier] = math.floor(w[tier] * luck + 0.5)
    return w


def simulate(econ, rolls, luck, seed):
    w = int_weights(econ, luck)
    order = [t["id"] for t in econ["tiers"]]
    total = sum(w.values())
    threshold = econ["pity"]["threshold"]
    variants = econ["variants"]
    rng = random.Random(seed)

    counts = {t: 0 for t in order}
    var_counts = {v["id"]: 0 for v in variants}
    pity_hits = 0
    since_divine = 0

    for _ in range(rolls):
        roll = rng.randint(1, total)
        acc = 0
        tier = order[-1]
        for t in order:
            acc += w[t]
            if roll <= acc:
                tier = t
                break

        since_divine += 1
        if since_divine >= threshold:
            tier = "Divine"
            pity_hits += 1
        if tier == "Divine":
            since_divine = 0

        counts[tier] += 1

        vr = rng.randint(1, 100)
        acc = 0
        for v in variants:
            acc += v["chance"]
            if vr <= acc:
                var_counts[v["id"]] += 1
                break

    return counts, var_counts, total, pity_hits


def check(econ, counts, rolls, luck, total):
    w = int_weights(econ, luck)
    rows = []
    ok = True
    for t in econ["tiers"]:
        tier = t["id"]
        expected = w[tier] / total
        observed = counts[tier] / rolls
        diff = observed - expected
        rel = diff / expected if expected > 0 else 0.0
        sigma = math.sqrt(rolls * expected * (1 - expected))
        z = diff * rolls / sigma if sigma > 0 else 0.0
        if expected > 0.01:
            passed = abs(rel) <= 0.05
        else:
            passed = abs(z) <= SIGMA3
        ok = ok and passed
        rows.append({
            "luck": luck,
            "tier": tier,
            "weight": w[tier],
            "expected_pct": round(expected * 100, 4),
            "observed_pct": round(observed * 100, 4),
            "rel_diff_pct": round(rel * 100, 3),
            "z": round(z, 2),
            "check": "rel<=5%" if expected > 0.01 else "|z|<=3",
            "pass": passed,
        })
    return rows, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rolls", type=int, default=100_000)
    ap.add_argument("--luck", type=float, nargs="*", default=[1.0, 2.0, 3.0])
    ap.add_argument("--seed", type=int, default=20261106)
    args = ap.parse_args()

    econ = load()
    all_rows = []
    all_ok = True
    summary = []

    for i, luck in enumerate(args.luck):
        counts, var_counts, total, pity_hits = simulate(econ, args.rolls, luck, args.seed + i)
        rows, ok = check(econ, counts, args.rolls, luck, total)
        all_rows.extend(rows)
        all_ok = all_ok and ok

        print(f"\nluck {luck:.2f}  rolls={args.rolls:,}  total_weight={total}  pity_hits={pity_hits}")
        print(f"  {'tier':<10}{'expect%':>10}{'obs%':>10}{'rel':>9}{'z':>7}  pass")
        for r in rows:
            print(f"  {r['tier']:<10}{r['expected_pct']:>10.4f}{r['observed_pct']:>10.4f}"
                  f"{r['rel_diff_pct']:>8.2f}%{r['z']:>7.2f}  {'OK' if r['pass'] else 'FAIL'}")
        vsum = sum(var_counts.values())
        print("  variants: " + "  ".join(f"{k}={v / vsum * 100:.2f}%" for k, v in var_counts.items()))
        summary.append({"luck": luck, "rolls": args.rolls, "pity_hits": pity_hits, "pass": ok})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nwrote {OUT_CSV.relative_to(ROOT)}")
    print(f"G1: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())