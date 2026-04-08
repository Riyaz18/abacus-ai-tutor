from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from ai_logic import get_abacus_explanation
from voice_engine import listen_to_student

app = FastAPI(
    title="Abacus Guru - AI Tutor",
    description="Voice + Text Abacus Tutor with step-by-step explanations",
    version="1.0"
)

# Serve static files if needed later
#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui", response_class=HTMLResponse)
def serve_ui():
    if not os.path.exists("index.html"):
        return HTMLResponse("<h1 style='color:red'>index.html not found. Create it first.</h1>", status_code=404)
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/")
def home():
    return {"message": "Abacus Guru API is running", "ui": "/ui"}


@app.get("/ask")
def ask_abacus(problem: str = Query(..., description="e.g. 25 plus 8 or twenty five minus eight")):
    try:
        result = get_abacus_explanation(problem)
        return JSONResponse(content=result)
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/voice-ask")
def voice_ask():
    try:
        spoken_text = listen_to_student()
        
        if spoken_text.startswith("No speech") or spoken_text.startswith("Voice error"):
            return {"error": spoken_text}
        
        result = get_abacus_explanation(spoken_text)
        return {
            "spoken_input": spoken_text,
            "solution": result
        }
    except Exception as e:
        return {"error": str(e)}