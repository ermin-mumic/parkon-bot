from datetime import datetime, timedelta
import zoneinfo
from google.cloud.firestore import FieldFilter
import os
import httpx
import json

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
PUBLIC_URL = os.getenv("PUBLIC_URL")

def _get_time_now_and_window(hours_ahead: int=2):
    now = datetime.now(zoneinfo.ZoneInfo("Europe/Zurich"))
    window_end = now + timedelta(hours=hours_ahead)
    return now, window_end

async def check_sessions(db, hours_ahead:int=2):
    if db is None:
        return {
            "status": "error",
            "code": "db_connection_failed",
            "message": "Verbindung zur Datenbank fehlgeschlagen."
        }
    
    now, window_end = _get_time_now_and_window(hours_ahead)

    query = (
        db.collection("Sessions")
            .where(filter=FieldFilter("reminderSent", "==", False))
            .where(filter=FieldFilter("endTime", ">=", now))
            .where(filter=FieldFilter("endTime", "<=", window_end))
    )

    docs = list(query.stream())
    reminded_ids = []

    for doc in docs:
        data = doc.to_dict()

        besucher = data.get("besucherID")
        car = data.get("car")
        kanton = car.get("kanton")
        kennzeichen = car.get("kennzeichen")
        endTime = data.get("endTime")
        durationHours = data.get("durationHours")
        notification_text = f"Die Besucheranmeldung für {besucher} mit Auto {kanton} {kennzeichen} endet um {(endTime.astimezone(zoneinfo.ZoneInfo('Europe/Zurich'))).strftime('%H:%M Uhr (%d.%m.%Y)')}."


        if NTFY_TOPIC:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://ntfy.sh/",
                        data=json.dumps({
                            "topic": NTFY_TOPIC,
                            "message": notification_text,
                            "title": "Besucheranmeldung",
                            "actions": [
                                {
                                    "action": "http",
                                    "label": "Verlängern",
                                    "url": PUBLIC_URL + "/register",
                                    "method": "POST",
                                    "headers": {
                                        "Content-Type": "application/json"
                                    },
                                    "body": json.dumps({
                                        "name": besucher,
                                        "duration_text": f"{durationHours}"
                                    }),
                            }]
                        }),
                        timeout=10.0,
                    )
                    print("ntfy status:", response.status_code, response.text)
            except Exception as e:
                print(f"Fehler beim Senden der NTFY-Benachrichtigung: {e}")
        else:
                print(f"NTFY_TOPIC ist nicht gesetzt. Keine Benachrichtigung gesendet.")


        doc.reference.update({"reminderSent": True})
        reminded_ids.append(doc.id)

    return {
        "status": "ok",
        "checked": len(docs),
        "reminded": reminded_ids,
        "window_start": now.isoformat(),
        "window_end": window_end.isoformat(),
    }

