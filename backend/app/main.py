import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
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
# Admin configuration
# -------------------------

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_USERNAME or ADMIN_PASSWORD is not configured")

security = HTTPBasic()

# -------------------------
# FastAPI
# -------------------------

app = FastAPI(
    title="ReviewTap API",
    version="0.1.0"
)

# -------------------------
# Admin authentication
# -------------------------

def verify_admin(
    credentials: HTTPBasicCredentials = Depends(security)
):
    if (
        credentials.username != ADMIN_USERNAME
        or credentials.password != ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


# -------------------------
# Card model
# -------------------------

class CardCreate(BaseModel):
    id: str
    google_review_url: str


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
# Create a card (ADMIN)
# -------------------------

@app.post("/cards")
def create_card(
    card: CardCreate,
    _: bool = Depends(verify_admin)
):
    try:

        # Check if the card already exists
        existing = (
            supabase
            .table("cards")
            .select("*")
            .eq("id", card.id)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=409,
                detail="Card already exists"
            )

        # Create the card
        response = (
            supabase
            .table("cards")
            .insert({
                "id": card.id,
                "google_review_url": card.google_review_url
            })
            .execute()
        )

        return {
            "message": "Card created successfully",
            "card": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create card: {str(e)}"
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