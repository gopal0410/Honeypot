import argparse
import threading
import sys
import os
import paramiko
from Honeypot_ssh import Honeypot_SSH
from Honeypot_http import Honeypot_HTTP

def ensure_ssh_key(filename="server.key"):
    if not os.path.exists(filename):
        print(f"[*] Generating new SSH host key: {filename}")
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(filename)

def run_ssh(address, port):
    try:
        ensure_ssh_key()
        honeypot = Honeypot_SSH(address, port)
        honeypot.main()
    except Exception as e:
        print(f"[!] SSH Honeypot Error: {e}")

def run_web(address, port):
    try:
        honeypot = Honeypot_HTTP(address, port)
        honeypot.main()
    except Exception as e:
        print(f"[!] HTTP Honeypot Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-protocol Honeypot (SSH & HTTP)")
    parser.add_argument('-a', '--address', type=str, default="0.0.0.0", help="IP address to bind to")
    parser.add_argument('-sp', '--ssh-port', type=int, default=2222, help="Port for SSH honeypot")
    parser.add_argument('-wp', '--web-port', type=int, default=8080, help="Port for HTTP honeypot")
    
    parser.add_argument('-s', '--ssh', action="store_true", help="Run SSH honeypot")
    parser.add_argument('-w', '--web', action="store_true", help="Run HTTP honeypot")

    args = parser.parse_args()

    # If neither is specified, run both
    run_all = not args.ssh and not args.web
    
    threads = []

    if args.ssh or run_all:
        print(f"[-] Starting SSH Honeypot on {args.address}:{args.ssh_port}...")
        ssh_thread = threading.Thread(target=run_ssh, args=(args.address, args.ssh_port), daemon=True)
        ssh_thread.start()
        threads.append(ssh_thread)

    if args.web or run_all:
        print(f"[-] Starting HTTP Honeypot on {args.address}:{args.web_port}...")
        web_thread = threading.Thread(target=run_web, args=(args.address, args.web_port), daemon=True)
        web_thread.start()
        threads.append(web_thread)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n[!] Shutting down honeypots...")
        sys.exit(0)
