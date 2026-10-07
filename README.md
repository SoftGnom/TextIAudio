# TextIAudio
Sistema àgil, modular i 100% offline per a la síntesi de veu (TTS amb Piper) i transcripció d'àudio (STT amb VOSK) en contenidors Docker aïllats.


# 🎙️ Text & Audio Processing Environment (Offline & Isolated)

Aquest projecte proporciona un entorn de processament de veu i text completament **aïllat i local (offline)** utilitzant contenedors Podman / Docker. Està dissenyat per executar tasques de **Síntesi de Veu (Text-to-Speech - TTS)** i **Transcripció d'Àudio (Speech-to-Text - STT)** sense necessitat de connexió a Internet ni enviament de dades a serveis externs.

---

## 🚀 Característiques Principals

- **🔒 Aïllament de Xarxa (`network_mode: none`):** Els contenidors s'executen sense accés a xarxa per garantir la màxima privacitat.
- **🗣️ Text-to-Speech (TTS):** Utilitza **Piper TTS** per generar àudio natural d'alta qualitat a partir de text.
- **🎧 Speech-to-Text (STT):** Utilitza **VOSK** per transcriure àudio a text en local. Adaptació automàtica de formats d'àudio mitjançant `ffmpeg`.
- **🌐 Suport Multilingüe:** Preparat per treballar en **Català (`ca`)**, **Castellà (`es`)** i **Anglès (`en`)**.
- **📁 Compartició de Dades Volàtils:** Intercanvi de fitxers d'entrada/sortida mitjançant el volum compartit `data_io`.

---

## 🏗️ Arquitectura del Projecte

El projecte està estructurat separant el codi executable, els models pesats d'IA i l'àrea d'entrada/sortida de dades (`data_io`):

```text
.
├── descarges.txt          # Guia de descàrrega dels models
├── README.md              # Documentació del projecte
└── Implamantacio/
    ├── compose.yml        # Orchestració dels serveis i volums
    ├── Dockerfile.piper   # Contenidor per a Piper TTS
    ├── Dockerfile.vosk    # Contenidor per a VOSK STT
    └── Volums/
        ├── data_io/       # Directori d'intercanvi d'àudios i textos (I/O)
        ├── Models/        # Models d'IA pesats (persistents)
        │   ├── piper/     # Models .onnx i .json de Piper
        │   └── vosk/      # Carpetes de models descomprimits de Vosk
        ├── STT/           # Scripts Python i configuració per a Transcripció
        │   ├── config_stt.json
        │   └── transcriure.py
        └── TTS/           # Scripts Python i configuració per a Síntesi
            ├── config_tts.json
            └── sintetitzar.py

```

---

## ⚙️ Requisits Previs

* **Podman** (o Docker) amb **podman-compose** / **docker-compose**.
* El socket de Podman actiu (si s'utilitza emulació de Docker API):
```bash
systemctl --user enable --now podman.socket

```



---

## 📥 Preparació Previa: Descàrrega de Models (Fase en Línia)

Aquesta és **l'única fase que requereix connexió a Internet**. Cal descarregar els models i ubicar-los a la carpeta de volums corresponent abans d'iniciar els serveis en aïllament.

### 1. Models de Transcripció VOSK (STT)

Descarrega i descomprimeix els fitxers a `Implamantacio/Volums/Models/vosk/`:

| Idioma | Model | Enllaç / Comanda de descàrrega |
| --- | --- | --- |
| **Català (CA)** | `vosk-model-small-ca-0.4` | [Descargar Zip](https://www.google.com/search?q=https://alphacephei.com/vosk/models/vosk-model-small-ca-0.4.zip) |
| **Castellà (ES)** | `vosk-model-small-es-0.42` | [Descargar Zip](https://www.google.com/search?q=https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip) |
| **Anglès (EN)** | `vosk-model-en-us-0.22` | [Descargar Zip](https://www.google.com/search?q=https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip) |

### 2. Models de Síntesi Piper (TTS)

Descarrega els parells de fitxers (`.onnx` i `.onnx.json`) i desa'ls a `Implamantacio/Volums/Models/piper/`:

* **Català (`ca`):** `ca_ES-upc_ona-medium.onnx` + `.json`
* **Castellà (`es`):** `es_ES-davefx-medium.onnx` + `.json`
* **Anglès (`en`):** `en_US-amy-medium.onnx` + `.json`

*(Trobaràs les URLs de descàrrega directa al fitxer `descarges.txt`).*

---

## 🛠️ Instal·lació i Desplegament

1. Situa't a la carpeta del projecte:
```bash
cd Implamantacio

```


2. Construeix i arrenca els contenidors en segon pla:
```bash
podman compose up --build -d

```


3. Comprova que els dos contenidors estan actius:
```bash
podman ps

```



---

## 💻 Guia d'Ús

Tots els fitxers d'àudio o text que vulguis processar o generar han de passar per la carpeta **`Implamantacio/Volums/data_io/`**.

### 1. Síntesi de Veu (Text-to-Speech - TTS)

Pots generar àudio directament des d'un text introduït per línia de comandes o des d'un fitxer `.txt`.

* **Generar àudio des d'un text directament (ex: Català):**
```bash
podman exec -it TEXT-TO-SPEECH python sintetitzar.py --text "Hola, aquest és un text de prova sintetitzat en català." --lang ca --output prova_ca.wav

```


* **Generar àudio des d'un fitxer de text (`/data_io/input.txt`):**
```bash
podman exec -it TEXT-TO-SPEECH python sintetitzar.py --text_file input.txt --lang es --output prova_es.wav

```



*El fitxer `.wav` resultant estarà disponible a `Implamantacio/Volums/data_io/`.*

---

### 2. Transcripció d'Àudio (Speech-to-Text - STT)

Col·loca el teu fitxer d'àudio (`.wav`, `.mp3`, `.m4a`, etc.) a la carpeta `Implamantacio/Volums/data_io/`.

* **Transcriure un fitxer d'àudio (ex: Català):**
```bash
podman exec -it SPEECH-TO-TEXT python transcriure.py --input el_teu_audio.wav --lang ca --output transcripcio.txt

```


* **Transcriure en altres idiomes (ex: Anglès o Castellà):**
```bash
podman exec -it SPEECH-TO-TEXT python transcriure.py --input audio_en.mp3 --lang en --output transcripcio_en.txt

```



*El fitxer de text resultant es guardarà automàticament a `Implamantacio/Volums/data_io/`.*

---

## ⚙️ Configuració Avançada

Si vols canviar els models per defecte o afegir noves veus/idiomes, pots modificar els fitxers JSON de configuració ubicats a:

* `Implamantacio/Volums/TTS/config_tts.json` (per a Piper)
* `Implamantacio/Volums/STT/config_stt.json` (per a VOSK)



---

### Quines alternatives existeixen i quan val la pena el canvi?

#### 1. Per al reconeixement de veu (STT)

* **L'alternativa principal:** **Faster-Whisper** (o `whisper.cpp`).
* **Per què valorar-ho?** La precisió de Whisper és molt superior a la de Vosk. Entén millor els accents, el vocabulari complex, les frases fetes i no es confon tant si hi ha soroll de fons.
* **El cost:** Consumeix bastant més memòria RAM i CPU. Si no tens una targeta gràfica (GPU) dedicada, la transcripció pot trigar uns segons en lloc de ser immediata com en Vosk.
* **Verdict:** Canvia a Whisper si Vosk falla massa sovint entenent el que dius. Si Vosk t'entén bé, mantén-lo per la seva velocitat.

#### 2. Per a la síntesi de veu (TTS)

* **Alternatives principals:** **Kokoro-82M** o **XTTS-v2** (Coqui).
* **Per què valorar-ho?**
* **Kokoro-82M:** És un model recent, extraordinàriament lleuger i amb una naturalitat d'àudio que supera Piper sense requerir molta potència.
* **XTTS-v2:** Permet la **clonació de veu** (generar àudio amb la teva pròpia veu o la de qualsevol persona a partir d'una mostra de 6 segons).


* **El cost:** XTTS requereix obligatòriament una GPU dedicada per generar àudio en temps real. Kokoro és més assequible però té menys varietat de veus en català.
* **Verdict:** Mantén Piper si busques que l'àudio es generi a l'instant en qualsevol ordinador. Explora Kokoro o XTTS si necessites una veu hiperrealista o clonada.

