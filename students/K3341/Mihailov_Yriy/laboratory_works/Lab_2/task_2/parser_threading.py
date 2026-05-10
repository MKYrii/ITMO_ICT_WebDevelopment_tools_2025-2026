import threading
import time

from parser_main import parse_and_save, URLS, USER_ID


def thread_worker(url, user_id):
    parse_and_save(url, user_id)


def main():
    threads = []

    start = time.perf_counter()
    for url in URLS:
        t = threading.Thread(target=thread_worker, args=(url, USER_ID))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print(f"Total time (threading): {time.perf_counter() - start:.5f}s")


if __name__ == "__main__":
    main()