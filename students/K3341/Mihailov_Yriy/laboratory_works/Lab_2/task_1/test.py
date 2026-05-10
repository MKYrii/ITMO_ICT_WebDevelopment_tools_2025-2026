import time


def run_test():
    n = 10 ** 9
    num_threads = 10
    s = 0
    start_time = time.time()

    ranges = [(i + 1, i + n // num_threads) for i in range(0, n, n // num_threads)]

    for i in range(num_threads):
        p = 0
        for j in range(ranges[i][0], ranges[i][1] + 1):
            p += j
        s += p

    print(s)
    print(time.time() - start_time)


if __name__ == '__main__':
    run_test()