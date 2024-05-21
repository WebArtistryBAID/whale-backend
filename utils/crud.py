import datetime
from decimal import Decimal, getcontext

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from data.models import *
from data.schemas import OrderedItemCreateSchema, OrderCreateSchema


getcontext().prec = 5


def ensure_not_none(value):
    if value is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return value


def create_user(session: Session, user_id: str, user_name: str, pinyin: str | None = None, phone: str | None = None):
    user = User(
        id=user_id,
        name=user_name,
        pinyin=pinyin,
        phone=phone
    )
    session.add(user)
    session.commit()
    return user


def get_user(session: Session, user_id: str):
    return session.query(User).filter(User.id == user_id).one_or_none()


def delete_user(session: Session, user: User):
    session.delete(user)
    session.commit()


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


def get_option_item(session: Session, optionitem_id: int):
    return session.query(OptionItem).filter(OptionItem.id == optionitem_id).one_or_none()


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
    for id in schema.appliedOptions:
        ordered_item.appliedOptions.append(get_option_item(session, id))
    session.add(ordered_item)
    return ordered_item


def get_order(session: Session, order_id: int):
    return session.query(Order).filter(Order.id == order_id).one_or_none()


def get_order_by_number(session: Session, number: str):
    return session.query(Order).filter(Order.number == number).order_by(Order.createdTime.desc()).first()


def get_orders_query_by_user(user_id: str):
    # Note that this does not return everything queried - this is an uncompleted query to be paginated
    return select(Order).filter(Order.userId == user_id).order_by(Order.createdTime.desc())


def get_orders_by_user(session: Session, user_id: str):
    return session.query(Order).filter(Order.userId == user_id).order_by(Order.createdTime.desc()).all()


def create_order(session: Session, schema: OrderCreateSchema, user: User):
    order = Order(
        status=OrderStatus.notStarted,
        createdTime=datetime.datetime.now(),
        userId=user.id
    )
    for item in schema.items:
        order.items.append(create_ordered_item(session, order.id, item))
    total_price = Decimal("0")
    for item in order.items:
        item_type = get_item_type(session, item.itemTypeId)
        total_price += item_type.basePrice * item_type.salePercent
        for option in item.appliedOptions:
            total_price += option.priceChange
        total_price *= item.amount
    order.totalPrice = total_price

    latest = session.query(Order).order_by(Order.createdTime.desc()).first()
    if latest is None or (datetime.datetime.today() - latest.createdTime).days > 0:
        order.number = "001"
    else:
        order.number = str(int(latest.number) + 1).zfill(3)
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
