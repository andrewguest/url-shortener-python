import random
import string

from beanie.operators import And

from models import ShortURL


async def get_or_generate_short_url(long_url: str) -> str:
    """
    Return the short URL associated with the given `long_url` or create a new short URL and store it in the database
    and associate it with the given `long_url`.

    Args:
        long_url: The URL that the short URL will redirect to.

    Returns:
        str: The short URL associated with the given `long_url`.
    """

    if not long_url.startswith("http://") and not long_url.startswith("https://"):
        long_url = "https://" + long_url

        # Verify that the given URL is not already in the DB
    mongo_query = And(ShortURL.full_url == long_url, ShortURL.is_expired == False)
    existing_doc = await ShortURL.find(mongo_query).first_or_none()

    if existing_doc is not None:
        return existing_doc.short_url
    else:
        characters = string.ascii_uppercase + string.ascii_lowercase
        # Generate a random string of 5 characters that are a mix of upper and lowercase letters
        random_string = "".join(random.choice(characters) for _ in range(5))

        # Check if the random string is in the DB already
        mongo_query = And(
            ShortURL.short_url == random_string, ShortURL.is_expired == False
        )
        existing_doc = await ShortURL.find(mongo_query).first_or_none()

        # If `random_string` is already in the DB, then regenerate a new random string and try again
        while existing_doc is not None:
            random_string = "".join(random.choice(characters) for _ in range(5))
            mongo_query = And(
                ShortURL.short_url == random_string, ShortURL.is_expired == False
            )
            existing_doc = await ShortURL.find(mongo_query).first_or_none()

        new_doc = ShortURL(
            short_url=f"{random_string}",
            full_url=long_url,
        )
        await new_doc.insert()

        return new_doc.short_url
