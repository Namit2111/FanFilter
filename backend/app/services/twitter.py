from typing import Optional, Dict
import aiohttp
from fastapi import HTTPException
from app.core.constants import TWITTER_API_HOST
from app.core.config import get_settings

async def get_twitter_followers(username: str, cursor: Optional[str] = None) -> Dict:
    """
    Fetch Twitter followers using the RapidAPI Twitter API.
    """
    url = f"https://{TWITTER_API_HOST}/followers.php?screenname={username}"
    

    settings = get_settings()
    headers = {
        "x-rapidapi-key": settings.RAPID_API_KEY,
        "x-rapidapi-host": TWITTER_API_HOST,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Failed Twitter API call")
            data = await response.json()
            # print(data)
            return {
                "users": data.get("followers", []),
                "next_cursor_str": data.get("next_cursor")
            } 