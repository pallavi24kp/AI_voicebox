# 🎙️ AI VoiceBot — End-to-End Intelligent Voice Assistant

An end-to-end AI VoiceBot with a **professional web frontend**, powered by Whisper ASR, DistilBERT intent classification, and gTTS speech synthesis. The full pipeline converts audio → text → intent → response → audio in under 3–5 seconds.

---

## ✨ Features

- 🎙️ **Live microphone recording** with animated waveform visualizer
- 🧠 **Automatic Speech Recognition** using `faster-whisper` (Whisper small)
- 🎯 **Intent Classification** using a fine-tuned DistilBERT model
- 💬 **Contextual Response Generation** from a centralized template engine
- 🔊 **Text-to-Speech** output using gTTS, played back in the browser
- ⌨️ **Text input mode** as a fallback — type a query without a mic
- 📊 **Pipeline step visualizer** (ASR → NLP → Response → TTS)
- 🌐 **Self-hosted frontend** served directly by FastAPI

---

## 🗂️ Project Structure

```
AI_voicebot/
├── app/
│   ├── asr/
│   │   └── transcriber.py          # Whisper ASR
│   ├── nlp/
│   │   └── intent_predictor.py     # DistilBERT intent classification
│   ├── responses/
│   │   ├── response_generator.py   # Response dispatcher
│   │   └── response_templates.py   # Centralized response templates
│   └── tts/
│       └── synthesizer.py          # gTTS text-to-speech
├── data/                           # Runtime-generated audio files (gitignored)
├── evaluation/
│   └── confusion_matrix.png        # Model evaluation output
├── frontend/
│   ├── index.html                  # SPA shell
│   ├── style.css                   # Premium dark-mode UI
│   └── app.js                      # Recording, API calls, UI logic
├── models/                         # Trained DistilBERT model + label mapping
├── scripts/
│   ├── generate_dataset.py         # One-time dataset generator
│   └── train_intent_model.py       # One-time model trainer
├── main.py                         # FastAPI app entry point
├── requirements.txt
└── .gitignore
```

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone <repo_url>
cd AI_voicebot
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Open the frontend
Navigate to **http://localhost:8000** in your browser.

> The FastAPI server serves both the REST API and the web frontend from the same process — no separate frontend server needed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check |
| `POST` | `/voicebot` | **Full pipeline** — audio file → JSON (transcription + intent + response + audio URL) |
| `POST` | `/transcribe` | Audio file → transcribed text |
| `POST` | `/predict-intent` | Text → `{ intent, confidence }` |
| `POST` | `/generate-response` | Intent + text → response text |
| `POST` | `/synthesize` | Text → MP3 audio file |
| `GET`  | `/data/{filename}` | Serve generated audio files |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## 🎯 Supported Intents

| Intent | Example |
|--------|---------|
| `order_status` | "Where is my order?" |
| `cancel_order` | "I want to cancel my order" |
| `refund_request` | "I need a refund" |
| `payment_problem` | "My card was declined" |
| `delivery_delay` | "My delivery is delayed" |
| `account_update` | "Update my email address" |
| `complaint` | "I want to file a complaint" |
| `product_info` | "Tell me about this product" |
| `technical_support` | "App is not working" |
| `subscription_issue` | "Cancel my subscription" |

---

## 🏗️ Pipeline Architecture

```
User Audio
    │
    ▼
┌─────────────────┐
│   ASR (Whisper) │  → transcribed text
└─────────────────┘
    │
    ▼
┌──────────────────────┐
│  NLP (DistilBERT)    │  → intent + confidence
└──────────────────────┘
    │
    ▼
┌────────────────────────┐
│  Response Engine       │  → response text
│  (Template-based)      │
└────────────────────────┘
    │
    ▼
┌─────────────────┐
│   TTS (gTTS)    │  → MP3 audio file
└─────────────────┘
    │
    ▼
Browser Audio Playback
```

---

## 📊 Model Evaluation

Intent classifier evaluated on held-out test data:

- **Accuracy**, **Precision**, **Recall**, **F1 Score**
- Confusion matrix available at `evaluation/confusion_matrix.png`

---

## 🔮 Future Improvements

- Streaming audio support (WebSocket)
- Multi-language ASR and TTS
- Generative response engine (LLM-based)
- Docker containerization
- Cloud deployment (GCP / AWS)
