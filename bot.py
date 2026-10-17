"""Havo.uz Telegram boti: havo yomonlashsa Telegram kanalga ogohlantirish yuboradi.

Sozlash:
  1) Telegramda @BotFather orqali bot yarating va TOKEN oling.
  2) Kanal yarating, botni kanalga ADMIN qiling.
  3) Muhit o'zgaruvchilari: BOT_TOKEN, CHAT_ID (masalan @tozahavo_uz), ixtiyoriy AQI_LIMIT (standart 100).
  4) Har 3 soatda ishga tushiring: cron, GitHub Actions yoki PythonAnywhere.
Kerak: pip install requests
"""
import os, requests

CITIES = [("Toshkent",41.31,69.28),("Samarqand",39.65,66.96),("Buxoro",39.77,64.42),("Namangan",41.00,71.67),
 ("Andijon",40.78,72.34),("Nukus",42.46,59.61),("Farg'ona",40.38,71.78),("Qo'qon",40.53,70.94),
 ("Qarshi",38.86,65.79),("Termiz",37.22,67.28),("Jizzax",40.12,67.84),("Guliston",40.49,68.78),
 ("Navoiy",40.10,65.37),("Urganch",41.55,60.63)]
LEVELS = [(50,"Yaxshi"),(100,"O'rtacha"),(150,"Sezgirlar uchun zararli"),(200,"Zararli"),(10**9,"Juda zararli")]
TOKEN, CHAT = os.environ["BOT_TOKEN"].strip(), os.environ["CHAT_ID"].strip()
LIMIT = int(os.environ.get("AQI_LIMIT", "100"))

def tg(method, **params):
    return requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", json=params, timeout=30).json()

# Tekshiruv (tokenni ko'rsatmaydi)
me = tg("getMe")
print("Bot:", me.get("result", {}).get("username"), "| ok:", me.get("ok"), "| xato:", me.get("description"))
ch = tg("getChat", chat_id=CHAT)
print("CHAT_ID uzunligi:", len(CHAT), "| faqat lotin harflar:", CHAT.isascii(), "| boshlanishi:", CHAT[:1])
print("Kanal:", ch.get("ok"), ch.get("result", {}).get("title"), "| xato:", ch.get("description"))

def level(a): return next(n for m, n in LEVELS if a <= m)

r = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality", timeout=30, params={
    "latitude": ",".join(str(c[1]) for c in CITIES), "longitude": ",".join(str(c[2]) for c in CITIES),
    "current": "us_aqi", "timezone": "auto"})
r.raise_for_status()
data = r.json()
data = data if isinstance(data, list) else [data]
bad = sorted(((d["current"]["us_aqi"], c[0]) for c, d in zip(CITIES, data)
              if d.get("current", {}).get("us_aqi") is not None and d["current"]["us_aqi"] > LIMIT), reverse=True)
if bad:
    lines = [f"⚠️ Havo sifati ogohlantirishi (AQI > {LIMIT})"] + [f"• {n}: {a} ({level(a)})" for a, n in bad]
    lines.append("Bolalar va sezgir odamlar tashqarida kamroq bo'lsin. Batafsil: https://olimaxon890-max.github.io/havo-uz/")
    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", timeout=30,
                         json={"chat_id": CHAT, "text": "\n".join(lines),
                               "link_preview_options": {"is_disabled": True}})
    if not resp.ok:
        raise SystemExit(f"Telegram xatosi {resp.status_code}: {resp.text}")
    print("Yuborildi:", bad)
else:
    print("Hamma shahar me'yorda.")
