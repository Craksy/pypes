import sys
from os import system
from client import Client


def main(args):
    if len(args) < 3:
        print("Invalid arguments. Usage:")
        print("retropy IP USERNAME [--debug]")
        exit()
    if len(args) > 3 and (args[3] == "--debug"):
        DEBUG_MODE = True
    system("cls" if sys.platform == "win32" else "clear")
    client = Client(args[1], args[2])


if __name__ == "__main__":
    main(sys.argv)
