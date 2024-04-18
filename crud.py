import datetime
from decimal import Decimal, getcontext

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import *
from schemas import GenericErrorSchema, OrderedItemCreateSchema, OrderCreateSchema


getcontext().prec = 5


def assert_not_null(value):
    if value is None:
        raise HTTPException(status_code=404, detail=GenericErrorSchema(message="Not Found"))
    return value


def get_categories(session: Session):
    return session.query(Category).all()


def get_category(session: Session, category_id: int):
    return session.query(Category).filter(Category.id == category_id).one_or_none()


def get_tags(session: Session):
    return session.query(Tag).all()


def get_tag(session: Session, tag_id: int):
    return session.query(Tag).filter(Tag.id == tag_id).one_or_none()


def get_option_types(session: Session):
    return session.query(OptionType).all()


def get_option_type(session: Session, optiontype_id: int):
    return session.query(OptionType).filter(OptionType.id == optiontype_id).one_or_none()


def get_option_items(session: Session, optiontype_id: int):
    return session.query(OptionItem).filter(OptionItem.type_id == optiontype_id).all()


def get_item_types(session: Session):
    return session.query(ItemType).all()


def get_item_type(session: Session, itemtype_id: int):
    return session.query(ItemType).filter(ItemType.id == itemtype_id).one_or_none()


def get_item_types_by_category(session: Session, category_id: int):
    return session.query(ItemType).filter(ItemType.categoryId == category_id).all()


def get_ordered_item(session: Session, ordereditem_id: int):
    return session.query(OrderedItem).filter(OrderedItem.id == ordereditem_id).one_or_none()


def create_ordered_item(session: Session, order: int, schema: OrderedItemCreateSchema):
    ordered_item = OrderedItem(
        orderId=order,
        itemTypeId=schema.itemType,
        amount=schema.amount
    )
    ordered_item.appliedOptions = [get_option_type(session, id) for id in schema.appliedOptions]
    session.add(ordered_item)
    session.commit()
    return ordered_item


def get_order(session: Session, order_id: int):
    return session.query(Order).filter(Order.id == order_id).one_or_none()


def create_order(session: Session, schema: OrderCreateSchema):
    order = Order(
        status=OrderStatus.notStarted,
        createdTime=datetime.datetime.now(),
        contactName=schema.contactName,
        contactRoom=schema.contactRoom
    )
    order.items = [create_ordered_item(session, order.id, item) for item in schema.items]
    total_price = Decimal("0")
    for item in order.items:
        total_price += (item.itemType.basePrice * item.amount) * item.itemType.salePercent
        for option in item.appliedOptions:
            total_price += option.priceChange
    order.totalPrice = total_price

    latest = session.query(Order).order_by(Order.createdTime.desc()).first()
    if latest is None or (datetime.datetime.today() - latest.createdTime) > 0:
        order.number = "001"
    else:
        order.number = (int(latest.number) + 1).zfill(3)
    session.add(order)
    session.commit()
    return order


def update_order_status(session: Session, order: Order, new_status: str):
    order.status = new_status
    session.commit()


def delete_order(session: Session, order: Order):
    session.delete(order)
    session.commit()


def get_settings(session: Session, key: str):
    return session.query(SettingItem).filter(SettingItem.key == key).one_or_none()
