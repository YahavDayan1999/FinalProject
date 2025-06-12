from fastapi import APIRouter, Query, Body, HTTPException, Depends
import math
from utils.middlewares import get_current_user
from database.dao import venues_dao, artists_dao, shows_dao, user_dao, purchase_dao
from data.show_data import Show, Artist, Venue, VenueUpdate, ArtistUpdate, ShowUpdate

router = APIRouter()


@router.get("/sales/{show_id}")
def view_sales(show_id: str):
    show = shows_dao.get_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    base_price = show["price"]
    sold = show.get("sold_tickets", 0)
    cap = venues_dao.get_by_id(show["venue"])["capacity"]
    demand = (sold / cap) * 100 if cap else 0

    if demand >= 90:
        price = base_price * 1.4
    elif demand >= 75:
        price = base_price * 1.2
    elif demand >= 50:
        price = base_price * 1.1
    else:
        price = base_price

    revenue = sold * price
    return {
        "show": f"{artists_dao.get_by_id(show['artist'])['name']} at {venues_dao.get_by_id(show['venue'])['name']} on {show['date']}",
        "revenue": round(revenue, 2),
        "sold_tickets": sold,
    }


@router.post("/recommend-pricing")
def recommend_dynamic_pricing(
    artist_name: str = Body(embed=True)
):
    prices = []
    artists = artists_dao.list_all()
    artists_map = {str(artist["_id"]): artist for artist in artists}
    venues = venues_dao.list_all()
    venues_map = {str(venue["_id"]): venue for venue in venues}
    shows = shows_dao.list_all()
    for show in shows:
        purchases = purchase_dao.get_show_purchases(str(show["_id"]))
        artist = artists_map.get(str(show["artist"]))
        venue = venues_map.get(str(show["venue"]))

        if not artist or not venue:
            continue
        if (
            (not artist_name or artist_name.lower() == artist["name"].lower())
        ):
            price = show["price"]
            sold = len(purchases)
            cap = venue["seats"] * venue["rows"]
            demand = (sold / cap) * 100 if cap else 0
            if demand >= 90:
                price *= 1.4
            elif demand >= 75:
                price *= 1.2
            elif demand >= 50:
                price *= 1.1
            prices.append(price)

    if not prices:
        return {"suggestion": None, "max": None}

    avg = sum(prices) / len(prices)
    return {"suggestion": round(avg * 0.9, 2), "max": round(max(prices) * 1.1, 2)}


@router.delete("/concerts/{concert_id}")
def delete_concert(concert_id: str):
    try:
        # Call the DAO to delete the concert by ID
        result = shows_dao.delete(concert_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Concert not found")
        return {"status": 200, "message": "Concert deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"message": "Failed to delete concert", "error": str(e)},
        )


@router.delete("/venues/{venue_id}")
def delete_venue(venue_id: str):
    try:
        # Call the DAO to delete the venue by ID
        result = venues_dao.delete(venue_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        return {"status": 200, "message": "Venue deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"message": "Failed to delete venue", "error": str(e)},
        )


@router.delete("/artists/{artist_id}")
def delete_artist(artist_id: str):
    try:
        # Call the DAO to delete the artist by ID
        result = artists_dao.delete(artist_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Artist not found")
        return {"status": 200, "message": "Artist deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"message": "Failed to delete artist", "error": str(e)},
        )


@router.post("/venues")
def create_venue(venue: Venue):
    try:
        rows = math.isqrt(venue.capacity)
        seats_per_row = math.ceil(venue.capacity / rows)
        venue_data = venue.model_dump()
        venue_data.update({"rows": rows, "seats": seats_per_row})
        new_id = venues_dao.create(venue_data)
        return {
            "data": {
                "_id": str(new_id),
                "name": venue.name,
                "capacity": venue.capacity,
                "rows": venue_data["rows"],
                "seats": venue_data["seats"],
            },
            "status": 200,
            "message": "Created venue succesfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"data": None, "message": "Failed to create venue", "error": str(e)},
        )


@router.post("/artists")
def create_artist(artist: Artist):
    try:
        artist_data = artist.model_dump()
        new_id = artists_dao.create(artist_data)
        return {
            "data": {"genre": artist.genre, "name": artist.name, "_id": str(new_id)},
            "status": 200,
            "message": "Created artist successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Failed to create artist",
                "error": str(e),
            },
        )


@router.post("/concerts")
def create_show(show: Show):
    show_data = show.model_dump()
    new_id = shows_dao.create(show_data)
    return {
        "data": {
            "_id": str(new_id),
            "artist": show.artist_id,
            "venue": show.venue_id,
            "price": show.price,
            "base_price": show.price,
            "date": show.date,
        },
        "status": 200,
        "message": "Created concert successfully",
    }



@router.put("/artists/{artist_id}")
def update_artist(artist_id: str, artist: Artist):
    try:
        artist_update = ArtistUpdate(
            name=artist.name,
            genre=artist.genre
        )
        result = artists_dao.update(artist_id, artist_update)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Artist not found")
        return {
            "data": {
                "genre": artist.genre,
                "name": artist.name,
                "_id": artist_id
            },
            "status": 200,
            "message": "Updated artist successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Failed to update artist",
                "error": str(e),
            },
        )


@router.put("/venues/{venue_id}")
def update_venue(venue_id: str, venue: Venue):
    try:
        rows = math.isqrt(venue.capacity)
        seats_per_row = math.ceil(venue.capacity / rows)
        venue_update = VenueUpdate(
            name=venue.name,
            capacity=venue.capacity,
            rows=rows,
            seats=seats_per_row
        )
        result = venues_dao.update(venue_id, venue_update)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        return {
            "data": {
                "_id": venue_id,
                "name": venue.name,
                "capacity": venue.capacity,
                "rows": rows,
                "seats": seats_per_row,
            },
            "status": 200,
            "message": "Updated venue successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Failed to update venue",
                "error": str(e),
            },
        )


@router.put("/concerts/{concert_id}")
def update_concert(concert_id: str, show: Show):
    try:
        show_update = ShowUpdate(
            artist_id=show.artist_id,
            venue_id=show.venue_id,
            price=show.price,
            date=show.date
        )
        result = shows_dao.update(concert_id, show_update)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Concert not found")
        return {
            "data": {
                "_id": concert_id,
                "artist": show.artist_id,
                "venue": show.venue_id,
                "price": show.price,
                "base_price": show.price,
                "date": show.date,
            },
            "status": 200,
            "message": "Updated concert successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Failed to update concert",
                "error": str(e),
            },
        )


@router.get("/purchases")
def get_purchases():
    try:
        purchases = user_dao.get_all_purchases()
        return {
            "status": 200,
            "message": "Purchases fetched successfully",
            "data": purchases,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"data": None, "message": "Fetching purchases failed", "error": str(e)})