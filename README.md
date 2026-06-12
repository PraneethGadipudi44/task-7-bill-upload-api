# Energy Bill Upload API

This FastAPI app exposes a single upload endpoint for utility bill PDFs.

## Files

- `app.py` - FastAPI application
- `requirements.txt` - Python dependencies

## Run locally

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

The API will start at `http://127.0.0.1:8000`.

## Test the upload endpoint

```bash
curl -X POST "http://127.0.0.1:8000/upload-bill" \
  -H "accept: application/json" \
  -F "file=@sample_bill.pdf;type=application/pdf"
```

## What the endpoint does

- Accepts a PDF file at `POST /upload-bill`
- Saves the file into a temporary server-side directory
- Returns a unique file identifier and upload details
- Queues a placeholder OCR trigger for future integration

## Error handling

- Non-PDF uploads return HTTP 400
- Empty uploads return HTTP 400
- Save failures return HTTP 500
