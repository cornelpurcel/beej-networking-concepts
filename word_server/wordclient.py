import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2
ENCODING = "utf-8"


def usage():
    print("usage: wordclient.py server port", file=sys.stderr)


packet_buffer = b""


def get_next_word_packet(s: socket.socket) -> bytes:
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer

    # TODO -- Write me!

    word_packet = process_next_word_packet()
    if word_packet is not None:
        packet_length = len(word_packet)
        packet_buffer = packet_buffer[packet_length:]
        return word_packet

    local_buffer = s.recv(4096)
    if not local_buffer:
        print("connection is closed?")
        return None
    packet_buffer += local_buffer

    word_packet = process_next_word_packet()
    if word_packet is not None:
        packet_length = len(word_packet)
        packet_buffer = packet_buffer[packet_length:]
        return word_packet


def process_next_word_packet() -> bytes:
    if len(packet_buffer) < 2:
        return None

    word_length = int.from_bytes(packet_buffer[:2], "big")

    packet_length = 2 + word_length

    if len(packet_buffer) < packet_length:
        return None

    return packet_buffer[:packet_length]


def extract_word(word_packet: bytes) -> str:
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    # TODO -- Write me!

    word_length = int.from_bytes(word_packet[:2], "big")
    word = word_packet[2:].decode(ENCODING)
    assert len(word) == word_length

    return word


# Do not modify:


def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
