#!/usr/bin/env python3
"""Фіналізація контенту: слайд-джункт геть, rada.info → локальні файли через weserv-проксі."""
import hashlib, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path("/home/agentuser/projects/lcpto-site")
IMG = ROOT / "static" / "img"
IMG.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

removed = rewritten = failed = 0
for md in ROOT.joinpath("content").rglob("*.md"):
    s = md.read_text(encoding="utf-8")
    orig = s

    # 1) слайдшоу-зображення (users_files/slides/) — це стіна фото з шаблону, не контент
    s, n = re.subn(r"!\[[^\]]*\]\(https://rada\.info/upload/[^\s)\"]*/slides/[^)]+\)\s*", "", s)
    removed += n

    # 2) решту rada.info зображень — локально через weserv (він качається, де прямий 403)
    def repl(m):
        global rewritten, failed
        url = m.group(2)
        h = hashlib.md5(url.encode()).hexdigest()[:10]
        ext = (url.rsplit(".", 1)[-1].lower())[:4]
        name = f"{h}.{ext}"
        dest = IMG / name
        if not dest.exists():
            try:
                proxy = "https://images.weserv.nl/?url=" + urllib.parse.quote(
                    url.replace("https://", "").replace("http://", ""), safe="")
                req = urllib.request.Request(proxy, headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    dest.write_bytes(r.read())
                time.sleep(0.3)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"  ! {url}: {e}", file=sys.stderr)
                return m.group(0)
        rewritten += 1
        return f"{m.group(1)}(/img/{name})"

    s = re.sub(r"(!\[[^\]]*\]\()(https://rada\.info/[^)\s\"]+)(\))", repl, s)

    # 3) обгорнути «голі» rada.info URL без ![]() — теж локально
    s = re.sub(r"(?<!\()(https://rada\.info/upload/[^\s)\"]+\.(?:jpg|jpeg|png|webp|gif))",
               lambda m: f"/img/{hashlib.md5(m.group(1).encode()).hexdigest()[:10]}.{m.group(1).rsplit('.',1)[-1].lower()[:4]}"
               if (IMG / f"{hashlib.md5(m.group(1).encode()).hexdigest()[:10]}.{m.group(1).rsplit('.',1)[-1].lower()[:4]}").exists()
               else m.group(1), s)

    if s != orig:
        md.write_text(s, encoding="utf-8")

print(f"  слайд-джункт прибрано: {removed}")
print(f"  зображень локалізовано: {rewritten}")
print(f"  помилок: {failed}")
print(f"  файлів у static/img: {len(list(IMG.iterdir()))}")
