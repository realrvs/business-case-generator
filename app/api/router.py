from fastapi import APIRouter

from app.api.endpoints import (
    auth, health, projects, jira, analytics, ai, 
    jira_cloud, bottlenecks, executive_summary, reports,
    business_case
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(health.router)
router.include_router(projects.router)
router.include_router(jira.router)
router.include_router(analytics.router)
router.include_router(ai.router)
router.include_router(jira_cloud.router)
router.include_router(bottlenecks.router)
router.include_router(executive_summary.router)
router.include_router(reports.router)
router.include_router(business_case.router)
