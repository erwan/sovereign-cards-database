#!/usr/bin/env python3
"""
OCR card headers under public/cards and update ``deck.yaml``.

Strips:
- Name: top 60px (Title Case per word)
- Type: 40px band starting at y=270 from the top. If OCR yields ``unknown`` but
  the card already has a non-empty, non-unknown ``type``, the existing value is kept.

By default, OCR updates **both** ``name`` and ``type``. Pass ``--name`` and/or
``--type`` to update only those fields; other keys on each card (including any
the script does not know about) are left unchanged. Top-level ``description``
is preserved when the file is rewritten.

Requires Tesseract on PATH (e.g. ``brew install tesseract``).

Examples:

  # All decks: refresh name and type (default)
  python scripts/ocr_card_headers.py

  # Only set type from OCR; leave name and other keys untouched
  python scripts/ocr_card_headers.py --type

  # Only set name
  python scripts/ocr_card_headers.py --name

  # One deck, dry-run, type only
  python scripts/ocr_card_headers.py --deck cult_of_apsynthos --dry-run --type

  # Explicitly both fields (same as default)
  python scripts/ocr_card_headers.py --name --type
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps
import pytesseract

CARDS_ROOT = Path(__file__).resolve().parent.parent / "public" / "cards"
TOP_PX = 60
TYPE_STRIP_Y = 270
TYPE_STRIP_H = 40
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

VALID_TYPES = frozenset({"unknown", "unit", "reflex", "augment", "colony"})
TYPE_PATTERN = re.compile(
    r"\b(unit|reflex|augment|colony)\b",
    re.IGNORECASE,
)
MULTI_CAPS = re.compile(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b")
SINGLE_CAPS = re.compile(r"\b[A-Z]{4,}\b")


def is_cover_filename(name: str) -> bool:
    return name.lower() == "cover.png"


def _prepare_strip_for_ocr(strip: Image.Image) -> Image.Image:
    gray = strip.convert("L")
    gray = ImageOps.autocontrast(gray)
    w2, h2 = gray.size
    scale = max(1, int(300 / max(h2, 1)))
    if scale > 1:
        gray = gray.resize((w2 * scale, h2 * scale), Image.Resampling.LANCZOS)
    return gray


def crop_horizontal_strip(path: Path, y0: int, height: int) -> Image.Image | None:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if y0 >= h:
        return None
    y1 = min(y0 + height, h)
    region = im.crop((0, y0, w, y1))
    return _prepare_strip_for_ocr(region)


def ocr_strip(image: Image.Image) -> str:
    config = "--psm 6"
    text = pytesseract.image_to_string(image, config=config)
    return text or ""


def trim_short_caps_edges(name: str) -> str:
    parts = name.split()
    while len(parts) > 1 and len(parts[0]) <= 2 and parts[0].isalpha():
        parts.pop(0)
    while len(parts) > 1 and len(parts[-1]) <= 2 and parts[-1].isalpha():
        parts.pop()
    return " ".join(parts) if parts else name


def title_from_ocr(raw: str) -> str:
    joined = re.sub(r"\s+", " ", raw).strip()
    phrases = MULTI_CAPS.findall(joined)
    singles = SINGLE_CAPS.findall(joined)
    candidates = phrases + singles
    if candidates:

        def rank(p: str) -> tuple[int, int]:
            return (len(p), p.count(" "))

        best = max(candidates, key=rank)
        return trim_short_caps_edges(best)
    cleaned = re.sub(r"[^A-Za-z0-9\s\-'.]", " ", joined)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) >= 2 else "?"


def capitalize_each_word(s: str) -> str:
    if s == "?":
        return s
    return " ".join(w.capitalize() for w in s.split())


def parse_name(raw_top: str) -> str:
    name = title_from_ocr(raw_top)
    if not name or name == "?":
        name = re.sub(r"\s+", " ", raw_top).strip() or "?"
    return capitalize_each_word(name)


def parse_type(raw_type_strip: str) -> str:
    joined = re.sub(r"\s+", " ", raw_type_strip).strip()
    m = TYPE_PATTERN.search(joined)
    if m:
        t = m.group(1).lower()
        if t in VALID_TYPES and t != "unknown":
            return t
    return "unknown"


def write_deck_yaml(deck_dir: Path, cards: list[dict], description: str = "") -> None:
    out = deck_dir / "deck.yaml"
    if description.strip():
        data: dict = {"description": description, "cards": cards}
    else:
        data = {"cards": cards}
    out.write_text(
        yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=10_000,
        ),
        encoding="utf-8",
    )


def load_deck(deck_dir: Path) -> tuple[list[dict], str] | None:
    p = deck_dir / "deck.yaml"
    if not p.is_file():
        return None
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        return None
    cards = data["cards"]
    desc_raw = data.get("description")
    description = desc_raw if isinstance(desc_raw, str) else ""
    return (cards, description)


def process_deck(
    deck_dir: Path,
    *,
    dry_run: bool,
    verbose: bool,
    want_name: bool,
    want_type: bool,
) -> int:
    loaded = load_deck(deck_dir)
    if loaded is None:
        print(f"skip (no deck.yaml): {deck_dir.name}", file=sys.stderr)
        return 0
    cards, description = loaded
    if not cards:
        print(f"skip (empty cards): {deck_dir.name}", file=sys.stderr)
        return 0

    updated = 0
    for i, entry in enumerate(cards):
        if not isinstance(entry, dict):
            continue
        img_name = entry.get("image")
        if not isinstance(img_name, str) or not img_name:
            continue
        if is_cover_filename(Path(img_name).name):
            continue

        suffix = Path(img_name).suffix.lower()
        if suffix not in IMAGE_SUFFIXES:
            continue

        img_path = deck_dir / img_name
        if not img_path.is_file():
            print(f"warn: missing file {img_path}", file=sys.stderr)
            continue

        raw_top = ""
        raw_type = ""
        name = entry.get("name")
        typ = entry.get("type")

        if want_name:
            top = crop_horizontal_strip(img_path, 0, TOP_PX)
            if top is None:
                print(f"warn: empty top strip {img_path}", file=sys.stderr)
                continue
            raw_top = ocr_strip(top)
            name = parse_name(raw_top)

        if want_type:
            type_img = crop_horizontal_strip(img_path, TYPE_STRIP_Y, TYPE_STRIP_H)
            raw_type = ocr_strip(type_img) if type_img is not None else ""
            typ = parse_type(raw_type)
            prev_type = entry.get("type")
            if typ == "unknown" and isinstance(prev_type, str) and prev_type.strip() and prev_type != "unknown":
                typ = prev_type

        old_name = entry.get("name")
        old_type = entry.get("type")
        changed = (want_name and old_name != name) or (want_type and old_type != typ)
        if changed:
            updated += 1
            if verbose:
                print(
                    f"{deck_dir.name}/{img_name}: top={raw_top!r} type_strip={raw_type!r} "
                    f"-> name={name!r} type={typ}"
                )

        if want_name:
            entry["name"] = name
        if want_type:
            entry["type"] = typ

    if not dry_run and updated:
        write_deck_yaml(deck_dir, cards, description)
    elif dry_run and updated:
        print(f"[dry-run] would update {updated} card(s) in {deck_dir.name}", file=sys.stderr)

    return updated


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--deck",
        metavar="SLUG",
        help="Only process public/cards/<SLUG>",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="OCR and report but do not write deck.yaml",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print OCR text per card")
    parser.add_argument(
        "--name",
        action="store_true",
        dest="set_name",
        help="OCR title strip and set only the name field",
    )
    parser.add_argument(
        "--type",
        action="store_true",
        dest="set_type",
        help="OCR type strip and set only the type field",
    )
    args = parser.parse_args()

    explicit_fields = args.set_name or args.set_type
    want_name = args.set_name if explicit_fields else True
    want_type = args.set_type if explicit_fields else True

    if not CARDS_ROOT.is_dir():
        print(f"Missing {CARDS_ROOT}", file=sys.stderr)
        return 1

    if args.deck:
        dirs = [CARDS_ROOT / args.deck]
        if not dirs[0].is_dir():
            print(f"No such deck: {args.deck}", file=sys.stderr)
            return 1
    else:
        dirs = sorted(p for p in CARDS_ROOT.iterdir() if p.is_dir())

    total = 0
    for d in dirs:
        total += process_deck(
            d,
            dry_run=args.dry_run,
            verbose=args.verbose,
            want_name=want_name,
            want_type=want_type,
        )

    if args.dry_run:
        print(f"Total cards with changes: {total} (files not written)")
    else:
        print(f"Updated entries across deck.yaml files: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
