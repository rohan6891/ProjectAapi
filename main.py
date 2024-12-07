from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import user, data
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.mount("/static", StaticFiles(directory="ScraData"), name="static")

# Register routers
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
