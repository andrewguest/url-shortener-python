import os

from beanie.operators import And
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from models import CreateShortURLRequest, ShortURL
from utils.helpers import get_or_generate_short_url


short_urls_router = APIRouter()
DOMAIN: str | None = os.environ.get("DOMAIN")


@short_urls_router.post("/new-url", response_class=HTMLResponse)
async def create_new_url(short_url_request: CreateShortURLRequest):
    short_url = await get_or_generate_short_url(short_url_request.long_url)

    html_div = """
        <p class="text-xl mt-8">{domain_name}/{short}</p>
    """.format(domain_name=DOMAIN, short=short_url)

    return HTMLResponse(content=html_div)


@short_urls_router.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_full_url(short_url: str):
    # Verify that the given URL is in the DB
    mongo_query = And(ShortURL.short_url == short_url, ShortURL.is_expired == False)
    existing_doc = await ShortURL.find(mongo_query).first_or_none()
    print(f"Short URL: {short_url}")

    if existing_doc is not None:
        # Increment the `visits` counter before redirecting
        existing_doc.visits += 1
        await existing_doc.save()
        return RedirectResponse(existing_doc.full_url)
    else:
        return RedirectResponse("/")
