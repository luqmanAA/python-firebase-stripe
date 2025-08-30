import json
import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore


load_dotenv()


firebase_config = os.getenv("FIREBASE_CONFIG", {})
if not firebase_config:
    raise RuntimeError("FIREBASE_CONFIG environment variable not set")


firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()


def verify_firebase_token(id_token: str):
    """Verify Firebase ID Token and return user info"""
    try:
        decoded = auth.verify_id_token(id_token)
        user = auth.get_user(decoded["uid"])
        return {"uid": user.uid, "email": user.email}
    except Exception:
        return None


def set_user_subscription(uid: str, status: str):
    """Update user subscription status in Firestore"""
    doc_ref = db.collection("users").document(uid)
    doc_ref.set({"subscription_status": status}, merge=True)


def get_user_subscription(uid: str):
    """Get user subscription status from Firestore"""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("subscription_status", "free")
    return "free"
