import os
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Tutorial, Message

app = FastAPI(title="FarmConnect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class CreatedResponse(BaseModel):
    id: str


def serialize_doc(doc: dict) -> dict:
    d = dict(doc)
    if d.get("_id") is not None:
        d["id"] = str(d.pop("_id"))
    # Convert datetime to isoformat if present
    for k in ("created_at", "updated_at"):
        if k in d and hasattr(d[k], "isoformat"):
            d[k] = d[k].isoformat()
    return d


@app.get("/")
def root() -> dict:
    return {"message": "FarmConnect backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "Unknown"
            try:
                cols = db.list_collection_names()
                response["collections"] = cols[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:60]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:60]}"

    return response


# Products endpoints
@app.post("/api/products", response_model=CreatedResponse)
def create_product(product: Product):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("product", product)
    return {"id": inserted_id}


@app.get("/api/products")
def list_products(limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("product", limit=min(limit or 50, 100))
    return [serialize_doc(doc) for doc in docs]


# Tutorials endpoints
@app.post("/api/tutorials", response_model=CreatedResponse)
def create_tutorial(tutorial: Tutorial):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("tutorial", tutorial)
    return {"id": inserted_id}


@app.get("/api/tutorials")
def list_tutorials(limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("tutorial", limit=min(limit or 50, 100))
    return [serialize_doc(doc) for doc in docs]


# Community messages endpoints
@app.post("/api/messages", response_model=CreatedResponse)
def create_message(message: Message):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("message", message)
    return {"id": inserted_id}


@app.get("/api/messages")
def list_messages(room: str = "general", limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filter_dict = {"room": room} if room else {}
    docs = get_documents("message", filter_dict=filter_dict, limit=min(limit or 50, 200))
    return [serialize_doc(doc) for doc in docs]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
