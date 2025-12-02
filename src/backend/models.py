from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True) # 로봇 식별 ID
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    model_type = Column(String, index=True)
    status = Column(String, default="running") # running, completed, failed

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    step = Column(Integer)
    observation = Column(JSON) # JSON 형태로 저장
    action = Column(JSON)      # JSON 형태로 저장
    reward = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
