#!/usr/bin/env python3.12

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

        handler_method = getattr(
            self, f"handler_{request.method.value}", self.error_handler_501
        )
        return handler_method(request)

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
            return self.error_handler_404(request)

    def handler_OPTIONS(self, request):
        STATUS = self.status(HTTPStatus.OK)
        HEADERS = self.headers(
            {
                "Allow": ", ".join(
                    [m.strip("handler_") for m in dir(self) if m.startswith("handler_")]
                )
            }
        )
        BLANK = b"\r\n"
        BODY = b""

        return b"".join([STATUS, HEADERS, BLANK, BODY])

    def error_handler(self, status):
        STATUS = self.status(status)
        HEADERS = self.headers()
        BLANK = b"\r\n"
        BODY = f"<h1>{status.value} {status.phrase}</h1>".encode()

        return b"".join([STATUS, HEADERS, BLANK, BODY])

    def error_handler_404(self, request):
        return self.error_handler(HTTPStatus.NOT_FOUND)

    def error_handler_501(self, request):
        return self.error_handler(HTTPStatus.NOT_IMPLEMENTED)

    def status(self, status_code):
        return f"HTTP/1.1 {status_code.value} {status_code.phrase}\r\n".encode()

    def headers(self, additional={}):
        always = {"Server": "Apprendre Web Server"}

        return b"".join(
            [
                f"{key}: {value}\r\n".encode()
                for key, value in (always | additional).items()
            ]
        )


if __name__ == "__main__":
    server = HttpServer()
    server.run()
