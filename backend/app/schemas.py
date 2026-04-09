from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    start: str = Field(..., description="Cidade de origem")
    goal: str = Field(..., description="Cidade de destino")
    algorithm: str = Field(..., description="ucs|dls|greedy|astar")
    depth_limit: int | None = Field(default=None, ge=1)


class RouteResponse(BaseModel):
    algorithm: str
    path: list[str] | None
    cost: float
    iterations: list[dict]
    metrics: dict


class CompareRequest(BaseModel):
    start: str
    goal: str
    depth_limit: int = Field(default=4, ge=1)


class AttractionsRequest(BaseModel):
    city: str
    model: str | None = None


class ManualPlateRequest(BaseModel):
    plate: str
