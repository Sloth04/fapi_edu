from typing import List

from fastapi import HTTPException, Depends

from app import schemas
from app.internal import get_current_active_user


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")


allow_create_and_delete_resource = RoleChecker(["admin"])
