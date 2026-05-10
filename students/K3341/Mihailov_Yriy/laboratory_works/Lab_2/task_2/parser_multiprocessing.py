import multiprocessing
import time

from parser_main import parse_and_save, URLS, USER_ID


def process_worker(url, user_id):
    parse_and_save(url, user_id)


def main():
    processes = []

    start = time.perf_counter()
    for url in URLS:
        p = multiprocessing.Process(target=process_worker, args=(url, USER_ID))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print(f"Total time (multiprocessing): {time.perf_counter() - start:.5f}s")


if __name__ == "__main__":
    main()