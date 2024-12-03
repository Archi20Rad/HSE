from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib
import io

pipeline = joblib.load(r"pipeline_model.pkl")

app = FastAPI()

class Item(BaseModel):
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: float
    engine: int
    max_power: float
    torque: float
    seats: int
    max_torque_rpm: float

class Items(BaseModel):
    objects: List[Item]

@app.post("/predict_item")
def predict_item(item: Item) -> float:
    try:
        item_dict = item.dict()
        df = pd.DataFrame([item_dict])

        prediction = pipeline.predict(df)
        return prediction[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_items")
def predict_items(file: UploadFile):
    try:
        content = file.file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        # Проверяем наличие необходимых колонок
        required_columns = [
            "year", "km_driven", "fuel", "seller_type", "transmission",
            "owner", "mileage", "engine", "max_power", "torque", "seats", 'max_torque_rpm'
        ]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="Некорректный формат данных")

        predictions = pipeline.predict(df)
        df["predicted_price"] = predictions

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        response = StreamingResponse(
            output,
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=predictions.csv"

        # Возвращаем файл с результатами
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))