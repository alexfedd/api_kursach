import os

DATABASE_URL = f"postgresql+asyncpg://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@postgres:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = os.environ["ENVIRONMENT"]