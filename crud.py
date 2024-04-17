from sqlalchemy.orm import Session
from models import *


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


def get_order(session: Session, order_id: int):
    return session.query(Order).filter(Order.id == order_id).one_or_none()


def update_order_status(session: Session, order_id: int, new_status: str):
    order = session.query(Order).filter(Order.id == order_id).one_or_none()
    if order:
        order.status = new_status
        session.commit()
        return True
    return False


def get_settings(session: Session, key: str):
    return session.query(SettingItem).filter(SettingItem.key == key).one_or_none()
