import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.openapi.utils import get_openapi

from web.startup import *
from core.factory.web import get_current_app
from core.factory.cloudauth import get_current_auth


app = get_current_app()
auth = get_current_auth()


@app.on_event("startup")
async def startup_event():
    init_error_handling()
    init_cors()
    # init_graphql()
    init_routes()
    init_swagger()
        

@app.middleware("http")
async def init_request(request: Request, call_next):
    if request.method == 'OPTIONS':
        pass
    else:
        await init_master_db()
        await init_workspace(request)
        await init_tenant_db(request)
        pass
    return await call_next(request)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8002, debug=True)

# app.add_middleware(TenantDbMiddleware)
# app.add_middleware(WorkspaceMiddleware)
# app.add_middleware(MasterDbMiddleware)
# app.add_middleware(HTTPSRedirectMiddleware)
