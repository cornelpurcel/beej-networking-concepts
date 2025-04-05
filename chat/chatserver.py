from dataclasses import dataclass
import socket
import sys
import select
import logging

from chatcommon import ChatSocket, MessageType, ChatMessage

logging.basicConfig(
    format="{asctime} - [{levelname}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


@dataclass
class ChatUser:
    nickname: str


@dataclass
class ChatSession:
    chat_socket: ChatSocket
    # when session is first established, we do not know the user's identity.
    # It will get populated later when the user sends a HELLO message
    # TODO: do not accept messages from user if identity has not been established through a HELLO message
    # TODO: check that identity matches with the nickname in incoming messages
    user: ChatUser | None


class ChatServer:
    port: int

    read_sockets: set[socket.socket] = set()
    receiving_sockets: dict[socket.socket, ChatSession] = {}

    def __init__(self, port: int):
        self.port = port

    def run(self):
        lsock: socket.socket = socket.socket()
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind(("", self.port))

        logger.info(f"listening on port {self.port}...")
        lsock.listen()
        self.read_sockets.add(lsock)

        self.poll_current_connections()

    def poll_current_connections(self):
        while True:
            ready_to_read: list[socket.socket]
            ready_to_read, _, _ = select.select(self.read_sockets, [], [])

            for sock in ready_to_read:
                if sock in self.receiving_sockets.keys():
                    self.serve_established_connection(self.receiving_sockets[sock])
                else:
                    self.serve_new_connection(sock)

    def terminate_session(self, chat_session: ChatSession):
        raw_sock = chat_session.chat_socket.sock

        peer_address = raw_sock.getpeername()

        self.read_sockets.remove(raw_sock)
        self.receiving_sockets.pop(raw_sock)

        nickname = chat_session.user.nickname
        logger.info(f"Terminated session for {nickname} at {peer_address}")
        self.broadcast_leave_message(nickname)

    def serve_established_connection(self, chat_session: ChatSession):

        chat_sock = chat_session.chat_socket
        chat_message = chat_sock.get_next_packet()

        if chat_message is None:
            logger.debug("next message from socket was None, disconnecting socket...")
            self.terminate_session(chat_session)
            return

        match chat_message.type:
            case MessageType.CHAT:
                self.handle_chat_message(chat_message)
            case MessageType.HELLO:
                self.handle_hello_message(chat_session, chat_message)
            case _:
                # the other types of messages can only originate from server
                # so this match should never have them
                raise ValueError(
                    f"Unexpected message type received in server: {chat_message.type}"
                )

        logger.debug(f"got message {chat_message}")

    def serve_new_connection(self, sock: socket.socket):
        receiving_sock, connection_addr = sock.accept()
        logger.info(f"{connection_addr} connected...")
        self.read_sockets.add(receiving_sock)
        self.receiving_sockets[receiving_sock] = ChatSession(
            chat_socket=ChatSocket(receiving_sock), user=None
        )

    def handle_chat_message(self, chat_message: ChatMessage) -> None:
        nickname = chat_message.nickname
        message = chat_message.message

        logger.info(
            f"{nickname} sends CHAT message with '{message}'. Broadcasting to everybody..."
        )

        self.broadcast_message(chat_message)

    def handle_hello_message(
        self, chat_session: ChatSession, chat_message: ChatMessage
    ) -> None:
        nickname = chat_message.nickname
        logger.debug(f"{nickname} says HELLO. Sending JOIN message to everybody...")

        if chat_session.user is not None:
            raise ValueError(
                f"User at {chat_session.chat_socket.sock.getpeername()} has already established their identity: {chat_session.user}"
            )

        logger.debug(
            f"Setting user with nickname {nickname} for user connected at {chat_session.chat_socket.sock.getpeername()}"
        )
        chat_session.user = ChatUser(nickname)
        self.broadcast_join_message(nickname)

    def broadcast_join_message(self, nickname):
        """Broadcast nickname has joined to all connected sockets"""
        join_message = ChatMessage(type=MessageType.JOIN, message="", nickname=nickname)

        self.broadcast_message(join_message)

    def broadcast_leave_message(self, nickname):
        """Broadcast nickname has left to all connected sockets"""
        leave_message = ChatMessage(
            type=MessageType.LEAVE, message="", nickname=nickname
        )

        self.broadcast_message(leave_message)

    def broadcast_message(self, message: ChatMessage):
        """Broadcast message to all connected sockets"""
        for socket, chat_session in self.receiving_sockets.items():
            nickname = chat_session.user.nickname
            logger.debug(f"Sending message to {nickname} at {socket.getpeername()}")
            chat_session.chat_socket.send_message(message)


def main(argv: list[str]):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    chatServer = ChatServer(port)
    chatServer.run()


def usage():
    print("usage: chatserver.py port", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
