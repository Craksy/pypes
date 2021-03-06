#!/usr/bin/env python3
import asyncio
import curses
import curses.ascii
import json
import sys
from asyncio.streams import StreamReader, StreamWriter
from curses import ERR, wrapper
from typing import Any, Optional, Tuple

from chatwin import ChatWin
from inputfield import InputField
from protocol import Protocol

PORT = 42069
DEBUG_MODE = False

B2C = 1000 / 255
C2B = 255 / 1000


def hex2rgb(hexstring: str) -> Tuple[int, int, int]:
    """Convert Hex color string to (r,g,b) tuple

    Args:
        hexstring (str): Hex color to convert

    Returns:
        Tuple[int, int, int]: R,G,B tuple
    """
    if hexstring.startswith("#"):
        hexstring = hexstring[1:]
    value = int(hexstring, 16)
    return value >> 16 & 0xFF, value >> 8 & 0xFF, value & 0xFF


def rgb2curs(r:int, g:int, b:int):
    """Convert regular rgb to curses rgb

    Contrary to standard 24bit RGB, curses uses values in the range 0-1000.

    Args:
        r (int): The red color component
        g (int): The green color component
        b (int): The blue color component

    Returns:
        Tuple[int, int, int]: curses color
    """
    return int(r * B2C), int(g * B2C), int(b * B2C)


class MainWin:
    """The main curses window.

    Contains the in- and out streams that interact with the socket, and is
    responsible for handling the communication with the server.  Actual display
    and user input is handled by the child components `MainWin.input_field` and
    `MainWin.output_field`.

    Args:
        display (screen): The main curses display. Dependency injected by the curses wrapper.
    """

    def __init__(self, display):
        """Initialize the main window

        """
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
        """Return the id for `color` or define a new color pair if it hasn't
        been created yet.

        :param color: The color to request
        :type color: str
        :return: The color
        :rtype: int
        """
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
        """Try to read user input, yielding control back to the event loop if none is
        available."""
        while True:
            try:
                char = self.display.getch()
            except:
                char = ERR
            if char is not ERR:
                await self.handle_input(char)
            else:
                await asyncio.sleep(0.1)

    async def handle_input(self, char:int):
        """Handle received keyboard input.

        Check input handle handle deletion and submission with backspace and
        enter. Otherwise assume printable character and try to insert it in the
        input field.

        :param char: The keycode for the pressed key.
        :type char: int
        """
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

    def handle_message(self, typ:str, data:Optional[Any]=None):
        """handle a server message

        :param typ: The protocol message type
        :type typ: str
        :param data: the `payload` component of the received message, defaults to None
        :type data: Optional[Any], optional
        """
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

    async def send(self, typ:str, **kwargs):
        """Send a message to the server

        Every key/value pair in `kwargs` will be added as a field in the `payload` of the final message.

        :param typ: The protocol message type
        :type typ: str
        """
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

    async def authenticate(self, name:str) -> bool:
        """Perform the handshake with the server

        :param name: the requested name.
        :type name: str
        :return: success status of the handshake
        :rtype: bool
        """
        while True:
            typ, _ = await self.recv()
            if typ == Protocol.SERVER_HELLO:
                await self.send(Protocol.CLIENT_NAME, name=name)
                continue
            if typ == Protocol.SERVER_WELCOME:
                return True


def main(display):
    win = MainWin(display)
    win.run()


if __name__ == "__main__":
    wrapper(main)
