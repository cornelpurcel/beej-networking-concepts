import threading
import sys
import socket
from chatcommon import ChatSocket, ChatMessage, MessageType

from chatui import (
    init_windows,
    read_command,
    print_chat_message,
    print_message,
    end_windows,
)

# TODO quit program if server has been terminated

stop_event = threading.Event()


class ChatClient:
    BUFFER_SIZE = 16

    output_section_drawing_thread: threading.Thread
    chat_socket: ChatSocket

    nickname: str
    host: str
    port: int

    def draw_output_section(self):

        while True:
            message = self.chat_sock.get_next_packet()
            if message is None:
                print(
                    "Could not read any message, server probably stopped... exiting daemon thread..."
                )
                print("Signalling main thread to also stop, press Enter to exit...")
                stop_event.set()
                return

            print_chat_message(message)

    def start(self, nickname: str, host: str, port: int):
        self.nickname = nickname

        # connect to the server:
        sock = socket.socket()
        sock.connect((host, port))
        self.chat_sock = ChatSocket(sock)

        # we need to say hello so that server knows our identity
        self.chat_sock.send_message(
            ChatMessage(MessageType.HELLO, nickname=nickname, message="")
        )

        init_windows()

        output_section_drawing_thread = threading.Thread(
            target=self.draw_output_section, daemon=True
        )
        output_section_drawing_thread.start()

        # loop until daemon thread exits and sets the stop event
        while True and not stop_event.is_set():
            try:
                message_content = read_command(f"{self.nickname}> ")
            except:
                break

            message = ChatMessage(
                MessageType.CHAT, message=message_content, nickname=nickname
            )
            self.chat_sock.send_message(message)

        end_windows()


def main(argv: list[str]):
    try:
        port = int(argv[3])
        nickname = argv[1]
        host = argv[2]
    except:
        usage()
        return 1

    chatClient = ChatClient()
    chatClient.start(nickname, host, port)


def usage():
    print("usage: chatclient.py nickname host port", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
