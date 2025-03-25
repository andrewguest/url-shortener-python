import os
from contextlib import asynccontextmanager

import motor.motor_asyncio

from beanie import init_beanie
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import ShortURLs
from routes.url_router import short_urls_router


load_dotenv()

# Jinja2 templates setup
templates = Jinja2Templates(directory="templates")


# Create the MongoDB database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup connection to MongoDB
    print("Connecting to MongoDB")
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(database=client.aguest_me, document_models=[ShortURLs])

    print("Connected to MongoDB")
    app.include_router(short_urls_router)

    yield

    # Shutdown the connection to MongoDB
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
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
