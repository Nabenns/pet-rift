#!/usr/bin/env python3
"""Cek dan tampilkan status aset 3D.

Dua mode:
  python3 tools/check_assets.py                  -> tabel status semua pet
  python3 tools/check_assets.py --format markdown --no-fail

Yang diperiksa per folder assets/pets/<petid>/:
  model.glb, colormap-normal/gold/dark.png, render-08/30/88.png, meta.json

Tanpa dependensi. Ukuran PNG dibaca dari header IHDR, bukan PIL.

Exit code 1 kalau ada error keras (status done tapi file kurang, tri > 8000,
tinggi di luar rentang, thumbnail bukan 88x88). --no-fail memaksa exit 0.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PETS_DIR = ROOT / "assets" / "pets"
ASSETS_JSON = ROOT / "design" / "pet-assets.json"

HEIGHT_RANGE = {"chibi": (2.6, 2.9), "long": (2.2, 2.5)}
TRI_TARGET = 5000
TRI_HARD = 8000
REQUIRED_FILES = [
    "model.glb",
    "colormap-normal.png",
    "colormap-gold.png",
    "colormap-dark.png",
    "render-08.png",
    "render-30.png",
    "render-88.png",
    "meta.json",
]
META_KEYS = ["pet", "tier", "build", "tris", "height_studs", "colormaps", "renders", "updated", "status"]
REPO = "Nabenns/pet-rift"


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def load_contract() -> dict[str, dict]:
    if not ASSETS_JSON.exists():
        return {}
    data = json.loads(ASSETS_JSON.read_text())
    return {p["id"].lower(): p for p in data.get("pets", [])}


def check_pet(folder: Path, contract: dict[str, dict]) -> dict:
    petid = folder.name
    entry = contract.get(petid.lower(), {})
    contract_status = entry.get("status", "todo")
    errors: list[str] = []
    warns: list[str] = []

    if not entry:
        errors.append(f"folder '{petid}' tidak ada di design/pet-assets.json")

    files = {f.name: f for f in folder.iterdir() if f.is_file()}
    for name, path in files.items():
        if name != name.lower() or " " in name:
            errors.append(f"nama file tidak sesuai kontrak: {name}")
        if path.suffix.lower() == ".rbxm" or path.suffix.lower() == ".rbxmx":
            errors.append(f"{name}: jangan commit file biner Roblox")

    if petid != petid.lower():
        errors.append(f"nama folder harus huruf kecil: {petid}")

    missing = [name for name in REQUIRED_FILES if name not in files]
    has_any = bool(files)

    meta: dict = {}
    if "meta.json" in files:
        try:
            meta = json.loads(files["meta.json"].read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"meta.json tidak valid: {exc.msg}")
    for key in META_KEYS:
        if "meta.json" in files and key not in meta:
            errors.append(f"meta.json kehilangan field {key}")

    tris = meta.get("tris")
    if isinstance(tris, int):
        if tris > TRI_HARD:
            errors.append(f"tris {tris} > batas keras {TRI_HARD}")
        elif tris > TRI_TARGET:
            warns.append(f"tris {tris} di atas target {TRI_TARGET}")

    build = meta.get("build")
    height = meta.get("height_studs")
    if build in HEIGHT_RANGE and isinstance(height, (int, float)):
        lo, hi = HEIGHT_RANGE[build]
        if not (lo <= height <= hi):
            errors.append(f"tinggi {height} di luar {lo}-{hi} untuk build {build}")

    if "render-88.png" in files:
        size = png_size(files["render-88.png"])
        if size != (88, 88):
            got = f"{size[0]}x{size[1]}" if size else "bukan PNG"
            errors.append(f"render-88.png harus 88x88, dapat {got}")

    colormaps = sum(1 for n in ("colormap-normal.png", "colormap-gold.png", "colormap-dark.png") if n in files)
    renders = sum(1 for n in ("render-08.png", "render-30.png", "render-88.png") if n in files)

    if contract_status == "done":
        if missing:
            errors.append(f"status done di pet-assets.json tapi file kurang: {', '.join(missing)}")
        if not entry.get("mesh"):
            errors.append("status done tapi mesh asset id masih null")

    return {
        "pet": petid,
        "status": contract_status,
        "glb": "model.glb" in files,
        "colormaps": colormaps,
        "renders": renders,
        "meta": "meta.json" in files,
        "tris": tris if isinstance(tris, int) else None,
        "height": height if isinstance(height, (int, float)) else None,
        "errors": errors,
        "warns": warns,
        "missing": missing if has_any else REQUIRED_FILES,
        "has_any": has_any,
    }


def render_table(rows: list[dict], contract: dict[str, dict]) -> str:
    header = f"{'PET':<10} {'STATUS':<8} {'GLB':<4} {'CMAP':<5} {'RENDER':<7} {'META':<5} {'TRIS':>6} {'TINGGI':>7}"
    out = [header, "-" * len(header)]
    for row in rows:
        out.append(
            f"{row['pet']:<10} {row['status']:<8} "
            f"{('ya' if row['glb'] else '-'):<4} "
            f"{str(row['colormaps']) + '/3':<5} "
            f"{str(row['renders']) + '/3':<7} "
            f"{('ya' if row['meta'] else '-'):<5} "
            f"{(row['tris'] if row['tris'] is not None else '-'):>6} "
            f"{(row['height'] if row['height'] is not None else '-'):>7}"
        )
    return "\n".join(out)


def render_markdown(rows: list[dict], sha: str | None) -> str:
    lines = ["## Cek aset 3D", "", "| Pet | Status | GLB | Colormap | Render | Tri | Tinggi |", "|---|---|---|---|---|---|---|"]
    for row in rows:
        if not row["has_any"]:
            continue
        lines.append(
            f"| {row['pet']} | {row['status']} | {'ya' if row['glb'] else '-'} | "
            f"{row['colormaps']}/3 | {row['renders']}/3 | "
            f"{row['tris'] if row['tris'] is not None else '-'} | "
            f"{row['height'] if row['height'] is not None else '-'} |"
        )

    problems = [(row["pet"], kind, msg) for row in rows for kind, msgs in (("ERROR", row["errors"]), ("WARN", row["warns"])) for msg in msgs]
    if problems:
        lines += ["", "### Temuan", ""]
        for pet, kind, msg in problems:
            lines.append(f"- **{kind}** `{pet}`: {msg}")
    else:
        lines += ["", "Tidak ada temuan. Semua file sesuai kontrak."]

    if sha:
        previews = []
        for row in rows:
            for name in ("render-08.png", "render-30.png", "render-88.png"):
                if not (PETS_DIR / row["pet"] / name).exists():
                    continue
                url = f"https://raw.githubusercontent.com/{REPO}/{sha}/assets/pets/{row['pet']}/{name}"
                previews.append(f"**{row['pet']} {name}**\n\n![{row['pet']} {name}]({url})")
        if previews:
            lines += ["", "### Preview", ""] + previews

    lines += ["", f"Diperiksa {len(rows)} folder di `assets/pets/`."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["table", "markdown"], default="table")
    parser.add_argument("--no-fail", action="store_true")
    parser.add_argument("--render-preview", default=None, help="sha commit untuk URL gambar")
    args = parser.parse_args()

    contract = load_contract()
    folders = sorted([p for p in PETS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")]) if PETS_DIR.exists() else []
    rows = [check_pet(folder, contract) for folder in folders]

    if args.format == "markdown":
        print(render_markdown(rows, args.render_preview))
    else:
        print(render_table(rows, contract))
        print()
        for row in rows:
            for msg in row["errors"]:
                print(f"ERROR {row['pet']}: {msg}")
            for msg in row["warns"]:
                print(f"WARN  {row['pet']}: {msg}")
        pending = [c["id"] for c in contract.values() if c.get("status") != "done" and c["id"].lower() not in {r["pet"] for r in rows}]
        if pending:
            print(f"\nbelum ada folder: {', '.join(pending)}")

    errors = sum(len(row["errors"]) for row in rows)
    done = sum(1 for row in rows if row["status"] == "done")
    orphan_done = sorted(c["id"] for c in contract.values() if c.get("status") == "done" and c["id"].lower() not in {r["pet"] for r in rows})
    for pid in orphan_done:
        print(f"ERROR {pid}: status done tapi folder assets/pets/ tidak ada", file=sys.stderr)
        errors += 1
    print(f"\n{len(rows)} folder, {done} selesai, {errors} error", file=sys.stderr if args.format == "table" else sys.stdout)
    if args.no_fail:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())