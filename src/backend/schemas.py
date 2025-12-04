from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class EpisodeCreate(BaseModel):
    client_id: str
    model_type: str

class EpisodeResponse(BaseModel):
    id: int
    client_id: str
    timestamp: datetime
    model_type: str
    status: str

    class Config:
        orm_mode = True

class LogCreate(BaseModel):
    episode_id: int
    step: int
    observation: Dict[str, Any]
    action: List[float]
    reward: float

class LogResponse(LogCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
