# Voice AI Patient Registration Agent

Backend for the Voice AI Patient Registration technical assessment.

## Current stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Vapi (to be connected in Step 2)

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start:

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## API

- GET /patients
- GET /patients/{patient_id}
- POST /patients
- PUT /patients/{patient_id}
- DELETE /patients/{patient_id}

## Next

1. Deploy API.
2. Create Vapi assistant.
3. Add Vapi custom tools.
4. Connect phone number.
5. Test natural registration and corrections.
