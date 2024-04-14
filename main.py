from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, MetaData, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create the object of FastAPI
app = FastAPI()

# connect to the database
engine = create_engine('sqlite:///webdev.db')
# metadata
metadata = MetaData()
metadata.reflect(bind=engine)
# create Session class
Session = sessionmaker(bind=engine)
# create session obj
session = Session()

# HANDLES
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

#-----CATEGORIES------
# GET /categories
# Get a list of available Category(s).
# Request format: Empty
# Response format: 200 OK application/json
# [List of Category]
@app.get("/categories")
async def categories():
    # get datas
    results = engine.execute(Categories.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "name": row.name} for row in results]
    return formatted_results

# GET /category
# Get a category from an ID.
# Request format (query parameters):
# 	id: int, the ID corresponding to the category
# Response format:
#   If successful: 200 OK application/json
# 		    {Category}
#   If unsuccessful: 404 Not Found / 401 Bad Request
@app.get("/category")
async def category(id: str):
    if (id == ''):    # correspond link that format like /category?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /category?id=1102
        # get datas
        category_content = session.query(Categories).filter_by(id=int(id)).first()
        if category_content:
            # convert format to json, then return
            category = [{"id": category_content.id, "name": category_content.name}]
            return category
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

#-----TAGS------
# GET /tags
# List all tags.
# Request format: Empty
# Response format: 200 OK application/json
# [List of Tag]
@app.get("/tags")
async def tags():
    # get datas
    results = engine.execute(Tags.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "name": row.name, "color": row.color} for row in results]
    return formatted_results

# GET /tag
# Get a tag from an ID.
# Request format (query parameters):
# 	id: int, the ID corresponding to the tag
# Response format:
#   If successful: 200 OK application/json
# 		{Tag}
#   If unsuccessful: 404 Not Found / 401 Bad Request
@app.get("/tag")
async def tag(id: str):
    if (id == ''):    # correspond link that format like /tag?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /tag?id=1102
        # get datas
        tag_content = session.query(Tags).filter_by(id=int(id)).first()
        if tag_content:
            # convert format to json, then return
            tag = [{"id": tag_content.id, "name": tag_content.name, "color": tag_content.color}]
            return tag
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

#-----ITEMTYPES------
# GET /items
# Get a list of available ItemType(s) (repeated)
# Request format: Empty
# Response format: 200 OK application/json
# [List of ItemType]
@app.get("/items")
async def items():
    # get datas
    results = engine.execute(ItemTypes.select())
    # convert format to json, then return
    formatted_results = []
    for row in results:
        tags = session.query(ItemTypes_Tags).filter_by(item=row['id']).all()
        tags_list = []
        for onetag in tags:
            category = session.query(Categories).filter_by(id=onetag.id).first()
            tag_name = session.query(Tags).filter_by(id=onetag.tag).first()
            tags_list.append(tag_name)
        formatted_result = [{"id": row.id, "category": category, "name": row.name, "tags": tags_list, "description": row.description, "base_price": row.base_price, "sale_percent": row.sale_percent}]
        formatted_results.append(formatted_result)
    return formatted_results

# GET /item
# Get an ItemType from an ID.
# Request format (query parameters):
# 	id: int, the ID corresponding to the ItemType
# Response format:
#   If successful: 200 OK application/json
# 	    {ItemType}
#   If unsuccessful: 404 Not Found / 401 Bad Request
@app.get("/item")
async def item(id: str):
    if (id == ''):    # correspond link that format like /item?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /item?id=1102
        # get datas
        itemtype_content = session.query(ItemTypes).filter_by(id=int(id)).first()
        if itemtype_content:
            category = session.query(Categories).filter_by(id=itemtype_content.id).first()
            tags = session.query(ItemTypes_Tags).filter_by(item=itemtype_content['id']).all()
            tags_list = []
            for onetag in tags:
                category = session.query(Categories).filter_by(id=onetag.id).first()
                tag_name = session.query(Tags).filter_by(id=onetag.tag).first()
                tags_list.append(tag_name)
            # convert format to json, then return
            itemtype = [{"id": itemtype_content.id, "category_id":category, "name": itemtype_content.name, "tags": tags_list, "description": itemtype_content.description, "base_price": itemtype_content.base_price, "sale_percent": itemtype_content.sale_percent}]
            return itemtype
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

# class ItemType(Base):
#     __tablename__ = 'ItemTypes'
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
#     category_id = Column(Integer, ForeignKey('Categories.id'), comment="C 表外键约束，产品类别")
#     name = Column(String(20), comment="产品名称")
#     description = Column(String(256), comment="产品描述")
#     base_price = Column(Float, comment="产品基础价格")
#     sale_percent = Column(Float, comment="产品打折情况")

#-----SEETINGS------
@app.get("/settings")
async def all_settings(key: str):
    # SECTION 1: GET ALL SETTINGS
    if (key == ''):    # correspond link that format like /settings?key=
        # get datas
        results = engine.execute(Settings.select())
        # convert format to json, then return
        formatted_results = [{"key": row.item, "value": row.value} for row in results]
        return formatted_results
    # SECTION 2: GET ONE PARTICULAR SETTING THAT SUBMIT BY GET METHOD
    else:    # correspond link that format like /settings?key=value
        query = session.query(Settings).filter_by(item=key).first()    # search if key exist
        if query:    # if key exist
            return query.value
        else:    # else
            return {"404 ERROR": "Key doesn't exist! Please check your input!"}

# get a specific order in json
@app.get("/order")
async def specific_order(id: str):
    if (id == ''):    # correspond link that format like /order?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /order?id=1102
        order_content = session.query(Orders).filter_by(id=int(id)).first()
        if order_content:
            order = [{"order_id": order_content.id,
                      "number": order_content.number,
                      "total_price": order_content.total_price,
                      "status": order_content.status,
                      "create_time": order_content.created_time,
                      "contact_name": order_content.contact_name,
                      "contact_room": order_content.contact_room}]

            ordered_items_ids = session.query(Orders_OrderedItems).filter_by(order_id=int(id)).all()
            for ordered_item_id in ordered_items_ids:
                ordered_item = session.query(OrderedItems).filter_by(id=ordered_item_id.ordereditem_id).first()
                item_type = session.query(ItemTypes).filter_by(id=ordered_item.item_type_id).first()
                item_format = [{"name": item_type.name,
                                "description": item_type.description,
                                "base_price": item_type.base_price,
                                "sale_percent": item_type.sale_percent}]

                options = session.query(OrderedItems_OptionItems).filter_by(id=ordered_item.item_type_id).all()
                for option in options:
                    option_content = session.query(OptionItems).filter_by(id=option.option_item_id).first()
                    option_type = session.query(OptionTypes).filter_by(id=option_content.type_id).first()
                    option_format = [{"name": option_type.name,
                                      "name": option_content.name,
                                      "price_change": option_content.price_change}]

                    one_item_format = [{"item": item_format,
                                        "option": option_format,
                                        "amount": ordered_item.amount}]
                    order.append(one_item_format)
            return order
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

#-----OPTIONTYPES------
# GET /optiontypes
# List all option types.
# Request format: Empty
# Response format: 200 OK application/json
# [List of OptionType]
@app.get("/optiontypes")
async def optiontypes():
    # get datas
    results = engine.execute(Tags.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "name": row.name} for row in results]
    return formatted_results

# GET /optiontype
# Get an OptionType from an ID.
# Request format (query parameters):
# 	id: int, the ID corresponding to the OptionType
# Response format:
#   If successful: 200 OK application/json
# 		{OptionType}
# 	If unsuccessful: 404 Not Found / 401 Bad Request
@app.get("/optiontype")
async def optiontype(id: str):
    if (id == ''):    # correspond link that format like /optiontype?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /optiontype?id=1102
        # get datas
        optiontype_content = session.query(Tags).filter_by(id=int(id)).first()
        if optiontype_content:
            # convert format to json, then return
            tag = [{"id": optiontype_content.id, "name": optiontype_content.name}]
            return tag
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

# GET /optionitems
# List all option items.
# Request format: Empty
# Response format: 200 OK application/json
# [List of OptionItem]
@app.get("/optionitems")
async def optionitems():
    # get datas
    results = engine.execute(OptionItems.select())
    # convert format to json, then return
    formatted_results = []
    for row in results:
        optiontype = session.query(OptionTypes).filter_by(id=row.id).first()
        formatted_result = [{"id": row.id, "type_id":optiontype, "name": row.name, "price_change": row.price_change}]
        formatted_results.append(formatted_result)
    return formatted_results

# GET /optionitem
# Get an OptionItem from an ID.
# Request format (query parameters):
# 	id: int, the ID corresponding to the OptionItem
# Response format:
#   If successful: 200 OK application/json
# 	    {OptionItem}
# 	If unsuccessful: 404 Not Found / 401 Bad Request
@app.get("/optionitem")
async def optionitem(id: str):
    if (id == ''):    # correspond link that format like /optionitem?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /optionitem?id=1102
        # get datas
        optionitem_content = session.query(OptionItems).filter_by(id=int(id)).first()
        if optionitem_content:
            optiontype = session.query(OptionTypes).filter_by(id=optionitem_content.id).first()
            # convert format to json, then return
            optionitem = [{"id": optionitem_content.id, "type_id":optiontype, "name": optionitem_content.name, "price_change": optionitem_content.price_change}]
            return optionitem
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}


# close the connection
session.close()
