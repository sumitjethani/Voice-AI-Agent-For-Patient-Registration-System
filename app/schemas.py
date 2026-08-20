from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
    "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN",
    "TX","UT","VT","VA","WA","WV","WI","WY","DC"
}

SEX_VALUES = {"Male", "Female", "Other", "Decline to Answer"}


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[EmailStr] = None
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str
    zip_code: str
    insurance_provider: Optional[str] = Field(default=None, max_length=255)
    insurance_member_id: Optional[str] = Field(default=None, max_length=100)
    preferred_language: Optional[str] = Field(default="English", max_length=100)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or not all(ch.isalpha() or ch in "-' " for ch in value):
            raise ValueError("must contain alphabetic characters, hyphens, or apostrophes")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str) -> str:
        if value not in SEX_VALUES:
            raise ValueError(f"sex must be one of: {', '.join(sorted(SEX_VALUES))}")
        return value

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 10:
            raise ValueError("must be a valid 10-digit U.S. phone number")
        return digits

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in US_STATES:
            raise ValueError("must be a valid 2-letter U.S. state abbreviation")
        return value

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value: str) -> str:
        value = value.strip()
        import re
        if not re.fullmatch(r"\d{5}(?:-\d{4})?", value):
            raise ValueError("must be a 5-digit ZIP or ZIP+4")
        return value


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = Field(default=None, min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = Field(default=None, max_length=255)
    insurance_member_id: Optional[str] = Field(default=None, max_length=100)
    preferred_language: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_phone: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value):
        if value is not None and value not in SEX_VALUES:
            raise ValueError(f"sex must be one of: {', '.join(sorted(SEX_VALUES))}")
        return value

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 10:
            raise ValueError("must be a valid 10-digit U.S. phone number")
        return digits

    @field_validator("state")
    @classmethod
    def validate_state(cls, value):
        if value is None:
            return value
        value = value.strip().upper()
        if value not in US_STATES:
            raise ValueError("must be a valid 2-letter U.S. state abbreviation")
        return value

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value):
        if value is None:
            return value
        import re
        if not re.fullmatch(r"\d{5}(?:-\d{4})?", value.strip()):
            raise ValueError("must be a 5-digit ZIP or ZIP+4")
        return value.strip()


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ApiResponse(BaseModel):
    data: object | None = None
    error: object | None = None
