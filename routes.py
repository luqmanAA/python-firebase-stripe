from fastapi import Depends, Request, HTTPException, Body, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from firebase.utils import verify_firebase_token
from helpers import verify_headers
from services import SubscriptionService, get_context_keys

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    context = get_context_keys()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            **context
        }
    )


@router.post("/verify-token/")
async def verify_token(payload: dict = Body(...)):
    id_token = payload.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing ID token")

    user_info = verify_firebase_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_info


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    return await SubscriptionService.create_stripe_subscription(request)


@router.get("/success", response_class=HTMLResponse)
async def success(request: Request, session_id: str = None):
    if not session_id:
        return HTMLResponse("<h1>Missing session ID!</h1>", status_code=400)

    await SubscriptionService.store_user_subscription(session_id)
    return templates.TemplateResponse("success.html", {"request": request})


@router.get("/cancel", response_class=HTMLResponse)
async def cancel(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})


@router.get("/me/subscription")
async def get_subscription(user=Depends(verify_headers)):
    return await SubscriptionService.get_user_subscription(user)
