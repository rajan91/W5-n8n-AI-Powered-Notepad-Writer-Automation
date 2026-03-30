# 🤖 N8N AI-Powered Notepad Writer Automation

> A fully automated pipeline that reads structured data, transforms it using an AI model via **OpenRouter**, and appends the result into a Windows Notepad file — every minute, hands-free.

---

## 🧠 What It Does

Every **60 seconds**, this n8n workflow:

1. Reads field values from an n8n **Set** node
2. Sends them to an **AI model** (via OpenRouter) with a custom formatting prompt
3. POSTs the AI-formatted result to a local **Flask API** (exposed via **ngrok**)
4. The Flask API writes the value to a **.txt file** using Python
5. **PyAutoGUI** opens the file in **Notepad**, then closes it automatically
6. If the file already exists — new values are **appended as new lines** (no data is overwritten)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Automation | [n8n](https://n8n.io) |
| AI Model | [OpenRouter](https://openrouter.ai) |
| API | Python + Flask |
| UI Automation | PyAutoGUI + pygetwindow |
| Tunnel | ngrok |
| OS | Windows (Notepad) |

---

## 📁 Project Structure

```
├── app.py              # Flask API (write / read / list / delete)
├── requirements.txt    # Python dependencies
├── index.html          # Optional browser UI to test the API
└── README.md           # This file
```

---

## 🚀 Quick Start

### 1. Install Python dependencies
```bash
pip install flask flask-cors pyautogui pygetwindow psutil
```

### 2. Start Flask API
```bash
python app.py
# Running at http://127.0.0.1:5000
```

### 3. Expose with ngrok
```bash
ngrok http 5000
# Copy the HTTPS URL → use in n8n HTTP Request node
```

### 4. Import cURL into n8n
```bash
curl -X POST https://YOUR-NGROK-URL/write \
  -H "Content-Type: application/json" \
  -d '{"file_name": "output", "value": "your AI-formatted value"}'
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/write` | Write or append a value to a .txt file |
| `GET` | `/read/<file_name>` | Read all lines from a file |
| `GET` | `/files` | List all .txt files |
| `DELETE` | `/delete/<file_name>` | Delete a file |

---

## ⚙️ n8n Workflow Nodes

```
[Cron — every 1 min]
       ↓
[Set Node — field values]
       ↓
[HTTP Request — OpenRouter AI]
       ↓
[HTTP Request — Flask /write]
       ↓
[Notepad opens & closes via PyAutoGUI]
```

---

## 📝 File Append Behaviour

- **New file** → created fresh with the value as line 1
- **Existing file** → new value appended as a new line (previous data preserved)
- File is written by Python directly — no Notepad Save dialog is triggered

---

## 🔐 Environment Variables

Create a `.env` file (never commit this):
```
OPENROUTER_API_KEY=your_key_here
NGROK_AUTH_TOKEN=your_token_here
```

Add to `.gitignore`:
```
.env
*.txt
__pycache__/
```

---

## 🐛 Common Issues

| Issue | Fix |
|---|---|
| Notepad doesn't open | Must run on Windows |
| `n` appears in file | Update to latest `app.py` (blind keypress removed) |
| ngrok URL changed | Restart ngrok, update n8n HTTP node URL |
| Flask port busy | Run `netstat -ano | findstr :5000` |

---

## 📄 License

MIT License — free to use and modify.

---

> Built with n8n · Flask · PyAutoGUI · OpenRouter · ngrok
