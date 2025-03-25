from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models import CreateShortURLRequest


short_urls_router = APIRouter()


@short_urls_router.post("/new-url", response_class=JSONResponse)
async def create_new_url(short_url_request: CreateShortURLRequest):
    return {"URL submitted": short_url_request.long_url}
