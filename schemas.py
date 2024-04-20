from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int
    name: str


class TagSchema(BaseModel):
    id: int
    name: str
    color: str


class OptionTypeSchema(BaseModel):
    id: int
    name: str
    defaultId: int

    class Config:
        from_attributes = True


class OptionItemSchema(BaseModel):
    id: int
    type: OptionTypeSchema
    name: str
    priceChange: Decimal

    class Config:
        from_attributes = True


class ItemTypeSchema(BaseModel):
    id: int
    category: CategorySchema
    name: str
    image: str
    tags: List[TagSchema]
    description: str
    shortDescription: str
    options: List[OptionTypeSchema]
    basePrice: Decimal
    salePercent: float

    class Config:
        from_attributes = True


class OrderedItemSchema(BaseModel):
    id: int
    orderId: int
    itemType: ItemTypeSchema
    appliedOptions: List[OptionItemSchema]
    amount: int

    class Config:
        from_attributes = True


class OrderedItemCreateSchema(BaseModel):
    itemType: int
    appliedOptions: List[int]
    amount: int

    class Config:
        from_attributes = True


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
        from_attributes = True


class OrderCreateSchema(BaseModel):
    items: List[OrderedItemCreateSchema]
    contactName: str
    contactRoom: str


class OrderEstimateSchema(BaseModel):
    time: int
    orders: int


class SettingItemSchema(BaseModel):
    key: str
    value: str


class GenericErrorSchema(BaseModel):
    message: str
