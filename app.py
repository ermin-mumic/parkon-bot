from fastapi import FastAPI, HTTPException
from register_car import register_car
from pydantic import BaseModel

try:
    from config.local import BESUCHER
except ImportError:
    BESUCHER = {}

app = FastAPI()

class RegisterRequest(BaseModel):
    name: str

@app.post("/register")
async def register(req: RegisterRequest):

    name= req.name.lower()

    if name not in BESUCHER:
        raise HTTPException(status_code=404, detail="Besucher nicht gefunden")
    
    cars = BESUCHER[name]

    for car in cars:
        kanton = car["kanton"]
        kennzeichen = car["kennzeichen"]
        await register_car(kanton, kennzeichen)
    
    return {"status": "ok", "person": name, "count": len(cars)}
    