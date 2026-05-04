import os, json, random, datetime, urllib.request, urllib.error, html
import requests
from openai import OpenAI

# --- antidup via GitHub issue marker ---
MSK = datetime.timezone(datetime.timedelta(hours=3))
today = datetime.datetime.now(MSK).strftime("%Y-%m-%d")
MARKER_TITLE = f"sent:{today}"
MARKER_LABEL = "sent-marker"

gh_token = os.environ.get("GITHUB_TOKEN")
repo = os.environ.get("GITHUB_REPOSITORY")


def gh(method, path, data=None):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "morning-motivation-bot",
        },
        data=json.dumps(data).encode() if data is not None else None,
    )
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def already_sent_today():
    if not (gh_token and repo):
        return False
    issues = gh(
        "GET",
        f"/repos/{repo}/issues?state=all&labels={MARKER_LABEL}&per_page=100",
    ) or []
    return any(i.get("title") == MARKER_TITLE for i in issues)


def mark_sent_today():
    if not (gh_token and repo):
        return
    try:
        gh("POST", f"/repos/{repo}/labels",
           {"name": MARKER_LABEL, "color": "ededed"})
    except Exception:
        pass
    issue = gh("POST", f"/repos/{repo}/issues",
               {"title": MARKER_TITLE, "labels": [MARKER_LABEL]})
    if issue and "number" in issue:
        gh("PATCH", f"/repos/{repo}/issues/{issue['number']}",
           {"state": "closed"})


if already_sent_today():
    print(f"Already sent today ({today}), exit.")
    raise SystemExit(0)

# --- generate motivation ---
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

themes = [
    "про маленькие шаги и прогресс",
    "про спокойствие и фокус на сегодняшнем дне",
    "про благодарность и наблюдение за деталями",
    "про смелость пробовать новое",
    "про дисциплину и привычки",
    "про энергию тела и движение",
    "про творчество и любопытство",
    "в духе стоиков (Марк Аврелий, Сенека), но простыми словами",
]

theme = random.choice(themes)

prompt = (
    f"Напиши утреннее мотивационное сообщение на русском на тему: {theme}. "
    "Сделай его тёплым, бодрящим, без клише, пафоса, эмодзи и хэштегов. "
    "Общий объём: 30–45 слов. "
    "Строго выведи текст в 2 коротких абзаца: первый абзац — поддерживающая мысль, "
    "второй абзац — лёгкий призыв к действию на сегодня. "
    "Между абзацами оставь одну пустую строку. "
    "Не добавляй заголовок, списки, кавычки и пояснения."
)

text = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.95,
    max_tokens=200,
).choices[0].message.content.strip()

safe_text = html.escape(text)

formatted_text = (
    "<b>Доброе утро</b>\n\n"
    f"{safe_text}"
)

r = requests.post(
    f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
    json={
        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
        "text": formatted_text,
        "parse_mode": "HTML",
    },
    timeout=15,
)

r.raise_for_status()
mark_sent_today()
print("Sent:", text)

