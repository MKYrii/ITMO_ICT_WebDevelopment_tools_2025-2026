import threading
import time

n = 10 ** 9
num_threads = 10
lock = threading.Lock()

sums = 0


def calculate_sum(start, end):
    global sums
    s = 0
    for i in range(start, end + 1):
        s += i

    print('done: s = {}'.format(s))

    lock.acquire()
    sums += s
    lock.release()


if __name__ == "__main__":
    ranges = [(i + 1, i + n // num_threads) for i in range(0, n, n // num_threads)]

    threads = []

    start_time = time.time()

    for i in range(num_threads):
        start, end = ranges[i][0], ranges[i][1]

        thread = threading.Thread(target=calculate_sum, args=(start, end))
        threads.append(thread)

        thread.start()

    for thread in threads:
        thread.join()


    print(sums)
    print(time.time() - start_time)

    # для проверки
    print((n + 1) * n // 2)