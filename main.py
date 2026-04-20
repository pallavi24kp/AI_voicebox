from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from app.asr.transcriber import transcribe_audio
from app.nlp.intent_predictor import predict_intent
from app.responses.response_generator import generate_response
from app.tts.synthesizer import text_to_speech

app = FastAPI(title="AI Voice Bot API", version="1.0.0")

# ---- CORS (needed for browser frontend) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "message": "AI VoiceBot API is running"}


# ------------------------------------------------------------------
# 1️⃣  Transcribe Endpoint
# ------------------------------------------------------------------
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = transcribe_audio(file_path)
    return {"transcription": text}


# ------------------------------------------------------------------
# 2️⃣  Predict Intent
# ------------------------------------------------------------------
@app.post("/predict-intent")
async def predict(text: str = Form(...)):
    result = predict_intent(text)
    return result


# ------------------------------------------------------------------
# 3️⃣  Generate Response
# ------------------------------------------------------------------
@app.post("/generate-response")
async def generate(intent: str = Form(...), text: str = Form(...)):
    response = generate_response(intent, text)
    return {"response": response}


# ------------------------------------------------------------------
# 4️⃣  Text-to-Speech
# ------------------------------------------------------------------
@app.post("/synthesize")
async def synthesize(text: str = Form(...)):
    audio_path = text_to_speech(text)
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="response.mp3"
    )


# ------------------------------------------------------------------
# 5️⃣  Full Voicebot (Audio → Audio)
# ------------------------------------------------------------------
@app.post("/voicebot")
async def voicebot(file: UploadFile = File(...)):
    # Save uploaded audio
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 1: ASR
    transcription = transcribe_audio(file_path)

    # Step 2: Intent Classification
    intent_result = predict_intent(transcription)

    # Step 3: Response Generation
    response_text = generate_response(
        intent_result["intent"],
        transcription
    )

    # Step 4: TTS
    response_audio = text_to_speech(response_text)

    # Return rich JSON for the frontend, plus a separate audio endpoint
    return JSONResponse({
        "transcription": transcription,
        "intent": intent_result["intent"],
        "confidence": intent_result["confidence"],
        "response": response_text,
        "audio_url": f"/{response_audio}"
    })


# ------------------------------------------------------------------
# 6️⃣  Serve generated audio files
# ------------------------------------------------------------------
@app.get("/data/{filename}")
async def serve_audio(filename: str):
    path = f"data/{filename}"
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, media_type="audio/mpeg")


# ------------------------------------------------------------------
# Static Frontend (must come LAST so API routes take priority)
# ------------------------------------------------------------------
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")