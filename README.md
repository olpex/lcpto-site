# ЛЦПТО — Львівський центр ПТО ДСЗ (демо на безкоштовному стеку)

Повний клон сайту **lcptodcz.lviv.ua** на сучасному безкоштовному стеку. Контент стягнуто з оригіналу, зображення локалізовано, верстка — власна тема.

**Live демо:** після `wrangler login` → `npx wrangler pages deploy public`

## Стек (весь безкоштовний)

| Потреба | Рішення | Ліміт Free |
|---|---|---|
| Хостинг + CDN + TLS | **Cloudflare Pages** | Безліміт трафіку, 500 збірок/міс, 20k файлів, 25 МБ/файл |
| Генератор сайту | **Hugo extended 0.167** | — |
| CMS для викладачів | **Decap CMS** (`/admin`) — GitHub OAuth | — |
| Форми / звернення | **Pages Functions** (`/api/contact`) + Turnstile | — |
| Анти-бот | **Cloudflare Turnstile** (безкоштовно) | — |
| Пошта домену | **Zoho Mail Free** або **Cloudflare Email Routing** (форвард) | 5 юзерів × 5 ГБ / безліміт форварду |
| Бекапи / файли | **Cloudflare R2** | 10 ГБ + 10M запитів/міс, 0 egress |
| Моніторинг | **UptimeRobot** | 50 моніторів, 5 хв |

## Структура

```
content/news/       — 20 новин (Markdown, фронтматер summary)
content/pages/      — 15 сторінок (про заклад, контакти…)
content/profesii/   — 6 професій
static/img/         — 156 локальних зображень (38 МБ)
static/admin/       — Decap CMS (config.yml + index.html)
functions/api/contact.js — Pages Function (Turnstile → WEBHOOK_URL)
themes/lcpto/       — власна тема (Manrope+Inter, дві теми)
hugo.toml           — конфіг (укр. локаль, меню, hero)
```

## Локально

```bash
hugo --minify            # зібрати в public/
hugo server -D           # http://localhost:1313
```

## Деплой на Cloudflare Pages

1. `wrangler login` (або підключити GitHub → Pages → Connect)
2. Build: `hugo --minify`, output `public`
3. Env для форм: `WEBHOOK_URL` (n8n / Telegram / Sheets), `TURNSTILE_SECRET`

Pages Function автоматично деплоїться з теки `functions/`.

## Теми (кастомізація UX/UI)

Дві теми без перенесення контенту — перемикач у шапці (`localStorage`):

- **Світла** (default) — `#0e5a8a` / `#e8a020`
- **Глибока синь** — `#1b2a4b`

Додати свою: продублювати блок `body.theme-*` у `themes/lcpto/assets/css/main.css` + кнопку в `baseof.html`.

## Адмінка

`/admin` → Decap CMS. Перед публікацією замінити `repo: OWNER/lcpto-site` у `static/admin/config.yml` на свій репозиторій та ввімкнути GitHub OAuth (Decap → GitHub).

## Оригінал

Архітектура оригіналу: `rada.info` (Metastudio), `school.org.ua` проксі, Cloudflare 1009 (країновий WAF). Дана версія знімає залежність від обох.
