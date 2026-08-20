from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health() -> dict[str, str]:
    return {"status": "ok"}
