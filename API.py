from fastapi import FastAPI, HTTPException, Depends
import main
from pydantic import BaseModel, Field
from bentoml import load


class Prediction(BaseModel):
    prediction: str


class Input(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


app = FastAPI(title="FastAPI with BentoML")


@app.get("/")
def home():
    return {"Hello": "Hello User"}


@app.get("/predict/", response_model=Prediction)
async def get(r: Input = Depends()):
    saved_path = "/home/raj/bentoml/repository/IrisClassifier/20220113171733_3FB345"
    service = load(saved_path)
    ans = str(service.predict([[r.sepal_length, r.sepal_width, r.petal_length, r.petal_width]]))
    ans = {"prediction": ans}
    return ans
