import sys
import typing
from dataclasses import dataclass


@dataclass
class AddressInfo:
    adress_from: bytes
    adress_to: bytes


@dataclass
class TcpValidationData:
    addresses: AddressInfo
    data: typing.ByteString


def ip_string_to_bytes(ip_string: str) -> bytes:
    return b"".join([int(number).to_bytes(1, "big") for number in ip_string.split(".")])


def readData() -> list[TcpValidationData]:
    result = []
    for i in range(10):
        addresses: AddressInfo
        tcp_data: bytes

        addresses_filename = f"tcp_data/tcp_addrs_{i}.txt"
        tcp_data_filename = f"tcp_data/tcp_data_{i}.dat"

        with open(addresses_filename, "r") as addresses_file:
            contents = addresses_file.read()
            raw_addresses = contents.strip().split(" ")
            addresses = AddressInfo(
                ip_string_to_bytes(raw_addresses[0]),
                ip_string_to_bytes(raw_addresses[1]),
            )

        with open(tcp_data_filename, "rb") as tcp_data_file:
            tcp_data = tcp_data_file.read()

        result.append(TcpValidationData(addresses, tcp_data))

    return result


def extract_original_checksum(tcp_data: bytes):
    return tcp_data[16:18]


def construct_pseudo_header(addresses: AddressInfo, tcp_length: int):
    result = (
        addresses.adress_from
        + addresses.adress_to
        + b"\00"
        + b"\06"
        + tcp_length.to_bytes(2, "big")
    )
    return result


def compute_checksum(
    tcp_data: bytes, addresses: AddressInfo, verbose: bool = False
) -> bytes:
    tcp_zero_checksum = tcp_data[:16] + b"\x00\x00" + tcp_data[18:]

    header = construct_pseudo_header(addresses, len(tcp_zero_checksum))

    # pad to right so that it has even number of bytes:
    if len(tcp_zero_checksum) % 2 == 1:
        tcp_zero_checksum += b"\x00"

    data = header + tcp_zero_checksum

    if verbose:
        print("tcp_data:\t\t", tcp_data.hex())
        print("tcp_zero_checksum:\t", tcp_zero_checksum.hex())
        print(f"length of pseudo header: {len(header)}")
        print(f"header itself:\t\t {header.hex()}")
        print("data:\t\t\t", data.hex())

    offset = 0
    total = 0

    while offset < len(data):
        # Slice 2 bytes and get their value

        word = int.from_bytes(data[offset : offset + 2], "big")

        total += word
        total = (total & 0xFFFF) + (total >> 16)  # carry around

        offset += 2  # go to the next 2-byte value

    return (~total) & 0xFFFF


if __name__ == "__main__":

    verbose = False
    if len(sys.argv) >= 2 and sys.argv[1] == "verbose":
        verbose = True

    data = readData()
    for i, example in enumerate(data):

        original_checksum = extract_original_checksum(example.data)

        our_checksum = compute_checksum(example.data, example.addresses, verbose)
        our_checksum_bytes = our_checksum.to_bytes(2, "big")

        if verbose:
            print("original checksum:\t", original_checksum.hex())
            print("our checksum:\t\t", our_checksum_bytes.hex())

            print("[raw] original checksum:\t", original_checksum)
            print("[raw] our checksum:\t\t", our_checksum_bytes)

        verdict = "PASS" if original_checksum == our_checksum_bytes else "FAIL"
        print(f"{i} {verdict}")

        print(
            "\n---------------------------------------------------------------------------------------------------\n"
        )
        # print(i)
        # print(example.addresses)
        # print("...")
        # print(example.data)
