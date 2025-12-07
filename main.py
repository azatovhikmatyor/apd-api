import joblib
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import pandas as pd
from chatbot import ask_chatbot

from utils import compute_behavior_risk

loaded = joblib.load("random_forest.joblib")
model = loaded['model']
preprocessor = loaded['preprocessor']


class UserInput(BaseModel):
    user_id: int
    ip: str

    day_of_week: int
    hour_of_day: int
    amount: int
    category: str
    channel: str
    city: str
    country: str
    device: str

    def as_df(self):
        return pd.DataFrame(
            data=[[self.day_of_week, self.hour_of_day, self.amount,
                  self.category, self.channel, self.city, self.country, self.device]],
            columns=['day_of_week', 'hour_of_day', 'amount', 'category', 'channel', 'city', 'country', 'device_type']
        )
    
    def as_x(self, preprocessor):
        df = self.as_df()
        x = preprocessor.transform(df)
        return pd.DataFrame(data=x, columns=preprocessor.get_feature_names_out())

    def as_personal_profile(self):
        return {
        "customer_id": self.user_id,
        "amount": self.amount,
        "hour_of_day": self.hour_of_day,
        "city": self.city,
        "country": self.country,
        "device_type": self.device,
        "ip_address": self.ip,
        "category": self.category,
        "channel": self.channel
      }




# user_input = UserInput(user_id="1", ip="1.2.3.4", amount=3000000, device="Android",
#                    city="Tashkent", country="Uzbekistan", category="health",
#                    day_of_week=1, hour_of_day=3, is_weekend=0, channel="transfer")

# compute_behavior_risk(user_input.as_personal_profile())


# x = sample.as_x(preprocessor)

# pred = model.predict(x)

# pred = pred.item()

# model.predict_proba(x)[0][1].item() * 100

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/demo")
async def demo():
    return {
        "message": "success"
    }


@app.post("/demo")
async def handle_demo(user_input: UserInput):
    
    x = user_input.as_x(preprocessor)

    # pred = model.predict(x)
    # pred = pred.item()

    global_risk_score = model.predict_proba(x)[0][1].item() * 100
    pp_risk, reasons = compute_behavior_risk(user_input.as_personal_profile())
    pp_risk = min(100, pp_risk)
    risk_score = global_risk_score * 0.1 + pp_risk * 0.9

    action = "block"
    if risk_score < 35:
        action = "ruxsat"
    elif risk_score < 60:
        action = "otp"
    
    return {
        "user_input": user_input,
        "output": {
            "risk_score": risk_score,
            "action": action, #"ruxsat", # ["blok", "otp"]
            "reasons": reasons
        }
    }


class Question(BaseModel):
    question: str

@app.post('/api/ask')
async def ask(question: Question):
    response = ask_chatbot(question=question.question)
    return response

