# Olive — Youth Mental-Wellbeing Support App (featuring Liv)

A free, privacy-first, non-clinical AI mental-wellbeing support application designed especially for teenagers and young people who may hesitate to talk about their problems because they fear being judged, dismissed, or misunderstood.

---

## 🌟 Core Behavioral Role & Boundaries

- **Not a Clinic or Therapist**: The AI is strictly a conversational support medium to help users feel heard, reflect on emotions, and receive gentle healthy suggestions.
- **Never Diagnoses**: Strictly refuses diagnostic queries (e.g. *"Do I have depression/bipolar?"*) and redirects with empathy and non-clinical support.
- **Human Connection First**: Designed to encourage reaching out to trusted people and professionals, not replace them.
- **Crisis Safety Interceptor**: Detects crisis or self-harm keywords and provides immediate one-tap access to **988**, **Crisis Text Line (741741)**, and **Teen Line**.

---

## 🎧 The 4 Conversation Modes

1. 🎧 **Just Listen**: Validates feelings without rushing into unsolicited advice or problem-solving.
2. 💡 **Give Me Advice**: Offers gentle, realistic, and practical coping techniques (grounding, breathing, routines).
3. 🔍 **Help Me Understand**: Explores and unpacks thoughts and emotions without psychological labels.
4. 💌 **Help Me Tell Someone**: Drafts natural, stress-free messages and conversation starters for parents, school counselors, teachers, friends, or trusted adults.

---

## 🛠️ Tech Stack

- **Frontend**: Flutter (Dart 3) cross-platform client in `frontend/` + Zero-setup web demonstration client in `backend/app/static/`.
- **Backend**: Python 3.10+ with FastAPI (Asynchronous REST API).
- **Database**: SQLite with SQLAlchemy & aiosqlite for zero-cost, local storage.
- **AI Layer**: Built-in zero-cost local empathetic engine + modular plug-in support for local Ollama LLMs (Llama 3, Gemma, Mistral).
- **Privacy & Authentication**: Local device PIN / Biometric gate protecting conversation history.

---

## 🚀 How to Run

### Option 1: One-Command Instant Launch (Web & Backend Demo)

1. Open your terminal and navigate to the project directory:
   ```bash
   cd ~/.gemini/antigravity-ide/scratch/ai_wellbeing_app
   ```

2. Run the start script:
   ```bash
   ./run.sh
   ```
   Or run the Python server directly:
   ```bash
   cd backend
   arch -x86_64 python3 run_backend.py # On Apple Silicon, or simply: python3 run_backend.py
   ```

3. Open your browser to:
   - **Interactive Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Option 2: Run Flutter App (Mobile / Desktop)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Get dependencies:
   ```bash
   flutter pub get
   ```

3. Run on your connected device, simulator, or desktop:
   ```bash
   flutter run
   ```

---

## 🧪 Running Automated Tests

Run the test suite to verify all endpoints, 4 conversation modes, safety screening, mood logs, and PIN security:

```bash
cd backend
arch -x86_64 python3 -m pytest tests/
```
