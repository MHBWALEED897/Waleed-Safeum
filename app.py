from flask import Flask, render_template_string, jsonify
import threading
import uuid
import time
from websocket import create_connection
from ssl import CERT_NONE
from json import dumps, loads
from gzip import decompress
import random

app = Flask(__name__)

# Global stats
stats = {"success": 0, "failed": 0, "retry": 0, "accounts": []}

# --- HTML TEMPLATE (Frontend) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Waleed Safeum - Flash Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #050505; color: #00ff00; font-family: 'Courier New', Courier, monospace; }
        .terminal { border: 2px solid #00ff00; box-shadow: 0 0 20px #004400; background: black; }
        .scanline { background: linear-gradient(to bottom, rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06)); background-size: 100% 2px, 3px 100%; pointer-events: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; }
    </style>
</head>
<body class="p-5">
    <div class="scanline"></div>
    <div class="max-w-3xl mx-auto terminal p-6 rounded-lg relative z-20">
        <h1 class="text-3xl font-bold text-center mb-4 text-white">WALEED SAFEUM MAKER</h1>
        <div class="grid grid-cols-2 gap-4 text-sm mb-6 border-b border-green-800 pb-4">
            <p>NAME: <span class="text-yellow-400">WALEED-SAFEUM</span></p>
            <p>STATUS: <span class="text-green-400">ACTIVE (FLASH)</span></p>
            <p>CREATOR: <span class="text-cyan-400">@SAMEER-XD</span></p>
            <p>API: <span class="text-red-400">SAFEUM CLOUD</span></p>
        </div>

        <div class="flex justify-around mb-8 bg-zinc-900 p-4 rounded border border-green-900">
            <div class="text-center">
                <p class="text-xs">SUCCESS</p>
                <p id="success" class="text-2xl font-bold">0</p>
            </div>
            <div class="text-center">
                <p class="text-xs text-red-500">FAILED</p>
                <p id="failed" class="text-2xl font-bold text-red-500">0</p>
            </div>
            <div class="text-center">
                <p class="text-xs text-yellow-500">RETRY</p>
                <p id="retry" class="text-2xl font-bold text-yellow-500">0</p>
            </div>
        </div>

        <div id="logs" class="h-64 overflow-y-auto bg-black p-3 text-xs border border-green-900 mb-4 rounded custom-scroll">
            <p class="text-gray-500">>> Waiting for system start...</p>
        </div>

        <button onclick="start()" class="w-full bg-green-600 hover:bg-green-700 text-black font-black py-3 rounded uppercase transition-all">Start Generating</button>
    </div>

    <script>
        let running = false;
        function start() {
            if(running) return;
            running = true;
            document.querySelector('button').innerText = "GENERATING...";
            setInterval(updateStats, 2000);
        }

        async function updateStats() {
            const response = await fetch('/get_stats');
            const data = await response.json();
            document.getElementById('success').innerText = data.success;
            document.getElementById('failed').innerText = data.failed;
            document.getElementById('retry').innerText = data.retry;
            
            const logs = document.getElementById('logs');
            if(data.accounts.length > 0) {
                logs.innerHTML = data.accounts.map(acc => `<p class='text-green-400'>[SUCCESS] Account: ${acc}:mmmm</p>`).join('') + logs.innerHTML;
            }
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC (Python) ---

def work():
    global stats
    while True:
        username = 'q' + ''.join(random.choices('qwertyuioplkjhgfdsazxcvbnm1234567890', k=13))
        try:
            con = create_connection("wss://195.13.182.217/Auth", 
                                  header={"app": "com.safeum.android"}, 
                                  sslopt={"cert_reqs": CERT_NONE}, timeout=10)
            
            payload = {
                "action": "Register",
                "subaction": "Desktop",
                "login": username,
                "password": {"m1x": "1a07f431a68b4fb69a5c96349137476cca613f019b1016e63a27e022ef09805c", "m2": "43c58959c91b494e05a47cad7bca5b5f52e5204d393e06829c34884fa807954b", "iv": "140c409aba2f6c7050518a826e6f2810", "message": "5080dc99f8e226891ee1f4b52a480e1d0278ff1c211e5107a5de2ceb6a646d40"},
                "devicename": "Xiaomi 220733SPH",
                "os": "AND"
            }
            
            con.send(dumps(payload))
            response = decompress(con.recv()).decode('utf-8')
            
            if '"status":"Success"' in response:
                stats["success"] += 1
                stats["accounts"].append(username)
            else:
                stats["failed"] += 1
            con.close()
        except:
            stats["retry"] += 1
        time.sleep(1)

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_stats')
def get_stats():
    return jsonify(stats)

# Start background thread
threading.Thread(target=work, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
