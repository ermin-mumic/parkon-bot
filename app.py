import os
from fastapi import FastAPI, HTTPException
from register_car import register_car
from pydantic import BaseModel
from google.cloud import firestore

try:
    db = firestore.Client()
except Exception:
    db = None

EMAIL = os.getenv("CONFIRMATION_EMAIL")
if not EMAIL:
    try:
        from config.local import EMAIL as LOCAL_EMAIL
        EMAIL = LOCAL_EMAIL
    except ImportError:
        EMAIL = ""

app = FastAPI()

class RegisterRequest(BaseModel):
    name: str

@app.post("/register")
async def register(req: RegisterRequest):

    if db is None:
        return {
            "status": "error",
            "code": "db_connection_failed",
            "message": "Verbindung zur Datenbank fehlgeschlagen."
        }
    
    name= req.name.capitalize()

    doc = db.collection("Besucher").document(name).get()
    if not doc.exists:
        return {
            "status": "error",
            "code": "unbekannter_besucher",
            "message": f"{name} ist als Besucher unbekannt.",
            "person": name
        }
    data = doc.to_dict()
    cars= data.get("cars", [])
    
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
    