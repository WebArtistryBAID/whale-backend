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
    default: OptionItemSchema

    class Config:
        orm_mode = True


class ItemTypeSchema(BaseModel):
    id: int
    categoryId: int
    name: str
    image: str
    description: str
    shortDescription: str
    options: List[OptionTypeSchema]
    basePrice: Decimal
    salePercent: float

    class Config:
        orm_mode = True


class OrderedItemSchema(BaseModel):
    id: int
    orderId: int
    itemType: ItemTypeSchema
    appliedOptions: List[OptionItemSchema]
    amount: int

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    id: int
    totalPrice: Decimal
    number: str
    status: str  # notStarted, inProgress, ready, or pickedUp
    createdTime: datetime
    contactName: str
    contactRoom: str
    items: List[OrderedItemSchema]

    class Config:
        orm_mode = True


class SettingItemSchema(BaseModel):
    key: str
    value: str
