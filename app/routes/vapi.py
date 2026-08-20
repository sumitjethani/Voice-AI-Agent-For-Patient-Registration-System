from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient

router = APIRouter(prefix="/vapi", tags=["Vapi"])


class VapiCheckPatientRequest(BaseModel):
    phone_number: str


@router.post("/check-patient")
def check_patient(
    payload: VapiCheckPatientRequest,
    db: Session = Depends(get_db),
):
    digits = "".join(ch for ch in payload.phone_number if ch.isdigit())

    if len(digits) != 10:
        return {
            "found": False,
            "patient": None,
            "error": "Invalid 10-digit U.S. phone number",
        }

    patient = db.scalar(
        select(Patient).where(
            Patient.phone_number == digits,
            Patient.deleted_at.is_(None),
        )
    )

    if not patient:
        return {
            "found": False,
            "patient": None,
            "error": None,
        }

    return {
        "found": True,
        "patient": {
            "patient_id": str(patient.patient_id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "phone_number": patient.phone_number,
        },
        "error": None,
    }