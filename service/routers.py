import asyncio
import aiohttp
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from service import contracts

router = APIRouter()


# Returns a welcome HTML page
@router.get("/", tags=["html"])
def root():
    html_content = '''
    <html>
        <body>
            <h1>Homework for the ITMO course Python Backend</h1>
            <h2>Endpoints:</h2>
            <ul>
            <li>/docs</li>
            <li>/users</li>
            <li>/users/{id}</li>
            <li>/compliment</li>
            </ul>
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)


# PATH PARAMETER - Returns json user data by user_id from https://reqres.in
@router.get("/users/{user_id}", tags=["users"])
async def read_user(user_id: int):
    async with aiohttp.ClientSession() as session:
        r = await session.get(f"https://reqres.in/api/users/{user_id}")

    if r.status == 200:
        return await r.json()
    else:
        raise HTTPException(status_code=r.status)


# QUERY PARAMETER - Returns a simple dictionary with the specified delay
@router.get("/compliment", tags=["delay"])
async def read_compliment(delay: int | None = None):
    if delay:
        await asyncio.sleep(delay)

    return {"You're": "wonderful"}


# REQUEST BODY - Returns code 201 and user data if the user was created
@router.post("/users", status_code=201, tags=["users"])
async def create_user(user: contracts.User):
    async with aiohttp.ClientSession() as session:
        r = await session.post(f"https://reqres.in/api/users", data={"name": user.name, "job": user.job})

    if r.status == 201:
        return await r.json()
    else:
        raise HTTPException(status_code=r.status)
