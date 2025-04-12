from fastapi import APIRouter, HTTPException
from api.schemas import UpdateRequest, UpdateResponse
from services.rating_logic import update_player_rating
import numpy as np

router = APIRouter()

@router.post("/update", response_model=UpdateResponse)
def update_rating(request: UpdateRequest):
    if len(request.games) == 0:
        return UpdateResponse(
            new_rating=request.rating,
            new_rd=request.rd,
            new_volatility=request.volatility
        )

    try:
        opp_ratings = [g.opp_rating for g in request.games]
        opp_rds = [g.opp_rd for g in request.games]
        results = [g.result for g in request.games]

        new_rating, new_rd, new_vol = update_player_rating(
            request.rating, request.rd, request.volatility,
            np.array(opp_ratings),
            np.array(opp_rds),
            np.array(results)
        )

        return UpdateResponse(
            new_rating=new_rating,
            new_rd=new_rd,
            new_volatility=new_vol
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
