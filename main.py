import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to path (for Models and Controllers)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

app = FastAPI(title="Backend API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import and register router
try:
    from Controllers.TestController import router as test_router
    app.include_router(test_router)
except Exception as e:
    print(f"Error importing TestController: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    # Create a dummy router for error reporting
    from fastapi import APIRouter
    test_router = APIRouter(prefix="/api/test", tags=["test"])
    @test_router.get("/")
    async def error_endpoint():
        return {{
            "error": "Failed to load TestController",
            "details": str(e),
            "traceback": traceback.format_exc()
        }}
    app.include_router(test_router)

@app.get("/")
async def root():
    return {{
        "message": "Backend API is running",
        "status": "ok",
        "swagger": "/docs",
        "api": "/api/test"
    }}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
