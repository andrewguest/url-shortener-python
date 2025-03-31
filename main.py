import logging.config
import json
import os
import time
from contextlib import asynccontextmanager

import motor.motor_asyncio

from beanie import init_beanie
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import ShortURL
from routes.api_router import api_router
from routes.url_router import short_urls_router


load_dotenv()

# Setup logging
with open("logging_conf.json", "r") as f:
    logging_conf = json.load(f)

logging.config.dictConfig(logging_conf)
fastapi_logger = logging.getLogger("fastapi")

# Jinja2 templates setup
templates = Jinja2Templates(directory="templates")


# Create the MongoDB database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup connection to MongoDB
    fastapi_logger.info("Connecting to MongoDB")

    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(database=client.aguest_me, document_models=[ShortURL])

    fastapi_logger.info("Connected to MongoDB")

    # Register other routers
    app.include_router(api_router)
    app.include_router(short_urls_router)

    yield

    # Shutdown the connection to MongoDB
    fastapi_logger.info("Disconnecting from MongoDB")
    client.close()


# App setup
app = FastAPI(
    title="Python URL shortener",
    description="Python application to create short URLs that redirect to long URLs.",
    version="0.0.1",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    fastapi_logger.info(
        f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}s)"
    )

    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
