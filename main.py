import logging
from argparse import ArgumentParser

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from packages import bert, crawler
from packages import FastAPIRunner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(bert)
app.include_router(crawler)


# @app.get("/home")
# def read_results():
#     return "Welcome to Fake News Detection API!"
#     # return templates.TemplateResponse("home.html", {"request": "home"})


@app.get("/", response_class=HTMLResponse)
async def get_html():
    try:
        with open("templates/home.html") as f:
            return f.read()

        # return templates.TemplateResponse(
        #     "home.html", {"request": request, "result": None}
        # )
    except FileNotFoundError:
        logger.error("home.html not found in static directory")
        raise HTTPException(status_code=500, detail="Template not found")


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    args = parser.parse_args()
    api = FastAPIRunner(args)
    api.run()
