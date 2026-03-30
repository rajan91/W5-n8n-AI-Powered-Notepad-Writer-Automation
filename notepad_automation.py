from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import pyautogui
import psutil
import os
import time

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
# PyAutoGUI config
# ─────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0.4

# Base folder where all text files will be saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def open_and_close_notepad(file_path: str):
    """Open the saved file in Notepad, then close the tab."""
    subprocess.Popen(["notepad.exe", file_path])
    time.sleep(3)

    # Bring Notepad into focus
    try:
        import pygetwindow as gw
        wins = gw.getWindowsWithTitle("Notepad")
        if wins:
            wins[0].activate()
            time.sleep(0.8)
    except ImportError:
        pyautogui.hotkey("alt", "tab")
        time.sleep(0.8)

    # Close only the current tab (Ctrl+W) — no save dialog because
    # the file was already written by Python
    pyautogui.hotkey("ctrl", "w")
    time.sleep(1.5)

    # Only dismiss a save dialog if one actually appears
    try:
        import pygetwindow as gw
        dialog_wins = [
            w for w in gw.getAllWindows()
            if "notepad" in w.title.lower() and w.width < 500
        ]
        if dialog_wins:
            pyautogui.press("tab")
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(0.5)
    except ImportError:
        pass


# ─────────────────────────────────────────────────────────────
# POST /write
# Body: { "file_name": "myfile", "value": "hello world" }
# ─────────────────────────────────────────────────────────────
@app.route("/write", methods=["POST"])
def write_to_file():
    data = request.get_json(force=True)

    # file_name = data.get("file_name", "").strip()
    file_name = "myfile"
    value     = data.get("value", "").strip()

    # ── Validation ──
    if not file_name:
        return jsonify({"success": False, "error": "file_name is required"}), 400
    if not value:
        return jsonify({"success": False, "error": "value is required"}), 400

    # Sanitise: ensure .txt extension
    if not file_name.endswith(".txt"):
        file_name += ".txt"

    file_path   = os.path.join(BASE_DIR, file_name)
    file_exists = os.path.exists(file_path)

    # ── Build content ──
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            existing = f.read()
        new_content = existing.rstrip("\n") + "\n" + value
        action = "appended"
    else:
        new_content = value
        action = "created"

    # ── Write file directly (reliable, no Save-dialog risk) ──
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # ── Open in Notepad then close the tab ──
    open_and_close_notepad(file_path)

    # ── Read back final contents ──
    with open(file_path, "r", encoding="utf-8") as f:
        final_contents = f.read()

    return jsonify({
        "success":   True,
        "action":    action,
        "file_name": file_name,
        "file_path": file_path,
        "contents":  final_contents
    }), 200


# ─────────────────────────────────────────────────────────────
# GET /read/<file_name>
# Returns the current contents of a file
# ─────────────────────────────────────────────────────────────
@app.route("/read/<file_name>", methods=["GET"])
def read_file(file_name):
    if not file_name.endswith(".txt"):
        file_name += ".txt"

    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": f"'{file_name}' not found"}), 404

    with open(file_path, "r", encoding="utf-8") as f:
        contents = f.read()

    lines = [line for line in contents.splitlines() if line.strip()]

    return jsonify({
        "success":   True,
        "file_name": file_name,
        "file_path": file_path,
        "lines":     lines,
        "contents":  contents
    }), 200


# ─────────────────────────────────────────────────────────────
# GET /files
# Lists all .txt files in the base directory
# ─────────────────────────────────────────────────────────────
@app.route("/files", methods=["GET"])
def list_files():
    txt_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".txt")]
    return jsonify({
        "success": True,
        "files":   txt_files
    }), 200


# ─────────────────────────────────────────────────────────────
# DELETE /delete/<file_name>
# Deletes a text file
# ─────────────────────────────────────────────────────────────
@app.route("/delete/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    if not file_name.endswith(".txt"):
        file_name += ".txt"

    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": f"'{file_name}' not found"}), 404

    os.remove(file_path)
    return jsonify({
        "success":   True,
        "message":   f"'{file_name}' deleted successfully."
    }), 200


# ─────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Notepad Writer Flask API")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)