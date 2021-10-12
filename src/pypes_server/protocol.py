
class Protocol:
    """
    Binds protocol identifiers to names.
    """

    # ?: Should there be SERVER and CLIENT prefixes? There is never any
    # ?: uncertainty about the source of a message. It provides a bit of clarity at most.
    DROP           = "DROP"
    MESSAGE        = "MESSAGE"
    COMMAND        = "COMMAND"
    SERVER_HELLO   = "SERVER_HELLO"
    SERVER_WELCOME = "SERVER_WELCOME"
    SERVER_INFO    = "SERVER_INFO"
    SERVER_BANNER  = "SERVER_BANNER"
    CLIENT_NAME    = "CLIENT_NAME"
    CLIENT_CMD     = "CLIENT_CMD"
    TELL           = "TELL"