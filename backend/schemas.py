from pydantic import BaseModel, Field


class ScoreItem(BaseModel):
    player_id: int
    rank: int | None = None
    score: int | None = None
    absent: bool = False


class ScoreSubmit(BaseModel):
    token: str
    judge_token: str | None = None
    results: list[ScoreItem] = Field(min_length=1)


class ScoreCorrection(BaseModel):
    operator_name: str = Field(min_length=1, max_length=60)
    reason: str = Field(min_length=1, max_length=300)
    results: list[ScoreItem] = Field(min_length=1)
