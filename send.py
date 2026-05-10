import os, json, random, datetime, html
from pathlib import Path
import requests
from openai import OpenAI

# --- защёлка от случайных дублей ---
MSK = datetime.timezone(datetime.timedelta(hours=3))
today = datetime.datetime.now(MSK).strftime("%Y-%m-%d")
LOCK = Path(__file__).parent / ".last-sent-date.txt"

if LOCK.exists() and LOCK.read_text(encoding="utf-8").strip() == today and "--force" not in os.sys.argv:
    print(f"Already sent today ({today}), exit.")
    raise SystemExit(0)

# --- генерация ---
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
formatted_text = f"<b>Доброе утро</b>\n\n{safe_text}"

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

LOCK.write_text(today, encoding="utf-8")
print("Sent:", text)
