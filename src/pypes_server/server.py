import logging
from asyncio.streams import StreamReader, StreamWriter, start_server

import protocol
import serverclient

PORT = 42069

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


class Server:
    """The server instance.

    Listens for and accept incomming connections, and assign them client handlers.
    Also responsible for anything that involves communication between clients,
    or things that alter the state of the server.

    Attributes:
        users(dict): A dictionary mapping names to client handlers
    """

    def __init__(self, ip: str, max_connections: int = 50):
        """Initialize the server

        Args:
            ip (str): The address to host the server on
            max_connections (int): Max number of users that can connect
        """
        self.users: dict[str, serverclient.UserClient] = {}
        self.host = (ip, PORT)

    async def begin_serving(self):
        """Begin listening for incomming connections"""
        logging.info("Starting server")
        self.server = await start_server(self.client_handler, *self.host)
        async with self.server:
            await self.server.serve_forever()

    async def broadcast_message(self, message: str, sender: serverclient.UserClient):
        """Broadcast a message to all users

        Args:
            message (str): The message to broadcast
            sender (UserClient): The client that sent the message
        """
        payload = {"message": message, "sender": sender.name, "color": sender.color}
        for user in self.users.values():
            try:
                user.send(
                    protocol.Protocol.MESSAGE,
                    message=message,
                    sender=sender.name,
                    color=sender.color,
                )
            except ConnectionError:
                logging.warning("Failed to broadcast to %s.", user)
                self.drop_user(user)

    def broadcast_info(self, message):
        payload = {"message": message}

    def drop_user(self, user: serverclient.UserClient, reason: str = None):
        """Drop a client"""
        logging.info("Dropping user %s", user)
        # user.drop(reason)
        if user.name and user.name in self.users:
            del self.users[user.name]

    async def client_handler(self, reader: StreamReader, writer: StreamWriter):
        """Accept a connection and create a handler for the new client"""
        client = None
        try:
            client = serverclient.UserClient(reader, writer, self)
            await client.handle()
        except:
            ...
        finally:
            if client and client.name in self.users:
                self.users.pop(client.name, None)
