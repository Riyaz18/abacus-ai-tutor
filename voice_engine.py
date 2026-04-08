import whisper
import speech_recognition as sr
import tempfile
import os

# Load once at startup
model = whisper.load_model("base")   # Change to "small" if you have more RAM/GPU

def listen_to_student():
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... Speak your abacus problem now.")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=8)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            temp_path = tmp.name

        result = model.transcribe(temp_path, language="en", fp16=False)
        os.unlink(temp_path)

        text = result["text"].strip()
        return text if text else "No speech detected"

    except sr.WaitTimeoutError:
        return "No speech detected. Please try again."
    except Exception as e:
        return f"Voice error: {str(e)}"