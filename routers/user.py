from fastapi import APIRouter, HTTPException
from api.models.user import RegisterReq, User
from api.database import db_instance
import bcrypt

router = APIRouter()

@router.post("/register/")
async def register_user(user: RegisterReq):
    existing_user = db_instance.db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_id = db_instance.db.users.insert_one({
        "username": user.username,
        "password": hashed_password.decode('utf-8'),
        "caseIds": user.caseIds
    }).inserted_id
    return {"message": "User created successfully", "user_id": str(user_id)}

@router.post("/login/")
async def login_user(user: User):
    existing_user = db_instance.db.users.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not bcrypt.checkpw(user.password.encode('utf-8'), existing_user['password'].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return {"message": "Login successful", "username": user.username}
