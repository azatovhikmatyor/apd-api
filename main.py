from pydantic import BaseModel
from fastapi import FastAPI
import random


app = FastAPI()

class UserInput(BaseModel):
    user_id: str
    amount: int
    device: str
    merchant: str
    city: str
    category: str
    ip: str


@app.get("/demo")
async def demo():
    return {
        "message": "success"
    }


@app.post("/demo")
async def handle_demo(user_input: UserInput):

    return {
        "user_input": user_input,
        "output": {
            "risk_score": round(random.random(), 2),
            "action": "ruxsat", # ["blok", "otp"]
            "reasons": "reasons"
        }
    }

