#!/usr/bin/env python3
"""design/pet-assets.json -> src/shared/PetAssets.luau

Kontrak aset 3D. Tugasnya cuma satu: memastikan tabel aset dan tabel ekonomi
tidak pernah bercabang dua. Kalau roster di economy.json berubah dan file ini
tidak ikut, generator menolak jalan.

Jalankan: python3 tools/gen_pet_assets.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "design" / "pet-assets.json"
ECONOMY = ROOT / "design" / "economy.json"
OUT = ROOT / "src" / "shared" / "PetAssets.luau"

VALID_STATUS = {"todo", "wip", "review", "done"}
VALID_BUILD = {"chibi", "long"}
HEIGHT_RANGE = {"chibi": (2.6, 2.9), "long": (2.2, 2.5)}
TRI_MAX = 8000


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def lua_str(value: str | None) -> str:
    if value is None:
        return "nil"
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def main() -> None:
    data = json.loads(ASSETS.read_text())
    economy = json.loads(ECONOMY.read_text())

    pets = data.get("pets")
    if not isinstance(pets, list) or not pets:
        fail("pet-assets.json: 'pets' harus list tidak kosong")

    econ_ids = [p["id"] for p in economy["pets"]]
    econ_tiers = {p["id"]: p["tier"] for p in economy["pets"]}
    asset_ids = [p["id"] for p in pets]

    if len(set(asset_ids)) != len(asset_ids):
        dupes = sorted({i for i in asset_ids if asset_ids.count(i) > 1})
        fail(f"id duplikat di pet-assets.json: {dupes}")

    missing = sorted(set(econ_ids) - set(asset_ids))
    extra = sorted(set(asset_ids) - set(econ_ids))
    if missing or extra:
        fail(f"roster bercabang. tidak ada di pet-assets: {missing}; tidak ada di economy: {extra}")

    seen_order = [p["id"] for p in economy["pets"]]
    if asset_ids != seen_order:
        fail("urutan id di pet-assets.json harus sama dengan economy.json")

    total = 0
    ready = 0
    lines: list[str] = []
    for pet in pets:
        pid = pet["id"]
        tier = pet.get("tier")
        build = pet.get("build")
        status = pet.get("status")

        if tier != econ_tiers[pid]:
            fail(f"{pid}: tier '{tier}' beda dengan economy.json '{econ_tiers[pid]}'")
        if build not in VALID_BUILD:
            fail(f"{pid}: build '{build}' tidak dikenal")
        if status not in VALID_STATUS:
            fail(f"{pid}: status '{status}' tidak dikenal")

        height = pet.get("height")
        if not isinstance(height, (int, float)):
            fail(f"{pid}: height harus angka")
        lo, hi = HEIGHT_RANGE[build]
        if not (lo <= height <= hi):
            fail(f"{pid}: height {height} di luar {lo}-{hi} untuk build {build}")

        tris = pet.get("tris", 0)
        if not isinstance(tris, int) or tris < 0:
            fail(f"{pid}: tris harus integer >= 0")
        if status == "done" and tris > TRI_MAX:
            fail(f"{pid}: tris {tris} > {TRI_MAX} padahal status done")

        mesh = pet.get("mesh")
        colormaps = pet.get("colormaps") or {}
        for variant in ("Normal", "Golden", "Dark"):
            if variant not in colormaps:
                fail(f"{pid}: colormaps kehilangan varian {variant}")
        if status == "done":
            if not mesh:
                fail(f"{pid}: status done tapi mesh masih null")
            for variant, asset in colormaps.items():
                if not asset:
                    fail(f"{pid}: status done tapi colormap {variant} masih null")

        total += 1
        if status == "done":
            ready += 1

        cm = ", ".join(f'{v} = {lua_str(colormaps[v])}' for v in ("Normal", "Golden", "Dark"))
        lines.append(
            "\t%s = {\n"
            '\t\tid = %s,\n'
            '\t\ttier = %s,\n'
            '\t\tbuild = %s,\n'
            "\t\theight = %.2f,\n"
            "\t\tmesh = %s,\n"
            "\t\tcolormaps = { %s },\n"
            "\t\ttris = %d,\n"
            '\t\tstatus = %s,\n'
            "\t},"
            % (pid, lua_str(pid), lua_str(tier), lua_str(build), float(height),
               lua_str(mesh), cm, tris, lua_str(status))
        )

    out = (
        "--!strict\n"
        "-- GENERATED FILE. DO NOT EDIT.\n"
        "-- Source: design/pet-assets.json + design/economy.json\n"
        "-- Regenerate: python3 tools/gen_pet_assets.py\n"
        "--\n"
        "-- mesh = nil artinya pet ini belum punya aset 3D; loader wajib memakai\n"
        "-- Pets/Builder (primitif). Kontrak lengkap: docs/09-3D-CONTRACT.md\n"
        "\n"
        "export type PetAsset = {\n"
        "\tid: string,\n"
        "\ttier: string,\n"
        "\tbuild: string,\n"
        "\theight: number,\n"
        "\tmesh: string?,\n"
        "\tcolormaps: { [string]: string? },\n"
        "\ttris: number,\n"
        "\tstatus: string,\n"
        "}\n"
        "\n"
        "local Pets: { [string]: PetAsset } = {\n"
        + "\n".join(lines) + "\n"
        "}\n"
        "\n"
        f"local Stats = {{ total = {total}, done = {ready} }}\n"
        "\n"
        "local PetAssets = {}\n"
        "\n"
        "PetAssets.Pets = Pets\n"
        "PetAssets.Stats = Stats\n"
        "\n"
        "-- Dipakai loader: hanya entri done yang boleh membangun mesh.\n"
        "function PetAssets.isReady(petId: string): boolean\n"
        "\tlocal asset: PetAsset? = Pets[petId]\n"
        "\treturn asset ~= nil and asset.status == \"done\" and asset.mesh ~= nil\n"
        "end\n"
        "\n"
        "return PetAssets\n"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out)
    print(f"ok: {OUT.relative_to(ROOT)} | {total} pet, {ready} siap mesh, {total - ready} pakai primitif")


if __name__ == "__main__":
    main()