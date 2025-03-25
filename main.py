from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from src.conf.config import settings
from src.routes import auth, contacts, users
import redis.asyncio as redis

if(settings.app_location == 'LOCAL'):
    redis_host = settings.redis_local_host
else:
    redis_host = settings.redis_host
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    r = None

    try:
        r = redis.Redis(
            host='localhost',
            port=settings.redis_port, db=0,
            encoding='utf-8',
            decode_responses=True
        )

        if await r.ping():
            print("Connection successfull")
            await FastAPILimiter.init(r)
            print("Limiter initialised")
        else:
            print(f"Connection failed")
            raise Exception("Redis ping failed")
    except Exception as e:
        print(f"err: {e}")

    finally:
        await r.close()
        print("Redis connection closed")

    yield

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')
    
@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_root():
    return {"message": "Hello World from API"}
