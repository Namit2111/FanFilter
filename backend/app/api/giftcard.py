from fastapi import APIRouter
from app.services.db.giftcard import create_gift_card, get_gift_card, get_all_gift_cards, deduct_credits

giftcard_router = APIRouter(prefix="/giftcard", tags=["giftcard"])

@giftcard_router.post("/create")
def create_gift_card_endpoint(credits: int):
    return create_gift_card(credits)

@giftcard_router.get("/get")
def get_gift_card_endpoint(code: str):
    return get_gift_card(code)

@giftcard_router.get("/get_all")
def get_all_gift_cards_endpoint():
    return get_all_gift_cards()

@giftcard_router.post("/deduct")
def deduct_credits_endpoint(code: str, amount: int):
    return deduct_credits(code, amount)