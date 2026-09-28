#!/usr/bin/env python3
"""Третя, заключна чистка: прибирає рештки, які лишились у «важких» файлах.

Після неї на сторінках не має лишатись нічого, крім реального тексту й фото.
"""
import re
from pathlib import Path

# тексти, які точно не належать контенту сторінки
JUNK_LINE = re.compile(
    r'^\s*(?:'
    r'для людей з порушеннями зору'
    r'|Меню сайту'
    r'|\s*[»›]\s*.*'                                   # хлібні крихти
    r'|Дата:\s*від.*'                                  # фільтр
    r'|[•\s]*Фільтрувати.*|.*Скинути\]?.*'
    r'|####\s*Код для вставки на сайт'
    r'|Логін:\s*\*|Пароль:\s*\*|Авторизуватись'
    r'|####\s*Онлайн-опитування:\s*'
    r'|####\s*Результати опитування'
    r'|####\s*Дякуємо!'
    r'|Ваш голос було підтверджено'
    r'|E-Mail:\s*\*|Підтвердити голос.*'
    r'|\*\*Увага!\*\* З метою уникнення фальсифікацій.*'
    r'|\d{2}:\d{2}\s+\d{2}\.\d{2}\.\d{4}'              # «10:18 20.03.2019» — дата публікації зі старого
    r'|\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}'
    r'|Львівський центр|професійно-технічної освіти\s*$|державної служби зайнятості\s*$'
    r'|.*Весь контент доступний за ліцензією.*|.*Creative Commons.*'
    r'|\[Вхід для адміністратора\].*|Розробка порталу:.*|\[«Vlada\.ua».*'
    r'|\[RSS-Новини\].*|\[A\]|\[K\]'
    r'|)\s*$', re.M)

# зіпсовані картинки «![(url)» — це результат попередньої заміни; відновлюємо з alt
RE_BROKEN_IMG = re.compile(r'!\[\]?\((?P<url>https?://[^)]+)\)')
RE_ANY_IMG_LINE = re.compile(r'^!\[.*\]\([^)]*\)\s*$')


def clean(body):
    lines = body.split("\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append("")
            continue
        if JUNK_LINE.match(s):
            continue
        # картинки з чужих доменів (rada.info, google cleardot) — вони не локальні
        if "rada.info" in s or "cleardot.gif" in s or "footer_banner" in s:
            continue
        out.append(ln.rstrip())
    text = "\n".join(out)
    text = re.sub(r'\n{3,}', '\n\n', text).strip() + "\n"
    return text


def main():
    rows = []
    for f in sorted(Path("content").rglob("*.md")):
        s = f.read_text(encoding="utf-8")
        if not s.startswith("---"):
            continue
        parts = s.split("---", 2)
        fm, body = parts[1], parts[2]
        nb = clean(body)
        if nb != body:
            f.write_text("---" + fm + "---\n\n" + nb, encoding="utf-8")
            rows.append((str(f.relative_to("content")), len(body), len(nb)))
    print(f"{'файл':<58} {'було':>6} {'стало':>6}")
    print("-" * 76)
    for n, b, a in rows:
        print(f"{n[:56]:<58} {b:>6} {a:>6}")
    print(f"\nоброблено: {len(rows)}")


if __name__ == "__main__":
    main()
