
# 🌱 GrowTalk.ai – WhatsApp-Based English Learning Assistant

GrowTalk.ai is a conversational AI English tutor that interacts with students via WhatsApp. It teaches vocabulary and reading comprehension using dialogic education principles, scaffolded hints, memory strategies, and warm Cantonese-English explanations.

---

## ✨ Features

- 💬 WhatsApp-based interactive learning
- 📘 Vocabulary training (hint → guess → explanation)
- 📖 Reading comprehension (closed + open questions)
- 🧠 LLM integration (Gemma via OpenRouter)
- 📊 Progress tracking via Google Sheets
- 🌈 Natural Cantonese dialogue with personalized feedback

---

## 🚀 Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/alan369963/growtalk_test1.git
cd growtalk_test1
```

---

## 🐍 Python (FastAPI + LLM server)

### Setup
```bash
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install -r requirements.txt
```

### Start FastAPI server
```bash
uvicorn whatsapp_webhook:app --reload --port 8000
```

---

## 💬 Node.js (WhatsApp Bot via `whatsapp-web.js`)

### Setup
```bash
cd whatsapp-bot
npm install
```

### Run the bot and scan QR code
```bash
node index.js
```

> Open WhatsApp > Settings > Linked Devices > Scan the QR in terminal.

---

## 🔐 Google Sheets Setup

1. Create a Google Cloud Project
2. Create a **Service Account** and download `creds.json`
3. Share your Google Sheets with the bot’s email  
   e.g. `my-bot@my-project.iam.gserviceaccount.com`
4. Put `creds.json` in your project root (same folder as `sheet_utils.py`)

---

## 🧾 Folder Structure

```
GrowTalk.ai/
├── whatsapp_webhook.py          # Main FastAPI webhook
├── sheet_utils.py               # Google Sheet functions
├── llm_utils.py                 # LLM prompt/response logic
├── vocab_session_controller.py  # Vocabulary training logic
├── reading_session_controller.py# Reading (closed questions)
├── open_reading_session_controller.py # Open-ended question logic
├── whatsapp_utils.py            # Python → WhatsApp message sending
├── whatsapp-bot/                # Node.js bot: QR login + message relay
├── requirements.txt             # Python dependencies
└── .gitignore                   # Make sure creds.json is ignored!
```

---

## 🔁 Typical Conversation Flow

1. Student sends `start` → receives greeting
2. Student types `vocab`, `reading`, or `warm up`
3. Bot teaches using:
   - 🤖 LLM prompts
   - 🎯 Google Sheet learning data
   - ✅ WhatsApp replies
4. Progress is saved automatically

---

## 🔥 To-Do / Future Improvements

- [ ] Deploy to cloud (Render / Railway / Replit)
- [ ] Add Redis-based chat memory
- [ ] Add summary reporting for teachers
- [ ] Support multi-language UI

---

## 🧠 Credits

Built by [@alan369963](https://github.com/alan369963)  
Powered by OpenRouter, Google Sheets, and the WhatsApp Web API.

---

> 「GrowTalk」唔止教英文，仲想陪你一齊思考、一齊進步 🧡
