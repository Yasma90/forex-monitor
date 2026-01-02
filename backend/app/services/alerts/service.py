"""Alert service for CRUD operations"""

from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.alert import Alert, AlertHistory, AlertCreate, AlertUpdate, AlertStatus


class AlertService:
    """Service for managing alerts"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert(self, alert_data: AlertCreate, user_id: str = "default") -> Alert:
        """Create a new alert"""
        alert = Alert(
            name=alert_data.name,
            alert_type=alert_data.alert_type.value,
            base_currency=alert_data.base_currency,
            target_currency=alert_data.target_currency,
            threshold_value=alert_data.threshold_value,
            is_recurring=alert_data.is_recurring,
            cooldown_minutes=alert_data.cooldown_minutes,
            notify_push=alert_data.notify_push,
            notify_sound=alert_data.notify_sound,
            expires_at=alert_data.expires_at,
            user_id=user_id,
            status=AlertStatus.ACTIVE.value
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def get_all_alerts(self, user_id: str = "default", include_inactive: bool = False) -> list[Alert]:
        """Get all alerts for a user"""
        query = select(Alert).where(Alert.user_id == user_id)

        if not include_inactive:
            query = query.where(Alert.status == AlertStatus.ACTIVE.value)

        query = query.order_by(Alert.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_alert(self, alert_id: int, update_data: AlertUpdate) -> Optional[Alert]:
        """Update an alert"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if 'status' in update_dict and update_dict['status']:
            update_dict['status'] = update_dict['status'].value

        for key, value in update_dict.items():
            setattr(alert, key, value)

        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return False

        await self.db.delete(alert)
        await self.db.commit()
        return True

    async def mark_triggered(self, alert_id: int, trigger_value: float, message: str) -> None:
        """Mark an alert as triggered and log to history"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return

        # Update last triggered time
        alert.last_triggered_at = datetime.utcnow()

        # If not recurring, mark as triggered (inactive)
        if not alert.is_recurring:
            alert.status = AlertStatus.TRIGGERED.value

        # Add to history
        history = AlertHistory(
            alert_id=alert_id,
            trigger_value=trigger_value,
            message=message
        )
        self.db.add(history)

        await self.db.commit()

    async def get_alert_history(self, alert_id: Optional[int] = None, limit: int = 50) -> list[AlertHistory]:
        """Get alert trigger history"""
        query = select(AlertHistory).order_by(AlertHistory.triggered_at.desc()).limit(limit)

        if alert_id:
            query = query.where(AlertHistory.alert_id == alert_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def pause_alert(self, alert_id: int) -> Optional[Alert]:
        """Pause an alert"""
        return await self.update_alert(alert_id, AlertUpdate(status=AlertStatus.PAUSED))

    async def resume_alert(self, alert_id: int) -> Optional[Alert]:
        """Resume a paused alert"""
        return await self.update_alert(alert_id, AlertUpdate(status=AlertStatus.ACTIVE))
