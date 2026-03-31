"""
Fill empty msgstr in locale/*/LC_MESSAGES/django.po for Junior lesson strings
using deep-translator (Google). Run after makemessages.
"""
import pathlib
import time

import polib
from deep_translator import GoogleTranslator

root = pathlib.Path(__file__).resolve().parents[1]

# Lines we extract for lessons (must match gettext flow)
catalog_path = root / "scripts" / "prose_lines_utf8.txt"
lesson_lines = set(catalog_path.read_text(encoding="utf-8").splitlines())
lesson_lines.discard("")

for lang_code, target in (("en", "en"), ("it", "it")):
    po_path = root / "locale" / lang_code / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(po_path))
    tr = GoogleTranslator(source="ru", target=target)
    updated = 0
    for entry in po:
        if entry.msgstr is None:
            entry.msgstr = ""
    for entry in po:
        if not entry.msgid or entry.msgid not in lesson_lines:
            continue
        if entry.msgstr and entry.msgstr.strip():
            continue
        try:
            text = entry.msgid
            if len(text) > 4500:
                entry.msgstr = text
                continue
            out = tr.translate(text)
            entry.msgstr = out if out is not None else ""
            updated += 1
            time.sleep(0.12)
        except Exception as e:
            print(lang_code, "error:", e, "for", entry.msgid[:60])
    po.save(str(po_path))
    print(f"{lang_code}: updated {updated} entries")
