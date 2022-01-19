from functools import wraps

from fastapi.responses import JSONResponse


def errors_to_json(fn):
    @wraps(fn)
    async def decorated(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except Exception as error:
            return JSONResponse({'error': str(error)}, status_code=500)

    return decorated
