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
