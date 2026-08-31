import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
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
    raise RuntimeError(
        "ADMIN_USERNAME or ADMIN_PASSWORD is not configured"
    )

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
    business_name: str
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
# Admin page
# -------------------------

@app.get("/admin", response_class=HTMLResponse)
def admin_page(_: bool = Depends(verify_admin)):

    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>ReviewTap Admin</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                max-width: 500px;
                margin: 60px auto;
                padding: 20px;
                background: #f5f5f5;
            }

            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                margin-top: 0;
            }

            label {
                display: block;
                margin-top: 20px;
                margin-bottom: 6px;
                font-weight: bold;
            }

            input {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 16px;
            }

            button {
                width: 100%;
                margin-top: 25px;
                padding: 13px;
                background: #111;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                background: #333;
            }

            #result {
                margin-top: 20px;
                padding: 12px;
                border-radius: 6px;
                display: none;
            }

            .success {
                background: #d4edda;
                color: #155724;
            }

            .error {
                background: #f8d7da;
                color: #721c24;
            }

        </style>

    </head>


    <body>

        <div class="container">

            <h1>ReviewTap Admin</h1>

            <p>Create a new NFC card.</p>


            <form id="cardForm">


                <!-- Card ID -->

                <label for="card_id">
                    Card ID
                </label>

                <input
                    type="text"
                    id="card_id"
                    name="card_id"
                    placeholder="NFC-9999"
                    required
                >


                <!-- Business Name -->

                <label for="business_name">
                    Business Name
                </label>

                <input
                    type="text"
                    id="business_name"
                    name="business_name"
                    placeholder="The Dublin Pub"
                    required
                >


                <!-- Google Review URL -->

                <label for="google_review_url">
                    Google Review URL
                </label>

                <input
                    type="url"
                    id="google_review_url"
                    name="google_review_url"
                    placeholder="https://g.page/r/..."
                    required
                >


                <button type="submit">
                    Create Card
                </button>

            </form>


            <div id="result"></div>

        </div>


        <script>

            const form = document.getElementById("cardForm");

            const result = document.getElementById("result");


            form.addEventListener("submit", async (event) => {

                event.preventDefault();

                result.style.display = "none";


                const cardId =
                    document.getElementById("card_id").value;

                const businessName =
                    document.getElementById("business_name").value;

                const googleReviewUrl =
                    document.getElementById("google_review_url").value;


                try {

                    const response = await fetch("/cards", {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({

                            id: cardId,

                            business_name: businessName,

                            google_review_url: googleReviewUrl

                        })

                    });


                    const data = await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.detail || "Failed to create card"
                        );

                    }


                    result.className = "success";

                    result.style.display = "block";

                    result.textContent =
                        "Card created successfully: " + cardId;


                    form.reset();


                } catch (error) {

                    result.className = "error";

                    result.style.display = "block";

                    result.textContent = error.message;

                }

            });

        </script>

    </body>

    </html>
    """


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

                "business_name": card.business_name,

                "google_review_url": card.google_review_url,

                "status": "assigned"

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