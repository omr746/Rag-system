from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson import ObjectId
from datetime import datetime


class MachineLog(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    stream_id: str
    machine_project_id: ObjectId
    ts: datetime
    data: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("machine_id", 1)],
                "name": "machine_id_index",
                "unique": False
            },
        
        ]