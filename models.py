import enum

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DECIMAL, Enum, DateTime, Table
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(12))
    items = relationship('ItemType', back_populates='category', lazy='dynamic')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    color = Column(String(6))


class OptionItem(Base):
    __tablename__ = 'optionitems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    typeId = Column(Integer, ForeignKey('optiontypes.id', ondelete='CASCADE'))
    type = relationship('OptionType', back_populates='items')
    name = Column(String(20))
    priceChange = Column(DECIMAL(5, 2))


itemOptionAssociation = Table('item_option_association', Base.metadata,
                              Column('item_type_id', Integer, ForeignKey('itemtypes.id', ondelete='CASCADE'),
                                     primary_key=True),
                              Column('option_type_id', Integer, ForeignKey('optiontypes.id', ondelete='CASCADE'),
                                     primary_key=True)
                              )


class OptionType(Base):
    __tablename__ = 'optiontypes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    items = relationship('OptionItem', back_populates='type', lazy='dynamic')
    defaultId = Column(Integer, ForeignKey('optionitems.id', ondelete='SET NULL'))
    default = relationship('OptionItem', foreign_keys='defaultId')


class ItemType(Base):
    __tablename__ = 'itemtypes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoryId = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    category = relationship('Category', back_populates='items')
    name = Column(String(20))
    image = Column(String)
    description = Column(String(256))
    shortDescription = Column(String(256))
    options = relationship('OptionType', secondary=itemOptionAssociation)
    basePrice = Column(DECIMAL(5, 2))
    salePercent = Column(Float)


orderedItemOptionAssoc = Table('ordered_item_option_association', Base.metadata,
                               Column('ordered_item_id', Integer, ForeignKey('ordereditems.id', ondelete='CASCADE'),
                                      primary_key=True),
                               Column('option_item_id', Integer, ForeignKey('optionitems.id', ondelete='CASCADE'),
                                      primary_key=True)
                               )


class OrderedItem(Base):
    __tablename__ = 'ordereditems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'))
    order = relationship('Order', back_populates='items')
    itemTypeId = Column(Integer, ForeignKey('itemtypes.id', ondelete='SET NULL'))
    itemType = relationship('ItemType')
    appliedOptions = relationship('OptionItem', secondary=orderedItemOptionAssoc)
    amount = Column(Integer)


class OrderStatus(enum.Enum):
    notStarted = 'notStarted'
    inProgress = 'inProgress'
    ready = 'ready'
    pickedUp = 'pickedUp'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    items = relationship('OrderedItem', back_populates='order', lazy='dynamic')
    totalPrice = Column(DECIMAL(5, 2))
    number = Column(String(5))
    status = Column(Enum(OrderStatus))
    createdTime = Column(DateTime)
    contactName = Column(String(64))
    contactRoom = Column(String(5))


class SettingItem(Base):
    __tablename__ = 'settingsitems'

    key = Column(String, primary_key=True)
    value = Column(String)
