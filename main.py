from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import Base,engine
from app import models
from app.routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)


