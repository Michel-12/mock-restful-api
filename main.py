from fastapi import FastAPI, Depends
from database import engine
from models import BaseDB
from auth import authrouter
from operations import router
from contextlib import asynccontextmanager

#Ensure that db has specified tables
@asynccontextmanager
async def lifespan(api: FastAPI):
    BaseDB.metadata.create_all(bind=engine)
    yield

#Define API
api = FastAPI(lifespan=lifespan)
#Include routers
api.include_router(authrouter)
api.include_router(router)

