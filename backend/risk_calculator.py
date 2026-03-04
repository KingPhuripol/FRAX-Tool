"""
FRAX® Risk Calculator
อิงตามเกณฑ์จากเอกสาร: เกณฑ์จำแนกความเสี่ยงเครื่องคัดกรองผู้ป่วย

ระดับความเสี่ยง:
  0 = ไม่มีความเสี่ยง (No Risk)
  1 = เสี่ยงต่ำ       (Low Risk)
  2 = เสี่ยงปานกลาง  (Moderate Risk)
  3 = เสี่ยงสูง       (High Risk)
"""
from typing import Tuple, List


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_risk(data) -> Tuple[str, str, int, str]:
    """
    Returns: (risk_level_th, risk_level_en, frax_count, risk_factors_summary)
    """
    bmi = calculate_bmi(data.weight, data.height)

    # ---- กฎเร่งด่วน: Fragility Fracture = High Risk ทันที ----
    if data.fragility_fracture:
        frax_count = _count_frax(data)
        factors = [f"เคยกระดูกหักจากแรงกระแทกต่ำ"] + _list_factors(data)
        return ("เสี่ยงสูง", "High Risk", frax_count, " | ".join(factors))

    # ---- กฎเร่งด่วน: Osteoporosis จาก BMD = High Risk ทันที ----
    if data.has_bmd and data.bmd_result == "osteoporosis":
        frax_count = _count_frax(data)
        factors = ["ผล BMD เป็น Osteoporosis"] + _list_factors(data)
        return ("เสี่ยงสูง", "High Risk", frax_count, " | ".join(factors))

    frax_count = _count_frax(data)

    # ---- คำนวณ risk_score แบบ multi-criteria ----
    # เลือกระดับสูงสุดที่เข้าเกณฑ์ (กฎ: ถ้าเข้าหลายระดับให้เลือกสูงสุด)
    risk_score = 0

    # เกณฑ์อายุ
    if data.age >= 65:
        risk_score = max(risk_score, 2)   # อายุ ≥ 65 → อย่างน้อย Moderate
    elif data.age >= 50:
        risk_score = max(risk_score, 1)   # อายุ 50-64 → อย่างน้อย Low

    # เกณฑ์ BMI
    if bmi < 18.5:
        risk_score = max(risk_score, 2)   # BMI < 18.5 → Moderate
        if frax_count >= 1 or data.parent_hip_fracture:
            risk_score = max(risk_score, 3)   # BMI < 18.5 + ปัจจัยอื่น → High
    elif bmi < 20:
        risk_score = max(risk_score, 1)   # BMI 18.5–19.9 → Low

    # ประวัติพ่อ/แม่สะโพกหัก → Moderate
    if data.parent_hip_fracture:
        risk_score = max(risk_score, 2)

    # จำนวนปัจจัยเสี่ยง FRAX
    if frax_count >= 3:
        risk_score = max(risk_score, 3)   # ≥3 ข้อ → High
    elif frax_count >= 2:
        risk_score = max(risk_score, 2)   # ≥2 ข้อ → Moderate
    elif frax_count == 1:
        risk_score = max(risk_score, 1)   # 1 ข้อ → Low

    # ใช้สเตียรอยด์ + ปัจจัยอื่น → High
    if data.steroid_use and frax_count >= 2:
        risk_score = max(risk_score, 3)

    # โรคกระดูกพรุนทุติยภูมิ → Moderate
    if data.secondary_osteoporosis:
        risk_score = max(risk_score, 2)

    # อายุ ≥ 65 + FRAX ≥ 3 → High
    if data.age >= 65 and frax_count >= 3:
        risk_score = max(risk_score, 3)

    # BMD result
    if data.has_bmd:
        bmd_map = {
            "osteopenia": 2,
            "osteopenia_mild": 1,
            "normal": 0,
        }
        risk_score = max(risk_score, bmd_map.get(data.bmd_result or "normal", 0))

    level_map = {
        0: ("ไม่มีความเสี่ยง", "No Risk"),
        1: ("เสี่ยงต่ำ", "Low Risk"),
        2: ("เสี่ยงปานกลาง", "Moderate Risk"),
        3: ("เสี่ยงสูง", "High Risk"),
    }
    risk_level_th, risk_level_en = level_map[risk_score]
    factors = _list_factors(data)
    summary = " | ".join(factors) if factors else "ไม่มีปัจจัยเสี่ยง"

    return (risk_level_th, risk_level_en, frax_count, summary)


def _count_frax(data) -> int:
    """นับปัจจัยเสี่ยง FRAX 4 ข้อหลัก"""
    return sum([
        bool(data.smoking),
        bool(data.alcohol),
        bool(data.steroid_use),
        bool(data.secondary_osteoporosis),
    ])


def _list_factors(data) -> List[str]:
    parts = []
    if data.parent_hip_fracture:
        parts.append("พ่อ/แม่เคยสะโพกหัก")
    if data.smoking:
        parts.append("สูบบุหรี่")
    if data.alcohol:
        parts.append("ดื่มแอลกอฮอล์ ≥3 แก้ว/วัน")
    if data.steroid_use:
        label = "ใช้สเตียรอยด์ระยะยาว"
        if data.steroid_name:
            label += f" ({data.steroid_name})"
        parts.append(label)
    if data.secondary_osteoporosis:
        label = "โรคกระดูกพรุนทุติยภูมิ"
        if data.secondary_osteoporosis_detail:
            label += f" ({data.secondary_osteoporosis_detail})"
        parts.append(label)
    if data.has_bmd and data.bmd_result:
        bmd_labels = {
            "normal": "BMD: ปกติ",
            "osteopenia_mild": "BMD: Osteopenia เล็กน้อย",
            "osteopenia": "BMD: Osteopenia ชัดเจน",
            "osteoporosis": "BMD: Osteoporosis",
        }
        parts.append(bmd_labels.get(data.bmd_result, f"BMD: {data.bmd_result}"))
    return parts
