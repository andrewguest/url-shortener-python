from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models import CreateShortURLRequest
from utils.helpers import get_or_generate_short_url


api_router = APIRouter()


@api_router.post("/api/new-url", response_class=JSONResponse)
async def create_new_url(short_url_request: CreateShortURLRequest):
    short_url = await get_or_generate_short_url(short_url_request.long_url)

    return {
        "short": short_url,
        "long": short_url_request.long_url,
    }
