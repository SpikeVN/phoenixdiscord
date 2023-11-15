import socket
import threading
import sys
import os

host = "0.0.0.0"
port = int(os.environ["PORT"])


class Client(threading.Thread):
    def __init__(self, conn):
        super(Client, self).__init__()
        self.conn = conn
        self.data = ""

    def run(self):
        while True:
            self.data = self.data + self.conn.recv(1024)
            if self.data.endswith("\r\n"):
                print(self.data)
                self.data = ""

    def send_msg(self, msg):
        self.conn.send(msg)

    def close(self):
        self.conn.close()


class ConnectionThread(threading.Thread):
    def __init__(self, host, port):
        super(ConnectionThread, self).__init__()
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((host, port))
            self.s.listen(5)
        except socket.error:
            print("Failed to create socket")
            sys.exit()
        self.clients = []

    def run(self):
        while True:
            conn, address = self.s.accept()
            c = Client(conn)
            c.start()
            c.send_msg("\r\n")
            self.clients.append(c)
            print("[+] Client connected: {0}".format(address[0]))


def main():
    get_conns = ConnectionThread(host, port)
    get_conns.start()
    while True:
        try:
            response = input()
            for c in get_conns.clients:
                c.send_msg(response + "\r\n")
        except KeyboardInterrupt:
            sys.exit()


def do_stuff():
    threading.Thread(target=main, daemon=True).start()
