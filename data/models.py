import enum

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DECIMAL, Enum, DateTime, Table
from sqlalchemy.orm import relationship

from data.database import Base, storage

orderedItemOptionAssoc = Table('ordered_item_option_association', Base.metadata,
                               Column('ordered_item_id', Integer, ForeignKey('ordereditems.id', ondelete='CASCADE'),
                                      primary_key=True),
                               Column('option_item_id', Integer, ForeignKey('optionitems.id', ondelete='CASCADE'),
                                      primary_key=True)
                               )


tagItemTypeAssoc = Table('tag_item_type_association', Base.metadata,
                         Column('item_type_id', Integer, ForeignKey('itemtypes.id', ondelete='CASCADE'),
                                primary_key=True),
                         Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'),
                                primary_key=True)
                         )


itemOptionAssociation = Table('item_option_association', Base.metadata,
                              Column('item_type_id', Integer, ForeignKey('itemtypes.id', ondelete='CASCADE'),
                                     primary_key=True),
                              Column('option_type_id', Integer, ForeignKey('optiontypes.id', ondelete='CASCADE'),
                                     primary_key=True)
                              )


class User(Base):
    __tablename__ = 'users'

    id = Column(String(9), primary_key=True)
    name = Column(String(255))
    pinyin = Column(String(255))
    phone = Column(String(255))
    permissions = Column(String(1024), default="")
    blocked = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user')

    def __str__(self):
        return self.name + ' (' + self.pinyin + ')'


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(12))
    items = relationship('ItemType', back_populates='category')

    def __str__(self):
        return self.name


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    color = Column(String(10))

    def __str__(self):
        return self.name


class OptionItem(Base):
    __tablename__ = 'optionitems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    typeId = Column(Integer, ForeignKey('optiontypes.id', ondelete='CASCADE'))
    type = relationship('OptionType', back_populates='items', foreign_keys=[typeId])
    name = Column(String(20))
    isDefault = Column(Boolean, default=False, nullable=False)
    priceChange = Column(DECIMAL(5, 2))

    def __str__(self):
        return self.name


class OptionType(Base):
    __tablename__ = 'optiontypes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    items = relationship('OptionItem', back_populates='type', foreign_keys=[OptionItem.typeId])

    def __str__(self):
        return self.name


class ItemType(Base):
    __tablename__ = 'itemtypes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoryId = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    category = relationship('Category', back_populates='items')
    name = Column(String(20))
    image = Column(FileType(storage=storage))
    tags = relationship('Tag', secondary=tagItemTypeAssoc)
    description = Column(String(256))
    shortDescription = Column(String(256))
    options = relationship('OptionType', secondary=itemOptionAssociation)
    basePrice = Column(DECIMAL(5, 2))
    salePercent = Column(DECIMAL(5, 2))

    def __str__(self):
        return self.name


class OrderedItem(Base):
    __tablename__ = 'ordereditems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'))
    order = relationship('Order', back_populates='items')
    itemTypeId = Column(Integer, ForeignKey('itemtypes.id', ondelete='SET NULL'))
    itemType = relationship('ItemType')
    appliedOptions = relationship('OptionItem', secondary=orderedItemOptionAssoc)
    amount = Column(Integer)

    def __str__(self):
        return self.itemType.name + ' x' + str(self.amount) + ' (' + ', '.join([option.name for option in self.appliedOptions]) + ')'


class OrderStatus(enum.Enum):
    notStarted = 'notStarted'
    inProgress = 'inProgress'
    ready = 'ready'
    pickedUp = 'pickedUp'


class OrderType(enum.Enum):
    pickUp = 'pickUp'
    delivery = 'delivery'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    items = relationship('OrderedItem', back_populates='order')
    totalPrice = Column(DECIMAL(5, 2))
    number = Column(String(5))
    status = Column(Enum(OrderStatus))
    createdTime = Column(DateTime)
    type = Column(Enum(OrderType))
    deliveryRoom = Column(String(64))
    userId = Column(String(9), ForeignKey('users.id', ondelete='SET NULL'))
    user = relationship('User', back_populates='orders')
    onSiteName = Column(String(255))


class Ad(Base):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))
    image = Column(FileType(storage=storage))
    url = Column(String(1024))


class SettingItem(Base):
    __tablename__ = 'settingsitems'

    key = Column(String(32), primary_key=True)
    value = Column(String(2048))
