from datetime import datetime, timezone

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv, dotenv_values
from models import Task
import asyncio
import sys

load_dotenv()

DB_URL = dotenv_values(".env")["DB_URL"]

URLS = [
    "https://github.com/python/cpython/issues",
    "https://github.com/django/django/issues",
    "https://github.com/pallets/flask/issues",
    "https://github.com/fastapi/fastapi/issues",
    "https://github.com/microsoft/vscode/issues",
    "https://github.com/facebook/react/issues",
    "https://github.com/angular/angular/issues",
    "https://github.com/vuejs/core/issues",

    "https://github.com/numpy/numpy/issues",
    "https://github.com/pandas-dev/pandas/issues",
    "https://github.com/tensorflow/tensorflow/issues",
    "https://github.com/pytorch/pytorch/issues",
    "https://github.com/scikit-learn/scikit-learn/issues",

    "https://github.com/encode/httpx/issues",
    "https://github.com/aio-libs/aiohttp/issues",
    "https://github.com/sqlalchemy/sqlalchemy/issues"
]

USER_ID = 3


def extract_fields(html):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True)[:255] if soup.title else ""

    meta = soup.find("meta", attrs={"property": "og:description"}) or soup.find(
        "meta", attrs={"name": "description"}
    )
    description = meta.get("content", "") if meta else ""
    description = description[:255] if description else ""
    rel = soup.find("relative-time")
    if rel and rel.get("datetime"):
        deadline = datetime.fromisoformat(rel["datetime"].replace("Z", "+00:00"))
    else:
        deadline = datetime.now(timezone.utc)

    return title, description, deadline


async def _parse_and_save_async(url, user_id, engine):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            html = await resp.text()
            title, description, deadline = extract_fields(html)

            async with AsyncSession(engine) as db_session:
                new_task = Task(title=title, owner_user_id=user_id,
                                description=description, deadline=deadline)
                db_session.add(new_task)
                await db_session.commit()
    print(f"Saved: {title}")


def parse_and_save(url, user_id):
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    local_engine = create_async_engine(DB_URL)

    try:
        return asyncio.run(_parse_and_save_async(url, user_id, local_engine))
    finally:
        asyncio.run(local_engine.dispose())



