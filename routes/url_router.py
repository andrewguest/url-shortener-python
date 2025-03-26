import random
import string

from beanie.operators import And
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

from models import CreateShortURLRequest, ShortURL


short_urls_router = APIRouter()


@short_urls_router.post("/new-url", response_class=JSONResponse)
async def create_new_url(short_url_request: CreateShortURLRequest):
    if not short_url_request.long_url.startswith(
        "http://"
    ) and not short_url_request.long_url.startswith("https://"):
        short_url_request.long_url = "https://" + short_url_request.long_url

    # Verify that the given URL is not already in the DB
    mongo_query = And(
        ShortURL.full_url == short_url_request.long_url, ShortURL.is_expired == False
    )
    existing_doc = await ShortURL.find(mongo_query).first_or_none()

    if existing_doc is not None:
        return {
            "message": f"{short_url_request.long_url} already exists",
            "short": existing_doc.short_url,
        }
    else:
        characters = string.ascii_uppercase + string.ascii_lowercase
        # Generate a random string of 5 characters that are a mix of upper and lowercase letters
        random_string = "".join(random.choice(characters) for _ in range(5))

        # Check if the random string is in the DB already
        mongo_query = And(
            ShortURL.short_url == random_string, ShortURL.is_expired == False
        )
        existing_doc = await ShortURL.find(mongo_query).first_or_none()

        # If `random_string` is already in the DB, then regenerate a random string
        while existing_doc is not None:
            random_string = "".join(random.choice(characters) for _ in range(5))
            mongo_query = And(
                ShortURL.short_url == random_string, ShortURL.is_expired == False
            )
            existing_doc = await ShortURL.find(mongo_query).first_or_none()

        new_doc = ShortURL(short_url=random_string, full_url=short_url_request.long_url)
        await new_doc.insert()

        return {
            "message": f"{short_url_request.long_url} created",
            "short": new_doc.short_url,
            "long": new_doc.full_url,
        }


@short_urls_router.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_full_url(short_url: str):
    # Verify that the given URL is in the DB
    mongo_query = And(ShortURL.short_url == short_url, ShortURL.is_expired == False)
    existing_doc = await ShortURL.find(mongo_query).first_or_none()

    if existing_doc is not None:
        # Increment the `visits` counter before redirecting
        existing_doc.visits += 1
        await existing_doc.save()
        return RedirectResponse(existing_doc.full_url)
    else:
        return RedirectResponse("/")
