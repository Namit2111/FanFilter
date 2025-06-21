import json
import datetime
import aiohttp
from fastapi import HTTPException
from app.models.schemas import TwitterUser, AnalyzedUser,RelevantUsersResponse
from app.core.constants import GEMINI_API_ENDPOINT
from app.core.config import get_settings

async def analyze_user(user: TwitterUser, job_run: str = "manual", tag_prompt: str = "") -> AnalyzedUser:

    """
    Analyze a Twitter user using Google's Gemini API.
    """
    account_age_days = (datetime.datetime.utcnow() - datetime.datetime.strptime(user.created_at, "%a %b %d %H:%M:%S %z %Y").replace(tzinfo=None)).days
    
    payload = {
        "contents": f"""
        Analyze this Twitter user for bot likelihood 1-10 and give notes.
        - username: {user.screen_name}
        - name: {user.name}
        - bio: {user.description}
        - followers: {user.followers_count}
        - friends: {user.friends_count}
        - created_at_days: {account_age_days}
        - tweets: {user.statuses_count}
        - verified: {user.verified}
        Recent tweet: "{user.status.text if user.status else ''}"
        Tags: {tag_prompt or '(brand,person)'}
        """,
    }

    settings = get_settings()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_API_ENDPOINT, headers=headers, json=payload) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Gemini API call failed")
            result = await response.json()
            try:
                output_text = result["candidates"][0]["content"]["parts"][0]["text"]
                result_json = json.loads(output_text)
            except Exception:
                raise HTTPException(status_code=500, detail="Gemini response parsing failed")

    return AnalyzedUser(
        twitter_username=user.screen_name,
        bot_score=result_json.get("bot_score", 10),
        ai_notes=result_json.get("ai_notes", ""),
        tags=result_json.get("tags", ""),
        job_run=job_run,
        twitter_profile_url=f"https://x.com/{user.screen_name}",
        twitter_user_id=user.id,
        bio=user.description,
        followers_count=user.followers_count,
        following_count=user.friends_count,
        status_count=user.statuses_count,
        media_count=user.media_count,
        bookmarks_count=user.favourites_count,
        twitter_display_name=user.name
    ) 




from google import genai
from pydantic import BaseModel
from typing import Type
settings = get_settings()
# Initialize Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
# model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")  # You can change the model name as needed

async def analyze_user_gemini(
    prompt: str,
    model_name: str = "gemini-2.0-flash-lite",
):
    """
    Sends a system prompt and user query to Gemini, parses the response with a Pydantic model.

    Args:
        system_prompt (str): The system message prompt.
        user_query (str): The user message/query.
        response_model (Type[BaseModel]): Pydantic model class to parse the output.
        model_name (str): Gemini model to use. Defaults to 'gemini-1.5-pro'.

    Returns:
        An instance of the response_model parsed from the output.
    """

    full_prompt = prompt

    # Generate content
    response = client.models.generate_content(
        model=model_name, contents=full_prompt,config={
        "response_mime_type": "application/json",
        "response_schema": RelevantUsersResponse,
    })

    # Parse response
    return response.parsed  # This will be an instance of the Pydantic model

