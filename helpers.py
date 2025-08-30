from fastapi import Header, HTTPException

from firebase.utils import verify_firebase_token


def verify_headers(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header")

        return verify_firebase_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
