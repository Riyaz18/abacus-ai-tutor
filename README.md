**Developed by:** Mohamed Riyaz Khan – [nmohamedriyazkhan@gmail.com](mailto:nmohamedriyazkhan@gmail.com)  
**Submitted to:** Jameel Abdul Ahamed – [jameel.abdul@ee-consultant.com](mailto:jameel.abdul@ee-consultant.com)
# abacus-ai-tutor
A specialized AI-powered educational tool for mastering mental arithmetic. Features local LLM integration (Llama 3), real-time voice transcription (Whisper), and an interactive Canvas-based Soroban abacus.
# Abacus Tutor: AI Virtual Assistant for Mental Arithmetic

**Abacus Tutor** is a state-of-the-art educational tool that combines local AI models with an interactive simulation. It allows students to speak math problems and receive step-by-step bead movement instructions on a virtual Soroban abacus.

---

## 🌟 Key Features
- **Deterministic Math Logic:** Uses a custom Python engine to ensure 100% mathematical accuracy before passing data to the AI.
- **Privacy-First & Local:** All processing (Speech-to-Text and LLM) happens locally on the host machine.
- **Interactive Soroban Kit:** A functional Canvas-based abacus that visualizes solutions in real-time.
- **Robust NLP:** Specialized normalization layers to handle common phonetic mistakes in voice-to-math conversion (e.g., "slice" -> "plus").

---

## 🛠️ Technical Stack
* **Backend:** Python (FastAPI)
* **AI Models:**
    * **Llama 3 (via Ollama):** For pedagogical natural language generation.
    * **OpenAI Whisper (Base):** For state-of-the-art local speech-to-text.
* **Frontend:** HTML5, CSS3 (Tailwind-inspired UI with Dark Mode), JavaScript (Canvas API).
* **Audio Processing:** SpeechRecognition, PyAudio, FFmpeg.

---

## 🚀 How to Run (Detailed Setup)

To ensure the application runs successfully, please follow these steps in order:

### 1. System Dependencies
The project requires **FFmpeg** for audio processing and **Ollama** to run the local LLM.

* **Install FFmpeg:**
    * **Windows:** Run `choco install ffmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder to your System PATH.
    * **Mac:** `brew install ffmpeg`
    * **Linux:** `sudo apt update && sudo apt install ffmpeg`
* **Install Ollama:**
    1.  Download from [ollama.com](https://ollama.com).
    2.  Open your terminal and run: `ollama pull llama3`
    3.  **Important:** Ensure the Ollama application is running in your system tray.

### 2. Python Environment Setup
1.  Navigate to the project root directory in your terminal.
2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```
3.  **Activate the Environment:**
    * **Windows:** `.\venv\Scripts\activate`
    * **Mac/Linux:** `source venv/bin/activate`
4.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Launching the App
Run the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
Once the server starts, open your browser and navigate to:
```bash
http://127.0.0.1:8000/ui
```

## 🏗️ System Architecture

1. **Audio Capture**  
   `voice_engine.py` records audio via the microphone into a temporary `.wav` file.

2. **Transcription**  
   Whisper transcribes the audio. If no speech is detected, it returns a friendly error.

3. **Normalization**  
   `ai_logic.py` converts word‑based numbers (e.g., "twelve") into integers and cleans math operators.

4. **Logic Engine**  
   The system calculates the result and generates **"Abacus Steps"** (e.g., *"Add 5 to ones rod, carry 1 to tens rod"*).

5. **AI Explanation**  
   Llama 3 transforms the raw logic steps into a student‑friendly verbal guide.

6. **Visual Sync**  
   The UI shifts the virtual beads automatically to represent the final answer.

---

## 👨‍🏫 Developer Notes

- **Zero Hallucination** – By calculating the math in Python rather than letting the LLM "guess" the answer, we ensure the tutor is always right.  
- **UX Design** – The interface includes a full **"Interactive Abacus Kit"** allowing students to manually manipulate digits using `+` and `-` controls.
