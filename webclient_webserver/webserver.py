import os
from pathlib import Path
from string import Template
import socket
import sys

ENCODING = "ISO-8859-1"


class RequestLine:

    def __init__(self, method, url, protocol):
        self.method = method
        self.url = url
        self.protocol = protocol

    def __str__(self):
        return f"method: {self.method} url: {self.url} protocol: {self.protocol}"

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method: str):
        self._method = method

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol: str):
        self._protocol = protocol


class Request:

    def __init__(self, requestString: str):
        self._request = requestString

        self._initRequestLine()

    def _initRequestLine(self):
        endOfRequestLine = self._request.find("\r\n")
        requestLine = self._request[:endOfRequestLine]
        method, url, protocol = requestLine.split(" ")
        self.requestLine = RequestLine(method, url, protocol)

    @property
    def requestLine(self) -> RequestLine:
        return self._requestLine

    @requestLine.setter
    def requestLine(self, requestLine: RequestLine):
        self._requestLine = requestLine

    def __str__(self):
        return self._request


class MyHttpServer:
    httpResponseTemplate = Template(
        "HTTP/1.1 $response_code $response_code_message\r\nContent-Type: $content_type\r\nContent-Length: $content_length\r\nConnection: close\r\n\r\n$content"
    )
    httpResponseTemplateWithoutContent = Template(
        "HTTP/1.1 $response_code $response_code_message\r\nContent-Type: $content_type\r\nContent-Length: $content_length\r\nConnection: close\r\n\r\n"
    )

    responseCodeToMessageMap = {200: "OK", 404: "Not Found", 400: "Bad Request"}
    extensionToMimeTypeMap = {
        ".html": "text/html",
        ".txt": "text/plain",
        ".png": "image/png",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
    }

    def start(self, port: int):

        s: socket.socket = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))

        print(f"listening on port {port}...")
        s.listen()
        while True:
            connectionSocket, connectionAddress = s.accept()
            print(f"accepted connection from {connectionAddress}")
            request: Request = self.receiveRequest(connectionSocket)
            if request is None:
                self.sendResponse(
                    connectionSocket,
                    f"internal error oopsie",
                    500,
                )
                continue
            method = request.requestLine.method
            print(f"req line: {request.requestLine}")
            print(f"req method: {method}")
            print(f"req: \n{request}")

            filename = os.path.split(request.requestLine.url)[-1]
            fileExtension = os.path.splitext(filename)[-1]
            contentType = self.extensionToMimeTypeMap.get(fileExtension)
            if contentType is None:
                self.sendResponse(
                    connectionSocket,
                    f"cannot send files with extension '{fileExtension}'",
                    400,
                )
                continue

            try:
                print(f"trying to open {filename}")
                print(os.getcwd())
                with open(filename, "rb") as fp:
                    data = fp.read()
                    # print(data.decode(ENCODING))
                    self.sendResponseWithBinaryPayload(
                        connectionSocket, data, 200, contentType
                    )
                    continue
            except Exception as e:
                print(f"could not read file '{filename}': {e}")
                self.sendResponse(
                    connectionSocket,
                    f"could not read file '{filename}'",
                    404,
                )
                continue

    def sendResponse(
        self,
        socket: socket.socket,
        content: str,
        responseCode: int = 200,
        contentType: str = "text/plain",
    ):
        contentLength = len(content.encode(ENCODING))
        responseCodeMessage = self.responseCodeToMessageMap.get(
            responseCode, "UNKNOWN_MESSAGE"
        )
        response = self.httpResponseTemplate.substitute(
            {
                "content": content,
                "response_code": responseCode,
                "response_code_message": responseCodeMessage,
                "content_type": contentType,
                "content_length": contentLength,
            }
        )
        print("respone:", response)
        socket.sendall(response.encode(ENCODING))
        socket.close()

    def sendResponseWithBinaryPayload(
        self,
        socket: socket.socket,
        payload: bytes,
        responseCode: int = 200,
        contentType: str = "text/plain",
    ):
        contentLength = len(payload)
        responseCodeMessage = self.responseCodeToMessageMap.get(
            responseCode, "UNKNOWN_MESSAGE"
        )
        response = self.httpResponseTemplateWithoutContent.substitute(
            {
                "response_code": responseCode,
                "response_code_message": responseCodeMessage,
                "content_type": contentType,
                "content_length": contentLength,
            }
        )
        # am curious if 2 calls to sendall work?? :
        print("response without payload ", response)
        socket.sendall(response.encode(ENCODING))
        socket.sendall(payload)
        socket.close()

    def receiveRequest(self, s: socket.socket) -> Request:
        allBytes = bytearray()
        decoded = ""

        while True:
            buffer = s.recv(4096)
            if not buffer:
                print("Client closed connection.")
                break

            allBytes.extend(buffer)

            try:
                decoded = allBytes.decode(ENCODING)
            except UnicodeDecodeError:
                continue  # wait for more bytes

            if "\r\n" in decoded:
                break

        try:
            return Request(decoded)
        except Exception as e:
            print(f"Error constructing Request: {e}")
            return None


def main():
    if len(sys.argv) == 1 or len(sys.argv[1]) == 0:
        print("must specify a port to listen to!")
        return

    port = int(sys.argv[1])

    server = MyHttpServer()
    server.start(port)


if __name__ == "__main__":
    main()
