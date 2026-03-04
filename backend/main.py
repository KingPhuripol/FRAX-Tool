"""
FRAX® Tool - Backend API
FastAPI application with SQLite database
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import models
import schemas
from database import engine, get_db
from risk_calculator import calculate_bmi, calculate_risk

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FRAX® Tool API",
    description="ระบบฐานข้อมูลคัดกรองความเสี่ยงกระดูกหัก",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ─────────────────────────────────────────────
# Serve frontend
# ─────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# ─────────────────────────────────────────────
# API: Health Check
# ─────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "FRAX® Tool API is running"}


# ─────────────────────────────────────────────
# API: Stats
# ─────────────────────────────────────────────
@app.get("/api/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Patient).count()
    no_risk = db.query(models.Patient).filter(models.Patient.risk_level == "ไม่มีความเสี่ยง").count()
    low_risk = db.query(models.Patient).filter(models.Patient.risk_level == "เสี่ยงต่ำ").count()
    moderate_risk = db.query(models.Patient).filter(models.Patient.risk_level == "เสี่ยงปานกลาง").count()
    high_risk = db.query(models.Patient).filter(models.Patient.risk_level == "เสี่ยงสูง").count()
    return schemas.StatsResponse(
        total=total,
        no_risk=no_risk,
        low_risk=low_risk,
        moderate_risk=moderate_risk,
        high_risk=high_risk,
    )


# ─────────────────────────────────────────────
# API: Create Patient
# ─────────────────────────────────────────────
@app.post("/api/patients", response_model=schemas.PatientResponse, status_code=201)
def create_patient(data: schemas.PatientCreate, db: Session = Depends(get_db)):
    bmi = calculate_bmi(data.weight, data.height)
    risk_level_th, risk_level_en, frax_count, summary = calculate_risk(data)

    patient = models.Patient(
        first_name=data.first_name,
        last_name=data.last_name,
        age=data.age,
        gender=data.gender,
        height=data.height,
        weight=data.weight,
        bmi=bmi,
        fragility_fracture=data.fragility_fracture,
        fracture_location=data.fracture_location,
        parent_hip_fracture=data.parent_hip_fracture,
        smoking=data.smoking,
        alcohol=data.alcohol,
        steroid_use=data.steroid_use,
        steroid_name=data.steroid_name,
        secondary_osteoporosis=data.secondary_osteoporosis,
        secondary_osteoporosis_detail=data.secondary_osteoporosis_detail,
        has_bmd=data.has_bmd,
        bmd_result=data.bmd_result,
        frax_count=frax_count,
        risk_level=risk_level_th,
        risk_level_en=risk_level_en,
        risk_factors_summary=summary,
        recorded_by=data.recorded_by,
        notes=data.notes,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ─────────────────────────────────────────────
# API: Get All Patients
# ─────────────────────────────────────────────
@app.get("/api/patients", response_model=List[schemas.PatientResponse])
def get_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Patient)
    if search:
        like = f"%{search}%"
        query = query.filter(
            models.Patient.first_name.ilike(like)
            | models.Patient.last_name.ilike(like)
        )
    if risk_level:
        query = query.filter(models.Patient.risk_level == risk_level)
    return query.order_by(models.Patient.created_at.desc()).offset(skip).limit(limit).all()


# ─────────────────────────────────────────────API: Export All Patients as JSON
# ─────────────────────────────────────────────
@app.get("/api/patients/export/json")
def export_patients_json(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).order_by(models.Patient.created_at.desc()).all()
    data = {
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(patients),
        "patients": [
            {
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "age": p.age,
                "gender": p.gender,
                "height": p.height,
                "weight": p.weight,
                "bmi": p.bmi,
                "fragility_fracture": p.fragility_fracture,
                "fracture_location": p.fracture_location,
                "parent_hip_fracture": p.parent_hip_fracture,
                "smoking": p.smoking,
                "alcohol": p.alcohol,
                "steroid_use": p.steroid_use,
                "steroid_name": p.steroid_name,
                "secondary_osteoporosis": p.secondary_osteoporosis,
                "secondary_osteoporosis_detail": p.secondary_osteoporosis_detail,
                "has_bmd": p.has_bmd,
                "bmd_result": p.bmd_result,
                "frax_count": p.frax_count,
                "risk_level": p.risk_level,
                "risk_level_en": p.risk_level_en,
                "risk_factors_summary": p.risk_factors_summary,
                "recorded_by": p.recorded_by,
                "notes": p.notes,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
            }
            for p in patients
        ],
    }
    filename = f"frax_patients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────# API: Get Single Patient
# ─────────────────────────────────────────────
@app.get("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ป่วย")
    return p


# ─────────────────────────────────────────────
# API: Delete Patient
# ─────────────────────────────────────────────
@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ป่วย")
    db.delete(p)
    db.commit()
    return {"message": "ลบข้อมูลสำเร็จ", "id": patient_id}


# ─────────────────────────────────────────────
# Run directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
