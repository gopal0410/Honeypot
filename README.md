# Honeypot

SSH Honeypot — lightweight Python-based SSH honeypot for capturing and logging unauthorized connection attempts for analysis and research.

## Overview

Honeypot is a minimal SSH server emulator designed to accept SSH connections, log authentication attempts, and preserve session metadata for later analysis. It is intended for research, monitoring, and defensive security exercises in isolated and controlled environments.

## Features

- Accepts SSH connections and emulates an SSH server
- Logs connection attempts and authentication data to `ssh_honeypot.log`
- Uses provided host key files (`server.key`, `server.key.pub`)
- Simple single-file entry point for quick deployment: `Honeypot_ssh.py`

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (install with pip)

## Installation

1. Clone the repository:

   `git clone https://github.com/gopal0410/Honeypot.git`
   `cd Honeypot`

3. Create a virtual environment (recommended):

   `python3 -m venv venv`
   `source venv/bin/activate`

4. Install dependencies:

   `pip install -r requirements.txt`

## Configuration

- Host keys: `server.key` and `server.key.pub` are used as the SSH host key pair. Replace them with your own key pair if needed.
- Log file: `ssh_honeypot.log` stores connection and authentication events. Ensure the process has write permissions to this file or directory.

## Usage

Run the honeypot with Python:

   `python3 Honeypot_ssh.py`

The script listens for incoming SSH connections and appends events to `ssh_honeypot.log`. For production-like testing, run inside an isolated network or container and restrict outbound access.

## Security and Safety

- Run only in isolated, controlled environments (lab, VM, or container). Do not expose to untrusted networks without proper containment.
- Monitor logs and rotate them as needed. Logs may contain sensitive attacker-provided data.
- Consider network egress controls and sandboxing to prevent misuse.

## Logging and Data Handling

All events and attempted authentications are written to `ssh_honeypot.log`. Review and sanitize logs before sharing; they may include IP addresses, usernames, passwords, or payloads.

## Troubleshooting

- Permission errors: ensure the process user can read `server.key` and write `ssh_honeypot.log`.
- Dependency errors: confirm `pip install -r requirements.txt` completed successfully and the correct Python interpreter is used.

## Acknowledgements

This project is intended for defensive security research and education. Use responsibly.

