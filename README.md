# Case Management System

A REST API for managing cases, built with Python and FastAPI.

## Requirements

- Python 3.11+
- pip

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Project Structure

```
casemanagement/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── models.py        # Pydantic models
│   ├── database.py      # Database setup
│   └── routers/         # Route handlers
├── tests/
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Testing

```bash
pytest
```
