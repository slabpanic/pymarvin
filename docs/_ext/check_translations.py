"""Validate Chinese catalogs against a fresh Sphinx gettext extraction."""

import argparse
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

DOCS = Path(__file__).resolve().parents[1]
LOCALE = DOCS / "locale/zh_CN/LC_MESSAGES"


def check_translations(templates: Path, update: bool = False):
    """Require complete, current, non-fuzzy and syntactically valid translations."""
    pots = sorted(templates.glob("*.pot"))
    if not pots:
        raise ValueError(f"No gettext templates in {templates}")
    errors = []
    for pot in pots:
        with pot.open("rb") as stream:
            template = read_po(stream)
        path = LOCALE / pot.with_suffix(".po").name
        if path.exists():
            with path.open("rb") as stream:
                catalog = read_po(stream, locale="zh_CN")
        elif update:
            catalog = Catalog(locale="zh_CN", project="pymarvin")
            catalog.fuzzy = False
        else:
            errors.append(f"Missing catalog: {path}")
            continue
        if update:
            catalog.update(template, no_fuzzy_matching=True)
            catalog.obsolete.clear()
            for message in catalog:
                message.locations = [
                    (name.replace(str(DOCS.parent) + "/", ""), line)
                    for name, line in message.locations
                    if name != "of"
                ]
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as stream:
                write_po(stream, catalog, width=88, include_previous=False)
            continue
        expected = {m.id for m in template if m.id}
        actual = {m.id for m in catalog if m.id}
        if catalog.fuzzy or catalog.obsolete:
            errors.append(f"{path.name}: fuzzy header or obsolete entries")
        for msgid in sorted(expected - actual):
            errors.append(f"{path.name}: missing {msgid!r}")
        for msgid in sorted(actual - expected):
            errors.append(f"{path.name}: stale {msgid!r}")
        for message in catalog:
            if message.id and (not message.string or "fuzzy" in message.flags):
                errors.append(f"{path.name}: untranslated/fuzzy {message.id!r}")
        for message, problems in catalog.check():
            errors.append(f"{path.name}: invalid {message.id!r}: {problems}")
    for path in LOCALE.glob("*.po"):
        if path.stem not in {pot.stem for pot in pots}:
            errors.append(f"Stale catalog: {path}")
    if errors:
        raise ValueError("Translation errors:\n" + "\n".join(errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("templates", type=Path)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    check_translations(args.templates, update=args.update)
