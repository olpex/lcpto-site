#!/usr/bin/env python3
"""Прибирає з контенту рештки старого сайту lcptodcz.lviv.ua:
логотип-леттерхед, хлібні крихти, дубль H1, рядки «Дата/Перегляди»,
вклеєне мега-меню, банери партнерів і старий футер.

Пише звіт: скільки байтів було / стало, щоб видно було втрати.
"""
import re
import sys
from pathlib import Path

# --- що вважаємо сміттям ---
RE_LETTERHEAD_IMG = re.compile(r'^!\[Львівський центр[^\]]*\]\(/img/(?:7cd27240ce|a4eabd8a16)\.png\)\s*$')
RE_ORG_NAME_LINE = re.compile(r'^Львівський центр\s*$|^професійно-технічної освіти\s*$|^державної служби зайнятості\s*$')
RE_BREADCRUMB = re.compile(r'^\s*»\s*\[[^\]]+\]\(https://lcptodcz\.lviv\.ua[^)]*\)')
RE_META_LINE = re.compile(r'^\s*(?:Дата|Кількість переглядів)\s*:')
RE_FBCDN = re.compile(r'!\[[^\]]*\]\(https://static\.xx\.fbcdn\.net[^)]*\)')
RE_MENU_START = re.compile(r'^\s*\*\s+\[Головна\]\(https://lcptodcz\.lviv\.ua')
RE_MENU_ITEM = re.compile(r'^\s*\*\s+\[[^\]]+\]\(https://lcptodcz\.lviv\.ua[^)]*\)\s*$')
RE_HR = re.compile(r'^\s*\*\s*\*\s*\*\s*$')
RE_FOOTER_START = re.compile(r'^\s*Львівський центр\s*$|^\s*«Vlada\.ua»|^\s*Розробка порталу')

# банери партнерів / центрів ПТО — блоки, які треба вирізати повністю
PARTNER_HEADINGS = (
    "**Офіційні сайти органів влади і державних установ**",
    "**Центри ПТО ДСЗ України**",
)


def split_front_matter(text):
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def clean_body(body, title, report):
    lines = body.split("\n")
    out = []
    # 1) зрізаємо провідне сміття (лого, назва, хлібні крихти, мета, дубль H1)
    i = 0
    while i < len(lines):
        line = lines[i]
        if (not line.strip()
                or RE_LETTERHEAD_IMG.match(line)
                or RE_ORG_NAME_LINE.match(line)
                or RE_BREADCRUMB.match(line)
                or RE_META_LINE.match(line)):
            report["leading"] += 1
            i += 1
            continue
        # дубль H1 == title
        m = re.match(r'^#\s+(.+?)\s*$', line)
        if m and title:
            h = re.sub(r'\s+', ' ', m.group(1)).strip()
            t = re.sub(r'\s+', ' ', title).strip()
            if h.lower() == t.lower():
                report["dup_h1"] += 1
                i += 1
                continue
        break
    lines = lines[i:]

    # 2) шукаємо межу вклеєного меню і ріжемо все від неї
    cut = None
    for idx, line in enumerate(lines):
        if RE_MENU_START.match(line):
            cut = idx
            break
    if cut is None:
        # інколи меню без пункту «Головна» — тоді за першим щільним блоком
        for idx, line in enumerate(lines):
            if RE_MENU_ITEM.match(line):
                cut = idx
                break
    if cut is not None:
        report["menu_cut"] += 1
        # прибираємо розділювач і порожні рядки перед меню
        tail = lines[:cut]
        while tail and (not tail[-1].strip() or RE_HR.match(tail[-1])):
            tail.pop()
        lines = tail

    # 3) вирізаємо блоки банерів партнерів (якщо лишились)
    text = "\n".join(lines)
    for head in PARTNER_HEADINGS:
        pos = text.find(head)
        if pos != -1:
            report["partner_block"] += 1
            text = text[:pos]
    # 4) футер старого сайту
    text = re.sub(r'\n\s*[^\n]*Весь контент доступний за ліцензією.*$', '', text, flags=re.S)
    text = re.sub(r'\n\s*\[Вхід для адміністратора\]\(https://lcptodcz[^\n]*$', '', text)
    # 5) fbcdn-емодзі та леттерхед-картинки всередині
    text, n = RE_FBCDN.subn('', text)
    report["fbcdn"] += n
    text, n = RE_LETTERHEAD_IMG.subn('', text, count=0) if False else (text, 0)
    # 6) зайві порожні рядки
    text = re.sub(r'\n{3,}', '\n\n', text).strip() + "\n"
    return text


def main():
    root = Path("content")
    report = {"leading": 0, "dup_h1": 0, "menu_cut": 0, "partner_block": 0, "fbcdn": 0}
    rows = []
    for f in sorted(root.rglob("*.md")):
        fm, body = split_front_matter(f.read_text(encoding="utf-8"))
        if not fm:
            continue
        m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
        title = m.group(1) if m else ""
        before = len(body)
        new = clean_body(body, title, report)
        after = len(new)
        if after != before:
            f.write_text("---" + fm + "---\n" + new, encoding="utf-8")
            rows.append((str(f.relative_to(root)), before, after))

    print(f"{'файл':<58} {'було':>7} {'стало':>7}  різниця")
    print("-" * 90)
    tb = ta = 0
    for name, b, a in rows:
        tb += b; ta += a
        print(f"{name[:56]:<58} {b:>7} {a:>7}  {a-b:>+7}")
    print("-" * 90)
    print(f"{'РАЗОМ':<58} {tb:>7} {ta:>7}  {ta-tb:>+7}")
    print()
    print("лічильники:", report)
    print(f"оброблено файлів: {len(rows)}")


if __name__ == "__main__":
    main()
