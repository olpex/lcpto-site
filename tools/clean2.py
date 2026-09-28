#!/usr/bin/env python3
"""Фінальна чистка контенту від решток старого сайту.

Обережно: НЕ чіпає реальний текст і зображення. Прибирає лише:
- службові рядки jina-проксі
- хлібні крихти «» …»
- форми/фільтри («Фільтрувати», «Скинути», «Дата: від», «Кількість переглядів»)
- підписи «![Image N: …]» → лишає саму картинку
- залишки мега-меню з абсолютними посиланнями
- банери партнерів
- футер старого сайту, горизонтальні лінії-роздільники
"""
import re
from pathlib import Path

RE_JINA = re.compile(r'^\s*(URL Source:|Markdown Content:)\s*.*$', re.M)
RE_CRUMB = re.compile(r'^\s*[»›]\s*.*$', re.M)
RE_FORMS = re.compile(
    r'^\s*(?:Дата:\s*від|Фільтрувати|\[Скинути\]\([^)]*\)|Скинути|'
    r'Кількість переглядів\s*:.*|Дата\s*:\s*\d.*|'
    r'Виберіть\s*.*|Сортувати\s*.*)\s*$', re.M | re.I)
RE_IMAGE_N = re.compile(r'!\[Image \d+(?:: [^\]]*)?\]')
RE_MENU_LINE = re.compile(r'^\s*\*\s+\[[^\]]+\]\(https?://lcptodcz\.lviv\.ua[^)]*\)\s*$', re.M)
RE_ANY_OLD_LINK = re.compile(r'\[([^\]]*)\]\(https?://lcptodcz\.lviv\.ua[^)]*\)')
RE_PARTNER = re.compile(r'^\s*\*\*Офіційні сайти органів влади і державних установ\*\*.*$', re.M | re.S)
RE_OLD_FOOTER = re.compile(
    r'^\s*(?:Львівський центр\s*$|професійно-технічної освіти\s*$|державної служби зайнятості.*$|'
    r'\[Вхід для адміністратора\].*$|Розробка порталу:.*$|\[«Vlada\.ua».*$|'
    r'.*Весь контент доступний за ліцензією.*$|.*Creative Commons.*$)', re.M)
RE_HR = re.compile(r'^\s*(?:\*\s*){3,}$', re.M)
RE_EMPTY_LINK = re.compile(r'\[\]\([^)]*\)')
RE_MULTI_NL = re.compile(r'\n{3,}')
RE_SPACE = re.compile(r'[ \t]+$', re.M)


def clean(text):
    before = len(text)
    text = RE_JINA.sub('', text)
    text = RE_CRUMB.sub('', text)
    text = RE_FORMS.sub('', text)
    text = RE_IMAGE_N.sub('![', text)          # !\[Image 12 → ![
    text = RE_MENU_LINE.sub('', text)
    text = RE_ANY_OLD_LINK.sub(r'\1', text)     # розлінковуємо старі URL, лишаємо текст
    # банери партнерів: ріжемо від заголовка до кінця блоку
    text = re.sub(r'\*\*Офіційні сайти органів влади і державних установ\*\*.*?(?=\n##|\Z)',
                  '', text, flags=re.S)
    text = re.sub(r'\*\*Центри ПТО ДСЗ України\*\*.*?(?=\n##|\Z)', '', text, flags=re.S)
    text = RE_OLD_FOOTER.sub('', text)
    text = RE_HR.sub('', text)
    text = RE_EMPTY_LINK.sub('', text)
    text = RE_SPACE.sub('', text)
    text = RE_MULTI_NL.sub('\n\n', text)
    return text.strip() + "\n", before


def main():
    rows = []
    for f in sorted(Path("content").rglob("*.md")):
        s = f.read_text(encoding="utf-8")
        if not s.startswith("---"):
            continue
        parts = s.split("---", 2)
        fm, body = parts[1], parts[2]
        new_body, before = clean(body)
        if new_body != body:
            f.write_text("---" + fm + "---\n\n" + new_body, encoding="utf-8")
            rows.append((str(f.relative_to("content")), before, len(new_body)))

    print(f"{'файл':<58} {'було':>6} {'стало':>6}")
    print("-" * 76)
    tb = ta = 0
    for n, b, a in rows:
        tb += b; ta += a
        print(f"{n[:56]:<58} {b:>6} {a:>6}")
    print("-" * 76)
    print(f"{'РАЗОМ':<58} {tb:>6} {ta:>6}   оброблено: {len(rows)}")


if __name__ == "__main__":
    main()
