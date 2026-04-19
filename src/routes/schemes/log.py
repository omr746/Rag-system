from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

class MachineLogRequest(BaseModel):
    stream_id: str
    ts: datetime
    data: Dict[str, Any]
