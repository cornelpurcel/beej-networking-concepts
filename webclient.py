import socket
import sys

ENCODING = "ISO-8859-1"


class MyHttpClient:
    def get(self, host: str) -> str:
        dummyHttpRequest: str = (
            f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        )

        s: socket.socket = socket.socket()
        s.connect((host, 80))
        s.sendall(dummyHttpRequest.encode(ENCODING))

        res = self.waitForResponse(s)
        s.close()

        return res

    def waitForResponse(self, s: socket.socket) -> str:
        response: bytearray = bytearray()
        buffer = s.recv(4096)
        response.extend(buffer)
        while len(buffer) != 0:
            buffer = s.recv(4096)
            response.extend(buffer)

        return bytes(response).decode(ENCODING)


def main():
    if len(sys.argv) == 1:
        print("must specify a website to GET")
        return

    if len(sys.argv) == 2:
        host = sys.argv[1]

        client = MyHttpClient()
        res = client.get(host)
        print(f"res: {res}")

    if len(sys.argv) == 3:
        host = sys.argv[1]
        imagePath = sys.argv[2]

        client = MyHttpClient()
        res = client.get(host)
        print(f"res: {res}")


if __name__ == "__main__":
    main()
