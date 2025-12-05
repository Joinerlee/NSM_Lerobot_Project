from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from . import models, schemas, database

app = FastAPI(title="Lerobot Backend API")

@app.on_event("startup")
async def startup():
    # 테이블 생성 (프로덕션에서는 Alembic 마이그레이션 사용 권장)
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.post("/episodes/", response_model=schemas.EpisodeResponse)
async def create_episode(episode: schemas.EpisodeCreate, db: AsyncSession = Depends(database.get_db)):
    db_episode = models.Episode(client_id=episode.client_id, model_type=episode.model_type)
    db.add(db_episode)
    await db.commit()
    await db.refresh(db_episode)
    return db_episode

@app.post("/logs/", response_model=schemas.LogResponse)
async def create_log(log: schemas.LogCreate, db: AsyncSession = Depends(database.get_db)):
    # 에피소드 존재 확인
    result = await db.execute(select(models.Episode).filter(models.Episode.id == log.episode_id))
    episode = result.scalars().first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    db_log = models.Log(**log.dict())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

@app.get("/episodes/", response_model=List[schemas.EpisodeResponse])
async def read_episodes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Episode).offset(skip).limit(limit))
    episodes = result.scalars().all()
    return episodes
