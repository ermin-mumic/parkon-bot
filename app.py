from fastapi import FastAPI, HTTPException
from register_car import register_car
from pydantic import BaseModel

try:
    from config.local import BESUCHER
except ImportError:
    BESUCHER = {}

try:
    from config.local import EMAIL
except ImportError:
    EMAIL = "default@example.com"

app = FastAPI()

class RegisterRequest(BaseModel):
    name: str

@app.post("/register")
async def register(req: RegisterRequest):

    name= req.name.lower()

    if name not in BESUCHER:
        return {
            "status": "error",
            "code": "unbekannter_besucher",
            "message": f"{name} ist als Besucher unbekannt.",
            "person": name
        }
    
    cars = BESUCHER[name]
    results= []


    for car in cars:
        result = await register_car(car["kanton"], car["kennzeichen"], EMAIL)
        results.append(result)
    
    if not all(results):
        return {
            "status": "error",
            "code": "registrierung_fehlgeschlagen",
            "message": f"Die Registrierung für {name} ist fehlgeschlagen.",
            "person": name
        }
    
    return {
        "status": "ok",
        "person": name,
        "count": len(cars)
    }
    