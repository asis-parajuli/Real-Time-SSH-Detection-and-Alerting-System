import os
import time
import re
import smtplib
from collections import defaultdict
from datetime import datetime
from email.message import EmailMessage

LOG_FILE = "/var/log/auth.log"
ALERT_LOG = "alerts.log"
THRESHOLD = 5

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("ALERT_EMAIL")
APP_PASSWORD = os.getenv("ALERT_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("ALERT_RECIPIENT")

failed_attempts = defaultdict(int)

def send_email_alert(ip, count, timestamp):
    if not SENDER_EMAIL or not APP_PASSWORD or not RECIPIENT_EMAIL:
        print("[WARNING] Email settings are missing. Skipping email alert.")
        return

    subject = "SSH Brute-Force Alert"
    body = (
        f"Possible SSH brute-force attack detected.\n\n"
        f"Timestamp: {timestamp}\n"
        f"Attacker IP: {ip}\n"
        f"Failed Attempts: {count}\n"
        f"Log Source: {LOG_FILE}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] Alert email sent to {RECIPIENT_EMAIL}")

    except Exception as e:
        print(f"[ERROR] Failed to send email alert: {e}")

def write_alert(ip, count):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = (
        f"[{timestamp}] ALERT: Possible SSH brute-force attack detected "
        f"from {ip} ({count} failed attempts)"
    )

    print(alert_message)

    with open(ALERT_LOG, "a", encoding="utf-8") as alert_file:
        alert_file.write(alert_message + "\n")

    send_email_alert(ip, count, timestamp)

def follow_log(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()

            if not line:
                time.sleep(0.5)
                continue

            if "Failed password" in line:
                print("[FAILED SSH LOGIN]", line.strip())

                match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    ip = match.group(1)
                    failed_attempts[ip] += 1
                    count = failed_attempts[ip]

                    print(f"[INFO] {ip} -> {count} failed attempt(s)")

                    if count == THRESHOLD:
                        write_alert(ip, count)

if __name__ == "__main__":
    print("Starting real-time SSH intrusion detector...")
    print(f"Watching: {LOG_FILE}")
    print(f"Threshold: {THRESHOLD} failed attempts")
    print(f"Alert log file: {ALERT_LOG}")
    follow_log(LOG_FILE)