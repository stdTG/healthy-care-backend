from fastapi import Request

from app.context import init_current_workspace


async def init_workspace(request: Request):
    print("[WORKSPACE] Initialization")
    await init_current_workspace(request)
    print("[WORKSPACE] Done")
