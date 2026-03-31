"""
Fill all empty msgstr in locale/en and locale/it django.po (Google Translate ru→en / ru→it).
Run after makemessages when new strings appear (e.g. model verbose_name).
"""
import pathlib
import time

import polib
from deep_translator import GoogleTranslator

root = pathlib.Path(__file__).resolve().parents[1]

for lang_code, target in (("en", "en"), ("it", "it")):
    po_path = root / "locale" / lang_code / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(po_path))
    tr = GoogleTranslator(source="ru", target=target)
    updated = 0
    for entry in po:
        if entry.msgstr is None:
            entry.msgstr = ""
    for entry in po:
        if entry.obsolete:
            continue
        if not entry.msgid or not entry.msgid.strip():
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
            print(lang_code, "error:", e, "for", entry.msgid[:80])
    po.save(str(po_path))
    print(f"{lang_code}: filled {updated} empty entries")
