"""Additional v0.2 API router. Mounted separately to preserve v0.1."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator
from .multi_optimizer import Clinician, Visit, optimize, sample

router = APIRouter(prefix="/api/v2", tags=["v0.2"])


class VisitModel(BaseModel):
    id: str = Field(min_length=1)
    x: float
    y: float
    earliest: int = Field(ge=0, le=1440)
    latest: int = Field(ge=0, le=1440)
    duration: int = Field(default=30, ge=1, le=480)


class ClinicianModel(BaseModel):
    id: str = Field(min_length=1)
    x: float = 0
    y: float = 0
    shift_start: int = Field(default=540, ge=0, le=1440)
    shift_end: int = Field(default=1080, ge=0, le=1440)


class OptimizeRequest(BaseModel):
    visits: list[VisitModel] = Field(max_length=100)
    clinicians: list[ClinicianModel] = Field(min_length=1, max_length=20)


@router.get("/sample")
def get_sample():
    visits, clinicians = sample()
    return {"data_type": "synthetic", "visits": [vars(v) for v in visits],
            "clinicians": [vars(c) for c in clinicians], "result": optimize(visits, clinicians)}


@router.post("/optimize")
def post_optimize(payload: OptimizeRequest):
    try:
        return {"data_type": "synthetic_or_user_supplied",
                "result": optimize([Visit(**v.model_dump()) for v in payload.visits],
                                   [Clinician(**c.model_dump()) for c in payload.clinicians])}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
