import os
import time
import random
import threading
from json import dumps
from gzip import decompress
from ssl import CERT_NONE
from flask import Flask, render_template_string, jsonify

# WebSocket client import with auto-install
try:
    from websocket import create_connection
except ImportError:
    os.system('pip install websocket-client')
    from websocket import create_connection

app = Flask(__name__)

# Global Stats
stats = {
    "success": 0,
    "failed": 0,
    "retry": 0,
    "accounts": []
}

# --- Fresh UI Design ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Waleed Safeum - v3 Fresh</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #080808; font-family: 'Courier New', monospace; color: #00ff41; }
        .glow-box { border: 1px solid #00ff41; box-shadow: 0 0 15px rgba(0, 255, 65, 0.3); }
        .log-area { height: 350px; background: #000; border: 1px solid #1a1a1a; }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="glow-box w-full max-w-xl p-8 rounded-xl bg-black">
        <h1 class="text-2xl font-bold text-center mb-6 border-b border-green-900 pb-2">WALEED SAFEUM <span class="text-white text-sm">v3.0 FRESH</span></h1>
        
        <div class="grid grid-cols-3 gap-4 mb-8">
            <div class="text-center bg-zinc-900 p-3 rounded">
                <p class="text-[10px] text-gray-400">SUCCESS</p>
                <p id="success" class="text-xl font-bold">0</p>
            </div>
            <div class="text-center bg-zinc-900 p-3 rounded">
                <p class="text-[10px] text-red-500">FAILED</p>
                <p id="failed" class="text-xl font-bold text-red-500">0</p>
            </div>
            <div class="text-center bg-zinc-900 p-3 rounded text-yellow-500">
                <p class="text-[10px]">RETRY</p>
                <p id="retry" class="text-xl font-bold">0</p>
            </div>
        </div>

        <div id="log-screen" class="log-area rounded p-4 text-[11px] overflow-y-auto mb-6">
            <p class="text-blue-400">>> System ready for deployment...</p>
        </div>

        <button onclick="startProcess()" id="btn" class="w-full py-4 bg-green-600 hover:bg-green-700 text-black font-black rounded uppercase transition-all">
            Deploy Fresh Script
        </button>
    </div>

    <script>
        let running = false;
        function startProcess() {
            if(running) return;
            running = true;
            document.getElementById('btn').innerText = "GENERATING ACCOUNTS...";
            document.getElementById('btn').classList.replace('bg-green-600', 'bg-zinc-700');
            setInterval(fetchStats, 2000);
        }

        async function fetchStats() {
            const r = await fetch('/status');
            const d = await r.json();
            document.getElementById('success').innerText = d.success;
            document.getElementById('failed').innerText = d.failed;
            document.getElementById('retry').innerText = d.retry;
            
            const log = document.getElementById('log-screen');
            if(d.accounts.length > 0) {
                const last = d.accounts[d.accounts.length - 1];
                log.innerHTML = `<div class="mb-1"><span class="text-green-500">[OK]</span> ${last}:mmmm</div>` + log.innerHTML;
            }
        }
    </script>
</body>
</html>
"""

# --- Fresh Registration Logic ---

def worker_thread():
    global stats
    while True:
        # Dynamic Data
        user = "waleed_" + str(random.randint(100000, 999999))
        device_id = "".join(random.choices("0123456789abcdef", k=16))
        
        try:
            # Server IP connection
            ws = create_connection(
                "wss://195.13.182.217/Auth", 
                header={"app": "com.safeum.android"},
                sslopt={"cert_reqs": CERT_NONE},
                timeout=20
            )

            # Updated Fresh Parameters (Simulating latest app version)
            payload = {
                "action": "Register",
                "subaction": "Desktop",
                "login": user,
                "password": {
                    "m1x": "468b4fb69a5c96349137476cca613f019b1016e63a27e022ef09805c", # Fresh Key Simulation
                    "m2": "7bca5b5f52e5204d393e06829c34884fa807954b",
                    "iv": "140c409aba2f6c7050518a826e6f2810",
                    "message": "0278ff1c211e5107a5de2ceb6a646d407084bd88f05438f6"
                },
                "devicename": "OnePlus 9 Pro",
                "softwareversion": "1.1.0.1548",
                "os": "AND",
                "deviceuid": device_id,
                "osversion": "and_13.0.0"
            }

            ws.send(dumps(payload))
            response = decompress(ws.recv()).decode('utf-8')

            if '"status":"Success"' in response:
                stats["success"] += 1
                stats["accounts"].append(user)
            else:
                stats["failed"] += 1
            
            ws.close()
        except Exception:
            stats["retry"] += 1
        
        # Avoid server flooding
        time.sleep(3)

# --- Routes ---

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/status')
def get_status():
    return jsonify(stats)

# Initialize Threading
threading.Thread(target=worker_thread, daemon=True).start()

if __name__ == "__main__":
    # Vercel port compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
