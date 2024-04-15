from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, MetaData, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Union
import requests

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
            category = {"id": category_content.id, "name": category_content.name}
            return category
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

# POST/PATCH /category
# Create a new (POST) or edit an existing (PATCH) category by ID.
# Request format:
# 	{Category / Partial Category}
# For POST, there must not be an ID. For PATCH, there must be an ID to identify the Category to edit.
# Response format:
# 	If successful: 200 OK application/json
# 		{Category}
# 	If unsuccessful: 404 Not Found / 401 Bad Request
class post_Category(BaseModel):
    name: str

@app.post("/category")
async def post_category(new_category: post_Category):
    is_exist = session.query(Categories).filter_by(name=new_category.name).first()
    if is_exist:
        return {"message": "This Category has already EXIST!"}
    else:
        session.execute(Categories.insert().values(name=new_category.name))    # insert new data
        session.commit()
        add = session.query(Categories).filter_by(name=new_category.name).first()
        return add

# class patch_Category(BaseModel):
#     id: int
#     name: str | None = None
#
# @app.patch("/category")
# async def patch_category(change_category: patch_Category):
#     return change_category

# DELETE /category
# Delete a category by its ID.
# Request format:
# 	{
# 		“id”: int, id for the Category to delete
# 	}
# Response format: 200 OK / 401 Bad Request / 404 Not Found
class delete_Category(BaseModel):
    id: int

@app.delete("/category")
async def delete_category(del_category: delete_Category):
    is_exist = session.query(Categories).filter_by(id=del_category.id).first()
    if is_exist:
        return 11
    else:
        return {"message": "This Category does NOT EXIST!"}


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
            tag = {"id": tag_content.id, "name": tag_content.name, "color": tag_content.color}
            return tag
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}


# POST/PATCH /tag
# Create a new (POST) or edit an existing (PATCH) tag by ID.
# Request format:
# 	{Tag / Partial Tag}
# For POST, there must not be an ID. For PATCH, there must be an ID to identify the Tag to edit.
# Response format:
# 	If successful: 200 OK application/json
# 		{Tag}
# 	If unsuccessful: 404 Not Found / 401 Bad Request
class post_Tag(BaseModel):
    name: str
    color: str

@app.post("/tag")
async def post_tag(new_tag: post_Tag):
    is_exist = session.query(Tags).filter_by(name=new_tag.name).first()
    if is_exist:
        return {"message": "This Category has already EXIST!"}
    else:
        session.execute(Tags.insert().values(name=new_tag.name, color=new_tag.color))    # insert new data
        session.commit()
        add = session.query(Tags).filter_by(name=new_tag.name).first()
        return add


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
            itemtype = {"id": itemtype_content.id, "category_id":category, "name": itemtype_content.name, "tags": tags_list, "description": itemtype_content.description, "base_price": itemtype_content.base_price, "sale_percent": itemtype_content.sale_percent}
            return itemtype
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

#-----SEETINGS------
# GET /settings
# Get all settings values.
# Request format: Empty
# Response format:
# 	If successful: 200 OK application/json
# 		{“key1”: “value1”, “key2”: “value2”, “key3”: “value3”}
# 	If unsuccessful: 401 Bad Request application/json
# 		{
#           “message”: “A short message describing the error”
#       }

# GET /settings
# Get the value of a specific settings key.
# Request format (query parameters):
# 	key: string, corresponding to the setting the get
# Response format:
# 	If successful: 200 OK application/json
# 		A string value, representing the value of the corresponding setting.
# 	If not found: 404 Not Found
# 	If otherwise unsuccessful: 401 Bad Request application/json
# 		{
#           “message”: “A short message describing the error”
#       }

@app.get("/settings")
async def tags():
    # get datas
    results = engine.execute(Settings.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "item": row.item, "value": row.value} for row in results]
    return formatted_results

@app.get("/setting")
async def all_settings(item: str):
    # SECTION 1: GET ALL SETTINGS
    # if (item == ''):    # correspond link that format like /settings?key=
    #     # get datas
    #     results = engine.execute(Settings.select())
    #     # convert format to json, then return
    #     formatted_results = [{"item": row.item, "value": row.value} for row in results]
    #     return formatted_results
    # SECTION 2: GET ONE PARTICULAR SETTING THAT SUBMIT BY GET METHOD
    if item == '':
        return {"message": "ITEM can't be EMPTY!"}
    else:    # correspond link that format like /settings?key=value
        query = session.query(Settings).filter_by(item=item).first()    # search if key exist
        if query:    # if key exist
            return query.value
        else:    # else
            return {"404 ERROR": "Key doesn't exist! Please check your input!"}

# POST /settings
# Update the value of a setting.
# Request format: application/json
# 	{
# 		“key”: string, key for the SettingsItem to create or update,
# 		“value”: string, the value to update the SettingsItem to
# 	}
# Response format: 200 OK / 401 Bad Request
class post_Setting(BaseModel):
    item: str
    value: str

@app.post("/setting")
def post_Setting(new_setting: post_Setting):
    is_exist = session.query(Settings).filter_by(item=new_setting.item).first()
    if is_exist:
        return {"message": "This Setting has already EXIST!"}
    else:
        session.execute(Settings.insert().values(item=new_setting.item, value=new_setting.value))  # insert new data
        session.commit()
        add = session.query(Settings).filter_by(item=new_setting.item).first()
        return add

#-----ORDERS------
# GET /order
# Get a specific Order object by ID.
# Request format (query parameters):
# 	id: the integer corresponding to the ID of the Order
# Response format:
# 	If successful: 200 OK application/json
# 		{Order (with all contents)}
# 	If not found: 404 Not Found
# 	If otherwise unsuccessful: 401 Bad Request application/json
# 		{
#           “message”: “A short message describing the error”
#       }
@app.get("/order")
async def specific_order(id: str):
    if (id == ''):    # correspond link that format like /order?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /order?id=1102
        order_content = session.query(Orders).filter_by(id=int(id)).first()
        if order_content:
            itemtypes = []
            ordered_items_ids = session.query(Orders_OrderedItems).filter_by(order_id=int(id)).all()
            for ordered_item_id in ordered_items_ids:
                ordered_item = session.query(OrderedItems).filter_by(id=ordered_item_id.ordereditem_id).first()
                item = session.query(ItemTypes).filter_by(id=ordered_item.item_type_id).first()
                # some attributes
                category = session.query(Categories).filter_by(id=item.category_id).first()
                amount = ordered_item.amount

                # options that chosen by user
                option_items = session.query(OrderedItems_OptionItems).filter_by(ordered_item_id=ordered_item_id.ordereditem_id).all()
                applied_options = []
                for option_item in option_items:
                    applied_option = session.query(OptionItems).filter_by(id=option_item.option_item_id).first()
                    type = session.query(OptionTypes).filter_by(id=applied_option.type_id).first()
                    applied_option_format = {"id": applied_option.id, "name": applied_option.name, "type": type}
                    applied_options.append(applied_option_format)

                # tags
                tags = session.query(ItemTypes_Tags).filter_by(item=item.id).all()
                tags_list = []
                for onetag in tags:
                    tag_name = session.query(Tags).filter_by(id=onetag.tag).first()
                    tags_list.append(tag_name)
                options = session.query(OrderedItems_OptionItems).filter_by(ordered_item_id=ordered_item.item_type_id).all()

                # options
                options_list = []
                for option in options:
                    option_content = session.query(OptionItems).filter_by(id=option.option_item_id).first()
                    option_type = session.query(OptionTypes).filter_by(id=option_content.type_id).first()
                    options_list.append(option_type)
                    itemtype = {"id": item.id, "category_id": category, "name": item.name, "amount": amount,
                            "tags": tags_list, "description": item.description, "options": options_list, "applied_options": applied_options,
                            "base_price": item.base_price, "sale_percent": item.sale_percent}
                itemtypes.append(itemtype)
            order = {"id": order_content.id,
                      "number": order_content.number,
                      "items": itemtypes,
                      "total_price": order_content.total_price,
                      "status": order_content.status,
                      "create_time": order_content.created_time,
                      "contact_name": order_content.contact_name,
                      "contact_room": order_content.contact_room}
            return order
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

# GET /orders
# List all orders.
# Request format: Empty
# Response format: 200 OK application/json
# [List of Order]
@app.get("/orders")
async def orders():
    orders = []
    results = engine.execute(Orders.select())
    for row in results:
        itemtypes = []
        order_content = session.query(Orders).filter_by(id=row.id).first()
        # items
        ordered_items_ids = session.query(Orders_OrderedItems).filter_by(order_id=row.id).all()
        for ordered_item_id in ordered_items_ids:
            ordered_item = session.query(OrderedItems).filter_by(id=ordered_item_id.ordereditem_id).first()
            item = session.query(ItemTypes).filter_by(id=ordered_item.item_type_id).first()
            category = session.query(Categories).filter_by(id=item.category_id).first()
            tags = session.query(ItemTypes_Tags).filter_by(item=item.id).all()
            tags_list = []
            for onetag in tags:
                tag_name = session.query(Tags).filter_by(id=onetag.tag).first()
                tags_list.append(tag_name)
            options = session.query(OrderedItems_OptionItems).filter_by(ordered_item_id=ordered_item.item_type_id).all()
            # options
            options_list = []
            for option in options:
                option_content = session.query(OptionItems).filter_by(id=option.option_item_id).first()
                option_type = session.query(OptionTypes).filter_by(id=option_content.type_id).first()
                options_list.append(option_type)
                itemtype = {"id": item.id, "category_id": category, "name": item.name,
                            "tags": tags_list, "description": item.description, "options": options_list,
                            "base_price": item.base_price, "sale_percent": item.sale_percent}
            itemtypes.append(itemtype)
            order = {"id": order_content.id,
                 "number": order_content.number,
                 "items": itemtypes,
                 "total_price": order_content.total_price,
                 "status": order_content.status,
                 "create_time": order_content.created_time,
                 "contact_name": order_content.contact_name,
                 "contact_room": order_content.contact_room}
        orders.append(order)
    return orders
            # return options


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
            tag = {"id": optiontype_content.id, "name": optiontype_content.name}
            return tag
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}

# POST/PATCH /optiontype
# Create a new (POST) or edit an existing (PATCH) OptionType by ID.
# Request format:
# 	{OptionType / Partial OptionType}
# For POST, there must not be an ID. For PATCH, there must be an ID to identify the OptionType to edit.
# Response format:
# 	If successful: 200 OK application/json
# 		{OptionType}
# 	If unsuccessful: 404 Not Found / 401 Bad Request
# class post_OptionType(BaseModel):
#     name: str
#     color: str
#
# @app.post("/tag")
# async def post_tag(new_tag: post_Tag):
#     is_exist = session.query(Tags).filter_by(name=new_tag.name).first()
#     if is_exist:
#         return {"message": "This Category has already EXIST!"}
#     else:
#         session.execute(Tags.insert().values(name=new_tag.name, color=new_tag.color))    # insert new data
#         session.commit()
#         add = session.query(Tags).filter_by(name=new_tag.name).first()
#         return add


#-----OPTIONITEMS------
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
            optionitem = {"id": optionitem_content.id, "type_id":optiontype, "name": optionitem_content.name, "price_change": optionitem_content.price_change}
            return optionitem
        else:
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}


# close the connection
session.close()
