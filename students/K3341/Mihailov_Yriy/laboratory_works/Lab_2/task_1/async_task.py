import asyncio
import time

n = 10**9
num_threads = 10

async def calculate_sum_async(start, end):
    return await asyncio.to_thread(calculate_sum_sync, start, end)

def calculate_sum_sync(start, end):
    s = 0
    for i in range(start, end + 1):
        s += i
    print(f'done for {start} to {end}')
    return s

async def main():
    ranges = [(i + 1, i + n // num_threads) for i in range(0, n, n // num_threads)]

    start_time = time.time()

    tasks = []
    for i in range(num_threads):
        tasks.append(calculate_sum_async(ranges[i][0], ranges[i][1]))

    results = await asyncio.gather(*tasks)

    print('done: sum = {}'.format(sum(results)))
    print('done: time = {}'.format(time.time() - start_time))

    # для проверки
    print((n + 1) * n // 2)

if __name__ == '__main__':
    asyncio.run(main())