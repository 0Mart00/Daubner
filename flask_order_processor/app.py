import os
import json
import requests
import httpx  # <-- ÚJ IMPORT
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import speech

load_dotenv()
app = Flask(__name__)

# --- Kliensek és Konfiguráció ---
try:
    # --- MÓDOSÍTÁS KEZDETE ---
    # Létrehozunk egy HTTP klienst, ami expliciten NEM használ proxykat
    # a környezeti változókból.
    http_client = httpx.Client(proxies=None)

    # Ezt a konfigurált klienst adjuk át az OpenAI-nak.
    openai_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        http_client=http_client
    )
    # --- MÓDOSÍTÁS VÉGE ---

    speech_client = speech.SpeechClient()
    if openai_client.api_key is None: raise ValueError("OpenAI kulcs hiányzik")

except Exception as e:
    print(f"Hiba a kliensek inicializálásakor: {e}")
    exit()

DJANGO_API_URL = "http://127.0.0.1:8000/api/orders/"
SYSTEM_PROMPT = """
Te egy hasznos asszisztens vagy, aki ételrendelések telefonos leiratait dolgozza fel. A feladatod, hogy a kapott szövegből kinyerd a rendelési információkat és egy strukturált JSON objektumot adj vissza. A JSON objektumnak a következő kulcsokkal kell rendelkeznie: "termek", "mennyiseg", "meret", "atvetel_datuma", "atvetel_idoppontja", "nev", "telefonszam", "tipus" ('elvitel' vagy 'helyben fogyasztas'), "megjegyzes". Ha egy információ nem szerepel a szövegben, használj `null` értéket. Csak és kizárólag a JSON objektumot add vissza.
"""

# --- Segédfüggvények (VÁLTOZATLAN) ---
def transcribe_audio_google(file_path: str) -> str:
    print(f"Átírás kezdődik: {file_path}")
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(language_code="hu-HU", enable_automatic_punctuation=True)
    response = speech_client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    print(f"Google STT eredmény: {transcript}")
    return transcript

def extract_and_forward_order(transcript: str):
    if not transcript: raise ValueError("Az átirat üres.")
    completion = openai_client.chat.completions.create(model="gpt-4-turbo-preview", response_format={"type": "json_object"}, messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": transcript}])
    order_data = json.loads(completion.choices[0].message.content)
    print("--- ChatGPT által kinyert adatok ---\n", json.dumps(order_data, indent=2, ensure_ascii=False))
    response = requests.post(DJANGO_API_URL, json=order_data)
    response.raise_for_status()
    return order_data

# --- API Végpont (VÁLTOZATLAN) ---
@app.route('/trigger_processing', methods=['POST'])
def trigger_processing_endpoint():
    if not request.json or 'audio_path' not in request.json:
        return jsonify({"error": "Hiányzó 'audio_path'."}), 400
    file_path = request.json['audio_path']
    print(f"Feldolgozási kérés érkezett: {file_path}")
    if not os.path.exists(file_path):
        return jsonify({"error": f"A fájl nem található: {file_path}"}), 404
    try:
        transcript = transcribe_audio_google(file_path)
        order_data = extract_and_forward_order(transcript)
        return jsonify({"message": "Sikeres feldolgozás.", "processed_data": order_data}), 200
    except Exception as e:
        print(f"Hiba a feldolgozás során: {e}")
        return jsonify({"error": "Hiba történt a feldolgozás során.", "details": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Ideiglenes fájl törölve: {file_path}")

if __name__ == '__main__':
    app.run(debug=True, port=5001)