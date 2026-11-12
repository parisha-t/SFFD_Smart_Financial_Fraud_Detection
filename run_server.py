import http.server
import socketserver
import json
import numpy as np
import os
import webbrowser
import sys

sys.stdout.reconfigure(encoding='utf-8')

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class FintechHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/predict':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                v1 = float(data.get('v1', 0.0))
                v4 = float(data.get('v4', 0.0))
                v12 = float(data.get('v12', 0.0))
                v14 = float(data.get('v14', 0.0))
                v17 = float(data.get('v17', 0.0))

                anomaly_index = (abs(v1) * 0.12) + (abs(v4) * 0.28) + (abs(v12) * 0.25) + (abs(v14) * 0.40) + (abs(v17) * 0.30)
                probability = 1.0 / (1.0 + np.exp(-(anomaly_index - 3.20)))
                probability = float(np.clip(probability, 0.001, 0.999))
                is_fraud = bool(probability >= 0.50)

                response = {
                    "anomaly_index": round(anomaly_index, 4),
                    "probability": round(probability, 4),
                    "probability_pct": round(probability * 100, 2),
                    "is_fraud": is_fraud,
                    "verdict": "FRAUDULENT TRANSACTION DETECTED" if is_fraud else "TRANSACTION VERIFIED: LEGITIMATE",
                    "status_action": "Status: Blocked | Trigger Step-Up Re-Authentication" if is_fraud else "Status: Cleared | Low Latent Variance"
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print(f"=================================================================")
    print(f"🛡️  Smart Financial Fraud Detection Engine — Web Server")
    print(f"=================================================================")
    print(f"🌐 Serving UI & API at: http://localhost:{PORT}")
    print(f"📁 Root directory: {DIRECTORY}")
    print(f"💡 Press Ctrl+C to terminate.")
    print(f"=================================================================")
    with socketserver.TCPServer(("", PORT), FintechHandler) as httpd:
        httpd.serve_forever()
