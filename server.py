import sqlite3
import json
import os
import time
import zipfile
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

DB_FILE = "/data/vless_users.db"
HTTP_PORT = 8081
TARGET_IP = os.environ.get('IP', '127.0.0.1')
OWNER_KEY = "prvtspyyy404"
START_TIME = time.time()
UUID = "HASIBHOSSENTECH"
WS_PATH = "/@bouchor"

os.makedirs("/data", exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_ip TEXT UNIQUE,
        connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration TEXT DEFAULT '00:00:00',
        status TEXT DEFAULT 'ACTIVE',
        data_mb REAL DEFAULT 0.0
    )''')
    conn.commit()
    conn.close()

def get_connections():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT source_ip, duration, status, data_mb FROM connections')
    rows = c.fetchall()
    conn.close()
    return rows

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == '/':
            self.serve_html()
        elif p.path == '/api/stats':
            self.api_stats()
        elif p.path == '/api/termux':
            self.api_termux(p.query)
        elif p.path == '/download/vless':
            self.download_vless()
        elif p.path == '/download/singbox':
            self.download_singbox()
        elif p.path == '/download/clash':
            self.download_clash()
        elif p.path == '/download/all':
            self.download_all()
        else:
            self.send_error(404)
    
    def serve_html(self):
        uptime_seconds = int(time.time() - START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        current_host = self.headers.get('Host', 'localhost').split(':')[0]
        vless_link = f"vless://{UUID}@{current_host}:443?encryption=none&security=tls&sni={current_host}&type=ws&host={current_host}&path={WS_PATH}#VLESS-{current_host}"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLESS Config Downloader</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.5);
            border-radius: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            color: #00ff88;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0,255,136,0.5);
        }}
        .header p {{ color: #888; }}
        .config-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,255,136,0.2);
            border-color: #00ff88;
        }}
        .card h3 {{ color: #00ff88; margin-bottom: 15px; font-size: 1.5em; }}
        .card p {{ color: #aaa; margin-bottom: 20px; font-size: 0.9em; }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #00ff88 0%, #00b359 100%);
            color: #000;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin: 5px;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }}
        .btn-secondary {{
            background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%);
            color: white;
        }}
        .btn-dark {{
            background: linear-gradient(135deg, #4a4a4a 0%, #2a2a2a 100%);
            color: white;
        }}
        .btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,255,136,0.4);
        }}
        .vless-link {{
            background: #000;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
            color: #00ff88;
            border: 1px solid #00ff88;
        }}
        .info-panel {{
            background: rgba(0,0,0,0.5);
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #222;
        }}
        .status-online {{ color: #00ff88; animation: pulse 2s infinite; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        @media (max-width: 768px) {{
            .config-grid {{ grid-template-columns: 1fr; }}
            .btn {{ padding: 10px 20px; font-size: 12px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VLESS Config Generator</h1>
            <p>Download configuration for your device</p>
        </div>
        <div class="config-grid">
            <div class="card">
                <h3>VLESS Link</h3>
                <p>Universal VLESS URL - Works with V2Ray, Nekobox, Streisand</p>
                <a href="/download/vless" class="btn" download>Download .vless</a>
                <button class="btn btn-dark" onclick="copyToClipboard('{vless_link}')">Copy Link</button>
            </div>
            <div class="card">
                <h3>Sing-box</h3>
                <p>Modern proxy client (iOS, Android, Windows, Mac)</p>
                <a href="/download/singbox" class="btn" download>Download singbox.json</a>
            </div>
            <div class="card">
                <h3>Clash Meta</h3>
                <p>Clash Meta / Mihomo configuration</p>
                <a href="/download/clash" class="btn" download>Download clash.yaml</a>
            </div>
            <div class="card">
                <h3>All Configs</h3>
                <p>Download all configurations in ZIP</p>
                <a href="/download/all" class="btn btn-secondary" download>Download All (ZIP)</a>
            </div>
        </div>
        <div class="vless-link">
            <strong>VLESS URL:</strong><br>
            <span id="vless-url">{vless_link}</span>
        </div>
        <div class="info-panel">
            <h3 style="color:#00ff88; margin-bottom:15px;">Server Information</h3>
            <div class="info-row"><span>Server:</span><span>{current_host}</span></div>
            <div class="info-row"><span>UUID:</span><span>{UUID}</span></div>
            <div class="info-row"><span>Path:</span><span>{WS_PATH}</span></div>
            <div class="info-row"><span>Security:</span><span>TLS (Port 443)</span></div>
            <div class="info-row"><span>Status:</span><span class="status-online"> ONLINE</span></div>
            <div class="info-row"><span>Uptime:</span><span>{uptime_str}</span></div>
            <div class="info-row"><span>Connected Users:</span><span id="user-count">0</span></div>
        </div>
    </div>
    <script>
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text);
            alert('VLESS link copied to clipboard');
        }}
        function fetchStats() {{
            fetch('/api/stats')
                .then(res => res.json())
                .then(data => {{
                    document.getElementById('user-count').innerText = data.active_count;
                }});
        }}
        setInterval(fetchStats, 5000);
        fetchStats();
    </script>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def download_vless(self):
        current_host = self.headers.get('Host', 'localhost').split(':')[0]
        vless_link = f"vless://{UUID}@{current_host}:443?encryption=none&security=tls&sni={current_host}&type=ws&host={current_host}&path={WS_PATH}#VLESS-{current_host}"
        self.send_response(200)
        self.send_header('Content-type', 'application/x-vless')
        self.send_header('Content-Disposition', f'attachment; filename="vless-config-{current_host}.vless"')
        self.end_headers()
        self.wfile.write(vless_link.encode())
    
    def download_singbox(self):
        current_host = self.headers.get('Host', 'localhost').split(':')[0]
        config = {
            "outbounds": [{
                "type": "vless",
                "tag": f"{current_host.replace('.', '-')}-out",
                "server": current_host,
                "server_port": 443,
                "uuid": UUID,
                "flow": "",
                "tls": {"enabled": True, "server_name": current_host, "insecure": False},
                "transport": {"type": "ws", "path": WS_PATH, "headers": {"Host": current_host}}
            }]
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Disposition', f'attachment; filename="singbox-config-{current_host}.json"')
        self.end_headers()
        self.wfile.write(json.dumps(config, indent=2).encode())
    
    def download_clash(self):
        current_host = self.headers.get('Host', 'localhost').split(':')[0]
        yaml_content = f'''proxies:
  - name: "VLESS-{current_host}"
    type: vless
    server: {current_host}
    port: 443
    uuid: {UUID}
    network: ws
    tls: true
    servername: {current_host}
    ws-opts:
      path: {WS_PATH}
      headers:
        Host: {current_host}
proxy-groups:
  - name: PROXY
    type: select
    proxies:
      - "VLESS-{current_host}"
      - DIRECT
rules:
  - MATCH,PROXY
'''
        self.send_response(200)
        self.send_header('Content-type', 'application/x-yaml')
        self.send_header('Content-Disposition', f'attachment; filename="clash-config-{current_host}.yaml"')
        self.end_headers()
        self.wfile.write(yaml_content.encode())
    
    def download_all(self):
        current_host = self.headers.get('Host', 'localhost').split(':')[0]
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            vless_link = f"vless://{UUID}@{current_host}:443?encryption=none&security=tls&sni={current_host}&type=ws&host={current_host}&path={WS_PATH}#VLESS-{current_host}"
            zip_file.writestr(f'vless-{current_host}.vless', vless_link)
            singbox_config = {
                "outbounds": [{
                    "type": "vless",
                    "tag": f"{current_host.replace('.', '-')}-out",
                    "server": current_host,
                    "server_port": 443,
                    "uuid": UUID,
                    "tls": {"enabled": True, "server_name": current_host},
                    "transport": {"type": "ws", "path": WS_PATH, "headers": {"Host": current_host}}
                }]
            }
            zip_file.writestr(f'singbox-{current_host}.json', json.dumps(singbox_config, indent=2))
            clash_content = f'''proxies:
  - name: "VLESS-{current_host}"
    type: vless
    server: {current_host}
    port: 443
    uuid: {UUID}
    network: ws
    tls: true
    servername: {current_host}
    ws-opts:
      path: {WS_PATH}
      headers:
        Host: {current_host}
'''
            zip_file.writestr(f'clash-{current_host}.yaml', clash_content)
            readme = f'''VLESS Configuration for {current_host}
Server: {current_host}
Port: 443
UUID: {UUID}
Path: {WS_PATH}
Security: TLS
Installation:
- Android: Use v2rayNG or NekoBox
- iOS: Use Streisand or Sing-box
- Windows/Mac: Use v2rayN or Nekoray
'''
            zip_file.writestr('README.txt', readme)
        zip_buffer.seek(0)
        self.send_response(200)
        self.send_header('Content-type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="vless-configs-{current_host}.zip"')
        self.end_headers()
        self.wfile.write(zip_buffer.getvalue())
    
    def api_stats(self):
        rows = get_connections()
        ping_ms = int((time.time() - START_TIME) % 15) + 12
        self.send_json({
            'active_count': len(rows),
            'ping_ms': ping_ms
        })

    def api_termux(self, query):
        params = parse_qs(query)
        key = params.get('key', [''])[0]
        if key != OWNER_KEY:
            self.send_json({'error': 'Unauthorized'})
            return
        cmd = params.get('cmd', [''])[0]
        if cmd == 'list':
            rows = get_connections()
            data = [{'ip': r[0], 'duration': r[1], 'status': r[2], 'mb_consumed': r[3]} for r in rows]
            self.send_json(data)
        else:
            self.send_json({'error': 'Unknown command'})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', HTTP_PORT), Handler)
    print(f"VLESS Manager running on port {HTTP_PORT}")
    server.serve_forever()