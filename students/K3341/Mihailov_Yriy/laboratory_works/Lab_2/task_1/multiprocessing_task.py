import multiprocessing
import time

n = 10 ** 9
num_processes = 10


def calculate_sum(start, end):

    s = 0
    for i in range(start, end + 1):
        s += i

    print('done: s = {}'.format(s))

    return s


if __name__ == '__main__':
    ranges = [(i + 1, i + n // num_processes) for i in range(0, n, n // num_processes)]

    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_sum, ranges)

    total_sum = sum(results)
    print(total_sum)

    print('total time: {}'.format(time.time() - start_time))

    # для проверки
    print((n + 1) * n // 2)