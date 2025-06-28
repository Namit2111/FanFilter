from app.core.db import get_db
from datetime import datetime
from app.models.db import GiftCard
from app.utils.helpers import generate_gift_card_code
import csv

db = get_db()

def create_gift_card(credits: int):
    code = generate_gift_card_code()
    gift_card = GiftCard(
        code=code,
        credits=credits,
        created_at=datetime.now(),
    )
    result = db.gift_cards.insert_one(gift_card.model_dump())
    return code



def create_bulk_gift_cards(credits: int, count: int) -> str:
    codes = []
    for _ in range(count):
        code = create_gift_card(credits)
        codes.append(code)
    
    csv_file = "giftcards.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["GiftCardCode"])
        for code in codes:
            writer.writerow([code])
    
    return csv_file

def get_gift_card(code: str):
    gift_card = db.gift_cards.find_one({"code": code})
    if gift_card is None:
        return None
    gift_card['_id'] = str(gift_card['_id'])
    return gift_card

def get_all_gift_cards():
    def serialize_doc(doc):
        doc['_id'] = str(doc['_id'])
        return doc
    return [serialize_doc(doc) for doc in db.gift_cards.find()]

def update_gift_card(code: str, update_data: dict):
    result = db.gift_cards.update_one({"code": code}, {"$set": update_data})
    if result.modified_count == 0:
        return None
    return result.modified_count

def deduct_credits(code: str, amount: int):
    gift_card = get_gift_card(code)
    if gift_card is None:
        return None
    if gift_card['is_redeemed']:
        return None
    if gift_card['credits'] < amount:
        return None
    result = update_gift_card(code, {"credits": gift_card['credits'] - amount})   
    return result
