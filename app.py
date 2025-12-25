import os
import time
import uuid
import random
import threading
from json import dumps, loads
from gzip import decompress
from ssl import CERT_NONE
from flask import Flask, render_template_string, jsonify

try:
    from websocket import create_connection
except ImportError:
    os.system('pip install websocket-client')
    from websocket import create_connection

app = Flask(__name__)

# Global Counters
stats = {
    "success": 0,
    "failed": 0,
    "retry": 0,
    "accounts": []
}

# --- HTML UI (Modern Dark Theme) ---
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>Waleed Safeum v2</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #000; font-family: 'Courier New', monospace; color: #00ff00; }
        .terminal-box { border: 2px solid #00ff00; box-shadow: 0 0 20px #003300; }
        .log-stream { height: 300px; overflow-y: auto; background: rgba(0,0,0,0.8); }
        .success-text { color: #00ff00; font-weight: bold; }
    </style>
</head>
<body class="p-4 flex flex-col items-center">
    <div class="terminal-box w-full max-w-2xl p-6 rounded-lg bg-black">
        <h1 class="text-3xl text-center font-bold mb-4 text-white uppercase tracking-widest">Waleed Safeum Maker</h1>
        
        <div class="grid grid-cols-3 gap-4 mb-6 border-b border-green-900 pb-4">
            <div class="text-center">
                <p class="text-xs uppercase">Success</p>
                <p id="success" class="text-2xl font-bold text-green-400">0</p>
            </div>
            <div class="text-center">
                <p class="text-xs uppercase text-red-500">Failed</p>
                <p id="failed" class="text-2xl font-bold text-red-500">0</p>
            </div>
            <div class="text-center">
                <p class="text-xs uppercase text-yellow-500">Retry</p>
                <p id="retry" class="text-2xl font-bold text-yellow-500">0</p>
            </div>
        </div>

        <div id="log-container" class="log-stream p-3 text-xs mb-4 rounded border border-green-800 custom-scroll">
            <p class="text-gray-500 italic">>> Click Start to begin account generation...</p>
        </div>

        <button id="actionBtn" onclick="toggleStart()" class="w-full bg-green-500 hover:bg-green-600 text-black font-black py-4 rounded transition-all uppercase">
            Start Generating
        </button>
    </div>

    <script>
        let isRunning = false;
        function toggleStart() {
            if(!isRunning) {
                isRunning = true;
                document.getElementById('actionBtn').innerText = "Running... (Stop)";
                document.getElementById('actionBtn').classList.replace('bg-green-500', 'bg-red-600');
                updateUI();
            } else {
                location.reload(); // Simple way to stop background processes
            }
        }

        async function updateUI() {
            if(!isRunning) return;
            const res = await fetch('/status');
            const data = await res.json();
            
            document.getElementById('success').innerText = data.success;
            document.getElementById('failed').innerText = data.failed;
            document.getElementById('retry').innerText = data.retry;
            
            const logBox = document.getElementById('log-container');
            if(data.accounts.length > 0) {
                let lastAcc = data.accounts[data.accounts.length - 1];
                logBox.innerHTML = `<div><span class="text-green-400">[NEW]</span> ${lastAcc}:mmmm | Created Successfully!</div>` + logBox.innerHTML;
            }
            setTimeout(updateUI, 2000);
        }
    </script>
</body>
</html>
"""

# --- Background Worker Logic ---

def create_safeum_account():
    global stats
    while True:
        # Username generation
        username = 'waleed' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=8))
        
        try:
            # Note: 195.13.182.217 SafeUm ka server IP hai. 
            # Browser security certificate bypass karne ke liye SSL CERT_NONE zaroori hai.
            ws = create_connection("wss://195.13.182.217/Auth", 
                                  header={"app": "com.safeum.android"}, 
                                  sslopt={"cert_reqs": CERT_NONE}, 
                                  timeout=15)
            
            # Ye registration payload update kiya gaya hai
            payload = {
                "action": "Register",
                "subaction": "Desktop",
                "locale": "en_GB",
                "gmt": "+05",
                "login": username,
                "password": {
                    "m1x": "1a07f431a68b4fb69a5c96349137476cca613f019b1016e63a27e022ef09805c",
                    "m1y": "ba83a1300f777ada673afb9bc4d507da3000ea2fabaaa35a6616a0af666a4bb7",
                    "m2": "43c58959c91b494e05a47cad7bca5b5f52e5204d393e06829c34884fa807954b",
                    "iv": "140c409aba2f6c7050518a826e6f2810",
                    "message": "5080dc99f8e226891ee1f4b52a480e1d0278ff1c211e5107a5de2ceb6a646d40"
                },
                "devicename": "Samsung SM-G960F",
                "os": "AND",
                "softwareversion": "1.1.0.1384"
            }
            
            ws.send(dumps(payload))
            raw_data = ws.recv()
            response = decompress(raw_data).decode('utf-8')
            
            if '"status":"Success"' in response:
                stats["success"] += 1
                stats["accounts"].append(username)
            else:
                stats["failed"] += 1
            
            ws.close()
        except Exception as e:
            stats["retry"] += 1
        
        time.sleep(2) # Flood control ke liye gap zaroori hai

# --- Routes ---

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/status')
def get_status():
    return jsonify(stats)

# Start background thread
threading.Thread(target=create_safeum_account, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
