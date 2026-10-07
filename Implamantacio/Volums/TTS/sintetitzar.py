import argparse
import json
import os
import subprocess
import sys

def carregar_configuracio(config_path):
    """Carrega el fitxer de configuració JSON."""
    if not os.path.exists(config_path):
        print(f"❌ ERROR: Fitxer de configuració no trobat a {config_path}")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sintetitzar_text(text, idioma, output_file, config_path):
    config = carregar_configuracio(config_path)

    # Validar idioma
    lang_info = config["languages"].get(idioma)
    if not lang_info:
        print(f"❌ ERROR: Idioma '{idioma}' no suportat a la configuració. Opcions disponibles: {list(config['languages'].keys())}")
        sys.exit(1)

    # Construir rutes
    model_path = os.path.join(config["models_dir"], lang_info["model_file"])
    
    # Resoldre ruta de sortida (si és un nom de fitxer simple, es guarda a /data_io)
    if not os.path.isabs(output_file):
        output_path = os.path.join(config["data_dir"], output_file)
    else:
        output_path = output_file

    if not os.path.exists(model_path):
        print(f"❌ ERROR: El fitxer de model no existeix a {model_path}")
        sys.exit(1)

    # Assegurar que el directori de sortida existeix
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"🎙️ Generant àudio [{idioma}]...")
    print(f" └─ Model: {model_path}")
    print(f" └─ Sortida: {output_path}")

    # Comanda per executar Piper
    cmd = [
        "piper",
        "--model", model_path,
        "--output_file", output_path
    ]

    try:
        # Executem Piper passant el text per stdin
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=text)

        if process.returncode == 0:
            print(f"✅ Àudio generat amb èxit a: {output_path}")
        else:
            print(f"❌ ERROR en executar Piper:\n{stderr}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ ERROR inesperat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de síntesi de veu (Piper) basat en JSON.")
    parser.add_argument("--text", type=str, help="Text a sintetitzar.")
    parser.add_argument("--text_file", type=str, help="Fitxer .txt d'on llegir el text (dins de /data_io).")
    parser.add_argument("--lang", type=str, default="ca", help="Codi d'idioma (ca, es, en).")
    parser.add_argument("--output", type=str, default="sortida.wav", help="Nom o ruta del fitxer d'àudio de sortida.")
    parser.add_argument("--config", type=str, default="/app/config_tts.json", help="Ruta al JSON de configuració.")

    args = parser.parse_args()

    # Obtenir el text
    text_content = ""
    if args.text:
        text_content = args.text
    elif args.text_file:
        file_path = args.text_file if os.path.isabs(args.text_file) else os.path.join("/data_io", args.text_file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            print(f"❌ ERROR: El fitxer {file_path} no existeix.")
            sys.exit(1)
    else:
        print("❌ ERROR: Cal proporcionar --text o --text_file.")
        sys.exit(1)

    sintetitzar_text(text_content, args.lang, args.output, args.config)
