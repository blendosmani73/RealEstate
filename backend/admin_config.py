import os

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import User

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "blendosmani20@gmail.com").strip().lower()


def role_for_registration(email: str, requested_role: str) -> str:
    if email.strip().lower() == ADMIN_EMAIL:
        return "admin"
    if requested_role == "admin" and email.strip().lower() != ADMIN_EMAIL:
        return "user"
    return requested_role


def ensure_admin_account(db: Session) -> None:
    user = db.query(User).filter(func.lower(User.email) == ADMIN_EMAIL).first()
    if user is None:
        return
    if user.role != "admin":
        user.role = "admin"
        db.commit()
        print(f"Roli u përditësua në admin për: {user.email}")
