===================
Pypes documentation
===================




.. toctree::
   :hidden:

   modules

Overview
--------

This is the Pypes Chat Protocol spec and example implementations for server and client.

The protocol spec defines a set of rules for communication between Pypes servers
and clients. Ideally, it should be possible to make an implementation entirely
based on this spec. Clients and servers does not need to know implementation of
the other, only that they follow the same protocol.

Hopefully this will make it a good environment for collaboration between
students; anyone is free to make their own implementation of a server or client,
in any language they like, or contribute to an existing one guided by the specification.

Furthermore, the protocol itself is meant to be a collaboration.

Basics of the protocol
----------------------

All Communication between client and server happens through ``messages`` which are
just JSON objects. This ensures consistency and eliminates errors related to
manually parsing plain text. Just about every language provides a
JSON-serializer in some form, so it seems like an ideal format for something
that’s meant to be language agnostic.

Every message object has a \`type\` field and optionally a \`payload\` field with additional data.

An example of a message:

.. code:: json

    {
        "type": "EXAMPLE_TYPE",
        "payload": {
            "dataKey": "dataValue",
            "otherData": 42
        }
    }

The protocol spec is simply a set of rules that describe how to interpret and
respond to such messages.

Message Types
-------------

The message type is the primary way that servers and clients decide how to react to a received message.
Some message types exists for both client and server and can mean have different
meanings depending on the direction, but will usually be part of the same exchange.

For instance, the type ``MESSAGE``, when sent from a **client** means that the client
want to send a public chat message. The server reacts to this by broadcasting a
``MESSAGE`` with information about that client in the payload, and so when a
client receives it, it should be interpreted as “someone else sent a message”.

Server message types
~~~~~~~~~~~~~~~~~~~~

SERVER\_HELLO
^^^^^^^^^^^^^

This should be the first message between the client and server, and signifies
that the connection has been accepted by the server, and that its ready to
perform the initial handshake. After sending this, the server should await a
``CLIENT_NAME`` message in response.

**Payload fields:**
None


------------

SERVER\_WELCOME
^^^^^^^^^^^^^^^

Sent as response to ``CLIENT_NAME``, this completes the handshake and tells the
client that it was successful. The client should be enabled immediately after ``SERVER_WELCOME`` has been sent.
If the client was assigned a different username than the one requested
in ``CLIENT_NAME`` it must inform the client via the ``name`` payload field.

**Payload fields:**

- ``name``: the name assigned to the client. If excluded, its assumed that the
  requested name was accepted


------------

SERVER\_INFO
^^^^^^^^^^^^

Represents an info message from the server. Clients should display info messages as slightly emphasized chat entries, in a way that makes them distinct from regular messages.

**Payload fields:**

- ``message``: The message to be displayed


------------

SERVER\_BANNER
^^^^^^^^^^^^^^

Represents a banner message from the server, intended for things like MotD,
output from commands, or other messages that demands attention or should be
separated from regular chat output
Clients should display banner messages in a strongly emphasized way, possibly with a border or frame.

**Payload fields:**

- ``message``: The message to be displayed

- ``color``: Color of the banner, used to communicate severity/or type. If,
  where, and how to apply this is up to client implementation.
