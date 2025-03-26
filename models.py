from datetime import datetime, timedelta
from typing import Annotated

from beanie import Document, Indexed
from pydantic import BaseModel
from pymongo import IndexModel


class ShortURL(Document):
    """
    Expire these short URLs after 2 weeks to prevent people from using this example application in real world
    scenarios.

    We'll have indexes on the `full_url` and `short_url` fields and these two fields must each be unique.
    """

    full_url: Annotated[str, Indexed()]
    short_url: Annotated[str, Indexed()]
    visits: int = 0  # Allows me to track how many times a short URL has been used
    expires_at: datetime = datetime.now() + timedelta(
        weeks=2
    )  # By default, set a short URL to expire 2 weeks after creation
    is_expired: bool = False  # Easy way to check if a short URL is still usable

    class Settings:
        # Name of the collection in the MongoDB
        name = "url_shortener"
        # Indexes on the collection
        indexes = [
            IndexModel([("full_url", 1)], name="full_url_idx"),
            IndexModel([("short_url", 1)], name="short_url_idx"),
        ]


class CreateShortURLRequest(BaseModel):
    long_url: str
