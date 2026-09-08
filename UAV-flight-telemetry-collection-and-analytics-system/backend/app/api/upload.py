from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.parser import parse_log_file
from app.database import SessionLocal
from app.models.flight import FlightModel
import os
import json

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_flight_data(log_file: UploadFile = File(...)):
    log_path = f"{UPLOAD_DIR}/{log_file.filename}"
    with open(log_path, "wb") as f:
        f.write(await log_file.read())

    data, meta = parse_log_file(log_path)

    if not data:
        raise HTTPException(status_code=400, detail="Не вдалося вилучити телеметрію.")

    voltage_avg = sum(p["voltage"] for p in data if p["voltage"] > 0) / len(data)
    

    track_data = [
        {
            "time": point["time"],
            "roll": point.get("roll", 0),
            "pitch": point.get("pitch", 0),
            "yaw": point.get("yaw", 0),
        }
        for point in data
    ]

    db = SessionLocal()
    new_flight = FlightModel(
        filename=log_file.filename,
        telemetry_data=json.dumps(data),
        track_data=json.dumps(track_data),
        voltage_avg=voltage_avg,
        rssi_min=0,
        board_info=meta.get("board_info", ""),
        firmware=meta.get("firmware", ""),
    )
    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)
    db.close()

    return {"status": "uploaded", "flight_id": new_flight.id, "total_points": len(data)}