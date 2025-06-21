import json
import os
import aiofiles
from typing import List, Dict, Any
from fastapi import HTTPException

class JsonStorageService:
    def __init__(self, base_dir: str = "data"):
        """Initialize the JSON storage service with a base directory."""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    async def _read_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Read data from a JSON file."""
        filepath = os.path.join(self.base_dir, filename)
        try:
            if not os.path.exists(filepath):
                return []
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read JSON file: {str(e)}")

    async def _write_json_file(self, filename: str, data: List[Dict[str, Any]]) -> None:
        """Write data to a JSON file."""
        filepath = os.path.join(self.base_dir, filename)
        try:
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write JSON file: {str(e)}")

    async def insert_records(self, filename: str, records: List[Dict[str, Any]]) -> None:
        """Insert new records into a JSON file."""
        existing_data = await self._read_json_file(filename)
        existing_data.extend(records)
        await self._write_json_file(filename, existing_data)

    async def update_record(self, filename: str, record_id: str, update_data: Dict[str, Any]) -> None:
        """Update a specific record in a JSON file."""
        data = await self._read_json_file(filename)
        updated = False
        for item in data:
            if item.get('Id') == record_id:
                item.update(update_data)
                updated = True
                break
        
        if not updated:
            data.append({**update_data, 'Id': record_id})
        
        await self._write_json_file(filename, data) 