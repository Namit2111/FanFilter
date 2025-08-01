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
import asyncio
from fastapi.responses import StreamingResponse
from app.services.db.giftcard import deduct_credits

router = APIRouter()

# Utility to build Server-Sent Event (SSE) packets
def _sse_pack(data: dict, event: str | None = None) -> str:
    """Return a valid SSE string (with trailing blank line)."""
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data)}\n\n"  # note double \n terminator

async def flock_users(request: WebscrapeRequest, event_callback=None):
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
    
    # initial progress event
    if event_callback:
        await event_callback({"total_fetched": 0})

    while total_fetched < count:
        # print(len(analyzed_final_users))
        # print(total_fetched)
        try:
            response = await get_twitter_followers(username, next_cursor)
        except HTTPException as e:
            print(e)
            raise e
        users = response.get("users", [])
        next_cursor = response.get("next_cursor_str")
        
        total_fetched += len(users)
        if event_callback:
            await event_callback({"total_fetched": total_fetched})
        # print(next_cursor)
        if not users:
            break
        # Only fetch up to the remaining needed
        # users = users[: count - len(analyzed_final_users)]
        if not users:
            break
        prompt = load_txt_file(file_name="prompt.txt").format(user_request=user_prompt, followers=users)
        analyzed_users = await analyze_user_gemini(prompt)
        # print(analyzed_users)
        # Map analyzed results back to users
        if analyzed_users.total_matches == 0 or analyzed_users == None:
            # Add all users with default values
            for user in users:
                user["tags"] = []
                user["ai_analysis_notes"] = ""
                user["bot_score"] = 0
                user["prompt_match_score"] = 0
                analyzed_final_users.append(user)
        else:
            # Create a set of analyzed user IDs for quick lookup
            analyzed_ids = {id.user_id for id in analyzed_users.users}
       
            # Process all users
            for user in users:
                user_id = user.get("user_id")
                if user_id in analyzed_ids:
                    # Get analysis for matched users
                    for analysis in analyzed_users.users:
                        if analysis.user_id == user_id:
                            user["tags"] = analysis.tags
                            user["ai_analysis_notes"] = analysis.ai_analysis_notes
                            user["bot_score"] = analysis.bot_score
                            user["prompt_match_score"] = analysis.prompt_match_score  # Set to 1.0 for matched users if not provided
                            analyzed_final_users.append(user)
                            break
                else:
                    # Add default values for unmatched users
                    user["tags"] = []
                    user["ai_analysis_notes"] = ""
                    user["bot_score"] = 0
                    user["prompt_match_score"] = 0
                    analyzed_final_users.append(user)
                   
        if not next_cursor:
            break
        if event_callback:
            await event_callback({"cursor": next_cursor})
            await event_callback({"followers": analyzed_final_users})
    if not analyzed_final_users:
        raise HTTPException(status_code=404, detail="No followers found or user not found")

    return {
        "count": len(analyzed_final_users),
        "followers": analyzed_final_users,
        "next_cursor": next_cursor
    }

@router.post("/webscrape")
async def webscrape(request: WebscrapeRequest):
    """Fetch followers of a given Twitter username and analyze each follower. Returns a filtered list of analyzed users."""
    try:
        response = await flock_users(request)
    except HTTPException as e:
        raise e
    return response

# ---------------------------------------------------------------------------
#  Server-Sent Events endpoint (real-time "total fetched" progress)
# ---------------------------------------------------------------------------

@router.get("/webscrape-stream")
async def webscrape_stream(user_request: str, user_prompt: str, count: int = 100, cursor: str | None = None, code: str | None = None):
    """Stream total_fetched updates while followers are being processed."""

    if code:
        is_deducted = deduct_credits(code, count)
        if is_deducted == None:
            raise HTTPException(status_code=400, detail="Invalid gift card code or insufficient credits")
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    async def _event_cb(payload: dict):
        """Put an SSE string into the queue."""
        await queue.put(_sse_pack(payload))

    async def _runner():
        try:
            final_data = await flock_users(
                WebscrapeRequest(
                    user_request=user_request,
                    user_prompt=user_prompt,
                    count=count,
                    cursor=cursor
                ),
                event_callback=_event_cb,
            )
            # push final result
            await queue.put(_sse_pack(final_data, event="done"))
        except HTTPException as e:
            # send error then close
            await queue.put(_sse_pack({"error": e.detail}, event="error"))
        finally:
            # sentinel to close generator
            await queue.put(None)

    # Run the long-running job in the background so the generator can stream
    asyncio.create_task(_runner())

    async def _generator():
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(_generator(), media_type="text/event-stream")