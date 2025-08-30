import os
import stripe
from fastapi import FastAPI, Depends, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import firestore
from pydantic import BaseModel
from starlette.responses import JSONResponse

from firebase.utils import verify_firebase_token, set_user_subscription

# ---------- Stripe Setup ----------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
YOUR_DOMAIN = "http://localhost:8000"


# ---------- FastAPI App ----------
app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ---------- Models ----------
class User(BaseModel):
    email: str
    password: str


# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            'publishable_key': os.getenv("STRIPE_PUBLISHABLE_KEY"),
            'firebase_api_key': os.getenv("FIREBASE_API_KEY"),
            'firebase_auth_domain': os.getenv("FIREBASE_AUTH_DOMAIN"),
            'firebase_project_id': os.getenv("FIREBASE_PROJECT_ID")
        }
    )


@app.post("/verify-token/")
async def verify_token(payload: dict = Body(...)):
    id_token = payload.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing ID token")

    user_info = verify_firebase_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_info


@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        body = await request.json()
        id_token = body.get("id_token")
        user = verify_firebase_token(id_token)

        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": os.getenv("STRIPE_PRICE_ID"), "quantity": 1}],
            success_url=str(request.base_url) + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=str(request.base_url) + "cancel",
            metadata={"firebase_uid": user["uid"]}
        )

        return {"url": session.url}
    except Exception as e:
        print(str(e))
        return JSONResponse(status_code=400, content={"error": 'Something went wrong'})


@app.get("/success", response_class=HTMLResponse)
async def success(request: Request, session_id: str = None):
    if not session_id:
        return HTMLResponse("<h1>Missing session ID!</h1>", status_code=400)

    # Retrieve session from Stripe
    session = stripe.checkout.Session.retrieve(session_id)

    # Retrieve subscription
    subscription_id = session.get("subscription")
    subscription = stripe.Subscription.retrieve(subscription_id)

    # Save in Firebase

    db = firestore.client()
    uid = session["metadata"]["firebase_uid"]
    db.collection("users").document(uid).set({
        "subscription": {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_start": subscription["items"]["data"][0].current_period_start,
            "current_period_end": subscription["items"]["data"][0].current_period_end,
            "plan": subscription["items"]["data"][0]["price"]["nickname"]
        }
    }, merge=True)
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/cancel", response_class=HTMLResponse)
async def cancel(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})


@app.get("/me/subscription")
async def get_subscription(request: Request, user=Depends(verify_firebase_token)):
    db = firestore.client()
    doc = db.collection("users").document(user["uid"]).get()
    if not doc.exists:
        return {"subscription": None}

    return {"subscription": doc.to_dict().get("subscription")}
