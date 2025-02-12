import socket
import sys

ENCODING = "ISO-8859-1"


class MyHttpServer:
    def start(self, port: int):
        dummyHttpResponse: str = (
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\nConnection: close\r\n\r\nHello!"
        )

        s: socket.socket = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))

        print(f"listening on port {port}...")
        s.listen()
        while True:
            connectionSocket, connectionAddress = s.accept()
            print(f"accepted connection from {connectionAddress}")
            request: Request = self.receiveRequest(connectionSocket)
            method = request._requestLine.method
            print(f"req line: {request._requestLine}")
            print(f"req method: {method}")
            print(f"req: \n{request}")
            connectionSocket.sendall(dummyHttpResponse.encode(ENCODING))
            connectionSocket.close()

    def receiveRequest(self, s: socket.socket) -> str:
        resultString: str = ""
        buffer = s.recv(4096)
        decodedString = buffer.decode(ENCODING)
        resultString += decodedString
        while "\r\n" not in decodedString:
            buffer = s.recv(4096)
            decodedString = buffer.decode(ENCODING)
            resultString += decodedString

        return Request(resultString)


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


def main():
    if len(sys.argv) == 1 or len(sys.argv[1]) == 0:
        print("must specify a port to listen to!")
        return

    port = int(sys.argv[1])

    server = MyHttpServer()
    server.start(port)


if __name__ == "__main__":
    main()
