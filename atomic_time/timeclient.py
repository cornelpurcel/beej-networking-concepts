import socket
import time

NIST_HOST = "time.nist.gov"
NIST_PORT = 37


def getSystemSeconsSince1990():
    """
    The time server returns the number of seconds since 1990, but Unix
    systems return the number of seconds since 1970. This function
    computes the number of seconds since 1900 on the system.
    """

    # Number of seconds between 1900-01-01 and 1970-01-01
    secondsDelta = 2208988800

    secondsSinceUnixEpoch = int(time.time())
    secondsSince1900Epoch = secondsSinceUnixEpoch + secondsDelta

    return secondsSince1900Epoch


class NISTClient:
    def getNISTTime(self) -> int:
        s = socket.socket()

        s.connect((NIST_HOST, NIST_PORT))
        timeBytes = self.receiveTime(s)

        return int.from_bytes(timeBytes, "big")

    def receiveTime(self, s: socket.socket) -> bytearray:
        allBytes = bytearray()

        while True:
            buffer = s.recv(4096)

            if not buffer:
                print("client closed connection...")
                break

            allBytes.extend(buffer)

        return allBytes


def main():

    nistClient = NISTClient()

    nistTime = nistClient.getNISTTime()
    systemTime = getSystemSeconsSince1990()

    print(f"NIST time\t:\t{nistTime}")
    print(f"System time\t:\t{systemTime}")


if __name__ == "__main__":
    main()
