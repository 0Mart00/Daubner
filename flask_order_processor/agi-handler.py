#!/usr/bin/env python3
import sys, os, shutil, requests

FLASK_PROCESSOR_URL = "http://127.0.0.1:5001/trigger_processing"
# FONTOS: Ez az útvonal legyen a szerveren, és az Asterisk felhasználó tudjon írni bele!
# A legegyszerűbb, ha a flask app mappáján belül van, és a tulajdonosát az asterisk felhasználóra állítod.
PROCESSING_DIR = "/home/your_user/flask_order_processor/recordings_to_process" 

def log_agi(message):
    sys.stderr.write(f"AGI_LOG: {message}\n")
    sys.stderr.flush()

def main():
    try:
        call_unique_id = sys.argv[1]
        source_path = f"/var/spool/asterisk/recording/order-{call_unique_id}.wav"
        dest_path = os.path.join(PROCESSING_DIR, f"order-{call_unique_id}.wav")
        if not os.path.exists(source_path):
            log_agi(f"A felvétel nem található: {source_path}")
            sys.exit(1)
        shutil.move(source_path, dest_path)
        log_agi(f"Fájl áthelyezve: {dest_path}")
        requests.post(FLASK_PROCESSOR_URL, json={"audio_path": dest_path}, timeout=10)
    except Exception as e:
        log_agi(f"Hiba az AGI szkriptben: {e}")

if __name__ == "__main__":
    os.makedirs(PROCESSING_DIR, exist_ok=True)
    main()