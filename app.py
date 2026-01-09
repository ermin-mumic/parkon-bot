import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import firestore
from datetime import datetime, timedelta, timezone
import zoneinfo
from helpers.register_car import register_car
from helpers.duration_parser import parse_duration_text
from helpers.check_sessions import check_sessions
from helpers.cleanup_sessions import cleanup_sessions

try:
    db = firestore.Client()
except Exception:
    db = None

EMAIL = os.getenv("CONFIRMATION_EMAIL")

app = FastAPI()

class RegisterRequest(BaseModel):
    name: str
    duration_text: str

@app.post("/register")
async def register(req: RegisterRequest):

    if db is None:
        return {
            "status": "error",
            "code": "db_connection_failed",
            "message": "Verbindung zur Datenbank fehlgeschlagen."
        }
    
    name= req.name.capitalize()
    duration_hours = parse_duration_text(req.duration_text)

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
        result = await register_car(car["kanton"], car["kennzeichen"], EMAIL, duration_hours)
        results.append(result)
    
    if not all(results):
        return {
            "status": "error",
            "code": "registrierung_fehlgeschlagen",
            "message": f"Die Registrierung für {name} ist fehlgeschlagen.",
            "person": name
        }
    
    start_time = datetime.now(zoneinfo.ZoneInfo("Europe/Zurich"))
    end_time = start_time + timedelta(hours=duration_hours)

    for car in cars:
        db.collection("Sessions").document(f"{name}_{car['kanton']}_{car['kennzeichen']}_{start_time.strftime('%d%m%Y_%H%M%S')}").set({
            "besucherID": name,
            "car": {
                "kanton": car["kanton"],
                "kennzeichen": car["kennzeichen"]
            },
            "startTime": start_time,
            "endTime": end_time,
            "durationHours": duration_hours,
            "reminderSent": False
        })

    if duration_hours <=2:
        await check_sessions(db, hours_ahead=2)

    return {
        "status": "ok",
        "person": name,
        "count": len(cars)
    }

@app.get("/check")
async def check():
    result = await check_sessions(db, hours_ahead=2)
    return result

@app.get("/cleanup")
async def cleanup():
    result = cleanup_sessions(db, keep_days=30)
    return result

    