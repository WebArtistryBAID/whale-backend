from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, MetaData
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

# close the connection
session.close()