import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

def carregar_configuracio(config_path):
    if not os.path.exists(config_path):
        print(f"❌ ERROR: Fitxer de configuració no trobat a {config_path}")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def preparar_audio_vosk(input_path):
    necesita_conversio = False
    try:
        with wave.open(input_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                necesita_conversio = True
    except Exception:
        necesita_conversio = True

    if not necesita_conversio:
        return input_path, None

    print("🔄 El format d'àudio no és directe per a Vosk. Convertint automàticament amb ffmpeg...")

    temp_wav = tempfile.NamedTemporaryFile(suffix="_vosk_temp.wav", delete=False)
    temp_wav_path = temp_wav.name
    temp_wav.close()

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-acodec", "pcm_s16le",
        temp_wav_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ ERROR en convertir l'àudio amb ffmpeg:\n{result.stderr.decode('utf-8')}")
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        sys.exit(1)

    return temp_wav_path, temp_wav_path

def transcriure_audio(input_file, idioma, output_file, config_path):
    config = carregar_configuracio(config_path)

    input_path = input_file if os.path.isabs(input_file) else os.path.join(config["data_dir"], input_file)
    if not os.path.exists(input_path):
        print(f"❌ ERROR: Fitxer d'àudio d'entrada no trobat a: {input_path}")
        sys.exit(1)

    lang_info = config["languages"].get(idioma)
    if not lang_info:
        print(f"❌ ERROR: Idioma '{idioma}' no configurat. Idiomes disponibles: {list(config['languages'].keys())}")
        sys.exit(1)

    model_path = os.path.join(config["models_dir"], lang_info["model_folder"])
    if not os.path.exists(model_path):
        print(f"❌ ERROR: La carpeta del model VOSK no existeix a: {model_path}")
        sys.exit(1)

    output_path = output_file if os.path.isabs(output_file) else os.path.join(config["data_dir"], output_file)

    # Convertir l'àudio si no és WAV mono 16-bit
    audio_processat_path, temp_to_clean = preparar_audio_vosk(input_path)

    print(f"🎧 Carregant model VOSK [{idioma}] des de: {model_path}")
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"❌ ERROR en carregar el model VOSK: {e}")
        if temp_to_clean and os.path.exists(temp_to_clean):
            os.remove(temp_to_clean)
        sys.exit(1)

    try:
        wf = wave.open(audio_processat_path, "rb")
    except Exception as e:
        print(f"❌ ERROR en obrir l'àudio adaptat: {e}")
        if temp_to_clean and os.path.exists(temp_to_clean):
            os.remove(temp_to_clean)
        sys.exit(1)

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    print(f"⏳ Transcribint: {input_file} ...")
    transcripcio_final = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if 'text' in result and result['text']:
                transcripcio_final += result['text'] + " "

    result = json.loads(rec.FinalResult())
    if 'text' in result and result['text']:
        transcripcio_final += result['text']

    wf.close()

    if temp_to_clean and os.path.exists(temp_to_clean):
        os.remove(temp_to_clean)

    text_net = transcripcio_final.strip()

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_net)
        print("-" * 50)
        print(f"✅ Transcripció completada i guardada a: {output_path}")
        print(f"📝 Text: {text_net}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ ERROR en guardar el fitxer de sortida: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de transcripció VOSK basat en JSON amb adaptació automàtica d'àudio.")
    parser.add_argument("--input", required=True, help="Nom o ruta del fitxer d'àudio (.wav, .mp3, .m4a, etc.) a /data_io.")
    parser.add_argument("--lang", default="ca", help="Idioma de transcripció (ca, es, en).")
    parser.add_argument("--output", default="transcripcio.txt", help="Nom o ruta del fitxer .txt de sortida.")
    parser.add_argument("--config", default="/app/config_stt.json", help="Ruta al JSON de configuració.")

    args = parser.parse_args()

    transcriure_audio(args.input, args.lang, args.output, args.config)
