--!strict
-- GENERATED FILE. DO NOT EDIT.
-- Source: design/economy.json
-- Regenerate: python3 tools/gen_economy.py
-- Weights are integers per 10.000 so luck multiplication has no float drift.


local Economy = {}

Economy.TIER_ORDER = { "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Divine" }
Economy.CHASE_TIERS = { "Legendary", "Mythic", "Divine" }

Economy.BASE_WEIGHTS = {
    ["Common"] = 4500,
    ["Uncommon"] = 3000,
    ["Rare"] = 1500,
    ["Epic"] = 750,
    ["Legendary"] = 200,
    ["Mythic"] = 45,
    ["Divine"] = 5,
}

Economy.TIERS = {
    ["Common"] = { weight = 45, shard = 5, color = "#8FA0B8", glow = 0 },
    ["Uncommon"] = { weight = 30, shard = 12, color = "#5FD08A", glow = 0 },
    ["Rare"] = { weight = 15, shard = 30, color = "#4FA8FF", glow = 0 },
    ["Epic"] = { weight = 7.5, shard = 90, color = "#B36BFF", glow = 0.1 },
    ["Legendary"] = { weight = 2, shard = 300, color = "#FFC24A", glow = 0.25 },
    ["Mythic"] = { weight = 0.45, shard = 1200, color = "#FF6B4A", glow = 0.4 },
    ["Divine"] = { weight = 0.05, shard = 6000, color = "#7CF6FF", glow = 0.6 },
}

Economy.VARIANTS = {
    ["Normal"] = { chance = 85, shardMult = 1, material = Enum.Material.SmoothPlastic, tint = "#FFFFFF" },
    ["Golden"] = { chance = 12, shardMult = 1.25, material = Enum.Material.Metal, tint = "#FFE08A" },
    ["Dark"] = { chance = 3, shardMult = 1.6, material = Enum.Material.SmoothPlastic, tint = "#4A3A6B" },
}
Economy.VARIANT_ORDER = { "Normal", "Golden", "Dark" }

Economy.PETS = {
    { id = "Mochi", tier = "Common", ears = "tall", tail = "puff", build = "chibi" },
    { id = "Pip", tier = "Common", ears = "round", tail = "puff", build = "chibi" },
    { id = "Bonbon", tier = "Common", ears = "round", tail = "fan", build = "chibi" },
    { id = "Nori", tier = "Common", ears = "tall", tail = "fan", build = "long" },
    { id = "Kobo", tier = "Uncommon", ears = "round", tail = "puff", build = "chibi" },
    { id = "Fernpup", tier = "Uncommon", ears = "tall", tail = "fan", build = "long" },
    { id = "Marble", tier = "Rare", ears = "tall", tail = "plume", build = "chibi" },
    { id = "Tide", tier = "Rare", ears = "fin", tail = "fan", build = "long" },
    { id = "Zephyr", tier = "Epic", ears = "fin", tail = "plume", build = "chibi" },
    { id = "Vesper", tier = "Epic", ears = "tall", tail = "plume", build = "long" },
    { id = "Aurelia", tier = "Legendary", ears = "tall", tail = "plume", build = "chibi" },
    { id = "Volt", tier = "Legendary", ears = "round", tail = "fan", build = "chibi" },
    { id = "Emberfox", tier = "Mythic", ears = "tall", tail = "plume", build = "chibi" },
    { id = "Astraeon", tier = "Divine", ears = "fin", tail = "plume", build = "long" },
}
Economy.PETS_BY_TIER = {}
for _, pet in Economy.PETS do
    local list = Economy.PETS_BY_TIER[pet.tier]
    if not list then list = {}; Economy.PETS_BY_TIER[pet.tier] = list end
    table.insert(list, pet)
end

Economy.LUCK_BASE = 1
Economy.LUCK_STEP = 0.15
Economy.LUCK_LEVELS = 10
Economy.LUCK_GAMEPASS_BONUS = 0.5
Economy.LUCK_STACK_MAX = 3
Economy.PITY_THRESHOLD = 8000
Economy.INVENTORY_CAP = 500
Economy.COOLDOWN_BASE = 3
Economy.COOLDOWN_STEP = 0.92
Economy.COOLDOWN_LEVELS = 8
Economy.RATE_LIMIT_PER_MINUTE = 45

Economy.UPGRADE_BASE_COST = {
    ["luck"] = 150,
    ["roll_speed"] = 100,
}
Economy.UPGRADE_GROWTH = {
    ["luck"] = 1.6,
    ["roll_speed"] = 1.5,
}
Economy.UPGRADE_LEVELS = {
    ["luck"] = 10,
    ["roll_speed"] = 8,
}

function Economy.weightsWithLuck(luck: number): ({ [string]: number }, number)
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
