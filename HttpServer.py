#!/usr/bin/env python3

import mimetypes
import os
from TcpServer import TcpServer
from http import HTTPStatus, HTTPMethod


class HttpRequest:
    def __init__(self, raw):
        lines = raw.split(b"\r\n")
        request_line = [l.decode() for l in lines[0].split(b" ")]

        # self.method = HTTPMethod[request_line[0]]
        self.method = getattr(HTTPMethod, request_line[0])

        self.uri = request_line[1] if len(request_line) > 1 else None
        self.http_version = request_line[2] if len(request_line) > 2 else "1.1"

    def __repr__(self):
        return f'{type(self).__name__}({", ".join([f"{k}={v}" for k, v in vars(self).items()])})'


class HttpServer(TcpServer):
    def handler(self, data):
        request = HttpRequest(data)

        print(f"Handing {request}")

        try:
            handler_method = getattr(self, f"handler_{request.method.value}")
            return handler_method(request)
        except AttributeError:
            return self.error_handler_501()

    def handler_GET(self, request):
        filename = request.uri.strip("/")

        if os.path.exists(filename):
            STATUS = self.status(HTTPStatus.OK)
            HEADERS = self.headers(
                {"Content-Type": mimetypes.guess_type(filename)[0] or "text/html"}
            )
            BLANK = b"\r\n"

            with open(filename, "rb") as f:
                BODY = f.read()

            return b"".join([STATUS, HEADERS, BLANK, BODY])

        else:
            return self.error_handler_404()

    def error_handler_404(self):
        STATUS = self.status(HTTPStatus.NOT_FOUND)
        HEADERS = self.headers()
        BLANK = b"\r\n"
        BODY = b"""
            <h1>404 Not Found</h1>
        """

        return b"".join([STATUS, HEADERS, BLANK, BODY])

    def error_handler_501(self):
        STATUS = self.status(HTTPStatus.NOT_IMPLEMENTED)
        HEADERS = self.headers()
        BLANK = b"\r\n"

        BODY = b"""
            <h1>501 Not Implemented</h1>
        """

        return b"".join([STATUS, HEADERS, BLANK, BODY])

    def status(self, status_code):
        return f"HTTP/1.1 {status_code.value} {status_code.phrase}\r\n".encode()

    def headers(self, additional={}):
        always = {"Server": "Apprendre Web Server", "Content-Type": "text/html"}

        return b"".join(
            [
                f"{key}: {value}\r\n".encode()
                for key, value in (always | additional).items()
            ]
        )


if __name__ == "__main__":
    server = HttpServer()
    server.run()
