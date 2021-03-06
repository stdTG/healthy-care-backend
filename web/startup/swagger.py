import json
from typing import Optional

from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse

from core.factory.web import get_current_app


def get_custom_swagger_ui_html(
        *,
        openapi_url: str,
        title: str,
        swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui"
                              "-dist@3.30.0/swagger-ui-bundle.js",
        swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.30.0/swagger-ui.css",
        swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
        oauth2_redirect_url: Optional[str] = None,
        init_oauth: Optional[dict] = None,
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        tagsSorter: "alpha",
        showExtensions: true,
        showCommonExtensions: true
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def init_swagger():
    app = get_current_app()

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_custom_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
        )
