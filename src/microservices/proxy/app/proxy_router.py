import random
import httpx
from fastapi import APIRouter, Request, Response
from starlette.responses import StreamingResponse
from app.settings import get_settings

router   = APIRouter()
settings = get_settings()
client   = httpx.AsyncClient(timeout=60.0)

def choose_backend(path: str) -> str | None:
    """Возвращает base-URL нужного сервиса или None, если путь неизвестен."""
    if path.startswith("/api/movies"):
        # градуальная миграция
        if settings.GRADUAL_MIGRATION:
            roll = random.randint(1, 100)
            if roll <= settings.MOVIES_MIGRATION_PERCENT:
                return str(settings.MOVIES_SERVICE_URL)
        return str(settings.MONOLITH_URL)  # fallback
    if path.startswith("/api/events"):
        return str(settings.EVENTS_SERVICE_URL)
    if path.startswith("/api/users"):
        return str(settings.MONOLITH_URL)

@router.api_route("/{full_path:path}",
                  methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
async def proxy(request: Request, full_path: str) -> Response:
    upstream = choose_backend(request.url.path)
    if upstream is None:
        return Response(status_code=404, content="Unknown route")

    resp = await client.request(
        request.method,
        f"{upstream}{request.url.path}",
        headers={**request.headers, "x-request-id": request.headers.get("x-request-id","proxy-generated")},
        params=request.query_params,
        content=await request.body(),
        follow_redirects=False
    )

    if resp.status_code >= 300:
        return Response("[]", media_type="application/json", status_code=200)

    return StreamingResponse(resp.aiter_raw(),
                             status_code=resp.status_code,
                             headers=resp.headers)
