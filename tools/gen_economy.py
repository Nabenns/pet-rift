#!/usr/bin/env python3
"""Generate src/shared/Economy.luau from design/economy.json.

Single source of truth: design/economy.json. Never edit the generated Luau by hand.
Usage: python3 tools/gen_economy.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "economy.json"
OUT = ROOT / "src" / "shared" / "Economy.luau"

HEADER = """--!strict
-- GENERATED FILE. DO NOT EDIT.
-- Source: design/economy.json
-- Regenerate: python3 tools/gen_economy.py
-- Weights are integers per 10.000 so luck multiplication has no float drift.
"""


def luau_number(x):
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return repr(x)


def main():
    data = json.loads(SRC.read_text())
    tiers = data["tiers"]
    pets = data["pets"]
    variants = data["variants"]

    total_w = sum(t["weight"] for t in tiers)
    assert abs(total_w - 100.0) < 1e-9, f"tier weights must sum to 100, got {total_w}"

    int_w = {t["id"]: round(t["weight"] * 100) for t in tiers}
    assert sum(int_w.values()) == 10000, f"integer weights must sum to 10000, got {sum(int_w.values())}"

    for tier in int_w:
        assert sum(1 for p in pets if p["tier"] == tier) >= 1, f"tier {tier} has no pet"

    vchance = sum(v["chance"] for v in variants)
    assert vchance == 100, f"variant chances must sum to 100, got {vchance}"

    lines = [HEADER, ""]
    lines.append("local Economy = {}")
    lines.append("")

    order = [t["id"] for t in tiers]
    lines.append("Economy.TIER_ORDER = { " + ", ".join(f'"{t}"' for t in order) + " }")
    lines.append("Economy.CHASE_TIERS = { " + ", ".join(
        f'"{t["id"]}"' for t in tiers if t["id"] in data["luck"]["applies_to"]) + " }")
    lines.append("")

    lines.append("Economy.BASE_WEIGHTS = {")
    for t in tiers:
        lines.append(f'    ["{t["id"]}"] = {int_w[t["id"]]},')
    lines.append("}")
    lines.append("")

    lines.append("Economy.TIERS = {")
    for t in tiers:
        lines.append(
            f'    ["{t["id"]}"] = {{ weight = {luau_number(t["weight"])}, shard = {t["shard"]}, '
            f'color = "{t["color"]}", glow = {luau_number(float(t["glow"]))} }},'
        )
    lines.append("}")
    lines.append("")

    lines.append("Economy.VARIANTS = {")
    for v in variants:
        lines.append(
            f'    ["{v["id"]}"] = {{ chance = {v["chance"]}, shardMult = {luau_number(float(v["shard_mult"]))}, '
            f'material = Enum.Material.{v["material"]}, tint = "{v["tint"]}" }},'
        )
    lines.append("}")
    lines.append("Economy.VARIANT_ORDER = { " + ", ".join(f'"{v["id"]}"' for v in variants) + " }")
    lines.append("")

    lines.append("Economy.PETS = {")
    for p in pets:
        lines.append(
            f'    {{ id = "{p["id"]}", tier = "{p["tier"]}", ears = "{p["ears"]}", '
            f'tail = "{p["tail"]}", build = "{p["build"]}" }},'
        )
    lines.append("}")
    lines.append("Economy.PETS_BY_TIER = {}")
    lines.append("for _, pet in Economy.PETS do")
    lines.append("    local list = Economy.PETS_BY_TIER[pet.tier]")
    lines.append("    if not list then list = {}; Economy.PETS_BY_TIER[pet.tier] = list end")
    lines.append("    table.insert(list, pet)")
    lines.append("end")
    lines.append("")

    luck = data["luck"]
    lines.append(f"Economy.LUCK_BASE = {luau_number(float(luck['base']))}")
    lines.append(f"Economy.LUCK_STEP = {luau_number(float(luck['upgrade_step']))}")
    lines.append(f"Economy.LUCK_LEVELS = {luck['upgrade_levels']}")
    lines.append(f"Economy.LUCK_GAMEPASS_BONUS = {luau_number(float(luck['gamepass_bonus']))}")
    lines.append(f"Economy.LUCK_STACK_MAX = {luau_number(float(luck['stack_max']))}")
    lines.append(f"Economy.PITY_THRESHOLD = {data['pity']['threshold']}")
    lines.append(f"Economy.INVENTORY_CAP = {data['roll']['inventory_cap']}")
    lines.append(f"Economy.COOLDOWN_BASE = {luau_number(float(data['roll']['cooldown_seconds']))}")
    lines.append(f"Economy.COOLDOWN_STEP = {luau_number(float(data['roll']['cooldown_step']))}")
    lines.append(f"Economy.COOLDOWN_LEVELS = {data['roll']['cooldown_levels']}")
    lines.append(f"Economy.RATE_LIMIT_PER_MINUTE = {data['roll']['rate_limit_per_minute']}")
    lines.append("")

    lines.append("Economy.UPGRADE_BASE_COST = {")
    for track, cfg in data["upgrades"].items():
        lines.append(f'    ["{track}"] = {cfg["base_cost"]},')
    lines.append("}")
    lines.append("Economy.UPGRADE_GROWTH = {")
    for track, cfg in data["upgrades"].items():
        lines.append(f'    ["{track}"] = {luau_number(float(cfg["growth"]))},')
    lines.append("}")
    lines.append("Economy.UPGRADE_LEVELS = {")
    for track, cfg in data["upgrades"].items():
        lines.append(f'    ["{track}"] = {cfg["levels"]},')
    lines.append("}")
    lines.append("")

    lines.append("""function Economy.weightsWithLuck(luck: number): ({ [string]: number }, number)
    local w: { [string]: number } = {}
    for tier, base in Economy.BASE_WEIGHTS do
        w[tier] = base
    end
    for _, tier in Economy.CHASE_TIERS do
        w[tier] = math.floor(w[tier] * luck + 0.5)
    end
    local total = 0
    for _, tier in Economy.TIER_ORDER do
        total += w[tier]
    end
    return w, total
end

function Economy.probabilities(luck: number): { [string]: number }
    local w, total = Economy.weightsWithLuck(luck)
    local p: { [string]: number } = {}
    for _, tier in Economy.TIER_ORDER do
        p[tier] = w[tier] / total
    end
    return p
end

function Economy.pickTier(roll: number, luck: number): string
    local w, total = Economy.weightsWithLuck(luck)
    assert(roll >= 1 and roll <= total, "roll out of range")
    local acc = 0
    for _, tier in Economy.TIER_ORDER do
        acc += w[tier]
        if roll <= acc then
            return tier
        end
    end
    return Economy.TIER_ORDER[#Economy.TIER_ORDER]
end

function Economy.pickPet(tier: string, rng: Random): any
    local list = Economy.PETS_BY_TIER[tier]
    return list[rng:NextInteger(1, #list)]
end

function Economy.pickVariant(roll: number): string
    local acc = 0
    for _, variant in Economy.VARIANT_ORDER do
        acc += Economy.VARIANTS[variant].chance
        if roll <= acc then
            return variant
        end
    end
    return Economy.VARIANT_ORDER[#Economy.VARIANT_ORDER]
end

function Economy.key(petId: string, variant: string): string
    return petId .. "|" .. variant
end

function Economy.sellValue(petId: string, variant: string): number
    for _, pet in Economy.PETS do
        if pet.id == petId then
            return math.floor(Economy.TIERS[pet.tier].shard * Economy.VARIANTS[variant].shardMult)
        end
    end
    return 0
end

function Economy.upgradeCost(track: string, level: number): number
    local base = Economy.UPGRADE_BASE_COST[track]
    if not base then return math.huge end
    if level >= Economy.UPGRADE_LEVELS[track] then return math.huge end
    return math.floor(base * (Economy.UPGRADE_GROWTH[track] ^ level) + 0.5)
end

function Economy.luckFor(luckLevel: number, hasLuckPass: boolean): number
    local luck = Economy.LUCK_BASE + luckLevel * Economy.LUCK_STEP
    if hasLuckPass then luck += Economy.LUCK_GAMEPASS_BONUS end
    return math.min(luck, Economy.LUCK_STACK_MAX)
end

function Economy.cooldownFor(speedLevel: number, hasFastRoll: boolean): number
    local cd = Economy.COOLDOWN_BASE * (Economy.COOLDOWN_STEP ^ speedLevel)
    if hasFastRoll then cd = cd / 2 end
    return math.max(cd, 0.5)
end

return Economy
""")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(lines)} lines)")
    print(f"tier weights: {int_w} total={sum(int_w.values())}")


if __name__ == "__main__":
    main()