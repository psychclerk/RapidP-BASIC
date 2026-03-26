"""Test suite for networking: PSocket, PServerSocket, PHTTP."""
import unittest
import sys
import os
import time
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rp_runtime.network import PSocket, PServerSocket, PHTTP


class TestPSocketBasic(unittest.TestCase):
    def test_constructor_defaults(self):
        s = PSocket()
        self.assertEqual(s.host, "127.0.0.1")
        self.assertEqual(s.port, 80)
        self.assertFalse(s.connected)
        self.assertEqual(s.timeout, 0)

    def test_connect_failure(self):
        s = PSocket()
        s.host = "127.0.0.1"
        s.port = 65432  # Unlikely to be open
        s.timeout = 500
        result = s.connect()
        self.assertEqual(result, 0)
        self.assertFalse(s.connected)

    def test_write_when_not_connected(self):
        s = PSocket()
        self.assertEqual(s.write("test"), 0)

    def test_read_when_not_connected(self):
        s = PSocket()
        self.assertEqual(s.read(), "")

    def test_readline_when_not_connected(self):
        s = PSocket()
        self.assertEqual(s.readline(), "")


class TestPSocketClientServer(unittest.TestCase):
    """Test actual client-server communication via PSocket bind/listen/accept."""

    def test_echo(self):
        import socket
        # Find a free port
        with socket.socket() as tmp:
            tmp.bind(('127.0.0.1', 0))
            port = tmp.getsockname()[1]

        server = PSocket()
        server.host = "127.0.0.1"
        server.port = port
        server.bind()
        server.listen(1)

        def client_thread():
            time.sleep(0.1)
            c = PSocket()
            c.host = "127.0.0.1"
            c.port = port
            c.timeout = 2000
            if c.connect():
                c.write("Hello")
                resp = c.read(1024)
                c.close()
                return resp
            return ""

        result = [None]
        def run_client():
            time.sleep(0.1)
            c = PSocket()
            c.host = "127.0.0.1"
            c.port = port
            c.timeout = 2000
            if c.connect():
                c.write("Hello")
                resp = c.read(1024)
                result[0] = resp
                c.close()

        t = threading.Thread(target=run_client, daemon=True)
        t.start()

        client = server.accept()
        self.assertIsNotNone(client)
        data = client.read(1024)
        self.assertEqual(data, "Hello")
        client.write("Echo: Hello")
        client.close()

        t.join(timeout=3)
        self.assertEqual(result[0], "Echo: Hello")
        server.close()


class TestPServerSocket(unittest.TestCase):
    def test_constructor_defaults(self):
        srv = PServerSocket()
        self.assertEqual(srv.host, "0.0.0.0")
        self.assertEqual(srv.port, 8080)
        self.assertEqual(srv.clientcount, 0)

    def test_start_stop(self):
        import socket
        with socket.socket() as tmp:
            tmp.bind(('127.0.0.1', 0))
            port = tmp.getsockname()[1]

        srv = PServerSocket()
        srv.host = "127.0.0.1"
        srv.port = port
        srv.start()
        time.sleep(0.1)
        self.assertTrue(srv._running)
        srv.stop()
        self.assertFalse(srv._running)

    def test_client_connect_and_broadcast(self):
        import socket
        with socket.socket() as tmp:
            tmp.bind(('127.0.0.1', 0))
            port = tmp.getsockname()[1]

        received = []
        def on_data(client, data):
            received.append(data)

        srv = PServerSocket()
        srv.host = "127.0.0.1"
        srv.port = port
        srv.ondatareceived = on_data
        srv.start()
        time.sleep(0.2)

        # Connect a client
        c = PSocket()
        c.host = "127.0.0.1"
        c.port = port
        c.timeout = 2000
        c.connect()
        time.sleep(0.2)
        self.assertEqual(srv.clientcount, 1)

        c.write("Hello Server")
        time.sleep(0.3)
        self.assertTrue(len(received) > 0)
        self.assertIn("Hello Server", received[0])

        c.close()
        time.sleep(0.3)
        srv.stop()


class TestPHTTP(unittest.TestCase):
    def test_constructor(self):
        h = PHTTP()
        self.assertEqual(h.statuscode, 0)
        self.assertEqual(h.responsetext, "")

    def test_url_parsing(self):
        h = PHTTP()
        h.url = "https://example.com/path"
        # Just verify no crash on construction
        self.assertEqual(h.timeout, 10000)


if __name__ == '__main__':
    unittest.main()
