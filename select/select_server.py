# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select


def run_server(port):
    lsock: socket.socket = socket.socket()
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind(("", port))

    print(f"listening on port {port}...")
    lsock.listen()

    read_sockets: set[socket.socket] = {lsock}
    receiving_sockets: set[socket.socket] = set()

    while True:
        ready_to_read: list[socket.socket]
        ready_to_read, _, _ = select.select(read_sockets, [], [])

        for sock in ready_to_read:
            if sock in receiving_sockets:
                try:
                    sock_address = sock.getpeername()
                except OSError as e:
                    print("error while getting peer name of connected socket: ", e)
                    print("disconnecting socket...")
                    read_sockets.remove(sock)
                    receiving_sockets.remove(sock)
                    continue

                buffer = sock.recv(4096)
                if buffer is None or len(buffer) == 0:
                    print(sock_address, ": disconnected")
                    read_sockets.remove(sock)
                    receiving_sockets.remove(sock)
                    continue

                print(f"{sock_address} {len(buffer)} bytes: ", buffer)
            else:
                receiving_sock, connection_addr = sock.accept()
                print(connection_addr, ": connected")
                read_sockets.add(receiving_sock)
                receiving_sockets.add(receiving_sock)


# --------------------------------#
# Do not modify below this line! #
# --------------------------------#


def usage():
    print("usage: select_server.py port", file=sys.stderr)


def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
