from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GiftCard(BaseModel):
    code: str
    credits: int
    created_at: datetime
    is_redeemed: bool = False
    redeemed_at: Optional[datetime] = None
