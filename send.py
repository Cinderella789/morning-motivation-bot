import os, requests
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
prompt = (
    "Сгенерируй 2 коротких мотивирующих предложения на русском для утра. "
    "Тон бодрый, без клише и пафоса. Без эмодзи и хэштегов."
)
text = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.9,
).choices[0].message.content.strip()

r = requests.post(
    f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage",
    json={"chat_id": os.environ["TG_CHAT_ID"], "text": text},
    timeout=15,
)
r.raise_for_status()
print("Sent:", text)
