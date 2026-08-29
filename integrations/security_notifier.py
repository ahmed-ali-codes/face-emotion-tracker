import os
import time
import threading
import requests
import smtplib
from email.message import EmailMessage
import cv2
from dotenv import load_dotenv

load_dotenv()

# Configuration
ALERT_METHOD = os.getenv("SECURITY_ALERT_METHOD", "none").lower()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

_last_alert_time = 0
_alert_cooldown = 30 # seconds

def send_telegram_alert(image_path):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram configured but tokens are missing.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                url,
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": "🚨 SECURITY ALERT: Unknown face detected!"},
                files={"photo": image_file}
            )
        print("📨 Telegram alert sent!")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

def send_email_alert(image_path):
    if not all([EMAIL_SMTP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_TO]):
        print("⚠️ Email configured but credentials are missing.")
        return
        
    msg = EmailMessage()
    msg['Subject'] = '🚨 SECURITY ALERT: Unknown face detected!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg.set_content('An unknown person was detected by your Smart Camera.')

    try:
        with open(image_path, 'rb') as img:
            img_data = img.read()
            msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename='intruder.jpg')

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send Email alert: {e}")

def _alert_task(frame):
    # Save temp image
    os.makedirs("temp", exist_ok=True)
    temp_path = "temp/intruder.jpg"
    cv2.imwrite(temp_path, frame)
    
    if ALERT_METHOD == "telegram":
        send_telegram_alert(temp_path)
    elif ALERT_METHOD == "email":
        send_email_alert(temp_path)
    else:
        print("🚨 Alert Triggered (No method configured in .env)")

def trigger_security_alert(frame):
    global _last_alert_time
    current_time = time.time()
    
    # Cooldown to avoid spamming
    if current_time - _last_alert_time > _alert_cooldown:
        _last_alert_time = current_time
        print("🚨 Triggering security alert thread...")
        threading.Thread(target=_alert_task, args=(frame,), daemon=True).start()
