from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float

    fragility_fracture: bool = False
    fracture_location: Optional[str] = None
    parent_hip_fracture: bool = False

    smoking: bool = False
    alcohol: bool = False
    steroid_use: bool = False
    steroid_name: Optional[str] = None
    secondary_osteoporosis: bool = False
    secondary_osteoporosis_detail: Optional[str] = None

    has_bmd: bool = False
    bmd_result: Optional[str] = None

    recorded_by: Optional[str] = None
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float
    bmi: float
    fragility_fracture: bool
    fracture_location: Optional[str]
    parent_hip_fracture: bool
    smoking: bool
    alcohol: bool
    steroid_use: bool
    steroid_name: Optional[str]
    secondary_osteoporosis: bool
    secondary_osteoporosis_detail: Optional[str]
    has_bmd: bool
    bmd_result: Optional[str]
    frax_count: int
    risk_level: str
    risk_level_en: str
    risk_factors_summary: Optional[str]
    recorded_by: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total: int
    no_risk: int
    low_risk: int
    moderate_risk: int
    high_risk: int
