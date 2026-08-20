from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient

router = APIRouter(prefix="/vapi", tags=["Vapi"])


class VapiCheckPatientRequest(BaseModel):
    phone_number: str

class VapiCreatePatientRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: str | None = None
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    zip_code: str
    insurance_provider: str | None = None
    insurance_member_id: str | None = None
    preferred_language: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


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


@router.post("/create-patient")
def create_patient(
    payload: VapiCreatePatientRequest,
    db: Session = Depends(get_db),
):
    digits = "".join(ch for ch in payload.phone_number if ch.isdigit())

    if len(digits) != 10:
        return {
            "success": False,
            "patient": None,
            "error": "Phone number must contain exactly 10 digits.",
        }

    existing_patient = db.scalar(
        select(Patient).where(
            Patient.phone_number == digits,
            Patient.deleted_at.is_(None),
        )
    )

    if existing_patient:
        return {
            "success": False,
            "patient": None,
            "error": "A patient with this phone number already exists.",
            "existing_patient_id": str(existing_patient.patient_id),
        }

    patient = Patient(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        date_of_birth=payload.date_of_birth,
        sex=payload.sex.strip(),
        phone_number=digits,
        email=payload.email,
        address_line_1=payload.address_line_1.strip(),
        address_line_2=payload.address_line_2,
        city=payload.city.strip(),
        state=payload.state.strip().upper(),
        zip_code=payload.zip_code.strip(),
        insurance_provider=payload.insurance_provider,
        insurance_member_id=payload.insurance_member_id,
        preferred_language=payload.preferred_language,
        emergency_contact_name=payload.emergency_contact_name,
        emergency_contact_phone=payload.emergency_contact_phone,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return {
        "success": True,
        "patient": {
            "patient_id": str(patient.patient_id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "phone_number": patient.phone_number,
        },
        "error": None,
    }