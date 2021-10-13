#!/usr/bin/env python3
import asyncio
import curses
import curses.ascii
import json
import sys
from asyncio.streams import StreamReader, StreamWriter
from curses import ERR, wrapper
from typing import Tuple

from _curses import window

from chatwin import ChatWin
from inputfield import InputField
from protocol import Protocol

PORT = 42069
DEBUG_MODE = False

B2C = 1000 / 255
C2B = 255 / 1000


def hex2rgb(hexstring: str) -> Tuple[int, int, int]:
    if hexstring.startswith("#"):
        hexstring = hexstring[1:]
    value = int(hexstring, 16)
    return value >> 16 & 0xFF, value >> 8 & 0xFF, value & 0xFF


def rgb2curs(r, g, b):
    return int(r * B2C), int(g * B2C), int(b * B2C)


class MainWin:
    def __init__(self, display):
        self.display: window = display
        self.reader: StreamReader
        self.writer: StreamWriter
        self.display.nodelay(True)
        self.display.clear()
        self.colors = dict()
        height, width = self.display.getmaxyx()

        self.input_field = InputField(width - 2, 3, height - 3, 0)
        self.output_field = ChatWin(width - 2, height - 4)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connect())
        loop.create_task(self.poll_input())
        loop.run_forever()

    def get_or_create_color(self, color):
        if not color in self.colors:
            r, g, b = rgb2curs(*hex2rgb(color))
            n = len(self.colors) + 10
            curses.init_color(n, r, g, b)
            curses.init_pair(n, n, 0)
            self.colors[color] = n
        return self.colors[color]

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(sys.argv[1], PORT)
        if not await self.authenticate("Guest"):
            self.display.addstr("failed auth")
            exit(1)
        while True:
            if not self.reader.at_eof():
                typ, dat = await self.recv()
                self.handle_message(typ, dat)
            else:
                await asyncio.sleep(0.1)

    async def poll_input(self):
        while True:
            try:
                char = self.display.getch()
            except:
                char = ERR
            if char is not ERR:
                await self.handle_input(char)
            else:
                await asyncio.sleep(0.1)

    async def handle_input(self, char):
        if char in (curses.KEY_BACKSPACE, "\b", "\x08", "\x7f", curses.ascii.BS):
            self.input_field.backspace()
        elif char == 10:
            message = self.input_field.flush_input()
            if message.startswith("/"):
                split = message[1:].split()
                cmd = split[0]
                args = split[1:]
                await self.send(Protocol.COMMAND, cmd=cmd, args=args)
            else:
                await self.send(Protocol.MESSAGE, message=message)
        else:
            self.input_field.add_char(char)
        self.input_field.refresh()

    def handle_message(self, typ, data=None):
        if typ == Protocol.MESSAGE:
            sender = data.get("sender")
            msg = data.get("message")
            color = self.get_or_create_color(data.get("color"))
            self.output_field.add_entry(sender, msg, color)
            self.input_field.refresh()
            self.output_field.refresh()
        elif typ == Protocol.SERVER_INFO:
            msg = data.get("message")
            self.output_field.add_banner(msg)
            self.output_field.refresh()

    async def recv(self):
        header = await self.reader.read(4)
        size = int.from_bytes(header, "little")
        if size > 0xFFF:
            # drop connection. beyond size limit
            ...
        data = await self.reader.read(size)
        try:
            message = json.loads(data)
            return message.get("type"), message.get("payload")
        except:
            print("could not deserialize data:", data)
            return None, None

    async def send(self, typ, **kwargs):
        message = {"type": typ}
        if kwargs:
            message["payload"] = kwargs
        data = json.dumps(message).encode("utf8")
        size = len(data)
        if size > 0xFFF:
            # throw error. size limit exeeded
            ...
        self.writer.write(int.to_bytes(size, 4, "little"))
        await self.writer.drain()
        self.writer.write(data)
        await self.writer.drain()

    async def authenticate(self, name):
        while True:
            typ, _ = await self.recv()
            if typ == Protocol.SERVER_HELLO:
                await self.send(Protocol.CLIENT_NAME, name=name)
                continue
            if typ == Protocol.SERVER_WELCOME:
                return True


def main(display: window):
    win = MainWin(display)
    win.run()


if __name__ == "__main__":
    wrapper(main)
