from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.engine import get_engine

router = APIRouter()


@router.get("")
async def list_skills(domain: str | None = None):
    skills = get_engine().list_skills()
    if domain:
        skills = [s for s in skills if s["domain"] == domain]
    domains = sorted({s["domain"] for s in get_engine().list_skills()})
    return {"skills": skills, "domains": domains, "count": len(skills)}


@router.get("/{skill_id:path}")
async def get_skill(skill_id: str):
    skill = get_engine().get_skill(skill_id)
    if skill is None:
        raise HTTPException(404, "skill not found")
    return skill
