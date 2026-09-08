from fastapi import APIRouter
from app.database import SessionLocal
from app.models.flight import FlightModel
import json

router = APIRouter()

@router.get("/flights")
def get_flights():
    db = SessionLocal()
    flights = db.query(FlightModel).all()
    db.close()
    return [{"id": f.id, "filename": f.filename, "duration": f.duration, "created": f.created_at} for f in flights]

@router.delete("/flights")
def clear_flights():
    db = SessionLocal()
    try:
        db.query(FlightModel).delete()
        db.commit()
        return {"status": "cleared"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@router.get("/flights/{flight_id}")
def get_flight(flight_id: int):
    db = SessionLocal()
    flight = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    db.close()
    if not flight:
        return {"error": "Not found"}
    return {
        "id": flight.id,
        "filename": flight.filename,
        "board_info": flight.board_info,
        "firmware": flight.firmware,
        "telemetry": json.loads(flight.telemetry_data),
        "stats": {
            "voltage_avg": flight.voltage_avg,
            "rssi_min": flight.rssi_min
        }
    }



@router.get("/flights/{flight_id}/track")
def get_flight_track(flight_id: int):
    db = SessionLocal()
    flight = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    db.close()

    if not flight:
        return {"error": "Not found", "track": []}

    if flight.track_data:
        try:
            track = json.loads(flight.track_data)
            if track and any(pt.get("roll") for pt in track[:10]):
                return {"track": track}
        except:
            pass

    if flight.telemetry_data:
        try:
            telemetry = json.loads(flight.telemetry_data)
            track = []

            r, p, y = 0.0, 0.0, 0.0
            prev_t = 0.0


            has_attitude = any(pt.get("roll") or pt.get("pitch") or pt.get("yaw") for pt in telemetry[:20])

            for point in telemetry:
                t = point.get("time", 0)
                dt = t - prev_t if prev_t > 0 else 0
                prev_t = t

                if has_attitude:
                    r = point.get("roll", 0)
                    p = point.get("pitch", 0)
                    y = point.get("yaw", 0)
                else:

                    r += point.get("ax", 0) * dt
                    p += point.get("ay", 0) * dt
                    y += point.get("az", 0) * dt

                track.append({
                    "time": t,
                    "roll": r,
                    "pitch": p,
                    "yaw": y
                })
            return {"track": track}
        except Exception as e:
            print(f"Error extracting track from telemetry: {e}")

    return {"track": []}