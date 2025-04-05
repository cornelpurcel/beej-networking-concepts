import threading
import time
import random


def calculate_sum(id: int, start: int, end: int, results: list[int]):
    result = 0
    for i in range(start, end + 1):
        result += i

    time.sleep(random.randint(1, 100) / 100)
    results[id] = result


def main():
    ranges = [[10, 20], [1, 5], [70, 80], [27, 92], [0, 16]]

    count = len(ranges)
    sums = [0] * count
    all_threads: list[threading.Thread] = []

    for i in range(count):
        thread = threading.Thread(
            target=calculate_sum, args=(i, ranges[i][0], ranges[i][1], sums)
        )
        thread.start()
        all_threads.append(thread)

    for thread in all_threads:
        thread.join()
        print("Joined ", thread.name)

    print("joined all threads!")
    print("ranges: ", ranges)
    print("results: ", sums)


if __name__ == "__main__":
    main()
