import os
import re
import json
import arrow
import requests
from typing_extensions import Literal
from decouple import config as env

_PLUMBER_URL = env("PLUMBER_API_URL")
_PLUMBER_KEY = env("PLUMBER_API_KEY")
_PLUMBER_LOG = env("PLUMBER_API_LOG", default=False, cast=bool)


class BaseClient(object):

    def __init__(self):
        self.base_url = _PLUMBER_URL
        self.auth = {"token": _PLUMBER_KEY}

    def __save_request_log(
        self,
        url: str,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        response: requests.Response,
        headers: dict | None = None,
        query: dict | None = None,
        body: dict | None = None,
    ) -> None:
        file_path = "log/plumber"
        os.makedirs(file_path, exist_ok=True)
        file_name = f"{file_path}/{arrow.now()}_{method}_{url}.json",
        with open(
            re.sub(r'[^\w\-]', '_', file_name),
            "w",
            encoding="utf-8",
        ) as file:
            data = {
                "method": method,
                "url": url,
                "headers": headers,
                "query_params": query,
                "body": body,
                "response": {
                    "status": response.status_code,
                    "body": response.json(),
                },
            }
            json.dump(data, file, indent=4)

    def make_request(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"] = "GET",
        query: dict | None = None,
        body: dict | None = None,
    ) -> requests.Response:
        if method not in ["GET", "POST", "PATCH", "DELETE", "PUT"]:
            return

        headers = {"x-api-key": self.auth.get("token")}
        url = f"{self.base_url}/{endpoint}"

        session = requests.Session()
        response = session.request(
            method, url, headers=headers, params=query, json=body
        )

        if _PLUMBER_LOG:
            self.__save_request_log(url, method, response, headers, query, body)

        return response
