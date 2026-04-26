import logging

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.service import get_sync_state_service
from app.services.sync_state import SyncStateService


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/sync-state",
    summary="Получить SyncState для всех таблиц",
)
async def get_all(
    service: SyncStateService = Depends(get_sync_state_service),
):
    return await service.get_all()


@router.get(
    "/sync-state/{table_name}",
    summary="Получить SyncState для конкретной таблицы",
)
async def get_by_table(
    table_name: str,
    service: SyncStateService = Depends(get_sync_state_service),
):
    state = await service.get_by_table(table_name)
    if not state:
        raise HTTPException(status_code=404, detail="Table not found")
    return state


@router.put(
    "/sync-state/reset",
    summary="Сбросить SyncState для всех таблиц",
)
async def reset_all(
    service: SyncStateService = Depends(get_sync_state_service),
):
    return await service.reset_all()


@router.put(
    "/sync-state/{table_name}/reset",
    summary="Сбросить SyncState для конкретной таблицы",
)
async def reset_table(
    table_name: str,
    service: SyncStateService = Depends(get_sync_state_service),
):
    state = await service.reset_table(table_name)
    if not state:
        raise HTTPException(status_code=404, detail="Table not found")
    return state
