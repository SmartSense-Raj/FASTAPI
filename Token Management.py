from typing import List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import databases
import sqlalchemy
import time
from datetime import datetime

DATABASE_URL = "sqlite:///./token.db"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)

token = sqlalchemy.Table(
    "token",
    metadata,
    sqlalchemy.Column("tokenid", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("count", sqlalchemy.INTEGER),
    sqlalchemy.Column("status", sqlalchemy.BOOLEAN, default=True),
    sqlalchemy.Column("time", sqlalchemy.FLOAT, nullable=False)
)


async def initialize():
    for i in range(1, 100):
        query = token.insert().values(
            tokenid=i,
            count=0,
            status=False,
            time = timestamp(datetime.now())
        )
        await database.execute(query)


async def delete_all_record():
    await database.execute("DELETE FROM TOKEN")


def timestamp(dt):
    return time.mktime(dt.timetuple()) + dt.microsecond / 1e6




class UserIN(BaseModel):
    count: int = Field(...)


class BaggageCount(BaseModel):
    count: int = Field(...)


class UserOUtToken(BaseModel):
    tokenid: int


class UserOUT(BaseModel):
    tokenid: int
    count: int
    status: bool
    time:float


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI(title='Token System')


@app.on_event('startup')
async def connect():
    await database.connect()
    await initialize()


@app.on_event('shutdown')
async def shutdown():
    await delete_all_record()
    await database.disconnect()


@app.get('/')
async def index():
    return {"Hello": "User"}


@app.get('/getUser', response_model=List[UserOUT])
async def get_all_user():
    query = "select * from token"
    user = await database.fetch_all(query)
    return user


@app.get("/getActiveToken", response_model=List[UserOUtToken])
async def get_active_token():
    query = "SELECT TOKENID FROM TOKEN WHERE STATUS =TRUE"
    user = await database.fetch_all(query)
    return user


@app.get('/getAvailableToken', response_model=BaggageCount)
async def get_available_token():
    query = "SELECT COUNT(TOKENID)  as count FROM TOKEN WHERE STATUS =FALSE"
    user = await database.fetch_all(query)
    return user[0]


@app.get("/getUserById/{id}", response_model=UserOUT)
async def get_by_id(id: int):
    user = await database.fetch_one("SELECT * FROM token WHERE tokenid=" + str(id))

    if user is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return user


@app.post('/createUser', response_model=UserOUT)
async def create_user(r: UserIN):
    query = "select min(tokenid) from token where status = 0 LIMIT 1"
    id = await database.fetch_one(query)
    if id[0] is None:
        raise HTTPException(status_code=404, detail="No Space is available")

    # if id[0] is None:
    #     query = "select max(tokenid) from token"
    #     id = await database.fetch_one(query)
    #
    #     if id[0] is not None and id[0] > 99:
    #         raise HTTPException(status_code=404, detail="ALl space is occupied")
    #     if id[0] is None:
    #         id = 1
    #     else:
    #         id = int(id[0]) + 1
    #
    #     query = token.insert().values(
    #         tokenid=id,
    #         count=r.count,
    #         status=True
    #     )
    # else:
    #     id = int(id[0])
    #     query = token.update().values(count=r.count, status=True).where(token.c.tokenid == int(id))

    id = int(id[0])
    query = token.update().values(count=r.count, status=True, time = timestamp(datetime.now())).where(token.c.tokenid == int(id))
    await database.execute(query)
    return await get_by_id(id)


@app.delete('/deleteById/{id}')
async def delete_by_id(id: int):
    query = token.update().values(count=0, status=False, time = 0).where(token.c.tokenid == id)
    temp = await database.execute(query)
    if temp > 0:
        return {"Message": "Successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="Data Not found")


@app.put('/updateBaggageCount/{id}', response_model=UserOUT)
async def update_baggage_count(id: int, r: BaggageCount = Depends()):
    query = token.update().values(count=r.count,time = timestamp(datetime.now())).where(token.c.tokenid == id)
    await database.execute(query)
    return await get_by_id(id)
