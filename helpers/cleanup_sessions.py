import zoneinfo
from datetime import datetime, timedelta

def cleanup_sessions(db, keep_days: int=30) -> dict:
    if db is None:
        return {
            "status": "error",
            "code": "db_connection_failed",
            "message": "Verbindung zur Datenbank fehlgeschlagen."
        }
    
    tz = zoneinfo.ZoneInfo("Europe/Zurich")
    cutoff = datetime.now(tz) - timedelta(days=keep_days)

    query = db.collection("Sessions").where("endTime", "<=", cutoff)

    deleted = 0
    batch = db.batch
    batch_count = 0

    for doc in query.stream():
        batch.delete(doc.reference)
        deleted += 1
        batch_count += 1

        if batch_count >= 500:
            batch.commit()
            batch = db.batch
            batch_count = 0
    if batch_count > 0:
        batch.commit()
    
    return {
        "status": "success",
        "deleted_sessions": deleted,
        "cutoff_date": cutoff.isoformat(),
        "keep_days": keep_days
    }
