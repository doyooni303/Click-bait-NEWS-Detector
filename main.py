from argparse import ArgumentParser

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import json

# Import your BERT router
from packages import bert, crawler, FastAPIRunner  # Adjust the import path as needed

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount your routers
app.include_router(bert)
app.include_router(crawler)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# We don't need the /process-news endpoint since we're using /BERT/detect directly
# Remove the Request class and process_news endpoint as they're not being used


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    try:
        return templates.TemplateResponse(
            "home2.html",  # Make sure this file exists in your templates directory
            {"request": request},
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Template not found")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    args = parser.parse_args()
    api = FastAPIRunner(args)
    api.run()
