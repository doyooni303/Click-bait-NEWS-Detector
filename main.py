from argparse import ArgumentParser

from fastapi import FastAPI
from packages import bert, crawler
from packages import FastAPIRunner

app = FastAPI()

app.include_router(bert)
app.include_router(crawler)


@app.get("/home")
def read_results():
    return "Welcome to Fake News Detection API!"


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    args = parser.parse_args()
    api = FastAPIRunner(args)
    api.run()
