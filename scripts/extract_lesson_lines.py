"""Extract prose lines from Junior and Pro lesson bodies (skip fenced code blocks)."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
path = root / "courses" / "management" / "commands" / "populate_db.py"
text = path.read_text(encoding="utf-8")


def prose_lines_from_section(section: str) -> set:
    lines_out = set()
    for m in re.finditer(r'"""(.*?)"""', section, re.DOTALL):
        body = m.group(1)
        in_fence = False
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if stripped:
                lines_out.add(line.rstrip("\r"))
    return lines_out


junior_section = text.split("junior_lessons = [", 1)[1].split("# 7. Заполняем уроки Pro", 1)[0]
pro_section = text.split("pro_lessons = [", 1)[1].split(
    "        ]\n        for order, title, content in pro_lessons:", 1
)[0]

lines_out = prose_lines_from_section(junior_section) | prose_lines_from_section(pro_section)

out = root / "scripts" / "prose_lines_utf8.txt"
out.write_text("\n".join(sorted(lines_out, key=lambda x: (len(x), x))), encoding="utf-8")
print("Wrote", len(lines_out), "lines to", out)
