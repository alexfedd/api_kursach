from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.v1.endpoints import auth, user, post, follow, like

app = FastAPI(
    title="Twitter Clone API",
    description="API для социальной сети, аналогичной Twitter.",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(post.router, prefix="/api/v1", tags=["Posts"])
app.include_router(follow.router, prefix="/api/v1", tags=["Follow"])
app.include_router(like.router, prefix="/api/v1", tags=["Likes"])