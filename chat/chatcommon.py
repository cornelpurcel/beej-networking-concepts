import socket
import json
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


BUFFER_SIZE = 16
ENCODING = "utf-8"


class MessageType(str, Enum):
    HELLO = "hello"
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"


@dataclass
class ChatMessage:
    type: MessageType
    message: str
    nickname: str


class ChatSocket:
    sock: socket.socket
    socket_buffer = bytes()

    def __init__(self, sock: socket.socket):
        self.sock = sock

    def get_next_packet(self) -> ChatMessage | None:
        logger.debug("getting next packet...")

        # pray to god we eventually get out of this loop:
        # TODO: add max iterations? like 1000 or something
        while True:
            logger.debug(f"Before reading bytes buffer is: '{self.socket_buffer}'")
            local_buffer = self.sock.recv(BUFFER_SIZE)
            logger.debug(f"READ BYTES: '{local_buffer}'")

            read_bytes = len(local_buffer)
            self.socket_buffer += local_buffer
            logger.debug(
                f"After reading bytes, extended buffer is: '{self.socket_buffer}'"
            )

            next_packet = self.process_next_packet()

            if next_packet is not None:
                return self.deserialize_message(next_packet)

            if next_packet is None and (not local_buffer or read_bytes == 0):
                logger.debug(
                    "Next packet is none and could not read more bytes. Connection is closed?"
                )
                return None

            if next_packet is None:
                logger.debug("looping again to read more bytes...")

    def deserialize_message(self, packet: bytes):
        # first two bytes are size of the message, so truncate it:
        payload = packet[2:]
        content_string = payload.decode(ENCODING)
        logger.debug(f"trying to deserialize string {content_string}")
        content_dict: dict = json.loads(content_string)

        message_type = content_dict.get("type", None)
        if message_type is None:
            return None

        message_content = content_dict.get("message", None)
        message_nickname = content_dict.get("nickname", None)

        return ChatMessage(message_type, message_content, message_nickname)

    def process_next_packet(self) -> bytes:
        logger.debug(
            f"processing next packet... {len(self.socket_buffer)} bytes available"
        )
        logger.debug(f"current buffer: {self.socket_buffer}")
        if len(self.socket_buffer) < 2:
            logger.debug("less than 2 bytes available")
            return None

        payload_length = int.from_bytes(self.socket_buffer[:2], "big")

        packet_length = payload_length + 2
        logger.debug(f"seems like packet length is {packet_length}")

        if len(self.socket_buffer) < packet_length:
            logger.debug(
                f"length of buffer ({len(self.socket_buffer)}) smaller than packet length ({packet_length})"
            )
            return None

        packet = self.socket_buffer[:packet_length]

        # truncate the buffer:
        logger.debug("truncating buffer...")
        self.socket_buffer = self.socket_buffer[packet_length:]
        return packet

    def send_message(self, message: ChatMessage):

        message_string = json.dumps(asdict(message))
        logger.debug(f"Sending message {message_string}")
        message_bytes = message_string.encode(ENCODING)

        message_length = len(message_bytes)
        logger.debug(f"Sending message with length {message_length}")

        final_packet = message_length.to_bytes(2, "big") + message_bytes

        self.sock.sendall(final_packet)

        return
