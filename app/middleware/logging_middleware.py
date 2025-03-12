from starlette.requests import Request
from starlette.responses import Response
import json
from app.db.database import SessionLocal
from app.models.log import LogEntry
from fastapi.responses import StreamingResponse

async def log_request_response(request: Request, call_next):
    db = SessionLocal()

    # 🔹 Read and store the request body in request.state
    try:
        request_body_bytes = await request.body()
        request_body = request_body_bytes.decode("utf-8") if request_body_bytes else None
        request.state.body = request_body_bytes  # Store for reuse
    except Exception:
        request_body = None
        request.state.body = None

    # 🔹 Replace the request body so the route can read it
    async def receive():
        return {"type": "http.request", "body": request.state.body or b""}

    request._receive = receive  # Override the request's receive method

    # 🔹 Process the request in the router
    response = await call_next(request)

    # 🔹 Avoid logging redirect responses (307)
    if response.status_code == 307:
        return response

    # 🔹 Read and decode the response body
    response_body = None
    if isinstance(response, StreamingResponse):
        response_body_bytes = b"".join([chunk async for chunk in response.body_iterator])
        response.body_iterator = iter([response_body_bytes])
        response_body = response_body_bytes.decode("utf-8") if response_body_bytes else None
    else:
        try:
            response_body = response.body.decode("utf-8") if hasattr(response, "body") else None
        except Exception:
            response_body = "Error decoding response body"

    # 🔹 Extract 'uti' from the response
    uti = None
    try:
        response_json = json.loads(response_body)
        uti = response_json.get("uti", None)
        message = response_json.get("message", None)        
    except (json.JSONDecodeError, TypeError):
        uti = None

    # 🔹 Log request and response
    log_entry = LogEntry(
        uti=uti,
        endpoint=str(request.url),
        method=request.method,
        status_code=response.status_code,
        message=message,
        request_body=request_body,
        response_body=response_body
    )
    db.add(log_entry)
    db.commit()
    db.close()

    return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
