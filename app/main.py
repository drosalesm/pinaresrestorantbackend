from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import OperationalError
from app.routers import product,auth
from fastapi.responses import JSONResponse
from app.middleware.logging_middleware import log_request_response

app = FastAPI()

# Include routers
app.include_router(product.router, prefix="/api", tags=["Products"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

app.middleware("http")(log_request_response)



# Global error handler for database connection issues
@app.exception_handler(OperationalError)
async def db_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"message": "Database unavailable", "status": "error", "http_code": 503, "data": []},
    )
