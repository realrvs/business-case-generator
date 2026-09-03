# -*- coding: utf-8 -*-
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check():
    return {"status": "ok", "service": "business-case-generator"}

@router.get("/readiness")
async def readiness():
    return {"status": "ready"}
