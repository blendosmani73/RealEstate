from fastapi import HTTPException, status

from database import Property, User


def can_modify_property(user: User, prop: Property) -> bool:
    if user.role == "admin":
        return True
    if prop.created_by_id is None:
        return False
    return prop.created_by_id == user.id


def require_property_modify(user: User, prop: Property) -> None:
    if can_modify_property(user, prop):
        return
    if prop.created_by_id is None:
        detail = "Vetëm administratori mund të ndryshojë pronat e importuara nga sistemi (ETL)."
    else:
        detail = "Mund të ndryshoni vetëm pronat që keni shtuar ju."
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
