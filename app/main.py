from fastapi import FastAPI
from .routers import auth, user, catalog

app = FastAPI(
    title="Local Library",
    description="Welcome to the Local Library API documentation! Here you will able to discover all of the ways you can interact with the API."
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(catalog.router)

@app.get('/')
async def root():
    return {
        "message": "Welcome to Locallibrary-FastAPI"
    }