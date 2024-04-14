from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 创建一个基类
Base = declarative_base()

# 定义数据表模型
class Category(Base):
    __tablename__ = 'Categories'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    name = Column(String(12), comment="产品类别名称")

class Tag(Base):
    __tablename__ = 'Tags'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    name = Column(String(20), comment="标签名")
    color = Column(String(20), comment="标签在前端显示的颜色，16 进制")

class ItemType(Base):
    __tablename__ = 'ItemTypes'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    category_id = Column(Integer, ForeignKey('Categories.id'), comment="C 表外键约束，产品类别")
    name = Column(String(20), comment="产品名称")
    description = Column(String(256), comment="产品描述")
    base_price = Column(Float, comment="产品基础价格")
    sale_percent = Column(Float, comment="产品打折情况")

class ItemType_Tag(Base):
    __tablename__ = 'ItemTypes_Tags'

    # id 为主键，多对多关系
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    item = Column(Integer, ForeignKey('ItemTypes.id'), comment="产品 id")
    tag = Column(Integer, ForeignKey('Tags.id'), comment="产品标签 id")

class OptionType(Base):
    __tablename__ = 'OptionTypes'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    name = Column(String(20), comment="产品可选项类别")
    default = Column(Integer, ForeignKey('OptionItems.id'), comment="OI 表外键约束，可选项的默认值")

class OptionItem(Base):
    __tablename__ = 'OptionItems'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    type_id = Column(Integer, ForeignKey('OptionTypes.id'), comment="OT 表外键约束，可选项的类别")
    name = Column(String(20), comment="可选项的值")
    price_change = Column(Float, comment="可选项带来的价格变化")

class OrderedItem(Base):
    __tablename__ = 'OrderedItems'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    item_type_id = Column(Integer, ForeignKey('ItemTypes.id'), comment="下单产品详细信息")
    amount = Column(Integer, comment="下单产品数量")

class OrderedItem_OptionItem(Base):
    __tablename__ = 'OrderedItems_OptionItems'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    ordered_item_id = Column(Integer, ForeignKey('OrderedItems.id'), comment="下单 id")
    option_item_id = Column(Integer, ForeignKey('OptionItems.id'), comment="产品可选项 id")

class Order(Base):
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    number = Column(Integer, comment="订单编号")
    total_price = Column(Float, comment="最终价格")
    status = Column(String(20), comment="产品状态")
    created_time = Column(String(64), comment="下单时间")
    contact_name = Column(String(64), comment="下单人姓名")
    contact_room = Column(String(10), comment="下单人房间号")

class Order_OrderedItem(Base):
    __tablename__ = 'Orders_OrderedItems'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    order_id = Column(Integer, ForeignKey('Orders.id'), comment="O表外键，订单 id")
    ordereditem_id = Column(Integer, ForeignKey('OrderedItems.id'), comment="产品情况 id")

class Setting(Base):
    __tablename__ = 'Settings'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    item = Column(String(1024), comment="网站配置——键")
    value = Column(String(1024), comment="网站配置——值")

# 创建数据库连接
engine = create_engine('sqlite:///webdev.db')

# 创建数据表
Base.metadata.create_all(engine)
