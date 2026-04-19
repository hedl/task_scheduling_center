from fastapi.responses import JSONResponse
from typing import Any

def unified_send(code: int, message: str, data: Any = None):
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )