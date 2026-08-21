# Voice AI Patient Registration System

A production-ready, HIPAA-conscious voice agent and REST API system designed to handle inbound patient registration calls with automated record lookups, duplicate detection, and structured demographic intake.

---

## Live Links & Testing Channels

* **Inbound Phone Number:** `+1 (430) 803-6066` *(US Telephony provisioned via Vapi)*
* **Interactive Web Voice Demo:** [https://voicepatient.up.railway.app/demo](https://voicepatient.up.railway.app/demo) *(Direct in-browser WebRTC voice test)*
* **Interactive API Documentation (Swagger UI):** [https://voicepatient.up.railway.app/docs](https://voicepatient.up.railway.app/docs)
* **Production API Base URL:** [https://voicepatient.up.railway.app](https://voicepatient.up.railway.app)

---

## System Architecture & Workflow

```text
 Caller (Phone / WebRTC) 
         │
         ▼
 ┌──────────────┐       Webhook Tool Calls       ┌────────────────────────┐
 │   Vapi.ai    │ ─────────────────────────────► │     FastAPI Server     │
 │ (Voice Agent)│ ◄───────────────────────────── │(Railway Cloud Platform)│
 └──────────────┘         JSON Response          └───────────┬────────────┘
                                                             │
                                                     SQLAlchemy ORM
                                                             │
                                                             ▼
                                                 ┌────────────────────────┐
                                                 │   SQLite / DB Store    │
                                                 │ (Persistent Records)   │
                                                 └────────────────────────┘
```


### Conversational Lifecycle
1. **Greeting & Immediate Lookup:** The assistant greets the caller and immediately asks for their 10-digit phone number.
2. **Pre-Registration Verification (`check_patient`):** 
   * The phone number is normalized to a 10-digit numeric string.
   * If a record exists, the agent welcomes the patient back by name and gracefully exits to prevent duplicate records.
   * If no record exists, the agent transitions seamlessly to new patient intake.
3. **Sequential Demographic Collection:** Required fields are collected one by one:
   * First Name & Last Name (with spelling verification on ambiguous inputs)
   * Date of Birth (standardized to `YYYY-MM-DD`)
   * Biological Sex (`Male`, `Female`, `Other`, `Decline to Answer`)
   * Full Address (Street Line 1, City, 2-letter State abbreviation, 5-digit ZIP code)
4. **Optional Fields:** The caller is prompted for email, insurance details, language preference, and emergency contacts (which can be skipped without blocking registration).
5. **Mandatory Explicit Confirmation:** The agent reads back a comprehensive summary of all provided data.
6. **Persistence (`create_patient`):** The record is committed to the database only after the caller provides an explicit affirmative response (*"Yes"*, *"That's correct"*, *"Looks good"*).

---

## Tech Stack

* **Backend Framework:** FastAPI (Python 3.11+)
* **Database & ORM:** SQLite / PostgreSQL with SQLAlchemy & Alembic-ready schemas
* **Data Validation:** Pydantic v2 (strict type enforcement, ISO-8601 timestamps, UUID primary keys)
* **Voice Engine & Orchestration:** Vapi AI (STT: Deepgram Nova-2, LLM: GPT-4o / GPT-3.5-Turbo, TTS: Cartesia / ElevenLabs)
* **Deployment & Hosting:** Railway Cloud
* **Testing:** Pytest & FastAPI TestClient

---

## API Endpoints

### 1. REST Management Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status check |
| `GET` | `/demo` | In-browser WebRTC interactive voice test interface |
| `GET` | `/patients` | List all active patient records (supports pagination & filtering) |
| `GET` | `/patients/{id}` | Retrieve a specific patient record by UUID |
| `POST` | `/patients` | Programmatically create a new patient record |
| `PUT` | `/patients/{id}` | Update existing patient demographics |
| `DELETE`| `/patients/{id}` | Soft-delete a patient record (`is_active = false`) |

### 2. Vapi Webhook Endpoints

* **`POST /vapi/check-patient`**
  * **Payload:** `{"phone_number": "10-digit string"}`
  * **Response:** `{"found": boolean, "patient": object | null, "message": string}`
* **`POST /vapi/create-patient`**
  * **Payload:** Full patient demographic object conforming to database schema.
  * **Response:** Created patient object with generated UUID and UTC timestamps.

---

## Local Development & Setup

### Prerequisites
* Python 3.10 or higher
* Git

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/sumitjethani/Voice-AI-Agent-For-Patient-Registration-System.git](https://github.com/sumitjethani/Voice-AI-Agent-For-Patient-Registration-System.git)
   cd Voice-AI-Agent-For-Patient-Registration-System
Create and Activate Virtual Environment:

macOS / Linux:

Bash
python3 -m venv .venv
source .venv/bin/activate
Windows (PowerShell):

PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
Install Dependencies:

Bash
pip install -r requirements.txt
Run Database Migrations / Local Server:

Bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Access Local Services:

Local API Docs: http://localhost:8000/docs

Local Voice Web Demo: http://localhost:8000/demo

Health Check: http://localhost:8000/health

Automated Testing Suite
Run the full test suite covering database isolation, CRUD operations, duplicate prevention, and webhook payloads:

Bash
pytest -v
To run with coverage reporting:

Bash
pytest --cov=app tests/
Testing & Verification Guide
1. Inbound Phone Test
Dial +1 (430) 803-6066 from any phone or VoIP service.

State that you want to register. Provide a 10-digit phone number, spell your name, and provide dates/addresses.

Verify the agent reads the details back before completing registration.

Call again using the same number to verify duplicate detection.

2. Browser Voice Demo Test
Open https://voicepatient.up.railway.app/demo.

Click Start Voice Call, grant microphone permissions, and conduct the intake conversation.

3. Swagger Verification
Open https://voicepatient.up.railway.app/docs.

Execute GET /patients to confirm the voice-registered patient has persisted to the database.

## Repository Structure

```text
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point, lifespan, & /demo route
│   ├── database.py          # SQLAlchemy engine, session maker, & Base
│   ├── models/
│   │   ├── __init__.py
│   │   └── patient.py       # Patient database model (UUID, timestamps, soft delete)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── patient.py       # Pydantic schemas for request/response validation
│   └── routes/
│       ├── __init__.py
│       ├── patients.py      # Standard REST CRUD operations
│       └── vapi.py          # Vapi webhook handlers (/check-patient, /create-patient)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures & in-memory test database setup
│   ├── test_patients.py     # REST API unit & integration tests
│   └── test_vapi.py         # Voice webhook validation & edge cases
├── requirements.txt         # Production & testing dependencies
├── Procfile                 # Deployment process command for Railway
└── README.md                # Project documentation
```