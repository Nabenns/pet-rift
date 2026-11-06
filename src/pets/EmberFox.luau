--[[
	EmberFox — pet blocky tier Mythic, dibangun 100% dari primitif.
	Sumber kebenaran: repo (file ini), bukan instance di Studio.
	Struktur: ReplicatedStorage.Pets.EmberFox (Model, PrimaryPart = Body)
	Atribut: Tier, DisplayName, Weight, OddsLabel

	Proporsi (total ~3.9 stud, ala pet Roblox):
	  0.00–1.00  kaki (kelihatan penuh)
	  1.00–2.05  badan (lebih lebar dari kepala, biar siluet kebaca)
	  2.05–3.15  kepala (nempel di badan, tanpa tumpang tindih)
	  3.15–3.95  telinga
]]

local Pets = game:GetService("ReplicatedStorage"):FindFirstChild("Pets")
if not Pets then
	Pets = Instance.new("Folder")
	Pets.Name = "Pets"
	Pets.Parent = game:GetService("ReplicatedStorage")
end

local C = {
	body   = Color3.fromHex("#E86F2B"),
	bodyHi = Color3.fromHex("#FF9550"),
	bodyLo = Color3.fromHex("#B85416"),
	belly  = Color3.fromHex("#FFD9AE"),
	inner  = Color3.fromHex("#C25E30"),
	dark   = Color3.fromHex("#2D2852"),
	eye    = Color3.fromHex("#1A1030"),
	white  = Color3.fromHex("#FFFFFF"),
	blush  = Color3.fromHex("#FF8E7A"),
	gold   = Color3.fromHex("#FFD24A"),
}

local V3, R = Vector3.new, math.rad

local function build()
	local model = Instance.new("Model")
	model.Name = "EmberFox"

	local function part(name, size, cf, color, shape, material)
		local p = Instance.new("Part")
		p.Name = name
		p.Shape = shape or Enum.PartType.Block
		p.Size = size
		p.CFrame = cf
		p.Color = color
		p.Material = material or Enum.Material.SmoothPlastic
		p.Anchored = true
		p.CanCollide = false
		p.CastShadow = true
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		p.Parent = model
		return p
	end

	-- ── kaki: 1 stud penuh, di luar siluet badan ─────────────────────
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			part("Leg", V3(1.0, 0.46, 0.46),
				CFrame.new(sx * 0.68, 0.5, sz * 0.6) * CFrame.Angles(0, 0, R(90)), C.bodyLo)
			part("Paw", V3(0.56, 0.22, 0.62), CFrame.new(sx * 0.68, 0.11, sz * 0.6), C.dark)
		end
	end

	-- ── badan: 1.5 lebar (lebih lebar dari kepala 1.4) ───────────────
	local body = part("Body", V3(1.5, 1.05, 1.7), CFrame.new(0, 1.52, -0.05), C.body)
	part("BodyTop", V3(1.44, 0.26, 1.64), CFrame.new(0, 1.95, -0.05), C.bodyHi)
	part("Belly", V3(1.3, 0.5, 1.5), CFrame.new(0, 1.3, 0.12), C.belly)
	model.PrimaryPart = body

	-- ── leher: bilah emas + celah gelap, penanda batas badan/kepala ──
	part("Neck", V3(1.16, 0.3, 1.16), CFrame.new(0, 2.1, 0.02), C.bodyLo)
	-- badan: 1.5 x 1.7, permukaan depan z = 0.8, samping x = 0.75
	part("CollarF", V3(1.68, 0.18, 0.18), CFrame.new(0, 2.0, 0.89), C.gold)
	part("CollarB", V3(1.68, 0.18, 0.18), CFrame.new(0, 2.0, -0.99), C.gold)
	part("CollarL", V3(0.18, 0.18, 1.88), CFrame.new(-0.84, 2.0, -0.05), C.gold)
	part("CollarR", V3(0.18, 0.18, 1.88), CFrame.new(0.84, 2.0, -0.05), C.gold)
	part("Tag", V3(0.26, 0.26, 0.1), CFrame.new(0, 1.86, 0.84), C.gold, Enum.PartType.Ball, Enum.Material.Neon)

	-- ── kepala: 1.4 lebar, duduk tepat di atas leher ─────────────────
	part("Head", V3(1.4, 1.1, 1.28), CFrame.new(0, 2.63, 0.08), C.body)
	part("HeadTop", V3(1.34, 0.24, 1.22), CFrame.new(0, 3.14, 0.08), C.bodyHi)
	part("Muzzle", V3(0.74, 0.44, 0.4), CFrame.new(0, 2.46, 0.82), C.belly)
	part("Nose", V3(0.24, 0.2, 0.2), CFrame.new(0, 2.52, 1.0), C.dark, Enum.PartType.Ball)

	-- muka kepala di z = 0.72
	for _, sx in ipairs({ -1, 1 }) do
		part("Eye", V3(0.34, 0.32, 0.2), CFrame.new(sx * 0.36, 2.76, 0.64), C.eye, Enum.PartType.Ball)
		part("Glint", V3(0.12, 0.12, 0.08), CFrame.new(sx * 0.43, 2.82, 0.72), C.white, Enum.PartType.Ball)
		part("Blush", V3(0.3, 0.16, 0.06), CFrame.new(sx * 0.56, 2.56, 0.72), C.blush)
		part("Brow", V3(0.28, 0.07, 0.06),
			CFrame.new(sx * 0.36, 2.94, 0.72) * CFrame.Angles(0, 0, R(sx * 6)), C.inner)
	end

	-- ── permata dahi ─────────────────────────────────────────────────
	part("Gem", V3(0.2, 0.2, 0.16), CFrame.new(0, 3.0, 0.68), C.gold, Enum.PartType.Ball, Enum.Material.Neon)

	-- ── telinga ──────────────────────────────────────────────────────
	for _, sx in ipairs({ -1, 1 }) do
		part("Ear", V3(0.34, 0.8, 0.38),
			CFrame.new(sx * 0.45, 3.5, 0.0) * CFrame.Angles(0, 0, R(sx * -9)), C.body)
		part("EarInner", V3(0.18, 0.46, 0.06),
			CFrame.new(sx * 0.45, 3.48, 0.2) * CFrame.Angles(0, 0, R(sx * -9)), C.inner)
	end

	-- ── ekor 3 segmen ────────────────────────────────────────────────
	part("Tail1", V3(0.34, 0.34, 0.58), CFrame.new(0, 1.6, -1.0) * CFrame.Angles(R(-28), 0, 0), C.bodyLo)
	part("Tail2", V3(0.28, 0.28, 0.5), CFrame.new(0, 2.0, -1.2) * CFrame.Angles(R(-50), 0, 0), C.body)
	part("TailTip", V3(0.24, 0.24, 0.4), CFrame.new(0, 2.3, -1.3) * CFrame.Angles(R(-60), 0, 0), C.belly)

	-- ── mahkota (aksen tier Mythic) ──────────────────────────────────
	part("CrownBand", V3(0.74, 0.14, 0.74), CFrame.new(0, 3.26, 0.05), C.gold)
	for _, sx in ipairs({ -1, 0, 1 }) do
		part("CrownSpike", V3(0.13, 0.28, 0.13),
			CFrame.new(sx * 0.26, 3.46, 0.05), C.gold, Enum.PartType.Block, Enum.Material.Neon)
	end

	-- ── jambul pipi: bikin siluet nggak kotak polos ──────────────────
	for _, sx in ipairs({ -1, 1 }) do
		part("Cheek", V3(0.2, 0.34, 0.44),
			CFrame.new(sx * 0.72, 2.52, 0.1) * CFrame.Angles(0, 0, R(sx * -12)), C.bodyLo)
	end

	-- ── tanda dada: belah ketupat krem ───────────────────────────────
	part("ChestMark", V3(0.34, 0.34, 0.06),
		CFrame.new(0, 1.72, 0.83) * CFrame.Angles(0, 0, R(45)), C.belly)

	model:SetAttribute("Tier", "Mythic")
	model:SetAttribute("DisplayName", "Emberfox")
	model:SetAttribute("Weight", 0.45)
	model:SetAttribute("OddsLabel", "1 in 222")

	return model
end

-- pasang ke ReplicatedStorage
local old = Pets:FindFirstChild("EmberFox")
if old then old:Destroy() end
local pet = build()
pet.Parent = Pets

-- salinan display untuk screenshot
local WS = game:GetService("Workspace")
for _, n in ipairs({ "PetDisplay", "PetPreview" }) do
	local o = WS:FindFirstChild(n)
	if o then o:Destroy() end
end
local disp = pet:Clone()
disp.Name = "PetDisplay"
disp.Parent = WS

-- PivotTo pakai PrimaryPart (Body), jadi jangan diberi CFrame absolut:
-- hitung bounding box dulu, tempelkan dasar pet tepat di atas panggung (y = 0.1).
local bbCF, bbSize = disp:GetBoundingBox()
local bottom = bbCF.Position.Y - bbSize.Y / 2
disp:PivotTo(disp:GetPivot() + Vector3.new(0, 0.1 - bottom, 22))

local ext = pet:GetExtentsSize()
return string.format("OK %s parts=%d bounds=%.2f x %.2f x %.2f odds=%s",
	pet:GetAttribute("DisplayName"), #pet:GetDescendants(), ext.X, ext.Y, ext.Z, pet:GetAttribute("OddsLabel"))