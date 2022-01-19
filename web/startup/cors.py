from fastapi.middleware.cors import CORSMiddleware

from core.factory.web import get_current_app


def init_cors():
    print("[APP] Init CORS")

    app = get_current_app()

    origins = [
        "*",
        "http://localhost",
        "http://localhost:3000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
