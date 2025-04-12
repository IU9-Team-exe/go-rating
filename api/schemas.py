from pydantic import BaseModel, Field
from typing import List

class GameInput(BaseModel):
    opp_rating: float = Field(..., description="Рейтинг оппонента")
    opp_rd: float = Field(..., description="RD оппонента")
    result: float = Field(..., description="Результат от лица игрока")

class UpdateRequest(BaseModel):
    rating: float = Field(..., description="Рейтинг игрока")
    rd: float = Field(..., description="RD игрока")
    volatility: float = Field(..., description="Волатильность игрока")
    games: List[GameInput]

class UpdateResponse(BaseModel):
    new_rating: float
    new_rd: float
    new_volatility: float
