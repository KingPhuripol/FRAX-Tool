from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ข้อมูลพื้นฐาน
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)       # "ชาย" | "หญิง"
    height = Column(Float, nullable=False)         # ซม.
    weight = Column(Float, nullable=False)         # กก.
    bmi = Column(Float, nullable=False)

    # ประวัติกระดูก
    fragility_fracture = Column(Boolean, default=False)
    fracture_location = Column(String, nullable=True)
    parent_hip_fracture = Column(Boolean, default=False)

    # ปัจจัยเสี่ยง FRAX (4 ข้อหลัก)
    smoking = Column(Boolean, default=False)
    alcohol = Column(Boolean, default=False)
    steroid_use = Column(Boolean, default=False)
    steroid_name = Column(String, nullable=True)
    secondary_osteoporosis = Column(Boolean, default=False)
    secondary_osteoporosis_detail = Column(String, nullable=True)

    # BMD (ถ้ามี)
    has_bmd = Column(Boolean, default=False)
    bmd_result = Column(String, nullable=True)
    # "normal" | "osteopenia_mild" | "osteopenia" | "osteoporosis"

    # ผลการคำนวณความเสี่ยง
    frax_count = Column(Integer, default=0)
    risk_level = Column(String, nullable=False)
    # "ไม่มีความเสี่ยง" | "เสี่ยงต่ำ" | "เสี่ยงปานกลาง" | "เสี่ยงสูง"
    risk_level_en = Column(String, nullable=False)
    risk_factors_summary = Column(Text, nullable=True)

    # ข้อมูลเพิ่มเติม
    recorded_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
