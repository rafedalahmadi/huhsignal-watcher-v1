import yfinance as yf
import time
import requests

# إعدادات المستخدم
deepseek_api_key = "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"
telegram_token = "6763167199:AAE5USiAFQfSG7GV1OpgT9eTHtxyay2U_Go"
telegram_chat_id = "1002823093448"
symbol = "US500"
interval = "5m"
num_candles = 80

def get_latest_candles():
    df = yf.download(tickers=symbol, interval=interval, period="2d", progress=False)
    return df.tail(num_candles)

def format_candles(df):
    text = ""
    for timestamp, row in df.iterrows():
        text += f"[{timestamp}] | O:{float(row['Open']):.2f} H:{float(row['High']):.2f} L:{float(row['Low']):.2f} C:{float(row['Close']):.2f} V:{int(row['Volume'])}\n"
    return text

def ask_deepseek(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepseek_api_key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "أنت خبير في تحليل السوق باستخدام نماذج Wyckoff وSmart Money وElliott Waves. حلل هذه البيانات وحدد إذا كانت هناك فرصة قوية."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("❌ DeepSeek Error:", response.text)
        return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def main_loop():
    print("⏳ Downloading last 80 candles...")
    df = get_latest_candles()
    candles_text = format_candles(df)
    
    print("🧠 Sending to DeepSeek...")
    ai_result = ask_deepseek(candles_text)

    if ai_result and "فرصة" in ai_result and "٪" in ai_result:
        print("🚀 Opportunity found, sending alert...")
        send_telegram_message("📊 تحليل السوق:\n\n" + ai_result)
    else:
        print("⚠️ No opportunity found.")

while True:
    main_loop()
    print("⏲️ Waiting 5 minutes...")
    time.sleep(300)

