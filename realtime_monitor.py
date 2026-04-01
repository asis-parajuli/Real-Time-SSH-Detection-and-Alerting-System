import time

LOG_FILE = "/var/log/auth.log"

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

if __name__ == "__main__":
    print("Starting real-time SSH log monitor...")
    print(f"Watching: {LOG_FILE}")
    follow_log(LOG_FILE)
