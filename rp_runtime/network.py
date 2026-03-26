import socket
import threading
import ssl as _ssl


class PSocket:
    def __init__(self):
        self._sock = None
        self._new_socket()
        self.host = "127.0.0.1"
        self.port = 80
        self.connected = False
        self.timeout = 0
        self._ssl = False
        self._ssl_context = None

        # Events
        self.onconnect = None
        self.ondisconnect = None
        self.ondataready = None
        self.onerror = None

    def _new_socket(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _fire(self, event, *args):
        if event and callable(event):
            try:
                event(*args)
            except Exception:
                pass

    def connect(self):
        try:
            if self._sock is None:
                self._new_socket()
            if self.timeout > 0:
                self._sock.settimeout(self.timeout / 1000.0)
            self._sock.connect((self.host, int(self.port)))
            if self._ssl:
                ctx = self._ssl_context or _ssl.create_default_context()
                self._sock = ctx.wrap_socket(self._sock, server_hostname=self.host)
            self.connected = True
            self._fire(self.onconnect)
            return 1
        except Exception as e:
            self._fire(self.onerror, str(e))
            return 0

    def close(self):
        try:
            self._sock.close()
        except Exception:
            pass
        self._sock = None
        self.connected = False
        self._fire(self.ondisconnect)

    def write(self, data):
        if not self.connected:
            return 0
        try:
            self._sock.sendall(str(data).encode('utf-8'))
            return 1
        except Exception as e:
            self._fire(self.onerror, str(e))
            return 0

    def writeline(self, data):
        return self.write(str(data) + "\r\n")

    def read(self, max_bytes=4096):
        if not self.connected:
            return ""
        try:
            return self._sock.recv(max_bytes).decode('utf-8', errors='replace')
        except Exception:
            return ""

    def readline(self):
        if not self.connected:
            return ""
        try:
            buf = b""
            while True:
                ch = self._sock.recv(1)
                if not ch or ch == b"\n":
                    break
                buf += ch
            return buf.decode('utf-8', errors='replace').rstrip('\r')
        except Exception:
            return ""

    # Server support
    def bind(self):
        try:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self.host, int(self.port)))
            return 1
        except Exception as e:
            self._fire(self.onerror, str(e))
            return 0

    def listen(self, backlog=5):
        try:
            self._sock.listen(int(backlog))
            return 1
        except Exception as e:
            self._fire(self.onerror, str(e))
            return 0

    def accept(self):
        try:
            conn, addr = self._sock.accept()
            client = PSocket()
            client._sock = conn
            client.host = addr[0]
            client.port = addr[1]
            client.connected = True
            return client
        except Exception as e:
            self._fire(self.onerror, str(e))
            return None


class PServerSocket:
    """Simple TCP server that accepts connections in a background thread."""

    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8080
        self._sock = None
        self._running = False
        self._thread = None
        self.clients = []

        # Events
        self.onclientconnect = None
        self.onclientdisconnect = None
        self.ondatareceived = None
        self.onerror = None

    def _fire(self, event, *args):
        if event and callable(event):
            try:
                event(*args)
            except Exception:
                pass

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, int(self.port)))
        self._sock.listen(5)
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

    def _accept_loop(self):
        while self._running:
            try:
                self._sock.settimeout(1.0)
                conn, addr = self._sock.accept()
                client = PSocket()
                client._sock = conn
                client.host = addr[0]
                client.port = addr[1]
                client.connected = True
                self.clients.append(client)
                self._fire(self.onclientconnect, client)
                # Start a reader thread for this client
                t = threading.Thread(target=self._client_reader, args=(client,), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    self._fire(self.onerror, str(e))
                break

    def _client_reader(self, client):
        while client.connected and self._running:
            try:
                data = client._sock.recv(4096)
                if not data:
                    break
                self._fire(self.ondatareceived, client, data.decode('utf-8', errors='replace'))
            except Exception:
                break
        client.connected = False
        if client in self.clients:
            self.clients.remove(client)
        self._fire(self.onclientdisconnect, client)

    def broadcast(self, data):
        msg = str(data).encode('utf-8')
        for c in list(self.clients):
            try:
                c._sock.sendall(msg)
            except Exception:
                pass

    def stop(self):
        self._running = False
        for c in list(self.clients):
            try:
                c._sock.close()
            except Exception:
                pass
        self.clients.clear()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    @property
    def clientcount(self):
        return len(self.clients)


class PHTTP:
    """Simple HTTP client using sockets (no external dependencies)."""

    def __init__(self):
        self.host = ""
        self.port = 80
        self.url = ""
        self.statuscode = 0
        self.responsetext = ""
        self.responseheaders = {}
        self.timeout = 10000
        self.usessl = False

    def get(self, url=None):
        return self._request("GET", url)

    def post(self, url=None, body=""):
        return self._request("POST", url, body)

    def _request(self, method, url=None, body=""):
        if url:
            self.url = url
        # Parse URL
        u = self.url
        if u.startswith("https://"):
            self.usessl = True
            u = u[8:]
            if self.port == 80:
                self.port = 443
        elif u.startswith("http://"):
            u = u[7:]

        # Split host and path
        if "/" in u:
            host_part, path = u.split("/", 1)
            path = "/" + path
        else:
            host_part = u
            path = "/"

        if ":" in host_part:
            self.host, p = host_part.rsplit(":", 1)
            self.port = int(p)
        else:
            self.host = host_part

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout / 1000.0)
            sock.connect((self.host, int(self.port)))

            if self.usessl:
                ctx = _ssl.create_default_context()
                sock = ctx.wrap_socket(sock, server_hostname=self.host)

            request_line = f"{method} {path} HTTP/1.1\r\n"
            headers = f"Host: {self.host}\r\nConnection: close\r\n"
            if body:
                headers += f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                headers += "Content-Type: application/x-www-form-urlencoded\r\n"
            request = request_line + headers + "\r\n"
            if body:
                request += body

            sock.sendall(request.encode('utf-8'))

            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            sock.close()

            resp_text = response.decode('utf-8', errors='replace')
            if "\r\n\r\n" in resp_text:
                header_part, self.responsetext = resp_text.split("\r\n\r\n", 1)
            else:
                header_part = resp_text
                self.responsetext = ""

            header_lines = header_part.split("\r\n")
            if header_lines:
                status_line = header_lines[0]
                parts = status_line.split(" ", 2)
                if len(parts) >= 2:
                    self.statuscode = int(parts[1])
                for hl in header_lines[1:]:
                    if ":" in hl:
                        k, v = hl.split(":", 1)
                        self.responseheaders[k.strip()] = v.strip()

            return self.responsetext
        except Exception:
            self.statuscode = 0
            self.responsetext = ""
            return ""


# Aliases
RSocket = PSocket
