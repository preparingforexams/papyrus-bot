import enum
import inspect
import json
import os
from typing import Dict, Optional

import requests

from . import models
from ..helper import escape_markdown
from ..logger import create_logger

API_BASE_URL = os.getenv("API_BASE_URL") or "http://localhost:4000"
API_BASE_PATH = os.getenv("API_BASE_PATH") or "api"


class ApiException(Exception):
    response: requests.Response

    def __str__(self):
        s = "failure\n```\n"
        if isinstance(self.args[0], requests.Response):
            try:
                s += escape_markdown(json.dumps(self.args[0].json()['errors'], indent=2))
            except TypeError:
                s = escape_markdown("\n".join(self.args))[:4000]  # simply cut off error message in case of HTML content
        else:
            s = escape_markdown("\n".join(self.args))[:4000]  # simply cut off error message in case of HTML content
        s += "\n```"

        return s


class Endpoint(enum.Enum):
    ITEM = "items"
    CHAT = "chats"


def get(endpoint: Endpoint) -> requests.Response:
    url = "/".join([API_BASE_URL, API_BASE_PATH, endpoint.value])

    return requests.get(url)


def post(endpoint: Endpoint, data: Dict, headers: Dict = None) -> requests.Response:
    if not headers:
        headers = {}
    if "Content-Type" not in headers.keys():
        headers.update({"Content-Type": "application/json"})

    url = "/".join([API_BASE_URL, API_BASE_PATH, endpoint.value])

    data = json.dumps(data)
    return requests.post(url, data=data, headers=headers)


def put(endpoint: Endpoint, data: Dict, headers: Dict = None) -> requests.Response:
    if not headers:
        headers = {}
    if "Content-Type" not in headers.keys():
        headers.update({"Content-Type": "application/json"})

    url = "/".join([API_BASE_URL, API_BASE_PATH, endpoint.value])

    data = json.dumps(data)
    return requests.put(url, data=data, headers=headers)


# noinspection DuplicatedCode
def create_item(item: models.ItemBase) -> models.Item:
    log = create_logger(inspect.currentframe().f_code.co_name)

    response = post(
        Endpoint.ITEM,
        models.ItemCreate.parse_obj({
            "item": item,
        }).dict()
    )
    if not response.ok:
        log.error(f"response nok for `api#add_item`\n\t[{response.status_code}]: {response.text}")
        raise ApiException(response)

    data = response.json()["data"]
    return models.Item.parse_obj(data)


# noinspection DuplicatedCode
def create_chat(chat: models.ChatBase) -> Optional[models.Chat]:
    log = create_logger(inspect.currentframe().f_code.co_name)

    response = post(
        Endpoint.CHAT,
        models.ChatCreate.parse_obj({
            "chat": chat,
        }).dict()
    )
    if not response.ok:
        log.error(f"response nok for `api#add_chat`\n\t[{response.status_code}]: {response.text}")
        raise ApiException(response)

    return models.Chat.parse_obj(response.json()["data"])


def get_items() -> models.ItemResponse:
    log = create_logger(inspect.currentframe().f_code.co_name)

    response = get(Endpoint.ITEM)
    if not response.ok:
        log.error(f"response nok for `api#get_items`\n\t[{response.status_code}]: {response.text}")
        raise ApiException(response)

    return models.ItemResponse.parse_obj(response.json())


def find_item_by_name(name: str) -> Optional[models.Item]:
    items = get_items()
    for item in items.data:
        if item.name.lower() == name.lower():
            return item

    return None


def mark_as_done(item: models.Item) -> models.ItemResponse:
    log = create_logger(inspect.currentframe().f_code.co_name)

    update = models.ItemUpdate.parse_obj({
        "id": item.id,
        "item": {
            "done": True
        }
    })

    response = put(Endpoint.ITEM, update.dict(exclude_unset=True))
    if not response.ok:
        log.error(f"response nok for `api#mark_as_done`\n\t[{response.status_code}]: {response.text}")
        raise ApiException(response)

    print(response.json())
    return models.Item.parse_obj(response.json()["data"])
