from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient
from ..schemas import ApiResponse, PatientCreate, PatientRead, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])


def response(data=None, error=None):
    return {"data": data, "error": error}


@router.get("", response_model=ApiResponse)
def list_patients(
    last_name: Optional[str] = Query(default=None),
    date_of_birth: Optional[date] = Query(default=None),
    phone_number: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Patient).where(Patient.deleted_at.is_(None))

    if last_name:
        stmt = stmt.where(Patient.last_name.ilike(last_name))
    if date_of_birth:
        stmt = stmt.where(Patient.date_of_birth == date_of_birth)
    if phone_number:
        digits = "".join(ch for ch in phone_number if ch.isdigit())
        stmt = stmt.where(Patient.phone_number == digits)

    patients = db.scalars(stmt.order_by(Patient.created_at.desc())).all()
    return response([PatientRead.model_validate(p).model_dump(mode="json") for p in patients])


@router.get("/{patient_id}", response_model=ApiResponse)
def get_patient(patient_id: UUID, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)

    if not patient or patient.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return response(PatientRead.model_validate(patient).model_dump(mode="json"))


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    digits = "".join(ch for ch in payload.phone_number if ch.isdigit())

    existing = db.scalar(
        select(Patient).where(
            Patient.phone_number == digits,
            Patient.deleted_at.is_(None),
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "A patient with this phone number already exists",
                "patient_id": str(existing.patient_id),
            },
        )

    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)

    print(
        "[PATIENT_CREATED]",
        PatientRead.model_validate(patient).model_dump(mode="json"),
        flush=True,
    )

    return response(PatientRead.model_validate(patient).model_dump(mode="json"))


@router.put("/{patient_id}", response_model=ApiResponse)
def update_patient(
    patient_id: UUID,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
):
    patient = db.get(Patient, patient_id)

    if not patient or patient.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Patient not found")

    updates = payload.model_dump(exclude_unset=True)

    if "phone_number" in updates and updates["phone_number"]:
        duplicate = db.scalar(
            select(Patient).where(
                Patient.phone_number == updates["phone_number"],
                Patient.patient_id != patient_id,
                Patient.deleted_at.is_(None),
            )
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Phone number already belongs to another patient")

    for key, value in updates.items():
        setattr(patient, key, value)

    patient.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(patient)

    return response(PatientRead.model_validate(patient).model_dump(mode="json"))


@router.delete("/{patient_id}", response_model=ApiResponse)
def delete_patient(patient_id: UUID, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)

    if not patient or patient.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.deleted_at = datetime.now(timezone.utc)
    patient.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(patient)

    return response({
        "patient_id": str(patient.patient_id),
        "deleted_at": patient.deleted_at.isoformat(),
    })
