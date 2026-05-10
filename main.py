from fastapi import FastAPI

from src.api import users, categories, locations, posts, comments

app = FastAPI(title="Blogicum API", description="API for Blogicum project", version="1.0.0")

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
