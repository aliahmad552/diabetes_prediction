from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
import joblib
import numpy as np
import pandas as pd
import pickle

app = FastAPI()

model = joblib.load('model.joblib')

MODEL_VERSION = "0.11.1"

scaler = joblib.load('scaler.joblib')

class Patient(BaseModel):
    Pregnancies: int=Field(...,description = "how many times patient pregnant")
    Glucose:float=Field(...,description = "Glucose of patient recorded")
    BloodPressure:float=Field(...,description = "BloodPressure of patient recorded")
    SkinThickness:float=Field(...,description = "Skin Thickness of patient recorded")
    Insulin:float=Field(...,description = "Insullin of patient recorded")
    BMI:float=Field(...,description = "BMI of patient recorded")
    DiabetesPedigreeFunction:float=Field(...,description = "Diabetes pedigree Function of patient recorded")
    Age:int=Field(...,description = "Age of patient recorded")


@app.get("/")
def read_index():
    return FileResponse("templates/index.html")

@app.get("/health")
def health_check():
    return {
        'status':'OK',
        'version':MODEL_VERSION,
        'model_loaded':model is not None
    }

@app.post("/predict")
def predict(data: Patient):
    scaled_cols= scaler.transform([[data.Pregnancies,data.Glucose,data.BloodPressure,data.SkinThickness,data.Insulin,data.BMI,data.DiabetesPedigreeFunction,data.Age]])

    # Load the feature names used during training
    feature_names = model.feature_names_in_

    # Create DataFrame with the correct columns
    input_df = pd.DataFrame([np.concatenate([scaled_cols], axis=1)[0]], 
                        columns=feature_names)
    
    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code = 200, content = {'Prediction':int(prediction)})
