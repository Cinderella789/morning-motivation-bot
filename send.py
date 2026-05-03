import os, random, requests
from openai import OpenAI

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
    f"Напиши утреннее мотивационное сообщение на русском, 2–3 предложения (30–45 слов), "
    f"на тему: {theme}. "
    "Тон тёплый и бодрящий, без клише и пафоса, без эмодзи и хэштегов. "
    "Заверши лёгким призывом к действию на сегодня."
)

text = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.95,
    max_tokens=200,
).choices[0].message.content.strip()

r = requests.post(
    f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage",
    json={"chat_id": os.environ["TG_CHAT_ID"], "text": text},
    timeout=15,
)
r.raise_for_status()
print("Sent:", text)
