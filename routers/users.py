from fastapi import APIRouter, Depends

from models import User
from schemas import UserRead
from security import get_current_user




router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(get_current_user)):
    return user