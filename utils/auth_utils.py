import bcrypt
from fastapi import HTTPException
from database import db_instance

async def get_users_collection():
    user_agent_collection = db_instance.get_collection("user_agents")  # No need to await here
    return user_agent_collection

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

async def create_user(username: str, password: str) -> str:
    users_collection =await get_users_collection()
    hashed_password = hash_password(password)
    user = {"username": username, "password": hashed_password}
    result = await users_collection.insert_one(user)
    return str(result.inserted_id)

async def get_user_by_username(username: str):
    users_collection = await get_users_collection()  # Await the async function here
    print("in get_user_by_username func")
    
    # Ensure find_one is awaited if it is async
    user = await users_collection.find_one({"username": username})
    
    return user
