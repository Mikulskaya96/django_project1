# -*- coding: utf-8 -*-
"""Remove fuzzy flag from all entries so gettext uses msgstr (Django/GNU gettext skips fuzzy)."""
import pathlib

import polib


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    for lang in ("en", "it"):
        path = root / "locale" / lang / "LC_MESSAGES" / "django.po"
        po = polib.pofile(str(path))
        n = 0
        for entry in po:
            if entry.fuzzy:
                entry.fuzzy = False
                entry.previous_msgid = None
                entry.previous_msgid_plural = None
                entry.previous_msgctxt = None
                n += 1
        po.save()
        print(f"{path.name} ({lang}): cleared fuzzy on {n} entries")


if __name__ == "__main__":
    main()
