import argparse
import logging
import time

from socket import socket
from socketserver import (
    TCPServer,
    BaseRequestHandler,
)

SERVER_ADDRESS = "localhost"
SERVER_PORT = 31415
TERMINATION_CHARACTER = "\n"

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--address")
parser.add_argument("--port")


class RequestRethrower(BaseRequestHandler):
    logger = logging.getLogger(f"{__name__}.RequestRethrower")

    def handle(self):
        self.request: socket
        client_address = self.client_address[0]
        self.logger.debug(f"new request from '{client_address}'")
        data = ""
        while True:
            data += self.request.recv(1024).decode()
            if TERMINATION_CHARACTER in data:
                read = data.split(TERMINATION_CHARACTER, 1)[0]
                self.logger.debug(f"[{client_address}] read data: '{read}'")
                self.logger.debug(f"[{client_address}] write data: '{read}'")
                self.request.sendall(f"{read}{TERMINATION_CHARACTER}".encode())
                try:
                    data = data.split(TERMINATION_CHARACTER, 1)[1]
                except IndexError:
                    data = ""
            elif not data:
                break
            else:
                time.sleep(0.1)
        self.logger.debug(f"end of request from '{client_address}'")


if __name__ == "__main__":
    logger = logging.getLogger(f"{__name__}.main")

    args = parser.parse_args()
    address = args.server_address if args.address else SERVER_ADDRESS
    port = args.server_address if args.port else SERVER_PORT

    logger.debug(f"server address '{address}'")

    with TCPServer((address, port), RequestRethrower) as server:
        server.serve_forever()
