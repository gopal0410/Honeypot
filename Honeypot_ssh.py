import logging
import json
import paramiko
import socket
import threading
import os
from datetime import datetime, timezone

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, credentials=None, log_fn=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.credentials = credentials or []
        self.log_fn = log_fn

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        if self.credentials is not None:
            self.log_fn("auth", self.client_ip, username=username, password=password)
            for user, passw in self.credentials:
                if username == user and password == passw:
                    return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return True

class FakeFileSystem:
    def __init__(self):
        self.tree = {
                    "etc": {
                        "passwd": "root:x:0:0:root:/root:/bin/bash\nhoneypot-bear:x:1000:1000::/home/honeypot-bear:/bin/bash",
                        "hosts": "127.0.0.1 localhost\n127.0.1.1 ubuntu"
                    },
                    "home": {
                        "honeypot-bear": {
                            "notes.txt": "Remember to update credentials",
                            "credentials.txt": "db_password=Sup3rS3cur3!"
                        }
                    },
                    "tmp": {},
                    "var": {
                        "log": {
                            "auth.log": "May 16 10:22:01 ubuntu sshd: Accepted password for honeypot-bear"
                        }
                    }
                }
        self.current_path = [] 

    def _get_node(self, path=None):
        """Walk the dict tree to the given path (or current path)."""
        node = self.tree
        for part in (path if path is not None else self.current_path):
            node = node[part]
        return node

    def pwd(self):
        return "/" + "/".join(self.current_path)

    def ls(self):
        node = self._get_node()
        if isinstance(node, dict):
            return "  ".join(node.keys()) or "(empty)"
        return "Not a directory"

    def cd(self, target):
        if target == "..":
            if self.current_path:
                self.current_path.pop()
            return ""
        elif target == "~" or target == "/":
            self.current_path = []
            return ""
        else:
            node = self._get_node()
            if target in node and isinstance(node[target], dict):
                self.current_path.append(target)
                return ""
            elif target not in node:
                return f"cd: {target}: No such file or directory"
            else:
                return f"cd: {target}: Not a directory"

    def cat(self, filename):
        node = self._get_node()
        if filename in node:
            if isinstance(node[filename], str):
                return node[filename]
            return f"cat: {filename}: Is a directory"
        return f"cat: {filename}: No such file or directory"
    
class Honeypot_SSH:
    def __init__(self, bind_ip="0.0.0.0", port=2222):
        self.bind_ip = bind_ip
        self.port = port
        self.credentials = [('root', '123456'),
                ('admin', 'password'),
                ('ubuntu', 'admin'),
                ('user', 'qwerty'),
                ('oracle', 'welcome'),
                ('postgres', 'letmein'),
                ('test','passw0rd')]
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, "ssh-log.json")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.host_key = paramiko.RSAKey(filename="server.key")

    def log_activity(self, event_type, client_ip, **kwargs):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "src_ip": client_ip,
            **kwargs
        }
        with open(self.log_file, "a") as file:
            json.dump(entry, file, indent=4)
            file.write("\n\n")
        

    def shell(self, channel, client_ip):
        fs = FakeFileSystem()
        channel.send(f"honeypot-bear@ubuntu:{fs.pwd()}$ ".encode("utf-8"))
        command = b""
        while True:
            char = channel.recv(1)
            if not char:
                channel.close()
                return

            channel.send(char)
            command += char
            response = b""
            if char == b'\r' or char == b'\n':
                cmd = command.strip()
                self.log_activity("command", client_ip, command=cmd.decode("utf-8"))
                if cmd == b"exit":
                    response = "\nGoodBye!\r\n"
                    channel.send(response)
                    channel.close()
                    return
                elif cmd == b"whoami":
                    response = "honeypot-bear\r\n"
                elif cmd == b"ls":
                    response = fs.ls()
                elif cmd == b"pwd":
                    response = fs.pwd()
                elif cmd.startswith(b"cd "):
                    response = fs.cd(cmd[3:].decode("utf-8").strip())
                elif cmd.startswith(b"cat "):
                    response = fs.cat(cmd[4:].decode("utf-8").strip())
                else:
                    response = f"{cmd}: command not found"

                channel.send(b"\n" + response.encode("utf-8")+ b"\r\n")
                channel.send(f"honeypot-bear@ubuntu:{fs.pwd()}$ ".encode("utf-8"))
                command = b""
    
    def client_handler(self, client, addr):
        client_ip = addr[0]
        print(f"[-] {client_ip} has connected to the server.")

        try:
            transport = paramiko.Transport(client)
            transport.local_version = "SSH-2.0-OpenSSH_9.6p1"
            server = Server(client_ip = client_ip,credentials=self.credentials, log_fn=self.log_activity)
            
            transport.add_server_key(self.host_key)
            transport.start_server(server=server)

            channel = transport.accept(100)

            if channel is None:
                print("No channel was opened")
                return

            channel.send(b"Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n")
            self.shell(channel, client_ip)

        except Exception as error:
            print("--- An Error Has Occured ---")
            print("*"*3 + f"{error}" + "*"*3)
        
        finally:
            try:
                transport.close()
            except Exception as error:
                print("--- An Error has occured ---")
                print(f"{error}")
            client.close()
    
    def main(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.bind_ip, self.port))

        sock.listen(100)
        print(f"[-] SSH is listening on port {self.port}")

        while True:
            try:
                client, addr = sock.accept()
                ssh_thread = threading.Thread(target=self.client_handler, args=(client, addr))
                ssh_thread.start()
            except KeyboardInterrupt:
                print("\n[-] Exiting....")
            except Exception as error:
                print(f"{error}")


