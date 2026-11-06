--!strict
-- GENERATED FILE. DO NOT EDIT.
-- Source: design/pet-assets.json + design/economy.json
-- Regenerate: python3 tools/gen_pet_assets.py
--
-- mesh = nil artinya pet ini belum punya aset 3D; loader wajib memakai
-- Pets/Builder (primitif). Kontrak lengkap: docs/09-3D-CONTRACT.md

export type PetAsset = {
	id: string,
	tier: string,
	build: string,
	height: number,
	mesh: string?,
	colormaps: { [string]: string? },
	tris: number,
	status: string,
}

local Pets: { [string]: PetAsset } = {
	Mochi = {
		id = "Mochi",
		tier = "Common",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Pip = {
		id = "Pip",
		tier = "Common",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Bonbon = {
		id = "Bonbon",
		tier = "Common",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Nori = {
		id = "Nori",
		tier = "Common",
		build = "long",
		height = 2.40,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Kobo = {
		id = "Kobo",
		tier = "Uncommon",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Fernpup = {
		id = "Fernpup",
		tier = "Uncommon",
		build = "long",
		height = 2.40,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Marble = {
		id = "Marble",
		tier = "Rare",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Tide = {
		id = "Tide",
		tier = "Rare",
		build = "long",
		height = 2.40,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Zephyr = {
		id = "Zephyr",
		tier = "Epic",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Vesper = {
		id = "Vesper",
		tier = "Epic",
		build = "long",
		height = 2.40,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Aurelia = {
		id = "Aurelia",
		tier = "Legendary",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Volt = {
		id = "Volt",
		tier = "Legendary",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Emberfox = {
		id = "Emberfox",
		tier = "Mythic",
		build = "chibi",
		height = 2.70,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
	Astraeon = {
		id = "Astraeon",
		tier = "Divine",
		build = "long",
		height = 2.40,
		mesh = nil,
		colormaps = { Normal = nil, Golden = nil, Dark = nil },
		tris = 0,
		status = "todo",
	},
}

local Stats = { total = 14, done = 0 }

local PetAssets = {}

PetAssets.Pets = Pets
PetAssets.Stats = Stats

-- Dipakai loader: hanya entri done yang boleh membangun mesh.
function PetAssets.isReady(petId: string): boolean
	local asset: PetAsset? = Pets[petId]
	return asset ~= nil and asset.status == "done" and asset.mesh ~= nil
end

return PetAssets
