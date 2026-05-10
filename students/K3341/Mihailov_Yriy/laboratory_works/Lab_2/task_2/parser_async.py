import sys
import time
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from parser_main import _parse_and_save_async, URLS, USER_ID, DB_URL


async def main():

    start = time.time()
    engine = create_async_engine(DB_URL)

    tasks = []
    for url in URLS:
        tasks.append(_parse_and_save_async(url, USER_ID, engine))

    await asyncio.gather(*tasks)
    print(f"Total time (async): {time.time() - start}")


if __name__ == "__main__":

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())