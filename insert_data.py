# insert data (test) into datatable
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# connect to the database
engine = create_engine('sqlite:///webdev.db')
# metadata
metadata = MetaData()
metadata.reflect(bind=engine)
# create Session class
Session = sessionmaker(bind=engine)
# create session obj
session = Session()

# handles
Categories = metadata.tables['Categories']
Tags = metadata.tables['Tags']
ItemTypes = metadata.tables['ItemTypes']
ItemTypes_Tags = metadata.tables['ItemTypes_Tags']
OptionTypes = metadata.tables['OptionTypes']
OptionItems = metadata.tables['OptionItems']
OrderedItems = metadata.tables['OrderedItems']
OrderedItems_OptionItems = metadata.tables['OrderedItems_OptionItems']
Orders = metadata.tables['Orders']
Orders_OrderedItems = metadata.tables['Orders_OrderedItems']
Settings = metadata.tables['Settings']

# Categories:
# 1) coffee
# 2) tea
data_c = [{"name": "coffee"},
          {"name": "tea"}]
session.execute(Categories.insert(), data_c)

# Tags:
# 1) caffeine
# 2) hot
# 3) cold
data_t = [{"name": "caffeine", "color": "#ff0000"},
          {"name": "hot", "color": "#00ff00"},
          {"name": "cold", "color": "#0000ff"}]
session.execute(Tags.insert(), data_t)

# Settings:
# 1) a-111
# 2) b-222
data_s = [{"item": "a", "value": "111"},
          {"item": "b", "value": "222"}]
session.execute(Settings.insert(), data_s)

# ItemTypes
data_it = [{"category_id": 1, "name":"coffee a", "description": "coffee aaa", "base_price": 10.00, "sale_percent": 0.9},
           {"category_id": 1, "name":"coffee b", "description": "coffee bbb", "base_price": 9.00, "sale_percent": 1},
           {"category_id": 2, "name":"red tea", "description": "red tea good", "base_price": 11.00, "sale_percent": 0.8}]
session.execute(ItemTypes.insert(), data_it)

# ItemTypes_Tags
data_it_t = [{"item": 1, "tag": 1},
             {"item": 1, "tag": 3},
             {"item": 2, "tag": 1},
             {"item": 2, "tag": 2},
             {"item": 3, "tag": 1}]
session.execute(ItemTypes_Tags.insert(), data_it_t)

# OptionTypes
data_ot = [{"name": "sugar", "default": 1},
           {"name": "milk", "default": 3}]
session.execute(OptionTypes.insert(), data_ot)

# OptionItems
data_oi = [{"type_id": "1", "name": "full", "price_change": 0},
           {"type_id": "1", "name": "less", "price_change": -0.5},
           {"type_id": "2", "name": "yes", "price_change": 0},
           {"type_id": "2", "name": "no", "price_change": 0}]
session.execute(OptionItems.insert(), data_oi)

# Orders
data_od = [{"number": 1, "total_price": 21, "status": "start", "created_time": "2024-04-14 13:00", "contact_name": "ltx", "contact_room": 201}]
session.execute(Orders.insert(), data_od)

# OrderedItems
data_odi = [{"item_type_id": "1", "amount": 1},
            {"item_type_id": "3", "amount": 1}]
session.execute(OrderedItems.insert(), data_odi)

# Orders_OrderedItems
data_od_odi = [{"order_id": 1, "ordereditem_id": 1},
               {"order_id": 1, "ordereditem_id": 2}]
session.execute(Orders_OrderedItems.insert(), data_od_odi)

# OrderedItems_OptionItems
data_odi_oi = [{"ordered_item_id": 1, "option_item_id": 1},
               {"ordered_item_id": 1, "option_item_id": 4},
               {"ordered_item_id": 2, "option_item_id": 2},
               {"ordered_item_id": 2, "option_item_id": 4}]
session.execute(OrderedItems_OptionItems.insert(), data_odi_oi)

session.commit()