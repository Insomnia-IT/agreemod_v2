from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_sqla_session
from app.services.badge import BadgeService
from app.services.feeder import FeederService
from app.services.sync_state import SyncStateService


def get_badge_service(session: AsyncSession = Depends(get_sqla_session)):
    return BadgeService(session)


def get_feeder_service(session: AsyncSession = Depends(get_sqla_session)):
    return FeederService(session)


def get_sync_state_service(session: AsyncSession = Depends(get_sqla_session)):
    return SyncStateService(session)
