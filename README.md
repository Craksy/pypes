# Pypes Server

This is home of the Pypes Chat Protocol spec, and one possible implementation of the server side.

Ideally the spec will be strict enough that any server or client that implements
it correctly, can work with any other, but also flexible enough to allow for
interpretation where appropriate.


# Protocol

### Format
Communication between client and server is done through JSON serialized objects.
This ensures consistency in message format and eliminates errors related to
manually parsing plain text.

Every message object has a `type` field that determines the kind og message being sent.
A message can optionally have a `payload` field with additional data. 

**Example protocol message object:**
```json
{
    "type": "EXAMPLE_TYPE",
    "payload": {
        "dataKey": "dataValue",
        "otherData": 42
    }
}
```

### Type
The protocol spec is a set of rules that dictates how a client
and server ought to handle certain message types. 
The chat server and the chat client can be coded independently without any knowledge of
implementation details of the other, as long as they both adhere to this set of
rules (i.e. they both correctly implement the protocol)


### Payload
The message payload is a JSON object itself. It can contain any number of fields
or types. The protocol dictates which payload fields are to be expected and how
they should be interpreted. 

Payload fields can be marked as optional. For instance a message from the server could contain a "text_color" field. A client implementation that does not support colored output could be free to ignore it.


## Server message types

#### **SERVER_HELLO**  
  This should be the first message between the client and server, and signifies
  that the connection has been accepted by the server, and that its ready to
  perform the initial handshake. After sending this, the server should await a
  `CLIENT_NAME` message in response.

  **Payload fields:**  
  None

---

#### **SERVER_WELCOME**  
  Sent as response to `CLIENT_NAME`, this completes the handshake and tells the
  client that it was successful. The client should be enabled immediately after `SERVER_WELCOME` has been sent.
  If the client was assigned a different username than the one requested
  in `CLIENT_NAME` it must inform the client via the `name` payload field.

  **Payload fields:**  
  **name:** *the name assigned to the client. If excluded, its assumed that the
  requested name was accepted*

---

#### **SERVER_INFO**
  Represents an info message from the server. Clients should display info messages as slightly emphasized chat entries, in a way that makes them distinct from regular messages.

  **Payload fields:**  
  **message:** *The message to be displayed*

---

#### **SERVER_BANNER**
  Represents a banner message from the server, intended for things like MotD,
  output from commands, or other messages that demands attention or should be
  separated from regular chat output  
  Clients should display banner messages in a strongly emphasized way, possibly with a border or frame.

  **Payload fields:**  
  **message:** *The message to be displayed*  
  **color:** *Color of the banner, used to communicate severity/or type. If,
  where, and how to apply this is up to client implementation.*