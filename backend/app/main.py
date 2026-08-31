import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from supabase import create_client, Client

load_dotenv()

# -------------------------
# Supabase configuration
# -------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is not configured")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -------------------------
# FastAPI
# -------------------------

app = FastAPI(
    title="ReviewTap API",
    version="0.1.0"
)

# -------------------------
# Health check
# -------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "ReviewTap API is running"
    }

# -------------------------
# Database test
# -------------------------

@app.get("/test-db")
def test_db():
    try:
        response = (
            supabase
            .table("cards")
            .select("*")
            .execute()
        )

        return {
            "connected": True,
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

# -------------------------
# Get all cards
# -------------------------

@app.get("/cards")
def get_cards():
    try:
        response = (
            supabase
            .table("cards")
            .select("*")
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cards: {str(e)}"
        )

# -------------------------
# Get a specific card
# -------------------------

@app.get("/cards/{card_id}")
def get_card(card_id: str):
    try:
        response = (
            supabase
            .table("cards")
            .select("*")
            .eq("id", card_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Card not found"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve card: {str(e)}"
        )

# -------------------------
# NFC tap
# -------------------------

@app.get("/tap/{card_id}")
def tap_card(card_id: str):
    try:
        # 1. Buscar la tarjeta
        response = (
            supabase
            .table("cards")
            .select("*")
            .eq("id", card_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Card not found"
            )

        card = response.data[0]

        # 2. Registrar el tap
        supabase.table("taps").insert({
            "card_id": card_id
        }).execute()

        # 3. Redirigir a Google Reviews
        return RedirectResponse(
            url=card["google_review_url"],
            status_code=307
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process tap: {str(e)}"
        )