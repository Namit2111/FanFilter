from typing import List, Dict, Any
import aiohttp
from fastapi import HTTPException

async def update_nocodb(noco_url: str, token: str, table_id: str, records: List[Dict[str, Any]]) -> None:
    """
    Update records in NocoDB table.
    """
    headers = {
        "Content-Type": "application/json",
        "xc-token": token
    }
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{noco_url}/api/v2/tables/{table_id}/records", headers=headers, json=records) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="NocoDB update failed")

async def insert_nocodb(noco_url: str, token: str, table_id: str, records: List[Dict[str, Any]]) -> None:
    """
    Insert records into NocoDB table.
    """
    headers = {
        "Content-Type": "application/json",
        "xc-token": token
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{noco_url}/api/v2/tables/{table_id}/records", headers=headers, json=records) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="NocoDB insert failed") 