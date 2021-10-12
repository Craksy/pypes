#!/usr/bin/env python3
import json, socket, select, sys

from protocol import Protocol

PORT = 42069
DEBUG_MODE = False

# Utility methods
def debug(msg, *args, **kwargs):
    if not DEBUG_MODE:
        return


def clear_line():
    sys.stdout.write("\033[F")  # back to previous line
    sys.stdout.write("\033[K")  # clear line


def prev_line():
    sys.stdout.write("\033[F")  # back to previous line


def goto_col(n):
    sys.stdout.write(f"\x1b[{n}G")


def save_cur():
    sys.stdout.write("\x1b7")


def rest_cur():
    sys.stdout.write("\x1b8")


def goto_cur(y, x):
    sys.stdout.write(f"\x1b[{y};{x}H")


class Protocol:
    DROP = "DROP"
    MESSAGE = "MESSAGE"
    COMMAND = "COMMAND"
    SERVER_HELLO = "SERVER_HELLO"
    SERVER_WELCOME = "SERVER_WELCOME"
    CLIENT_NAME = "CLIENT_NAME"
    SERVER_INFO = "SERVER_INFO"
    SERVER_BANNER = "SERVER_INFO"
    TELL = "TELL"


class Client:
    def __init__(self, ip_addr, name):
        self.name = name
        self.server = self.connect(ip_addr)
        try:
            if not self.authenticate():
                print("failed handshake")
                exit(1)
            self.run()
        except KeyboardInterrupt:
            print("interrupt")
        finally:
            self.server.close()
            print("Bye")

    def connect(self, ip_addr):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((ip_addr, PORT))
            print("Connected")
            return server
        except:
            print("Failed to connect to {}:{}".format(ip_addr, PORT))
            exit(1)

    def receive_message(self):
        try:
            message = json.loads(self.server.recv(1024))
            return message["type"], message.get("payload")
        except ConnectionResetError:
            print("Connection closed by server")
            exit()

    def send_message(self, typ, data=None):
        message = json.dumps({"type": typ, "payload": data}).encode("utf8")
        self.server.send(message)

    def authenticate(self):
        while True:
            typ, data = self.receive_message()
            debug("type: {}, data: {}", typ, data)
            if typ == Protocol.SERVER_HELLO:
                self.send_message(Protocol.CLIENT_NAME, {"name": self.name})
                continue
            if typ == Protocol.SERVER_WELCOME:
                print("Authenticated")
                return True

    def run(self):
        while True:
            sockets_list = [sys.stdin.fileno(), self.server]
            read_sockets, _, _ = select.select(sockets_list, [], [], 1)
            for socks in read_sockets:
                if socks == self.server:
                    typ, data = self.receive_message()
                    self.handle_message(typ, data)
                else:
                    self.handle_input()

    def handle_input(self):
        message = sys.stdin.readline()
        sys.stdout.flush()
        clear_line()
        sys.stdout.flush()
        if message.startswith("/"):
            split = message.split()
            payload = {"cmd": split[0][1:], "args": split[1:]}
            self.send_message(Protocol.COMMAND, payload)
        elif message.startswith("@"):
            split = message.split()
            target = split[0][1:]
            message = "".join(split[1:])
            self.send_message(Protocol.TELL, {"target": target, "message": message})
        else:
            self.send_message(Protocol.MESSAGE, {"message": message})

    def handle_message(self, typ, data):
        debug("handle message.\nType: {}\ndata:{}({})", typ, data, type(data))
        if typ == Protocol.MESSAGE:
            clear_line()
            sys.stdout.flush()
            msg = data["message"]
            sender = data["sender"]
            color = data.get("color")
        elif typ == Protocol.SERVER_INFO:
            msg = data["message"]
            spc = " " * 15 + "│"
            lines = msg.split("\n")
        elif typ == Protocol.TELL:
            clear_line()
            sys.stdout.flush()
            msg = data["message"]
            sender = data["sender"]
            color = data.get("color")
