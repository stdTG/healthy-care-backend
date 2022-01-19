from .router import router


@router.get("/ping")
async def pong():
    print("testing simple endpoint")
    return {
        "result": "ok",
        "details": "pong",
    }


@router.get("/version")
async def version():
    return {
        "result": "ok",
        "details": "staging.0.0.20",
    }
