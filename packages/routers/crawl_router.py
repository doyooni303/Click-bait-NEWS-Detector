from fastapi import APIRouter

from packages.config import DataInput
from packages.crawling import crawl

crawler = APIRouter(prefix="/crawl")


# router 마다 경로 설정
@crawler.get("/", tags=["CRAWL"])
async def start_crawl():
    return "Input the URL"


# router 마다 경로 설정
@crawler.post("/{url}", tags=["CRAWl"], response_model=DataInput)
async def get_crawl(url: str):
    info = crawl(url)
    return {"title": info["title"], "content": info["content"]}
