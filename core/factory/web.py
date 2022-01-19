from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.utils.strings import dict_w_camel_keys


class SnakeCaseResponse(JSONResponse):
    def render(self, content: Any):
        if content:
            content = dict_w_camel_keys(content)
        return super().render(content)


__web_app = FastAPI(title="Alakine Backend Application", docs_url=None,
                    default_response_class=SnakeCaseResponse)


def get_current_app() -> FastAPI:
    global __web_app
    return __web_app
