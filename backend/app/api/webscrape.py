# Simplified endpoint: only requires a Twitter username
from fastapi import APIRouter, HTTPException
from app.models.schemas import TwitterUser, AnalyzedUser
from app.services.twitter import get_twitter_followers
from app.services.gemini import analyze_user,analyze_user_gemini
from app.utils.helpers import chunk_list
from app.core.constants import BOT_SCORE_CUTOFF, OPENAI_BATCH_SIZE
from app.utils.utils import load_txt_file
from app.models.schemas import WebscrapeRequest
import json

router = APIRouter()


@router.post("/webscrape")
async def webscrape(request: WebscrapeRequest):
    """Fetch followers of a given Twitter username and analyze each follower. Returns a filtered list of analyzed users."""
    try:
        response = await get_twitter_followers(request.user_request)
    except HTTPException as e:
        # Propagate upstream error
        raise e
    # print(response)
    users = response.get("users", [])
    print(len(users))   
    if not users:
        raise HTTPException(status_code=404, detail="No followers found or user not found")


    prompt = load_txt_file(file_name="prompt.txt").format(user_request=request.user_prompt,followers=users)

    analyzed_users = await analyze_user_gemini(prompt)
    
    final_users = []
    for id in analyzed_users.users:
        user_id = id.user_id
        for user in users:
            if user.get("user_id") == user_id:
                final_users.append(user)

    with open("analyzed_users.json", "w") as f:
        json.dump(analyzed_users.dict(), f, indent=4)

    return {
        "count": analyzed_users.total_matches,
        "followers": final_users
    } 