from fastapi import APIRouter, HTTPException
from database.dao import shows_dao, venues_dao, artists_dao
from utils.bson_utils import convert_objectid

router = APIRouter()


@router.get("/historical")
def get_historical_shows():
    try:
        shows = shows_dao.list_all()
        return {
            "data": convert_objectid(shows),
            "status": 200,
            "message": "Fetch concerts successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Fetching concerts failed",
                "error": str(e),
            },
        )



@router.get("/concerts")
def list_shows():
    try:
        return {
            "data": convert_objectid(shows_dao.list_all()),
            "status": 200,
            "message": "Fetch concerts successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Fetching concerts failed",
                "error": str(e),
            },
        )


@router.get("/artists")
def list_artists():
    try:
        return {
            "data": convert_objectid(artists_dao.list_all()),
            "status": 200,
            "message": "Fetch artists successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Fetching artists failed",
                "error": str(e),
            },
        )


@router.get("/unavailable-seats/{show_id}")
def get_unavailable_seats(show_id: str):
    try:
        seats = shows_dao.get_unavailable_seats(show_id)
        return {
            "data": seats,
            "status": 200,
            "message": "Fetch unavailable seats successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"data": None, "message": "Fetching unavailable seats failed", "error": str(e)},
        )


@router.get("/venues")
def list_venues():
    try:
        return {
            "data": convert_objectid(venues_dao.list_all()),
            "status": 200,
            "message": "Fetch venues successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"data": None, "message": "Fetching venues failed", "error": str(e)},
        )
