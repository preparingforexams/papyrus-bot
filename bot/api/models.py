from typing import Optional, List

from pydantic import BaseModel

from ..helper import escape_markdown


class ChatBase(BaseModel):
    id: int
    name: str


class ChatCreate(ChatBase):
    chat: ChatBase


class Chat(ChatBase):
    pass


class ItemBase(BaseModel):
    name: str
    description: Optional[str]
    done: bool = False


class ItemCreate(BaseModel):
    item: ItemBase


class ItemUpdateChangeset(BaseModel):
    id: Optional[int]
    name: Optional[str]
    description: Optional[str]
    done: Optional[bool]


class ItemUpdate(BaseModel):
    id: int
    item: ItemUpdateChangeset


class Item(ItemBase):
    id: int

    def __str__(self):
        s = escape_markdown(self.name)
        if self.description:
            description = escape_markdown(self.description)
            s += f"\n{description}"

        return s


class ItemResponse(BaseModel):
    data: List[Item]
