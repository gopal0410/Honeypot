# Honeypot 🍯

A multi-protocol, Docker-ready Python honeypot designed to capture and analyze unauthorized SSH and HTTP connection attempts.

## 🚀 Quick Start (Docker Compose)

The easiest way to deploy is using Docker Compose. This handles dependencies, networking, and log persistence automatically.

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Deploy
```bash
git clone https://github.com/gopal0410/Honeypot.git
cd Honeypot
docker-compose up -d
```

### 3. Verify
- **SSH Honeypot**: Port `2222`
- **HTTP Honeypot**: Port `8080`
- **Logs**: Located in the `./logs` directory.

---

## 🛠 Manual Docker Deployment (Step-by-Step)

If you prefer using the Docker CLI directly, follow these steps:

### 1. Build the Image
```bash
docker build -t my-honeypot .
```

### 2. Prepare Log Directory
```bash
mkdir -p logs
```

### 3. Run the Container
```bash
docker run -d \
  --name honeypot-instance \
  -p 2222:2222 \
  -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  my-honeypot
```

---

## 🚩 Troubleshooting & Edge Cases

### 1. Port Already in Use
If you get an error like `Bind for 0.0.0.0:2222 failed: port is already allocated`:
- **Fix**: Change the host port in the run command.
- **Example**: `-p 4444:2222` (Maps host port 4444 to honeypot port 2222).

### 2. Permission Denied (Logs)
Since the container runs as `root`, logs created in the `logs/` folder will be owned by root.
- **Fix**: Use `sudo` to view/delete them, or change ownership:
  ```bash
  sudo chown -R $USER:$USER logs/
  ```

### 3. SSH Host Key Verification Failed
If you delete and recreate the container, it may generate a new SSH key, causing your SSH client to warn about a "Host Key Change".
- **Fix**: Persist the `server.key` by mounting it:
  ```bash
  -v $(pwd)/server.key:/app/server.key
  ```

### 4. Updating Code
If you modify `login.html` or the Python scripts, you must rebuild the image:
```bash
docker stop honeypot-instance
docker rm honeypot-instance
docker build -t my-honeypot .
# Run again...
```

---

## 🛠 Features

### 🔐 SSH Honeypot
- **Emulation**: Mimics an Ubuntu 22.04 LTS server.
- **Interaction**: Fake bash shell with `ls`, `cd`, `cat`, `pwd`, `whoami`.
- **Logging**: Captures source IP, credentials, and every command typed.

### 🌐 HTTP Honeypot
- **Emulation**: Serves a customizable login portal (`login.html`).
- **Detection**: Tags **SQL Injection (SQLi)** and **Cross-Site Scripting (XSS)**.
- **Probes**: Records all generic requests (GET/POST) to non-existent paths.

---

## 📂 Logs structure
- `logs/ssh-log.json`: SSH auth attempts and shell commands.
- `logs/http-honeypot.json`: HTTP probes and login data.

---

## ⚠️ Security Warning
**For research only.** 
- Run in a segmented network (VLAN) or dedicated VM.
- Restrict outbound access to prevent attackers from using the honeypot as a pivot.
- Monitor log sizes frequently.

## 📜 Acknowledgements
Intended for defensive security research. Use responsibly and legally.
