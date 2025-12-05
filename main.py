from fastapi import FastAPI


app = FastAPI()

@app.get("/demo")
async def demo():
    return {
        "message": "success"
    }
