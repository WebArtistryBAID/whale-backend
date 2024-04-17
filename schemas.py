from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int
    name: str


class TagSchema(BaseModel):
    id: int
    name: str
    color: str


class OptionItemSchema(BaseModel):
    id: int
    typeId: int
    name: str
    priceChange: Decimal


class OptionTypeSchema(BaseModel):
    id: int
    name: str
    defaultId: Optional[int] = None


class ItemTypeSchema(BaseModel):
    id: int
    categoryId: int
    name: str
    image: str
    description: str
    shortDescription: str
    options: List[int]
    basePrice: Decimal
    salePercent: float


class OrderedItemSchema(BaseModel):
    id: int
    orderId: int
    itemTypeId: Optional[int] = None
    appliedOptions: List[int]
    amount: int


class OrderSchema(BaseModel):
    id: int
    totalPrice: Decimal
    number: str
    status: str  # notStarted, inProgress, ready, or pickedUp
    createdTime: datetime
    contactName: str
    contactRoom: str
    items: List[int]


class SettingItemSchema(BaseModel):
    key: str
    value: str
