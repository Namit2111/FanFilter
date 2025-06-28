import asyncio
from typing import TypeVar, List
import random
import string

T = TypeVar('T')

async def sleep(ms: int) -> None:
    """
    Sleep for the specified number of milliseconds.
    """
    await asyncio.sleep(ms / 1000)

def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)] 

def generate_gift_card_code(length: int = 8) -> str:
    """
    Generate a random gift card code.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))