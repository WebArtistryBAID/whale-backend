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

# get categories: return a list of available category(s) types in json
@app.get("/categories")
async def categories():
    # get datatable object
    Categories = metadata.tables['Categories']
    # get datas
    results = engine.execute(Categories.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "name": row.name} for row in results]
    return formatted_results


# # get items: return a list of available item(s) types in json
@app.get("/items")
async def items():
    # get database obj
    Categories = metadata.tables['Categories']    # foreign key
    ItemTypes = metadata.tables['ItemTypes']
    # get datas
    results = engine.execute(ItemTypes.select())
    # convert format to json, then return
    formatted_results = [{"id": row.id, "category": session.query(Categories).filter_by(id=row['id']).first().name, "name": row.name, "base_price": row.base_price, "sale_precent": row.sale_percent} for row in results]
    return formatted_results

# get settings in json
@app.get("/settings")
async def all_settings(key: str):
    # SECTION 1: GET ALL SETTINGS
    # get datatable object
    Settings = metadata.tables['Settings']
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
    # get datatable object
    Orders = metadata.tables['Orders']
    Orders_OrderedItems = metadata.tables['Orders_OrderedItems']
    if (id == ''):    # correspond link that format like /order?id=
        return {"message": "ID can't be EMPTY!"}
    else:    # correspond link that format like /order?id=1102
        query1 = session.query(Orders).filter_by(id=int(id)).first()    # search if key exist
        if query1:    # if key exist
            pass
            # 解析下单类型
            query2 = session.query(Orders_OrderedItems).filter_by(order_id=int(id)).all()
            results2 = [item for item in query2]
            formatted_results = [{"order_id": row.order_id, "item_id": row.ordered_item_id} for row in results2]









        else:    # else
            return {"404 ERROR": "Order doesn't exist! Please check your input!"}
# close the connection
session.close()
