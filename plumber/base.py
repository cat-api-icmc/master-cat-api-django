import requests
from typing_extensions import Literal
from decouple import config as env

_PLUMBER_URL = env("PLUMBER_API_URL")
_PLUMBER_KEY = env("PLUMBER_API_KEY")


class BaseClient(object):

    def __init__(self):
        self.base_url = _PLUMBER_URL
        self.auth = {"token": _PLUMBER_KEY}

    def make_request(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"] = "GET",
        query: dict = {},
        body: dict = {},
    ) -> requests.Response:
        if method not in ["GET", "POST", "PATCH", "DELETE", "PUT"]:
            return

        headers = {"x-api-key": self.auth.get("token")}
        url = f"{self.base_url}/{endpoint}"

        session = requests.Session()
        return session.request(method, url, headers=headers, params=query, json=body)
