#!/usr/bin/env python3
import sys, logging, asyncio
from server import Server


def main(args):
    ip = args[1]
    server = Server(ip, 50)
    asyncio.run(server.begin_serving())


if __name__ == "__main__":
    fmt = "%(asctime)s - %(funcName)s:%(lineno)d\n[%(levelname)7s]"
    logging.basicConfig(level=logging.DEBUG, format=fmt)
    main(sys.argv)
