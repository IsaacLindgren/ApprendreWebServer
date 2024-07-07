#!/usr/bin/env python3

import socket


class TcpServer:
    def run(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port

        # create an INET, STREAMing socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a well-known port
        serversocket.bind((self.host, self.port))

        # become a server socket
        serversocket.listen(5)

        while True:
            (clientsocket, address) = serversocket.accept()

            print(f"Accepted client at {address}")

            ret = self.handler(clientsocket.recv(1024))
            clientsocket.sendall(ret)

            clientsocket.close()

    def handler(self, data):
        return data


if __name__ == "__main__":
    server = TcpServer()
    server.run()
