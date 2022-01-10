from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import databases
import sqlalchemy
from datetime import datetime
import uvicdirorn

DATABASE_URL = "sqlite:///./student.db"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)

student = sqlalchemy.Table(
    "student",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("std", sqlalchemy.Integer)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

app = FastAPI(title="Student API")


@app.on_event('startup')
async def connect():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


class RegisterIn(BaseModel):
    name: str = Field(...)
    std: int = Field(...)


class Register(BaseModel):
    id: int
    name: str
    std: int


# Create
@app.post('/student/', response_model=RegisterIn)
async def create(r: RegisterIn = Depends()):
    query = student.insert().values(
        name=r.name,
        std=r.std
    )
    student_id = await database.execute(query)

    return get_one(id)


# Read
@app.get('/student/{id}', response_model=Register)
async def get_one(id: int):
    try:
        if student.c.id != id:
            raise Exception

        query = student.select().where(student.c.id == id)
        user = await database.fetch_one(query)
        return {**user}

    except:
        raise HTTPException(status_code=404, detail="Student not found")


@app.get('/student/', response_model=List[Register])
async def get_all():
    query = student.select()
    users = await database.fetch_all(query)
    if len(users) == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return users


# Update
@app.put('/student/{id}', response_model=Register)
async def update(id: int, r: RegisterIn = Depends()):
    try:
        if student.c.id != id:
            raise Exception

        query = student.update().where(student.c.id == id).values(
            name=r.name,
            std=r.std
        )
        id = await database.execute(query)
        query = student.select().where(student.c.id == id)
        row = await database.fetch_one(query)

    except:
        raise HTTPException(status_code=404, detail="Student not found")

    return {**row}


@app.delete('/student/{id}')
async def delete(id: int):
    try:
        if student.c.id != id:
            raise Exception

        query = student.delete().where(student.c.id == id)
        await database.execute(query)

    except:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"Deleted": "Record deleted Successfully"}
