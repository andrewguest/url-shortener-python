import os
from contextlib import asynccontextmanager

import motor.motor_asyncio
import sentry_sdk
from beanie import init_beanie
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from models import ShortURL
from routes.api_router import api_router
from routes.url_router import short_urls_router

load_dotenv()
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Enable sending logs to Sentry
    enable_logs=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=0.1,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)


# Jinja2 templates setup
templates = Jinja2Templates(directory="templates")


# Create the MongoDB database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup connection to MongoDB
    sentry_sdk.logger.info("Connecting to MongoDB")

    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(database=client.aguest_me, document_models=[ShortURL])

    sentry_sdk.logger.info("Connected to MongoDB")

    # Register other routers
    app.include_router(api_router)
    app.include_router(short_urls_router)

    yield

    # Shutdown the connection to MongoDB
    sentry_sdk.logger.info("Disconnecting from MongoDB")
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


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return "User-agent: *\nDisallow: /"
