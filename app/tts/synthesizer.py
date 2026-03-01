from gtts import gTTS
import os
import uuid

def text_to_speech(text: str):
    
    filename = f"response_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("data", filename)

    tts = gTTS(text=text, lang="en")
    tts.save(filepath)

    return filepath