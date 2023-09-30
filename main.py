import uvicorn
from fastapi import FastAPI

from service.routers import router

# Creating additional metadata for the tags used to group path operations
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "delay",
        "description": "Delayed response",
    },
    {
        "name": "html",
        "description": "HTML document",
    },
]

# Creating an "instance" of the class FastAPI
app = FastAPI(
    title="Homework 2",
    description="Homework for the ITMO course Python Backend",
    contact={
        "name": "KELONMYOSA",
        "url": "https://github.com/KELONMYOSA"
    },
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/docs/redoc"
)

# Include routers
app.include_router(router)

# Start the uvicorn ASGI server with the specified parameters
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 80
    uvicorn.run(app, host=host, port=port)
