#!/usr/bin/env python3
"""Стягування контенту lcptodcz.lviv.ua → Hugo-контент (через r.jina.ai, бо CF 1009)."""
import json, os, re, sys, time, hashlib, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path("/home/agentuser/projects/lcpto-site")
RAW = ROOT / "_raw"
CONTENT = ROOT / "content"
STATIC_IMG = ROOT / "static" / "img"
for p in (RAW, CONTENT / "news", CONTENT / "pages", CONTENT / "profesii", STATIC_IMG):
    p.mkdir(parents=True, exist_ok=True)

JINA = "https://r.jina.ai/"
UA = {"User-Agent": "Mozilla/5.0"}

PAGES = {
    # slug: url
    "pro-zaklad": "https://lcptodcz.lviv.ua/pro-zaklad-10-09-13-28-02-2019/",
    "istoriya": "https://lcptodcz.lviv.ua/istoriya-lcpto-dsz-10-09-27-28-02-2019/",
    "kadry": "https://lcptodcz.lviv.ua/administraciya-10-09-37-28-02-2019/",
    "materialna-baza": "https://lcptodcz.lviv.ua/materialnotehnichna-baza-10-09-49-28-02-2019/",
    "metodychne": "https://lcptodcz.lviv.ua/kadrove-ta-navchalnometodichne-zabezpechennya-10-10-00-28-02-2019/",
    "kontakty": "https://lcptodcz.lviv.ua/kontakti-10-10-21-28-02-2019/",
    "publichna-informacia": "https://lcptodcz.lviv.ua/pro-dostup-do-publichnoi-informacii-14-47-15-04-09-2025/",
    "osvitni-poslugy": "https://lcptodcz.lviv.ua/osvitni-poslugi-10-17-18-28-02-2019/",
    "perelik-profesij": "https://lcptodcz.lviv.ua/perelik-profesij-10-17-32-28-02-2019/",
    "kursy-pk": "https://lcptodcz.lviv.ua/napryami-kursiv-cilovogo-priznachennya-10-20-55-28-02-2019/",
    "platni-poslugy": "https://lcptodcz.lviv.ua/platni-poslugi-10-23-51-28-02-2019/",
    "pravyla-prijomu": "https://lcptodcz.lviv.ua/pravila-prijomu-do-cpto-10-24-24-28-02-2019/",
    "pracevlashtuvannya": "https://lcptodcz.lviv.ua/pracevlashtuvannya-10-25-14-28-02-2019/",
    "kvalifikacijnyj-centr": "https://lcptodcz.lviv.ua/kvalifikacijnij-centr-14-40-39-12-02-2026/",
    "zakonodavstvo": "https://lcptodcz.lviv.ua/zakonodavchonormativna-baza-10-27-18-28-02-2019/",
    "distancijne": "https://lcptodcz.lviv.ua/distancijne-navchannya-10-23-35-28-02-2019/",
    "dualne": "https://lcptodcz.lviv.ua/dualne-navchannya-10-21-35-28-02-2019/",
    "sluhacham": "https://lcptodcz.lviv.ua/sluhacham-10-24-04-28-02-2019/",
    "robotodavtsyam": "https://lcptodcz.lviv.ua/robotodavcyam-10-25-57-28-02-2019/",
    "prezentacia": "https://lcptodcz.lviv.ua/prezentacii-10-26-42-28-02-2019/",
    "zvorotnyj-zvyazok": "https://lcptodcz.lviv.ua/feedback/",
}

NEWS = [
    "https://lcptodcz.lviv.ua/news/10-16-16-28-09-2026/",
    "https://lcptodcz.lviv.ua/news/09-39-42-28-09-2026/",
    "https://lcptodcz.lviv.ua/news/15-38-30-25-09-2026/",
    "https://lcptodcz.lviv.ua/news/15-35-13-25-09-2026/",
    "https://lcptodcz.lviv.ua/news/15-04-09-25-09-2026/",
    "https://lcptodcz.lviv.ua/news/14-03-57-25-09-2026/",
    "https://lcptodcz.lviv.ua/news/14-08-22-24-09-2026/",
    "https://lcptodcz.lviv.ua/news/16-12-20-23-09-2026/",
    "https://lcptodcz.lviv.ua/news/10-11-35-22-09-2026/",
    "https://lcptodcz.lviv.ua/news/13-04-52-21-09-2026/",
    "https://lcptodcz.lviv.ua/news/17-04-16-09-09-2026/",
    "https://lcptodcz.lviv.ua/news/17-02-48-09-09-2026/",
    "https://lcptodcz.lviv.ua/news/13-52-09-24-08-2026/",
    "https://lcptodcz.lviv.ua/news/10-15-23-22-07-2026/",
    "https://lcptodcz.lviv.ua/news/12-18-01-31-07-2026/",
    "https://lcptodcz.lviv.ua/news/13-57-11-21-07-2026/",
    "https://lcptodcz.lviv.ua/news/16-19-04-14-07-2026/",
    "https://lcptodcz.lviv.ua/news/12-39-39-08-06-2026/",
    "https://lcptodcz.lviv.ua/news/09-41-01-03-06-2026/",
    "https://lcptodcz.lviv.ua/news/15-15-38-10-06-2026/",
]

JUNK = [
    r"!\[[^\]]*\]\(https://www\.google\.com/images/cleardot\.gif\)",
    r"\[Select Language[^\]]*\]\([^)]*\)",
    r"!\[[^\]]*\]\(https://fonts\.gstatic\.com[^)]*\)",
    r"\[RSS-Новини\]\([^)]*\)",
    r"\[A\]\(https://alt\.lcptodcz\.lviv\.ua[^)]*\)",
    r"\[K\]\(https://alt\.lcptodcz\.lviv\.ua[^)]*\)",
    r"для людей з порушеннями зору",
    r"\[Мапа сайта\]\([^)]*\)",
    r"\[Показати код для вставки на сайт\]\([^)]*\)",
    r"#### Код для вставки на сайт",
    r"!\[Osv\.org\.ua[^\]]*\]\([^)]*\)",
    r"!\[Dytsadok\.org\.ua[^\]]*\]\([^)]*\)",
    r"!\[School\.org\.ua[^\]]*\]\([^)]*\)",
    r"#### Вхід для адміністратора",
    r"Логін: \*",
    r"Пароль: \*",
    r"Авторизуватись",
    r"#### Онлайн-опитування:[\s\S]*?(?=#### |$)",
    r"#### Результати опитування",
    r"\[Всі опитування\]\([^)]*\)",
    r"#### Дякуємо!",
    r"Ваш голос було підтверджено",
    r"Original text",
    r"Rate this translation",
    r"Your feedback will be used to help improve Google Translate",
]


def fetch(url: str, tries: int = 3) -> str:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(JINA + url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (i + 1))
    raise SystemExit(f"✗ {url}: {last}")


def clean(md: str) -> str:
    for pat in JUNK:
        md = re.sub(pat, "", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s_]+", "-", s)[:60].strip("-") or "page"


def localize_images(md: str) -> tuple[str, list[str]]:
    """Завантажити зображення rada.info локально; повернути оновлений md + список файлів."""
    out, files = md, []
    for url in sorted(set(re.findall(r"https://rada\.info/upload/[^\s)\"]+\.(?:jpg|jpeg|png|webp|gif)", md))):
        h = hashlib.md5(url.encode()).hexdigest()[:10]
        ext = url.rsplit(".", 1)[-1].lower()
        name = f"{h}.{ext}"
        dest = STATIC_IMG / name
        if not dest.exists():
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    dest.write_bytes(r.read())
                files.append(name)
                time.sleep(0.4)
            except Exception as e:  # noqa: BLE001
                print(f"    ! img {url}: {e}", file=sys.stderr)
                continue
        out = out.replace(url, f"/img/{name}")
    # slideshow-«стіни» зображень скорочуємо: лишаємо перші 4 у сторінці
    return out, files


def front(title: str, date: str, summary: str = "") -> str:
    fm = ["---", f"title: {json.dumps(title, ensure_ascii=False)}"]
    if date:
        fm.append(f"date: {date}")
    if summary:
        fm.append(f"summary: {json.dumps(summary, ensure_ascii=False)}")
    fm.append("draft: false")
    fm.append("---")
    return "\n".join(fm)


def parse_title(md: str, fallback: str) -> str:
    m = re.search(r"^Title:\s*(.+)$", md, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return m.group(1).strip() if m else fallback


def parse_body(md: str) -> str:
    m = re.search(r"Markdown Content:\s*\n(.*)$", md, re.S)
    return (m.group(1) if m else md).strip()


def main() -> None:
    got = {"pages": 0, "news": 0, "imgs": 0}

    # ---- новини ----
    for url in NEWS:
        m = re.search(r"/news/(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{4})/", url)
        hh, mm, _s, dd, mo, yy = m.groups()
        date = f"{yy}-{mo}-{dd}T{hh}:{mm}:00"
        raw = fetch(url)
        title = parse_title(raw, "Новина")
        body = clean(parse_body(raw))
        body, imgs = localize_images(body)
        got["imgs"] += len(imgs)
        slug = f"{yy}{mo}{dd}-{slugify(title)}"
        page = front(title, date) + "\n\n" + body + "\n"
        (CONTENT / "news" / f"{slug}.md").write_text(page, encoding="utf-8")
        got["news"] += 1
        print(f"  ✓ новина: {title[:60]}")
        time.sleep(1)

    # ---- сторінки ----
    for slug, url in PAGES.items():
        raw = fetch(url)
        title = parse_title(raw, slug)
        body = clean(parse_body(raw))
        body, imgs = localize_images(body)
        got["imgs"] += len(imgs)
        page = front(title, "2019-02-28") + "\n\n" + body + "\n"
        # професії — в окрему секцію
        section = "profesii" if slug in {
            "perelik-profesij", "osvitni-poslugy", "kursy-pk", "pravyla-prijomu",
            "platni-poslugy", "kvalifikacijnyj-centr"} else "pages"
        (CONTENT / section / f"{slug}.md").write_text(page, encoding="utf-8")
        got["pages"] += 1
        print(f"  ✓ сторінка: {title[:60]}")
        time.sleep(1)

    (RAW / "stats.json").write_text(json.dumps(got, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(got, ensure_ascii=False))


if __name__ == "__main__":
    main()
