import asyncio
from typing import TypeVar, List, Any

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