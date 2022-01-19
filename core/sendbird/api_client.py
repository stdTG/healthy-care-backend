import requests

from .sendbird_response import SendbirdResponse


class ClientConfigCommon:
    API_BASE_URL = "https://api-{app_id}.sendbird.com/v3/"

    def __init__(self, app_id, api_token):
        self.app_id = app_id
        self.api_token = api_token

    def get_url(self, url):
        if url.startswith("/"):
            url = url[1:]  # Removes slash
        base = self.API_BASE_URL.format(app_id=self.app_id)
        return f"{base}{url}"

    def request_headers(self):
        headers = {
            "Api-Token": self.api_token,
            "Content-Type": "application/json;charset=utf-8",
        }
        return headers


class ClientConfigApplications:
    API_BASE_URL = "https://gate.sendbird.com/api/v2/"

    def __init__(self, organization_api_key):
        self.organization_api_key = organization_api_key

    def get_url(self, url):
        if url.startswith("/"):
            url = url[1:]  # Removes slash
        base = self.API_BASE_URL
        return f"{base}{url}"

    def request_headers(self):
        headers = {
            "SENDBIRDORGANIZATIONAPITOKEN": self.organization_api_key,
            "Content-Type": "application/json;charset=utf-8",
        }
        return headers


class APIClient(object):
    def __init__(self, config):
        self.config = config

    async def request(self, http_method, url, **args):
        rbody = await self.request_raw(http_method, url, **args)
        resp = self.interpret_response(rbody)
        print(f"[SENDBIRD] RESPONSE ON SENDING: {resp.body}")
        return resp

    async def request_raw(self, http_method, url, **args):
        abs_url = self.config.get_url(url)
        headers = self.request_headers()
        method_to_use = getattr(requests, http_method.lower())

        # TODO: Handle other status codes besides 200
        print(f"[SENDBIRD] URL: {abs_url}")
        print(f"[SENDBIRD] HEADERS: {headers}")
        print(f"[SENDBIRD] METHOD: {http_method}")
        print(f"[SENDBIRD] BODY: {args}")

        return method_to_use(abs_url, headers=headers, json=args)

    def request_headers(self):
        return self.config.request_headers()

    def interpret_response(self, rbody):
        resp = SendbirdResponse(rbody.text)
        return resp
