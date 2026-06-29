from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Alert, User
from schemas import AlertCreate, AlertRead, AlertUpdate
from database import get_session
from security import get_current_user




router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(data: AlertCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    alert = Alert(
        symbol = data.symbol,
        condition = data.condition,
        threshold = data.threshold,
        user_id = user.id,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


@router.get("", response_model=list[AlertRead])
async def list_alerts(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    result = await session.execute(select(Alert).where(Alert.user_id == user.id))
    return result.scalars().all()


@router.get("/{alert_id}", response_model=AlertRead, status_code=status.HTTP_200_OK)
async def get_alert(alert_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    result = await session.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(
            404,
            detail="Alert not found"
        )
    return alert


@router.patch("/{alert_id}", response_model=AlertRead, status_code=status.HTTP_200_OK)
async def update_alert(alert_id: int, data: AlertUpdate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    result = await session.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(
            404,
            detail="Alert not found"
        )
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    await session.commit()
    await session.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    result = await session.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(
            404,
            detail="Alert not found"
        )
    await session.delete(alert)
    await session.commit()