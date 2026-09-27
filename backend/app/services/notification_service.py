from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str) -> Notification:
    """Helper function that generates and persists an in-app notification record."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        is_read=False
    )
    db.add(notif)
    return notif


def get_user_notifications(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Notification]:
    """Fetch paginated notifications for a given user ordered by newest first."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_unread_notification_count(db: Session, user_id: int) -> int:
    """Return count of unread notifications for a given user."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .count()
    )


def mark_notification_as_read(db: Session, user_id: int, notification_id: int) -> Notification:
    """Mark a single notification as read for a specific user."""
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found."
        )
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a specific user."""
    updated_count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .update({Notification.is_read: True}, synchronize_session=False)
    )
    db.commit()
    return updated_count
