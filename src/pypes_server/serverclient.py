import json
import logging
from asyncio.streams import StreamReader, StreamWriter
from random import choice
from typing import Any, Tuple

from protocol import Protocol

palette = [
    "2f4f4f",
    "556b2f",
    "a0522d",
    "2e8b57",
    "228b22",
    "800000",
    "708090",
    "808000",
    "483d8b",
    "008080",
    "b8860b",
    "4682b4",
    "d2691e",
    "9acd32",
    "33338b",
    "32cd32",
    "7f007f",
    "8fbc8f",
    "b03060",
    "9932cc",
    "ff4500",
    "00ced1",
    "ff8c00",
    "ffd700",
    "c71585",
    "4444cd",
    "00ff00",
    "00ff7f",
    "4169e1",
    "dc143c",
    "00bfff",
    "f4a460",
    "6666ff",
    "a020f0",
    "adff2f",
    "ff6347",
    "da70d6",
    "b0c4de",
    "ff00ff",
    "f0e68c",
    "fa8072",
    "ffff54",
    "6495ed",
    "dda0dd",
    "90ee90",
    "afeeee",
    "7fffd4",
    "ff69b4",
    "ffe4c4",
    "ffc0cb",
]

# ?: just put these inside of the relevant handlers?

welcome_text = """Velkommen til, {name}.
Du kan skrive /help for at få vist en liste over kommandoer."""

help_text = """Chatkommandoer kan bruges ved at begynde en besked med / og
navnet på en kommando. nogle kommandoer kan modtage et eller flere parametre
adskildt af mellemrum.

Kommandoer:
HELP              - viser denne besked
NAME <navn>       - Anmod om at skifte navn
COLOR <farve>     - skift farven dit navn bliver vist med. farven angives som
                    hexadecimal i formatet RRGGBB eller 0xRRGGBB"""


class UserClient:
    """Represents a client connected to the server

    A single connected client with two streams for communication. Functions as
    the main handler for clients, and is were most of the protocol is
    implemented. Anything beyond 1-to-1 communication with the server should be
    implemented in `Server` class; UserClients should not interact with eachother directly.

    Attributes:
        reader: The incoming data stream
        writer: The outgoing data stream
        name:   The username associated with this client
        color:  The color that this clients name has
        server: A reference to the server object.
    """

    def __init__(self, reader: StreamReader, writer: StreamWriter, server):
        """Initialize a new client.

        Args:
            reader (StreamReader):  The stream of incomming data
            writer (StreamWriter):  The stream to write to
            server (Server):        A reference to the server object instance.
        """
        self.reader = reader
        self.writer = writer
        self.name: str = ""
        self.color: str = ""
        self.server: server.Server = server

    async def send(self, type, **kwargs):
        """Send a message to the client

        Parse provided arguments to construct a message object.
        Serialize to JSON and send it to the client.

        Args:
            type (str): The protocol message type
            kwargs (dict): each key/value-pair will be put in the ``payload`` field of the sent message
        """
        try:
            message = {"type": type}
            if kwargs:
                message["payload"] = kwargs
            serialized = json.dumps(message).encode("utf8")
            size = len(serialized)
            if size > 0xFFF:
                # throw error. size limit exeeded
                ...
            self.writer.write(int.to_bytes(size, 4, "little"))
            await self.writer.drain()
            self.writer.write(serialized)
            await self.writer.drain()
        except Exception as e:
            logging.warning("We fked up: %s", e)

    async def recv(self, size) -> Tuple[str, Any]:
        """Receive a message from the client.

        Await a message from the client, parse the data as JSON, and deserialize
        it into a python a dict with the form:

        .. code-block:: text

            {
                'type': '<MESSAGE_TYPE>',
                'payload': <ADDITIONAL_DATA>
            }

        Args:
            size (int): Amount of bytes to read from the stream

        Returns:
            A (type, data) tuple, which represents the extracted `type` and
            `payload` fields of the received object.
        """
        header = await self.reader.read(4)
        size = int.from_bytes(header, "little")
        if size > 0xFFF:
            # drop connection. beyond size limit
            ...
        message = await self.reader.read(size)
        deserialized = json.loads(message)
        kind = deserialized["type"]
        data = deserialized["payload"]
        return kind, data

    async def handle(self):
        """Start handling this client

        Main entry point for the client handler.
        First performs the initial handshake to negotiate username, and then
        proceed with handling regular mesasges.
        Check type of received messages and forward to specific handler functions.
        """
        if not await self.perform_handshake():
            return
        await self.writer.drain()
        await self.send(
            Protocol.SERVER_INFO, message=welcome_text.format(name=self.name)
        )
        logging.info("Accepted client %s", self.name)
        while True:
            typ, data = await self.recv(1024)
            if typ == Protocol.MESSAGE:
                await self.handle_message(data)
            elif typ == Protocol.TELL:
                await self.handle_tell(data)
            elif typ == Protocol.COMMAND:
                await self.handle_command(data)

    async def handle_command(self, data):
        """Handle a COMMAND message sent from the client.

        A COMMAND message represents a user command sent from the client, for example a `/SlashCommand`.
        The payload of a COMMAND is an object with a `cmd` field which is the
        command being sent, and optionally an `args` fields with additional
        data. The structure is essentially the same as the (type, payload)
        format used for message objects.

        Args:
            data (dict): The {'cmd': ..., 'args': ...} command object
        """
        cmd = data.get("cmd").upper()
        args = data.get("args")
        logging.info("handling command %s with args %s", cmd, args)
        if cmd == "HELP":
            await self.send(Protocol.SERVER_INFO, message=help_text)
        elif cmd == "NAME":
            newname = args[0]
            if newname in self.server.users:
                await self.send(Protocol.SERVER_INFO, message="Navn optaget")
                return
            self.server.users[newname] = self
            del self.server.users[self.name]
            self.name = newname
        elif cmd == "COLOR":
            try:
                clr = args[0]
                int(clr, 16)
                self.color = clr
            except:
                await self.send(Protocol.SERVER_INFO, message="ugyldigt format")
                return

    async def handle_message(self, data):
        """handle a MESSAGE message.

        Handles a message sent from the client. Simply extract the message from
        the provided object, and forward it to the `Server` for broadcasting.
        MESSAGE does not require arguments.

        Args:
            data (dict): The payload. Expected to just contain a {'message': ...} object
        """
        message = data["message"]
        logging.info("[{} MESSAGE]: {}".format(self.name, message))
        await self.server.broadcast_message(message, self)

    async def handle_tell(self, data):
        """handle a TELL message.

        Handles a message sent from the client to another client.
        Extract the `message` and `target` from the provided payload, and forward to server.

        Args:
            data (dict): The payload. Expected to just contain a {'message': ..., 'target': ...} object
        """
        message = data["message"]
        recepient = data["target"]
        logging.info("[{} TELL]: {}".format(self.name, message))
        target = self.server.users.get(recepient)
        if target:
            payload = dict(message=message, sender=self.name, color=self.color)
            target.send(Protocol.TELL, **payload)
            # TODO: this is not going to work
            await self.send(Protocol.TELL, **payload)
        else:
            await self.send(Protocol.SERVER_INFO, message="User not found")

    async def perform_handshake(self):
        """Performs the initial name negotiation

        Before a client can join the chat, a handshake has to be completed.
        The handshake is simply a 3-message conversation that verifies the
        connection, makes sure that the client connects with a valid, available
        username; server says hello, client requests a name, server welcomes the
        client with the name they were assigned. The client can be assigned a
        different name, if the requested name was already taken.

        +-----------------+------------+------------------+
        | Server          |  direction |  Client          |
        +=================+============+==================+
        |HELLO            |  --->      |                  |
        +-----------------+------------+------------------+
        |                 |  <---      | NAME(requested)  |
        +-----------------+------------+------------------+
        |WELCOME(assigned)|  --->      |                  |
        +-----------------+------------+------------------+

        Returns:
            (bool) Success status of the handshake.
        """
        retry_count = 0
        while True:
            try:
                await self.send(Protocol.SERVER_HELLO)
                typ, data = await self.recv(1024)
                if not typ == Protocol.CLIENT_NAME:
                    raise Exception("Invalid response type. Expected 'NAME'")
                name = data["name"]
                # TODO: This entire thing could be a `Server.accept_user(name)` or something
                suffix = 0
                while name in self.server.users:
                    suffix += 1
                    name = data["name"] + str(suffix)
                self.name = name
                self.server.users[self.name] = self
                self.color = choice(palette)
                await self.send(Protocol.SERVER_WELCOME, name=self.name)
                return True
            except Exception as e:
                logging.warning("[%s]Handshake failed: %s", self, e)
                if retry_count <= 3:
                    logging.info(
                        "[%s]Attempting handshake again. Attempt %s/3",
                        self,
                        retry_count,
                    )
                    retry_count += 1
                    continue
                else:
                    logging.info("[%s]Retry limit reached. dropping client.", self)
                    self.writer.close()
                    return False
