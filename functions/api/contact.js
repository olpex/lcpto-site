// Cloudflare Pages Function: POST /api/contact → Sheet / email / Turnstile.
// Замінити sitekey та додати зв'язку: npx wrangler pages secret put TURNSTILE_SECRET.

export async function onRequestPost({ request, env }) {
  const form = await request.formData().catch(() => null);
  const body = form ? Object.fromEntries(form) : await request.json().catch(() => ({}));
  const { name, email, message, "cf-turnstile-response": token } = body;

  if (!name || !email || !message)
    return json({ error: "Заповніть усі поля." }, 400);

  // Turnstile — безкоштовно, валідація на сервері
  if (env.TURNSTILE_SECRET && token) {
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: new URLSearchParams({
        secret: env.TURNSTILE_SECRET,
        response: token,
        remoteip: request.headers.get("CF-Connecting-IP") || "",
      }),
    }).then(x => x.json());
    if (!r.success) return json({ error: "Не пройдено перевірку Turnstile." }, 400);
  }

  // Куди складати: Telegram / n8n / Google Sheets — один fetch
  if (env.WEBHOOK_URL) {
    await fetch(env.WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, message, at: new Date().toISOString(), ip: request.headers.get("CF-Connecting-IP") }),
    });
  }

  // Email — якщо налаштовано Workers Email / Resend
  // await env.EMAIL?.send({ to: "office@lcptodcz.lviv.ua", subject: `Звернення: ${name}`, body: message, from: email });

  return json({ ok: true, message: "Дякуємо! Звернення отримано." });
}

function json(o, status = 200) {
  return new Response(JSON.stringify(o), {
    status, headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
