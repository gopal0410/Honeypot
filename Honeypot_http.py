import http.server
import json
import re
import time
import socket
import urllib.parse
from datetime import datetime, timezone

SQLI_PATTERNS = re.compile(r"(\bunion\b|\bselect\b|\bdrop\b|\binsert\b|\bdelete\b|--|;|'|\bor\b\s+['\d]|/\*|\*/)",re.IGNORECASE,)
XSS_PATTERNS = re.compile(r"(<script|javascript:|on\w+=|<img|<svg|alert\s*\(|document\.cookie)", re.IGNORECASE)

class Honeypot_HTTP:
    def __init__(self, bind_ip="0.0.0.0", port=8080):
        self.bind_ip = bind_ip
        self.port = port
        self.log_file = "http-honeypot.json"

    def classify(self, value):
        tags = []
        if SQLI_PATTERNS.search(value):
            tags.append("sqli")
        if XSS_PATTERNS.search(value):
            tags.append("xss")
        if not tags:
            tags.append("plain")
        return tags
    
    def log_record(self, record):
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(record, indent=4) + "\n\n")
    
    def main(self):
        server = http.server.ThreadingHTTPServer(("", self.port), HTTPServer)
        print(f"[-] Listening on http://{self.bind_ip}:{self.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Exiting....")
            server.server_close()
        except Exception as error:
            print(f"{error}")

class HTTPServer(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass 

    def do_GET(self):
        if self.path == "/" or self.path == "/login":
            self._serve_login_page()
        else:
            self._log_generic("GET")
            self._send_404()
        
    def do_POST(self):
        if self.path == "/login":
            self._handle_login()
        else:
            self._log_generic("POST")
            self._send_404()
        
    def _serve_login_page(self):
        try:
            with open("login.html", "rb") as file:
                body = file.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self._send_text(500, b"login.html not found")
    
    def _handle_login(self):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")

        fields = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
        username = fields.get("username", [""])[0]
        password = fields.get("password", [""])[0]

        record = {
            "timestamp": int(time.time()),
            "datetime_utc": datetime.now(timezone.utc).isoformat(),
            "honeypot": socket.gethostname(),
            "event": "login_attempt",
            "remote_addr": self.client_address[0],
            "user_agent": self.headers.get("User-Agent",""),
            "username": username,
            "password": password,
            "username_tags": Honeypot_HTTP().classify(username),
            "password_tags": Honeypot_HTTP().classify(password),
            "raw_body": raw_body
        }
        if SQLI_PATTERNS.search(username) or SQLI_PATTERNS.search(password):
            record["event"] = "Injection Attack"
        elif XSS_PATTERNS.search(username) or XSS_PATTERNS.search(password):
            record["event"] = "Injection Attack"
        Honeypot_HTTP().log_record(record)

        self._send_text(200, b"Invalid username or password")

    def _log_generic(self, method):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = ""
        if length:
            raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        
        record = {
            "timestamp": int(time.time()),
            "datetime_utc": datetime.now(timezone.utc).isoformat(),
            "honeypot": socket.gethostname(),
            "event": "probe",
            "remote_addr": self.client_address[0],
            "user_agent": self.headers.get("User-Agent",""),
            "method": method,
            "uri": self.path,
            "headers": dict(self.headers),
            "raw_body": raw_body
        }

        Honeypot_HTTP().log_record(record)
    
    def _send_text(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()  
        self.wfile.write(body)

    def _send_404(self):
        self._send_text(404, b"Not Found")
