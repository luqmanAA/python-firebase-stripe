import os

import stripe
from firebase_admin import firestore
from starlette.responses import JSONResponse

from firebase.utils import verify_firebase_token

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def get_context_keys():
    return {
        'publishable_key': os.getenv("STRIPE_PUBLISHABLE_KEY"),
        'firebase_api_key': os.getenv("FIREBASE_API_KEY"),
        'firebase_auth_domain': os.getenv("FIREBASE_AUTH_DOMAIN"),
        'firebase_project_id': os.getenv("FIREBASE_PROJECT_ID")
    }


class SubscriptionService:

    @staticmethod
    async def create_stripe_subscription(request):
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

    @staticmethod
    async def store_user_subscription(session_id):
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

    @staticmethod
    async def get_user_subscription(user):
        db = firestore.client()
        doc = db.collection("users").document(user["uid"]).get()
        if not doc.exists:
            return {"subscription": []}

        return {"subscription": doc.to_dict().get("subscription")}
