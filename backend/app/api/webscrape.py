# Simplified endpoint: only requires a Twitter username
from fastapi import APIRouter, HTTPException
from app.models.schemas import TwitterUser, AnalyzedUser
from app.services.twitter import get_twitter_followers
from app.services.gemini import analyze_user_gemini
from app.utils.helpers import chunk_list
from app.core.constants import BOT_SCORE_CUTOFF, OPENAI_BATCH_SIZE
from app.utils.utils import load_txt_file
from app.models.schemas import WebscrapeRequest
import json

router = APIRouter()


async def flock_users(request: WebscrapeRequest):
    """
    Fetch and analyze up to `count` followers, paginating with cursor as needed.
    Each batch is analyzed immediately with Gemini, and results are accumulated.
    Returns analyzed users and the next cursor for further pagination.
    """
    username = request.user_request
    user_prompt = request.user_prompt
    count = request.count or 20  # Default batch size if not provided
    cursor = getattr(request, 'cursor', None)

    analyzed_final_users = []
    next_cursor = cursor
    total_fetched = 0

    while total_fetched < count:
        print(len(analyzed_final_users))
        try:
            response = await get_twitter_followers(username, next_cursor)
        except HTTPException as e:
            raise e
        users = response.get("users", [])
        next_cursor = response.get("next_cursor_str")
        total_fetched += len(users)
        print(next_cursor)
        if not users:
            break
        # Only fetch up to the remaining needed
        # users = users[: count - len(analyzed_final_users)]
        if not users:
            break
        prompt = load_txt_file(file_name="prompt.txt").format(user_request=user_prompt, followers=users)
        analyzed_users = await analyze_user_gemini(prompt)
        print(analyzed_users)
        # Map analyzed results back to users
        if analyzed_users.total_matches == 0 or analyzed_users == None:
            continue
        for id in analyzed_users.users:
            user_id = id.user_id
            for user in users:
                if user.get("user_id") == user_id:
                    user["tags"] = id.tags
                    user["ai_analysis_notes"] = id.ai_analysis_notes
                    user["bot_score"] = id.bot_score
                    analyzed_final_users.append(user)
        if not next_cursor:
            break

    if not analyzed_final_users:
        raise HTTPException(status_code=404, detail="No followers found or user not found")

    return {
        "count": len(analyzed_final_users),
        "followers": analyzed_final_users,
        "next_cursor": next_cursor
    }

# @router.post("/webscrape")
# async def webscrape(request: WebscrapeRequest):
#     """Fetch followers of a given Twitter username and analyze each follower. Returns a filtered list of analyzed users."""
#     try:
#         response = await get_twitter_followers(request.user_request)
#     except HTTPException as e:
#         # Propagate upstream error
#         raise e
#     # print(response)
#     users = response.get("users", [])
#     print(len(users))   
#     if not users:
#         raise HTTPException(status_code=404, detail="No followers found or user not found")


#     prompt = load_txt_file(file_name="prompt.txt").format(user_request=request.user_prompt,followers=users)

#     analyzed_users = await analyze_user_gemini(prompt)
    
#     final_users = []
#     for id in analyzed_users.users:
#         user_id = id.user_id
#         for user in users:
#             if user.get("user_id") == user_id:
#                 user["tags"] = id.tags
#                 user["ai_analysis_notes"] = id.ai_analysis_notes
#                 user["bot_score"] = id.bot_score
#                 final_users.append(user)

#     with open("analyzed_users.json", "w") as f:
#         json.dump(analyzed_users.dict(), f, indent=4)

#     return {
#         "count": analyzed_users.total_matches,
#         "followers": final_users
#     } 


@router.post("/webscrape")
async def webscrape(request: WebscrapeRequest):
    """Fetch followers of a given Twitter username and analyze each follower. Returns a filtered list of analyzed users."""
    try:
        response = await flock_users(request)
    except HTTPException as e:
        # Propagate upstream error
        raise e
    return response