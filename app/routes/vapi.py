from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from dateutil import parser as date_parser
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient

router = APIRouter(prefix="/vapi", tags=["Vapi"])


def parse_flexible_date(val: Any) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(str(val).strip())
    except Exception:
        pass
    try:
        return date_parser.parse(str(val)).date()
    except Exception:
        return None


class VapiCheckPatientRequest(BaseModel):
    phone_number: str


class VapiCreatePatientRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Any
    sex: str
    phone_number: str
    email: Optional[str] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


@router.post("/check-patient")
async def check_patient(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    # Handle direct payload or nested Vapi tool call payload
    if "message" in body and "toolCalls" in body["message"]:
        args = body["message"]["toolCalls"][0]["function"]["arguments"]
        phone_input = args.get("phone_number", "")
    else:
        phone_input = body.get("phone_number", "")

    digits = "".join(ch for ch in str(phone_input) if ch.isdigit())

    if len(digits) < 10:
        return {
            "found": False,
            "patient": None,
            "error": "Invalid phone number",
        }

    # Match last 10 digits
    lookup_digits = digits[-10:]

    patient = db.scalar(
        select(Patient).where(
            Patient.phone_number.endswith(lookup_digits),
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
async def create_patient(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    # Extract args if wrapped inside Vapi tool call
    if "message" in body and "toolCalls" in body["message"]:
        payload_data = body["message"]["toolCalls"][0]["function"]["arguments"]
    else:
        payload_data = body

    try:
        data = VapiCreatePatientRequest(**payload_data)
    except Exception as e:
        return {
            "success": False,
            "patient": None,
            "error": f"Validation error: {str(e)}",
        }

    digits = "".join(ch for ch in str(data.phone_number) if ch.isdigit())
    if len(digits) < 10:
        return {
            "success": False,
            "patient": None,
            "error": "Phone number must contain at least 10 digits.",
        }

    cleaned_phone = digits[-10:]
    parsed_dob = parse_flexible_date(data.date_of_birth)

    if not parsed_dob:
        return {
            "success": False,
            "patient": None,
            "error": "Could not parse date_of_birth.",
        }

    existing_patient = db.scalar(
        select(Patient).where(
            Patient.phone_number == cleaned_phone,
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

    # Normalize state to 2-letter uppercase if possible
    clean_state = data.state.strip().upper()
    if len(clean_state) > 2:
        state_map = {"CALIFORNIA": "CA", "NEW YORK": "NY", "TEXAS": "TX"}
        clean_state = state_map.get(clean_state, clean_state[:2])

    patient = Patient(
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        date_of_birth=parsed_dob,
        sex=data.sex.strip().capitalize(),
        phone_number=cleaned_phone,
        email=data.email,
        address_line_1=data.address_line_1.strip(),
        address_line_2=data.address_line_2,
        city=data.city.strip(),
        state=clean_state,
        zip_code="".join(ch for ch in str(data.zip_code) if ch.isdigit())[:5],
        insurance_provider=data.insurance_provider,
        insurance_member_id=data.insurance_member_id,
        preferred_language=data.preferred_language or "English",
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone="".join(ch for ch in str(data.emergency_contact_phone) if ch.isdigit())[-10:] if data.emergency_contact_phone else None,
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