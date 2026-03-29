#!/usr/bin/env python3
"""
OCR card headers under public/cards and update ``deck.toml``.

Strips:
- Name: top 60px (Title Case per word)
- Cost: 40×40 square over the bottom-left cost gem, ``COST_INSET_X`` px from the image left
  edge and ``COST_INSET_BOTTOM`` px up from the bottom (OCR: digit 0–9 or ``X``; Tesseract
  with invert fallback).
- Type: 40px band starting at y=270 from the top. Primary keyword (``unit``, etc.) is
  parsed from the segment before an em/en dash or ``--`` / `` - `` (same as before).
  For secondaries, the whole type line is tokenized into alphanumeric words; the first
  word (the primary type) is skipped, then each remaining word that appears in
  ``VALID_SECONDARY_BY_PRIMARY[primary]`` for the resolved primary type is collected in
  order (primary comes from OCR or, when OCR is ``unknown``, from existing TOML).
  Reflex cards have no secondary line: none is parsed, ``unknown`` is not stored, and any
  existing ``type_secondary`` in TOML is removed. If there is nothing after the first
  word, the secondary field is left empty (preserve existing). If there are words but
  none match a known secondary, ``[unknown]`` is used. Secondaries are stored as a TOML
  array (e.g. ``["human", "xeno"]``). If OCR
  yields ``unknown`` for the primary but the card already has a non-unknown ``type``,
  that value is kept. If secondary OCR is empty but ``type_secondary`` is already set,
  it is kept; otherwise the key is omitted.

By default, OCR updates ``name``, ``type``, and ``cost``. Pass ``--name``,
``--type``, and/or ``--cost`` to update only those fields; other keys on each card
(including any the script does not know about) are left unchanged. Top-level ``description``
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

  # Cost only (bottom-left 40×40 region; digit or X)
  python scripts/ocr_card_headers.py --cost

  # Re-coerce existing type_secondary strings/lists to canonical arrays (no image OCR)
  python scripts/ocr_card_headers.py --normalize-secondary
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import tomli
import tomli_w
from PIL import Image, ImageOps
import pytesseract

CARDS_ROOT = Path(__file__).resolve().parent.parent / "public" / "cards"
TOP_PX = 60
TYPE_STRIP_Y = 270
TYPE_STRIP_H = 40
COST_SQUARE = 40
COST_INSET_X = 20
COST_INSET_BOTTOM = 12
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

VALID_TYPES = frozenset({"unknown", "unit", "reflex", "augment", "colony"})
TYPE_PATTERN = re.compile(
    r"\b(unit|reflex|augment|colony)\b",
    re.IGNORECASE,
)
MULTI_CAPS = re.compile(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b")
SINGLE_CAPS = re.compile(r"\b[A-Z]{4,}\b")

# Per-primary allowed secondary tags (duplicated literals so each list can diverge).
VALID_SECONDARY_BY_PRIMARY: dict[str, frozenset[str]] = {
    "unknown": frozenset(
        {
            "antigrav",
            "unit",
            "facility",
            "human",
            "xeno",
            "chimera",
            "aciereys",
            "mech",
            "reflex",
            "synth",
        }
    ),
    "unit": frozenset(
        {
            "antigrav",
            "human",
            "xeno",
            "chimera",
            "aciereys",
            "mech",
            "synth",
        }
    ),
    "augment": frozenset(
        {
            "unit",
            "facility",
        }
    ),
    "colony": frozenset(
        {
            "facility",
        }
    ),
}

VALID_SECONDARY_TYPES: frozenset[str] = frozenset({"unknown"}).union(
    *VALID_SECONDARY_BY_PRIMARY.values()
)
_PRIMARY_KEYWORDS: frozenset[str] = frozenset({"unit", "reflex", "augment", "colony"})


def is_reflex_primary(primary: object) -> bool:
    return isinstance(primary, str) and primary.strip().lower() == "reflex"


def known_secondaries_for_primary(primary: object) -> frozenset[str]:
    if is_reflex_primary(primary):
        return frozenset()
    if isinstance(primary, str):
        p = primary.strip().lower()
        if p in VALID_SECONDARY_BY_PRIMARY:
            return VALID_SECONDARY_BY_PRIMARY[p]
    return VALID_SECONDARY_BY_PRIMARY["unknown"]


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


def crop_cost_square(path: Path) -> Image.Image | None:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    left = COST_INSET_X
    right = COST_INSET_X + COST_SQUARE
    upper = h - COST_INSET_BOTTOM - COST_SQUARE
    lower = h - COST_INSET_BOTTOM
    if left < 0 or upper < 0 or right > w or lower > h or right <= left or lower <= upper:
        return None
    region = im.crop((left, upper, right, lower))
    return _prepare_strip_for_ocr(region)


def ocr_strip(image: Image.Image) -> str:
    config = "--psm 6"
    text = pytesseract.image_to_string(image, config=config)
    return text or ""


_COST_OCR_WHITELIST = "0123456789Xx"


def ocr_cost_digit(image: Image.Image) -> str:
    cfg10 = f"--psm 10 -c tessedit_char_whitelist={_COST_OCR_WHITELIST}"
    cfg8 = f"--psm 8 -c tessedit_char_whitelist={_COST_OCR_WHITELIST}"

    def run(img: Image.Image) -> str:
        for cfg in (cfg10, cfg8):
            t = pytesseract.image_to_string(img, config=cfg) or ""
            if parse_cost_from_ocr(t) is not None:
                return t
        return ""

    t = run(image)
    if t:
        return t
    if image.mode == "L":
        t = run(ImageOps.invert(image))
        if t:
            return t
    return ""


def parse_cost_from_ocr(raw: str) -> int | str | None:
    m = re.search(r"[0-9]", raw)
    if m:
        return int(m.group(0))
    if re.search(r"[Xx]", raw):
        return "X"
    return None


def coerce_cost_value(raw: object) -> int | str | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int) and 0 <= raw <= 9:
        return raw
    if isinstance(raw, float) and raw == int(raw):
        return coerce_cost_value(int(raw))
    if isinstance(raw, str):
        s = raw.strip()
        if len(s) != 1:
            return None
        if s.isdigit():
            d = int(s)
            return d if 0 <= d <= 9 else None
        return s
    return None


def normalize_cost_compare(v: int | str | None) -> str | None:
    if v is None:
        return None
    if isinstance(v, int):
        return str(v)
    return v


def costs_represent_same(a: int | str | None, b: int | str | None) -> bool:
    return normalize_cost_compare(a) == normalize_cost_compare(b)


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


def primary_segment_before_dash(type_line: str) -> str:
    for sep in ("\u2014", "\u2013", "--", " - "):
        if sep in type_line:
            return type_line.split(sep, 1)[0].strip()
    return type_line.strip()


def parse_type(primary_segment: str) -> str:
    joined = re.sub(r"\s+", " ", primary_segment).strip()
    m = TYPE_PATTERN.search(joined)
    if m:
        t = m.group(1).lower()
        if t in VALID_TYPES and t != "unknown":
            return t
    return "unknown"


def _secondaries_from_phrase(phrase: str, known: frozenset[str]) -> list[str]:
    text = re.sub(r"\s+", " ", phrase).strip()
    if not text:
        return []
    whole = text.lower()
    if whole in known:
        return [whole]
    out: list[str] = []
    for w in text.split():
        t = w.strip().lower()
        if t in known:
            out.append(t)
        else:
            out.append("unknown")
    return out


def parse_type_secondary_list_from_type_line(type_line: str, primary: object) -> list[str]:
    if is_reflex_primary(primary):
        return []
    known = known_secondaries_for_primary(primary)
    line = re.sub(r"\s+", " ", type_line).strip()
    if not line:
        return []
    tokens = re.findall(r"[a-z0-9]+", line.lower())
    if not tokens:
        return []
    if tokens[0] in _PRIMARY_KEYWORDS:
        if len(tokens) <= 1:
            return []
        rest = tokens[1:]
    else:
        rest = list(tokens)
    seen: set[str] = set()
    out: list[str] = []
    for tok in rest:
        if tok in known and tok not in seen:
            seen.add(tok)
            out.append(tok)
    if not out:
        return ["unknown"]
    return out


def coerce_type_secondary(raw: object, primary: object) -> list[str]:
    if is_reflex_primary(primary):
        return []
    known = known_secondaries_for_primary(primary)
    if raw is None:
        return []
    if isinstance(raw, str):
        return parse_type_secondary_list_from_type_line(raw, primary)
    if isinstance(raw, list):
        out: list[str] = []
        for el in raw:
            if not isinstance(el, str):
                continue
            s = el.strip()
            if not s:
                continue
            low = s.lower()
            if low == "unknown":
                out.append("unknown")
                continue
            if low in known:
                out.append(low)
                continue
            out.extend(_secondaries_from_phrase(s, known))
        return list(dict.fromkeys(out))
    return []


def _ordered_card_for_toml(entry: dict) -> dict:
    priority = ("image", "name", "type", "type_secondary", "cost")
    out: dict = {}
    for k in priority:
        if k in entry:
            out[k] = entry[k]
    for k in sorted(entry.keys()):
        if k not in out:
            out[k] = entry[k]
    return out


def write_deck_toml(deck_dir: Path, cards: list[dict], description: str = "") -> None:
    ordered = [_ordered_card_for_toml(c) for c in cards]
    if description.strip():
        data: dict = {"description": description, "cards": ordered}
    else:
        data = {"cards": ordered}
    out = deck_dir / "deck.toml"
    out.write_text(tomli_w.dumps(data), encoding="utf-8")


def load_deck(deck_dir: Path) -> tuple[list[dict], str] | None:
    p = deck_dir / "deck.toml"
    if not p.is_file():
        return None
    with p.open("rb") as f:
        data = tomli.load(f)
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
    want_cost: bool,
) -> int:
    loaded = load_deck(deck_dir)
    if loaded is None:
        print(f"skip (no deck.toml): {deck_dir.name}", file=sys.stderr)
        return 0
    cards, description = loaded
    if not cards:
        print(f"skip (empty cards): {deck_dir.name}", file=sys.stderr)
        return 0

    updated = 0
    for entry in cards:
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
        raw_cost = ""
        name = entry.get("name")
        typ = entry.get("type")
        cost = coerce_cost_value(entry.get("cost"))
        old_list = coerce_type_secondary(entry.get("type_secondary"), entry.get("type"))
        type_sec_list = list(old_list)

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
            joined = re.sub(r"\s+", " ", raw_type).strip()
            typ = parse_type(primary_segment_before_dash(joined))
            prev_type = entry.get("type")
            if typ == "unknown" and isinstance(prev_type, str) and prev_type.strip() and prev_type != "unknown":
                typ = prev_type
            if is_reflex_primary(typ):
                type_sec_list = []
            else:
                parsed = parse_type_secondary_list_from_type_line(joined, typ)
                if not parsed:
                    type_sec_list = list(old_list)
                else:
                    type_sec_list = parsed

        if want_cost:
            cost_img = crop_cost_square(img_path)
            if cost_img is None:
                print(f"warn: empty cost crop {img_path}", file=sys.stderr)
                if cost is None:
                    cost = 0
            else:
                raw_cost = ocr_cost_digit(cost_img)
                parsed_cost = parse_cost_from_ocr(raw_cost)
                if parsed_cost is not None:
                    cost = parsed_cost
                elif cost is None:
                    cost = 0
                    print(f"warn: no cost OCR {img_path} raw={raw_cost!r}", file=sys.stderr)

        final_type = typ if want_type else entry.get("type")
        if is_reflex_primary(final_type):
            type_sec_list = []

        old_name = entry.get("name")
        old_type = entry.get("type")
        old_cost = coerce_cost_value(entry.get("cost"))
        new_sec_list = type_sec_list
        new_cost = cost if want_cost else old_cost
        changed = (want_name and old_name != name) or (
            want_type and (old_type != typ or old_list != new_sec_list)
        ) or (want_cost and not costs_represent_same(old_cost, new_cost)) or (
            is_reflex_primary(final_type) and "type_secondary" in entry
        )
        if changed:
            updated += 1
            if verbose:
                print(
                    f"{deck_dir.name}/{img_name}: top={raw_top!r} type_strip={raw_type!r} "
                    f"cost_ocr={raw_cost!r} -> name={name!r} type={typ} type_secondary={new_sec_list!r} cost={new_cost!r}"
                )

        if want_name:
            entry["name"] = name
        if want_type:
            entry["type"] = typ
        if want_cost and new_cost is not None:
            entry["cost"] = new_cost

        resolved_type = typ if want_type else entry.get("type")
        if is_reflex_primary(resolved_type):
            entry.pop("type_secondary", None)
        elif want_type:
            if type_sec_list:
                entry["type_secondary"] = type_sec_list
            else:
                entry.pop("type_secondary", None)

    if not dry_run and updated:
        write_deck_toml(deck_dir, cards, description)
    elif dry_run and updated:
        print(f"[dry-run] would update {updated} card(s) in {deck_dir.name}", file=sys.stderr)

    return updated


def normalize_secondary_in_deck(deck_dir: Path, *, dry_run: bool) -> int:
    loaded = load_deck(deck_dir)
    if loaded is None:
        print(f"skip (no deck.toml): {deck_dir.name}", file=sys.stderr)
        return 0
    cards, description = loaded
    updated = 0
    for entry in cards:
        if not isinstance(entry, dict):
            continue
        if "type_secondary" not in entry:
            continue
        raw = entry.get("type_secondary")
        desired = coerce_type_secondary(raw, entry.get("type"))
        if desired:
            if entry.get("type_secondary") != desired:
                updated += 1
                if not dry_run:
                    entry["type_secondary"] = desired
        else:
            updated += 1
            if not dry_run:
                entry.pop("type_secondary", None)

    if not dry_run and updated:
        write_deck_toml(deck_dir, cards, description)
    elif dry_run and updated:
        print(f"[dry-run] would normalize type_secondary on {updated} card(s) in {deck_dir.name}", file=sys.stderr)
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
        help="OCR and report but do not write deck.toml",
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
    parser.add_argument(
        "--cost",
        action="store_true",
        dest="set_cost",
        help="OCR cost (40×40 over bottom-left cost gem; digit or X) and set only the cost field",
    )
    parser.add_argument(
        "--normalize-secondary",
        action="store_true",
        help="Coerce type_secondary strings/lists to canonical lists (no OCR)",
    )
    args = parser.parse_args()

    if args.normalize_secondary and (args.set_name or args.set_type or args.set_cost):
        print("Cannot combine --normalize-secondary with --name/--type/--cost", file=sys.stderr)
        return 2

    explicit_fields = args.set_name or args.set_type or args.set_cost
    want_name = args.set_name if explicit_fields else True
    want_type = args.set_type if explicit_fields else True
    want_cost = args.set_cost if explicit_fields else True

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

    if args.normalize_secondary:
        total = 0
        for d in dirs:
            total += normalize_secondary_in_deck(d, dry_run=args.dry_run)
        if args.dry_run:
            print(f"Total type_secondary normalizations: {total} (files not written)")
        else:
            print(f"Normalized type_secondary across deck.toml files: {total} card row(s)")
        return 0

    total = 0
    for d in dirs:
        total += process_deck(
            d,
            dry_run=args.dry_run,
            verbose=args.verbose,
            want_name=want_name,
            want_type=want_type,
            want_cost=want_cost,
        )

    if args.dry_run:
        print(f"Total cards with changes: {total} (files not written)")
    else:
        print(f"Updated entries across deck.toml files: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
