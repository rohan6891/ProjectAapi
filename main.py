from fastapi import FastAPI, HTTPException
from api.routers import user, data

app = FastAPI()

# Register routers
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
