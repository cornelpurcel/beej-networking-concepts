from functools import reduce
from dataclasses import dataclass


@dataclass
class IpInfo:
    subnet: str
    host: str


# Dots-and-Numbers to bytes
def from_dan(ip: str) -> int:
    return reduce(
        lambda x, y: x | y,
        (
            int(number) << ((3 - index) * 8)
            for index, number in enumerate(ip.split("."))
        ),
    )


def to_dan(ip: int) -> str:
    return ".".join(str(ip >> ((3 - index) * 8) & 0xFF) for index in range(4))


def get_subnet_mask(slash: int) -> int:
    if slash < 0 or slash > 32:
        raise ValueError("Invalid subnet mask")

    return ((1 << slash) - 1) << (32 - slash)


def get_subnet(ip: str) -> IpInfo:
    simple_ip, subnet_mask_number = ip.split("/")

    subnet_mask_number = int(subnet_mask_number)
    subnet_mask = get_subnet_mask(subnet_mask_number)

    ip_as_number = from_dan(simple_ip)

    return IpInfo(
        to_dan(subnet_mask & ip_as_number), to_dan(~subnet_mask & ip_as_number)
    )


def test_dan(ip: str):
    number = from_dan(ip)
    string_again = to_dan(number)

    print("original ip:\t", ip)
    print("number:\t\t", number)
    print("number as hex:\t", hex(number))
    print("number as bin:\t", bin(number))
    print("back to string:\t", string_again)


def main():
    test_dan("255.0.254.1")
    test_dan("198.51.100.10")

    print(to_dan(get_subnet_mask(17)))
    print(to_dan(get_subnet_mask(24)))
    print(to_dan(get_subnet_mask(28)))

    print(get_subnet("198.51.100.10/24"))

    test_dan("10.100.30.90")

    print("0xC0A88225 to dan:", to_dan(0xC0A88225))

    print(hex((0x12FF5678 >> 16) & 0xFF))


if __name__ == "__main__":

    main()
