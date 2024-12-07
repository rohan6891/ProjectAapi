from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, Depends, Request
from database import db_instance
from utils.jwt_handler import create_access_token, verify_token
from utils.auth_utils import create_user,verify_password,get_user_by_username,hash_password
import bcrypt

router = APIRouter()

@router.post("/register")
async def register_user(req:Request):
    body = await req.json()
    user = await get_user_by_username(body["username"])
    if  user:
        raise HTTPException(status_code=409, detail="User Already Exists")
    user_id =await create_user(body["username"],body["password"])
    return {"success": True, "message": "User registered successfully"}

@router.post("/login")
async def login_user(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    user_id=str(user["_id"])
    token = create_access_token(data={"sub":user_id})
    return {"success": True, "message": "Login successful","token":token}

@router.get("/")
async def hello():
    return "Hello"


@router.get("/secure-data")
async def secure_data(request: Request):
    """
    Access protected data by verifying the JWT token.
    """
    # Extract and verify the token from the Authorization header
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    token = token.split("Bearer ")[1]
    payload = verify_token(token)
    
    return {"message": "Access to secure data granted", "username": payload["sub"]}
