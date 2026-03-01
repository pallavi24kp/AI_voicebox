from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

from app.asr.transcriber import transcribe_audio
from app.nlp.intent_predictor import predict_intent
from app.responses.response_generator import generate_response
from app.tts.synthesizer import text_to_speech

app = FastAPI(title="AI Voice Bot API")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)


# -------------------------------------------------
# 1️⃣ Transcribe Endpoint
# -------------------------------------------------
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):

    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = transcribe_audio(file_path)

    return {"transcription": text}


# -------------------------------------------------
# 2️⃣ Predict Intent
# -------------------------------------------------
@app.post("/predict-intent")
async def predict(text: str):

    result = predict_intent(text)

    return result


# -------------------------------------------------
# 3️⃣ Generate Response
# -------------------------------------------------
@app.post("/generate-response")
async def generate(intent: str, text: str):

    response = generate_response(intent, text)

    return {"response": response}


# -------------------------------------------------
# 4️⃣ Text-to-Speech
# -------------------------------------------------
@app.post("/synthesize")
async def synthesize(text: str):

    audio_path = text_to_speech(text)

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="response.mp3"
    )


# -------------------------------------------------
# 5️⃣ Full Voicebot (Audio → Audio)
# -------------------------------------------------
@app.post("/voicebot")
async def voicebot(file: UploadFile = File(...)):

    # Save uploaded file
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

    # Return audio file
    return FileResponse(
        response_audio,
        media_type="audio/mpeg",
        filename="voicebot_response.mp3"
    )