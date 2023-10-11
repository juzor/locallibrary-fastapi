from fastapi import FastAPI
from .routers import auth, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)

@app.get('/')
async def root():
    return {
        "message": "Welcome to Locallibrary-FastAPI"
    }