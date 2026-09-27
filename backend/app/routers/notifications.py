from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.notification import NotificationResponse, NotificationUnreadCount
from app.services import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
def get_my_notifications(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch paginated notifications for the currently authenticated user."""
    return notification_service.get_user_notifications(
        db=db, user_id=current_user.id, limit=limit, offset=offset
    )


@router.get("/unread-count", response_model=NotificationUnreadCount, status_code=status.HTTP_200_OK)
def get_my_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get total unread notification count for the currently authenticated user."""
    count = notification_service.get_unread_notification_count(db=db, user_id=current_user.id)
    return NotificationUnreadCount(unread_count=count)


@router.put("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read for the currently authenticated user."""
    updated_count = notification_service.mark_all_notifications_as_read(
        db=db, user_id=current_user.id
    )
    return {"message": "All notifications marked as read", "updated_count": updated_count}


@router.put("/{notification_id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a specific notification as read."""
    return notification_service.mark_notification_as_read(
        db=db, user_id=current_user.id, notification_id=notification_id
    )
