#!/usr/bin/env python3
"""Дотягує тіло сторінок, які попередній скрейп не забрав (лишилась сама шапка).

Для сторінок із «тонким» тілом: бере HTML через r.jina.ai, відкидає навігацію
й футер, дістає основний текст і ДОПИСУЄ його у файл.
"""
import re
import subprocess
import sys
from pathlib import Path

OLD = "https://lcptodcz.lviv.ua"

# сторінка -> старий URL
TARGETS = {
    "pages/istoriya.md": f"{OLD}/istoriya-lcpto-dsz-10-09-27-28-02-2019/",
    "pages/prezentacia.md": f"{OLD}/prezentacii-10-26-42-28-02-2019/",
    "pages/robotodavtsyam.md": f"{OLD}/robotodavcyam-10-25-57-28-02-2019/",
    "pages/sluhacham.md": f"{OLD}/sluhacham-10-24-04-28-02-2019/",
}

RE_NAV_LINE = re.compile(
    r'^\s*(?:\*\s+\[[^\]]+\]\(https?://[^)]*\)'
    r'|\[[^\]]*\]\(https?://[^)]*\)'
    r'|\[RSS-Новини\]'
    r'|\[A\]|\[K\]'
    r'|\*\s*\*\s*\*)\s*$'
)
RE_BOILER = re.compile(
    r'(school\.org\.ua|alt\.lcptodcz|static\.xx\.fbcdn|vlada\.ua|creativecommons'
    r'|auth_block|Кількість переглядів|адмін|Вхід для|Розробка порталу'
    r'|весь контент доступний)',
    re.I,
)


def fetch(url):
    r = subprocess.run(
        ["curl", "-s", "--max-time", "90", f"https://r.jina.ai/{url}"],
        capture_output=True, text=True,
    )
    return r.stdout


def extract(text):
    # відрізаємо службовий заголовок jina
    text = re.sub(r'^Title:.*?\n\n', '', text, flags=re.S)
    lines = text.split("\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if RE_NAV_LINE.match(s):
            continue
        if RE_BOILER.search(s):
            continue
        # суцільні рядки-посилання навігації без тексту
        if s.startswith("[") and s.endswith(")") and len(s) < 90:
            continue
        out.append(s)
    # прибираємо дублікати поспіль
    dedup = []
    for s in out:
        if not dedup or dedup[-1] != s:
            dedup.append(s)
    return dedup


def main():
    root = Path("content")
    for rel, url in TARGETS.items():
        f = root / rel
        if not f.exists():
            print(f"  ✗ немає {rel}")
            continue
        raw = fetch(url)
        if len(raw) < 500:
            print(f"  ✗ {rel}: порожня відповідь ({len(raw)}B)")
            continue
        blocks = extract(raw)
        body_new = "\n\n".join(blocks)
        s = f.read_text(encoding="utf-8")
        parts = s.split("---", 2)
        fm, body = parts[1], parts[2]
        if len(body_new) <= len(body.strip()) + 100:
            print(f"  = {rel}: джерело не дає більше ({len(body_new)}B проти {len(body.strip())}B)")
            continue
        f.write_text("---" + fm + "---\n\n" + body_new.strip() + "\n", encoding="utf-8")
        print(f"  ✓ {rel}: {len(body.strip())}B → {len(body_new)}B  ({len(blocks)} блоків)")
        print(f"      перші рядки: {' | '.join(blocks[:3])[:150]}")


if __name__ == "__main__":
    main()
