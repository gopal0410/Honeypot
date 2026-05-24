# Honeypot

A multi-protocol Python-based honeypot for capturing and logging unauthorized connection attempts via SSH and HTTP for analysis and research.

## Overview

Honeypot is a modular security tool designed to emulate services (SSH and HTTP), log authentication attempts, and preserve session metadata. It helps in monitoring attacker behavior and identifying common attack patterns like credential stuffing, SQL injection, and Cross-Site Scripting (XSS).

## Features

- **SSH Honeypot**:
  - Emulates an Ubuntu 22.04 LTS SSH server.
  - Logs connection attempts, authentication data, and commands executed in a fake shell.
  - Supports a virtual filesystem for basic interaction (`ls`, `cd`, `cat`, `pwd`, `whoami`).
  - Logs to `ssh-login.json`.
- **HTTP Honeypot**:
  - Emulates a simple login page (`login.html`).
  - Detects and tags SQL Injection (SQLi) and Cross-Site Scripting (XSS) attempts in form fields.
  - Logs "probes" (requests to non-existent paths) and login attempts.
  - Logs to `http-honeypot.json`.
- **Unified Entry Point**: Run both services concurrently or individually using `honeypot.py`.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`:
  - `paramiko` (for SSH emulation)
  - `cryptography`
  - (Other dependencies as listed)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gopal0410/Honeypot.git
   cd Honeypot
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- **SSH Host Keys**: `server.key` and `server.key.pub` are used as the SSH host key pair. Replace them with your own key pair for production-like testing.
- **Login Page**: Customize `login.html` to change the appearance of the HTTP honeypot.
- **Credentials**: The SSH honeypot uses a hardcoded list of common credentials (e.g., `root:123456`, `admin:password`).

## Usage

Run the honeypot using the main entry point:

```bash
# Run both SSH and HTTP honeypots with default settings
python3 honeypot.py

# Run only the SSH honeypot on a specific port
python3 honeypot.py --ssh --ssh-port 22

# Run only the HTTP honeypot on a specific port
python3 honeypot.py --web --web-port 80

# Bind to a specific interface
python3 honeypot.py -a 192.168.1.50
```

### Options:
- `-a`, `--address`: IP address to bind to (default: `0.0.0.0`)
- `-s`, `--ssh`: Run the SSH honeypot
- `-sp`, `--ssh-port`: Port for SSH (default: `2222`)
- `-w`, `--web`: Run the HTTP honeypot
- `-wp`, `--web-port`: Port for HTTP (default: `8080`)

## Security and Safety

- **Isolation**: Run only in isolated, controlled environments (lab, VM, or container). Do not expose to untrusted networks without proper containment.
- **Log Management**: Monitor and rotate logs (`ssh-login.json`, `http-honeypot.json`). Logs may contain sensitive attacker-provided data.
- **Egress Control**: Ensure the environment has restricted outbound access to prevent attackers from using the honeypot as a pivot point.

## Acknowledgements

This project is intended for defensive security research and education. Use responsibly.
