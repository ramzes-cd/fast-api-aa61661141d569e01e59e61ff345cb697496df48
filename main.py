from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api import auth, users, categories, locations, posts, comments
from src.core.logging import UserActionLoggingMiddleware, configure_logging

configure_logging()

app = FastAPI(title="Blogicum API", description="API for Blogicum project", version="1.0.0")
app.add_middleware(UserActionLoggingMiddleware)
app.mount("/media", StaticFiles(directory="uploads"), name="media")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(locations.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
def root():
    return {"message": "Welcome to Blogicum API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
