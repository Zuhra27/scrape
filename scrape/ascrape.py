import asyncio
import logging
import pathlib
from asyncio import Semaphore

from aiohttp import ClientSession


async def fetch(url:str, session:ClientSession, param:list, page=None):
    async with session.get(url =url, params = param) as response:
        html_body = await response.read()
        return {"body": html_body, "page": page}


async def fetch_with_sem(sem:Semaphore, url:str, session:ClientSession, param:list, page=None):
    async with sem:
        return await fetch(url, session, param, page)


async def main(start_page:int=1, last_page:int=15):
    logging.basicConfig(level=logging.DEBUG)
    tasks = []
    base_url = input("Enter your base url: ")
    param_key = input("Enter your param url key: ")
    sem = Semaphore(10)
    async with ClientSession() as session:
        for i in range(0, last_page):
            page = start_page + i
            param = {param_key : page}
            tasks.append(
                asyncio.create_task(
                    fetch_with_sem(sem, base_url, session, param, page=page)
                )
            )
        pages_content = await asyncio.gather(
            *tasks
        )
        return pages_content


results = asyncio.run(main())

output_dir = pathlib.Path().resolve() / "snapshots/pages"
output_dir.mkdir(parents=True, exist_ok=True)

for result in results:
    current_page = result.get("page")
    html_data = result.get("body")
    output_file = output_dir / f"{current_page}.html"
    output_file.write_text(html_data.decode())
