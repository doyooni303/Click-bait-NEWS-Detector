from argparse import ArgumentParser
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
            "home.html",  # Make sure this file exists in your templates directory
            {"request": request},
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Template not found")


# Exception handlers at app level
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    args = parser.parse_args()
    logger.info(f"Starting FastAPI server on {args.host}:{args.port}")
    api = FastAPIRunner(args)
    api.run()
